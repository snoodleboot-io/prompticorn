# Model Evaluation (Minimal)

## Purpose
Choose metrics that track the decision the model actually drives, and report them
with enough uncertainty that a difference is believable.

## Core Techniques

### 1. Match the Metric to the Class Balance
| Metric | Reads well when | Fails when |
|---|---|---|
| Accuracy | Classes roughly balanced | 1% positives — predict all-negative scores 0.99 |
| ROC-AUC | Balanced, or you rank both classes | Heavy imbalance — flattering, see below |
| PR-AUC / average precision | Positives are rare and are what you care about | Not comparable across datasets with different base rates |
| F1 | You need one number at a fixed threshold | Hides which side of the trade-off you lost |

ROC-AUC flatters an imbalanced model because its x-axis is the false positive
rate, `FP / (FP + TN)`. With 99% negatives, `TN` is enormous, so thousands of
false positives barely move the FPR. Precision, `TP / (TP + FP)`, has no such
cushion — those false positives land directly in the denominator. A fraud model
at 0.5% prevalence can post ROC-AUC 0.97 while its precision at usable recall
is 0.08.

### 2. Report an Interval, Not a Point
```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
import numpy as np

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
s = cross_val_score(model, X, y, cv=cv, scoring="average_precision")
print(f"{s.mean():.3f} +/- {1.96 * s.std() / np.sqrt(len(s)):.3f}")
```
A single held-out number is a sample of size one from the split distribution. On
a 2,000-row test set the standard error on AUC is often ±0.02, so the "+0.004
improvement" you are about to ship is noise.

### 3. Split Along the Axis of Deployment
Random `train_test_split` is right only when rows are i.i.d. With time-ordered
data use `TimeSeriesSplit`; with repeated users, sessions, or patients use
`GroupKFold` so the same entity never straddles the split. A random split on
grouped data leaks and typically inflates scores by several points.

### 4. Tune the Threshold Separately from the Model
`predict()` hardcodes 0.5, which is almost never the operating point you want.
Pick the threshold on a validation set from the precision-recall curve given
your cost ratio, then measure it once on test.

### 5. Calibrate When You Consume the Probability
If a downstream rule multiplies the score by a dollar amount, the score must
mean something. Boosted trees and SVMs are typically miscalibrated; check with
`sklearn.calibration.calibration_curve`, fix with `CalibratedClassifierCV`
(`method="isotonic"` with ample data, `"sigmoid"` when small).

### 6. Compare Against a Real Baseline
`DummyClassifier(strategy="prior")` and last-week's-value for forecasting. A
model that cannot beat the naive baseline by more than the confidence interval
is not a model.

## Warning Signs

- Accuracy quoted on a dataset with strong class imbalance
- One test-set number with no interval, no repeats, no seed variance
- Test set consulted more than once during model selection
- Metric computed on preprocessed-then-split data (scaler fit on all rows)
- Threshold left at 0.5 while the cost of FP and FN differ by 10x
- Offline metric improves, the business metric does not, and nobody investigates
