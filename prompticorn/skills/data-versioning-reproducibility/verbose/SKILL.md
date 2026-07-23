# Data Versioning Reproducibility (Verbose)

## Core Patterns

### Code Versioning Alone Is Not Reproducibility

A git SHA pins the transformation. It says nothing about what went into it. Check
out the commit that produced last quarter's model, rerun the pipeline, and the job
reads the *current* tables — with three months of new rows, a corrected billing
field, and a column that was backfilled in April. The output is different, and
nothing under version control can tell you why.

The claim "our pipeline is reproducible because it's in git" is therefore usually
false. Reproducibility of a result requires pinning four things:

| Dimension | Pinned by | Common failure |
|---|---|---|
| Code | Git commit SHA | Usually handled |
| Data | Content hash or snapshot id | Usually missing |
| Environment | Lockfile + image digest | Pinned by mutable tag |
| Randomness | Recorded seeds + determinism flags | Partially set, never recorded |

Miss any one and the result is not regenerable. In practice teams handle the first
and fail the other three.

### Content Addressing

Content addressing means the identifier of a dataset is a hash of its bytes. Two
useful properties follow. Identical content has one identifier regardless of path
or storage system, so deduplication is free. And any mutation changes the
identifier, so a silent in-place edit cannot masquerade as the same version.

```bash
dvc add data/raw/transactions.parquet
# -> data/raw/transactions.parquet.dvc  (small text file with the content hash)
git add data/raw/transactions.parquet.dvc data/raw/.gitignore
git commit -m "pin transactions snapshot 2026-07"
dvc push                       # bytes go to remote object storage

# On another machine, at any commit:
git checkout <sha> && dvc checkout    # exactly the bytes that commit was built on
```

Git holds the pointer; object storage holds the bytes. That split is the whole
trick — the repository stays small while every commit still names an exact dataset.

The critical distinction, stated plainly: `s3://bucket/data/latest.parquet` is a
*variable*. `md5:8f14e45fceea167a` is a *value*. Pipelines that reference the
former have no reproducibility story, no matter how carefully the code is reviewed.

| Approach | Best for | Watch out for |
|---|---|---|
| DVC | Files/directories alongside code | Needs a configured remote; not a warehouse tool |
| Git LFS | Small-to-medium binary assets | Poor fit above a few GB |
| Delta / Iceberg / Hudi | Warehouse tables | Retention policy can expire old snapshots |
| lakeFS | Whole-bucket branching semantics | Extra infrastructure to operate |
| Immutable date partitions | Append-only event data | Breaks the moment anyone backfills |

### Snapshots for Warehouse Data

Copying a 4 TB table per experiment is not viable. Open table formats solve this
with a transaction log: each commit produces a snapshot id, and reading an old
snapshot costs nothing extra because the underlying files are still there.

```sql
-- Delta Lake
select * from orders version as of 1042;
select * from orders timestamp as of '2026-03-15 00:00:00';

-- Iceberg
select * from orders for system_version as of 3821497;
select * from orders for system_time as of '2026-03-15 00:00:00';
```

Two operational cautions. First, **retention expires history**: Delta's
`VACUUM` and Iceberg's snapshot expiration delete the files old snapshots point to,
and your seven-day default silently makes six-month-old references unresolvable.
Set retention against your actual audit and reproduction window. Second, prefer
`version as of` over `timestamp as of` when recording provenance — a version id is
exact, whereas the timestamp form resolves to whatever snapshot was current then
and depends on the same history surviving.

For how the underlying files should be laid out, see `data-partitioning`; for
handling entity history within a table, see `slowly-changing-dimensions`.

### The Run Manifest

Every meaningful run emits one record binding inputs to output. This is the artifact
that answers "what produced this?" without archaeology.

```python
import hashlib, json, subprocess
from pathlib import Path

def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"

manifest = {
    "run_id": run_id,
    "git_sha": subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip(),
    "git_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"])),
    "inputs": {
        "transactions": file_hash("data/raw/transactions.parquet"),
        "orders_snapshot": delta_table.history(1).collect()[0]["version"],
    },
    "params": {"seed": 42, "max_depth": 8, "learning_rate": 0.05},
    "env": {
        "image": "registry/trainer@sha256:2b7c9f...",
        "lockfile": file_hash("uv.lock"),
    },
    "outputs": {"model": "s3://models/churn/v14/model.pkl"},
    "metrics": {"auc": 0.874, "n_train": 1_284_119},
}
Path(f"runs/{run_id}.json").write_text(json.dumps(manifest, indent=2, sort_keys=True))
```

Record `git_dirty`. A run from a working tree with uncommitted changes is not
reproducible from its SHA, and knowing that at read time is far better than
discovering it during an incident.

### Pipeline-Level Locking

DVC's pipeline stages give you a make-like dependency graph with content hashes on
both sides, so `dvc repro` re-executes only what actually changed.

```yaml
# dvc.yaml
stages:
  featurize:
    cmd: python src/featurize.py
    deps:
      - src/featurize.py
      - data/raw/transactions.parquet
    outs:
      - data/processed/features.parquet
  train:
    cmd: python src/train.py --seed 42
    deps:
      - src/train.py
      - data/processed/features.parquet
    params:
      - train.max_depth
      - train.learning_rate
    outs:
      - models/model.pkl
    metrics:
      - metrics.json:
          cache: false
```

