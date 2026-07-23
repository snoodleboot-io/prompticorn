# Data Versioning Reproducibility (Minimal)

## Purpose
Make any past result — a model, a report, a number in a board deck — regenerable months later, by pinning the data as rigorously as the code.

## Core Techniques

### 1. Versioning Code Without Versioning Data Makes "Reproducible" False
A git SHA identifies the transformation, not the input. Check out last quarter's commit, rerun the job, and you read today's tables — new rows, corrected values, a backfilled column. The output differs and nothing in your version control can explain why.

Reproducibility requires pinning **both**: the code SHA and an identifier for the exact bytes that went in.

### 2. Content-Address the Data, Then Lock It
Hash the content; the hash is the version. Identical bytes get one identifier no matter where they live, and any mutation produces a different one — so silent edits are impossible to miss.

```bash
dvc add data/raw/transactions.parquet
# writes transactions.parquet.dvc containing the content hash; commit that file
git add data/raw/transactions.parquet.dvc data/raw/.gitignore
git commit -m "pin transactions snapshot"

dvc checkout   # later, on any machine: fetches the exact bytes for this commit
```

The `.dvc` file is the lockfile: small, text, in git, and it names content rather than a mutable path. `s3://bucket/latest.parquet` is not a version — it is a variable.

### 3. Prefer Table Formats With Snapshot Isolation for Warehouse Data
Copying a 4 TB table is not versioning. Delta Lake, Iceberg, and Hudi keep a transaction log, so a snapshot id names the exact state at negligible cost.

```sql
select * from orders version as of 1042;
select * from orders timestamp as of '2026-03-15 00:00:00';
```

Record the snapshot id in the run manifest. "We trained on `orders` snapshot 1042" is reproducible; "we trained on `orders` in March" is not.

### 4. Emit a Run Manifest
Every training run, report, or scheduled job writes one record tying all inputs to the output.

```json
{"run_id":"2026-07-19T02:14Z-a91f","git_sha":"4c1e9b2",
 "data":{"transactions":"md5:8f14e45fceea167a","orders_snapshot":1042},
 "params":{"seed":42,"max_depth":8},
 "env":"sha256:2b7c...","output":"model:s3://models/churn/v14",
 "metrics":{"auc":0.874}}
```

Without this the question "what produced this model?" is answered by archaeology through Slack.

### 5. Control the Sources of Nondeterminism
Pinning inputs is not enough if the process is random. Set every seed, and know that some remain: GPU kernel nondeterminism, `set`/dict iteration ordering across processes, thread-scheduling-dependent float reduction ordering, and `LIMIT` without `ORDER BY`.

```python
random.seed(42); np.random.seed(42); torch.manual_seed(42)
torch.use_deterministic_algorithms(True)   # slower; raises on non-deterministic ops
```

Any query feeding a versioned artifact needs a total `ORDER BY` — otherwise identical inputs produce differently ordered output and different hashes.

### 6. Pin the Environment Too
A dependency resolved as `>=1.2` will resolve differently next year and can change numerical output. Commit a resolved lockfile (`uv.lock`, `poetry.lock`) and pin the container by digest, not by the `latest` tag.

## Warning Signs

- Data referenced by mutable path (`.../latest/`, `.../current/`)
- Training input described as "the customers table" with no snapshot or hash
- No record of which data produced a deployed model
- Seeds set in some places, not others; no seed recorded in the run metadata
- Environment pinned by tag rather than digest, or by an unresolved range
- Datasets copied to `_v2`, `_v2_final`, `_v2_final_fixed` directories
- Nobody has actually attempted to reproduce a past result end to end
