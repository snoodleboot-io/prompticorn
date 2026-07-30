# Test suite

Layout:

- `tests/unit/` — fast, isolated tests (builders, questions, registry, IR, UI).
- `tests/integration/` — end-to-end flows: `init` question pipeline → config → per-tool build.
- `tests/slow/` — long-running / large-fanout checks.
- `tests/security/` — security-focused checks.

## Testing strategies

### Value coverage (`integration/test_value_coverage_matrix.py`)

Proves that a value chosen in the `init` flow actually reaches generated output,
for **every** supported tool — closing two blind spots that per-builder tests
miss:

- **collected-but-never-applied** — an answer stored under a key no template
  reads (the historical `go_version` → `version` bug).
- **placeholder-never-fed / leaked** — a template var shipped unsubstituted for
  some builders (e.g. `{{PRIMARY_AGENTS_LIST}}`).

It drives the real single-language question flow with **non-default** answers and
a sentinel-injected config, then asserts, per tool: build succeeds, each chosen
answer maps to the right spec key, each literal value renders, nothing leaks, and
every collected key is classified. Known-open defects are pinned with `strict`
`xfail` markers tied to their Linear ticket — a fix flips the marker to an
unexpected pass, which fails the suite and signals the marker's removal.

Reusable seam: `select_from_answers({question_text: option})` builds a UI
selector that drives the flow from an explicit answer map without touching the
interactive Click command.

### Golden output corpus (`tests/golden/manifest.json`)

The pre-refactor baseline for the content-resolution seam. Snapshots every
builder's generated file tree across **tool × variant × repository-type ×
language** — 136 cells — as `{relative_path: sha256}`, with ISO dates normalized
so the corpus is stable across day boundaries and filesystem ordering.

Hashes rather than file bodies: the matrix is ~10,700 files, which is not
something to commit. A mismatch therefore reports *which* paths were added,
removed, or changed — not line-level content. Regenerate and inspect the working
tree for that.

Split across two jobs so a common-path regression fails fast:

| | Scope | Runtime |
|---|---|---|
| `unit/test_tool_output_golden.py` | `python-single` only, 34 cells | ~35s |
| `slow/test_golden_corpus_matrix.py` | the full 136-cell matrix | ~2m40s |

Both read the same corpus. The matrix definition lives in `tests/golden_corpus.py`.

**Regenerating** — only when output changes intentionally:

```bash
uv run python -m tests.golden_corpus
git diff -- tests/golden/manifest.json
```

Never regenerate to make a failing refactor pass. Read the reported diff first
and confirm every changed path is one you meant to change.