`dvc.lock` — generated, committed — records the resolved hash of every dependency
and output for the last successful run. That file is the lockfile for your data the
way `uv.lock` is for your dependencies, and it is what makes "reproduce commit
`4c1e9b2`" a mechanical operation rather than a research project.

### Determinism

Pinned inputs do not give identical outputs if the process itself is random.

```python
import os, random
import numpy as np
import torch

SEED = 42
os.environ["PYTHONHASHSEED"] = str(SEED)   # must be set before interpreter start
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
torch.use_deterministic_algorithms(True)   # raises on non-deterministic kernels
torch.backends.cudnn.benchmark = False     # autotuner picks varying algorithms
```

Sources of nondeterminism that survive seeding:

- **GPU reductions** — floating-point addition is not associative, and parallel
  reduction order varies between runs. Deterministic modes exist and cost 5–30%.
- **Thread count** — a parallel sum over 8 threads and over 16 threads give
  slightly different floats. Pin thread counts for bit-exact requirements.
- **`PYTHONHASHSEED`** — set inside the process is too late; string hashing is
  already randomized. Set it in the environment before launch.
- **Unordered queries** — `LIMIT` or `SAMPLE` without a total `ORDER BY` returns
  different rows across runs. Any query feeding a hashed artifact needs a
  deterministic total order.
- **Wall-clock in features** — `now()` inside a transformation makes output a
  function of run time. Pass an explicit `as_of` parameter instead.
- **Dict/set iteration across processes**, parallel file listing order, and
  filesystem-dependent `glob` ordering.

Decide the standard you need. **Bit-exact** reproduction is expensive and rarely
required. **Statistically equivalent** — metrics within a stated tolerance — is
usually the honest target, and should be written down as one, e.g. "AUC reproduces
within ±0.002."

### Environment

```dockerfile
FROM python:3.11-slim@sha256:9c1f...    # digest, not a tag
COPY uv.lock pyproject.toml ./
RUN uv sync --frozen                    # fail if the lock does not satisfy the spec
```

A `>=1.2` range resolves differently over time, and minor releases of numerical
libraries do change results. `--frozen` (or `poetry install --no-update`) makes
drift a build failure rather than a silent behavior change. Pin the base image by
digest: `python:3.11-slim` is republished and is not a version.

### Verify by Actually Reproducing

A reproducibility system that has never been exercised does not work — the failure
is always something nobody anticipated, like an expired snapshot or a
`PYTHONHASHSEED` set too late. Schedule the check:

```
Quarterly: pick a shipped model. From its manifest alone, on a clean machine,
rebuild it. Compare metrics against the recorded values within tolerance.
Record what was missing. Fix that gap.
```

## Common Anti-Patterns

❌ **Referencing data by mutable path** (`s3://bucket/latest/`) — the identifier
changes meaning without notice.
✅ Content hash or snapshot id, recorded in the run manifest.

❌ **Pinning code but not data** — "reproducible" is then simply untrue.
✅ Pin code, data, environment, and seeds together.

❌ **`timestamp as of` as the recorded provenance.**
✅ Record the exact version/snapshot id; timestamps depend on surviving history.

❌ **Default snapshot retention on a table you need to reproduce from.**
✅ Set retention to cover your audit and reproduction window explicitly.

❌ **Copying datasets into `_v2`, `_v2_final`, `_v2_final_fixed`.**
✅ One logical path, versioned by content; the pointer lives in git.

❌ **Seeds set but never recorded** — you cannot rerun with a seed you did not log.
✅ Seed is a parameter in the manifest, not a constant buried in the script.

❌ **Dependency ranges and `latest` image tags.**
✅ Committed lockfile and an image digest.

❌ **`LIMIT` or `SAMPLE` without a total `ORDER BY` upstream of a hashed output.**
✅ Deterministic total ordering on anything feeding a versioned artifact.

❌ **Assuming reproducibility because the tooling is installed.**
✅ Periodically rebuild a shipped artifact from its manifest and compare.

## Reproducibility Checklist

- [ ] Every dataset referenced by content hash or snapshot id, never a mutable path
- [ ] Data pointers (`.dvc`, `dvc.lock`) committed to git
- [ ] Warehouse reads pinned to an explicit table version
- [ ] Snapshot retention set to cover the required reproduction window
- [ ] Run manifest emitted with code SHA, input hashes, params, env, metrics
- [ ] Working-tree-dirty flag captured in the manifest
- [ ] All seeds set and recorded as parameters
- [ ] Determinism flags enabled where bit-exactness is required
- [ ] `PYTHONHASHSEED` set in the environment, before process start
- [ ] No wall-clock calls inside transformations; `as_of` passed explicitly
- [ ] Total `ORDER BY` on any query feeding a versioned artifact
- [ ] Dependency lockfile committed and installs run frozen
- [ ] Container base image pinned by digest
- [ ] Reproduction tolerance stated explicitly (bit-exact vs metric tolerance)
- [ ] A past artifact has been rebuilt from its manifest and verified
