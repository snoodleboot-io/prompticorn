# ML Deployment (Minimal)

## Purpose
Get a trained model serving traffic safely — packaged, versioned, and rolled out so a bad model is caught before it reaches every user.

## Core Techniques

### 1. Ship the Artifact, Not the Notebook
A deployable model is the weights *plus* everything needed to reproduce its inputs and outputs.

```
model-v1.4.2/
  model.pkl              # or .onnx / SavedModel / .safetensors
  requirements.lock      # exact versions — sklearn 1.3 unpickles into 1.5 badly
  feature_spec.json      # column names, dtypes, order, fill values
  preprocessor.pkl       # the *fitted* transformer, not a re-fit copy
  metadata.json          # training data hash, git sha, metrics, trained_at
```

Pin the framework version. Pickle formats are not stable across minor releases, and a silent unpickle warning usually precedes silently wrong predictions.

### 2. Kill Training/Serving Skew at the Source
The most common production ML bug is not the model — it is the serving path reimplementing feature logic that training did differently.

```python
# ❌ Two implementations that will drift apart
# train.py:  df["age_days"] = (df.now - df.signup).dt.days
# serve.py:  age_days = (datetime.now() - signup).days   # local vs UTC, floor vs round

# ✅ One implementation, imported by both
from features.transforms import account_age_days
```
Serialize the *fitted* preprocessor with the model. A scaler re-fit on serving data is not the same scaler.

### 3. Pick a Rollout Strategy Deliberately
| Strategy | Traffic to new model | Catches | Cost |
|---|---|---|---|
| Shadow | 0% (mirrored, predictions discarded) | Skew, latency, crashes | Double compute |
| Canary | 1% → 5% → 50% | Bad predictions, business regressions | Slow |
| Blue-green | 0% → 100% at once | Only infra faults | Instant rollback |

Shadow first, then canary. Blue-green alone is weak for models: the model runs fine and predicts badly, and every infra health check stays green.

### 4. Health-Check the Model, Not Just the Process
```python
@app.get("/health/model")
def model_health():
    p = model.predict(GOLDEN_ROWS)          # fixed rows checked into the repo
    assert np.allclose(p, GOLDEN_PREDS, atol=1e-6)
    return {"model_version": MODEL_VERSION, "ok": True}
```
A 200 from `/healthz` proves the web server is up. Golden-row assertions prove the *right model* loaded with the *right* preprocessing.

### 5. Keep Rollback One Step Away
Serve by version alias, not by rebuilding the image. Moving `production → v1.4.1` should be a pointer flip, so rollback takes seconds and never waits on CI.

## Warning Signs

- Feature code duplicated between the training job and the serving service
- Model file with no recorded training data version or git sha
- Framework version unpinned in the serving image
- First real evaluation of a new model happens after 100% rollout
- Rollback requires a rebuild and redeploy
- Preprocessor re-fit at serving time instead of loaded
- No golden-prediction test in the deploy pipeline
- Prediction responses that don't carry the model version
