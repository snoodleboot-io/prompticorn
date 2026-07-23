# MLOps Pipeline Design (Minimal)

## Purpose
Design the automated path from raw data to a registered, deployable model — reproducibly, so any past model can be rebuilt from what you recorded.

## Core Techniques

### 1. Version the Data and the Code Together
A pipeline is only reproducible if a single identifier pins *both*. Git alone pins the code; the same code over new data is a different model.

```python
run_id = registry.log_run(
    git_sha="8e1c3af",
    dataset_uri="s3://lake/churn/snapshot=2026-06-01/",
    dataset_sha256=hash_manifest(files),   # hash the file manifest, not the bytes
    params={"max_depth": 8, "lr": 0.05},
    metrics={"auc": 0.871},
)
```
Immutable, date-partitioned snapshots beat "the current table". If your source is mutable, materialize a snapshot as the first pipeline stage — otherwise re-running last month's job silently trains on today's data.

### 2. Split the Pipeline Into Cacheable Stages
```
ingest → validate → build_features → train → evaluate → register
```
Each stage takes explicit inputs and writes explicit outputs keyed by content hash. Re-running after a hyperparameter change should skip ingest and feature building entirely. Monolithic "train.py" jobs cannot do this and cost hours per iteration.

### 3. Make Data Validation a Gate, Not a Report
```python
# Fail the run before wasting GPU hours on bad data
assert df["age"].between(18, 120).all(), "age out of range"
assert df["plan"].isin(KNOWN_PLANS).mean() > 0.99, "unknown plan categories"
assert df["label"].mean() == pytest.approx(BASE_RATE, abs=0.05), "label shift"
assert len(df) > MIN_ROWS, "upstream job produced a partial dataset"
```
Silent upstream truncation is common and produces a model that trains fine and performs badly.

### 4. Gate Registration on Comparison, Not on a Threshold
```python
if new.auc < champion.auc - 0.005:
    raise PipelineFailed(f"regression: {new.auc:.3f} vs {champion.auc:.3f}")
registry.register(model, stage="staging")   # never straight to production
```
Compare against the current champion on the *same* holdout. An absolute threshold like "auc > 0.8" passes forever while the model quietly rots.

### 5. Separate Feature Definitions From Feature Materialization
Define a feature once; let the pipeline materialize it two ways — historical (point-in-time correct, for training) and online (low-latency, for serving). This is what a feature store buys you, and the reason it exists is skew prevention, not storage.

### 6. Trigger on Events, Not Only on Cron
Nightly retraining wastes compute when nothing changed and reacts too slowly when something did. Better triggers: new labeled data volume crossing a threshold, a drift alarm from monitoring, or a code merge to the feature library.

## Warning Signs

- Retraining cannot reproduce a model from three months ago
- "Latest" table read directly, with no immutable snapshot
- Feature engineering code living only in the training script
- Model promoted to production by the training job itself
- Pipeline stages that cannot be re-run independently
- Hyperparameters hardcoded in the script rather than logged as run params
- Evaluation holdout regenerated per run, making runs incomparable
