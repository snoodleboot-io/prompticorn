# Model Performance Debugging (Minimal)

## Purpose
Diagnose why a model underperforms by isolating the cause — data bug, capacity limit, optimization failure, or irreducible noise — before changing anything.

## Core Techniques

### 1. Try to Overfit a Tiny Subset First
```python
tiny_X, tiny_y = X[:50], y[:50]
model.fit(tiny_X, tiny_y)
print(model.score(tiny_X, tiny_y))     # expect ~1.0 for a model with capacity
```
This single test splits the entire diagnostic tree. A model that **cannot** drive training error near zero on 50 examples has a pipeline bug, a broken loss, a dead learning rate, or genuinely insufficient capacity — more data will not help. A model that **can** overfit 50 examples but generalizes poorly has a data, regularization, or distribution problem. Run this before touching architecture or hyperparameters; it takes seconds and eliminates half the hypotheses.

### 2. Read the Learning Curve
```python
from sklearn.model_selection import learning_curve
sizes, train, val = learning_curve(model, X, y, cv=5,
                                   train_sizes=np.linspace(0.1, 1.0, 8))
```
| Train | Validation | Diagnosis | Action |
|---|---|---|---|
| Low error | High error, gap not closing | Overfitting / variance | More data, more regularization, fewer features |
| High error | High error, curves converged | Underfitting / bias | More capacity, better features, train longer |
| Low error | High error, gap closing with n | Data-limited | Collect more data — it will pay off |
| Both flat and high early | — | Bug or broken features | Go back to technique 1 |

More data only helps when the curves are still converging. If they flattened 20,000 rows ago, doubling the dataset buys nothing.

### 3. Always Compare Against a Baseline
```python
from sklearn.dummy import DummyClassifier
DummyClassifier(strategy="most_frequent").fit(X_tr, y_tr).score(X_te, y_te)
```
A model at 94% accuracy on data that is 93% one class has learned essentially nothing. For regression, compare to predicting the mean; for forecasting, to the naive last-value forecast. Absolute scores are uninterpretable without this.

### 4. Suspect Leakage When Results Are Too Good
Near-perfect validation performance is a bug report, not a success. Check for: a feature derived from the target, an identifier that encodes the outcome, preprocessing fitted before the split, duplicate rows spanning both sides, or a temporal feature computed non-causally. Drop the top-importance feature and refit — if performance barely moves, it was a proxy; if it collapses to baseline, inspect that column closely.

### 5. Slice the Errors
```python
df["err"] = (df["y_pred"] != df["y_true"])
df.groupby("segment")["err"].agg(["mean", "size"]).sort_values("mean")
```
Aggregate metrics hide concentrated failure. A model at 92% overall may be at 55% on a segment that carries most of the business value. Slice by class, by cohort, by data source, by time period, and by feature-missingness — then read 30 actual misclassified examples. Nothing substitutes for looking at them.

### 6. Separate the Threshold From the Model
A classifier with good ranking (PR-AUC) and bad precision does not need retraining; it needs a different cutoff. Check ranking quality first, then calibration (`CalibratedClassifierCV`, reliability curve), then pick the threshold from the cost of a false positive versus a false negative. The default 0.5 is rarely the right operating point on imbalanced data.

## Warning Signs

- Validation score above what the problem plausibly allows
- Training and validation error both high and flat — nothing is learning
- Metric chosen without checking the class balance
- Large train/validation gap addressed by adding capacity
- Performance drop between offline evaluation and production
- Hyperparameters tuned before verifying the model can overfit 50 rows
- No single misclassified example has ever been read
