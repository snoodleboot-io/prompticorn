# Imbalanced Classification (Minimal)

## Purpose
Build and evaluate classifiers when the class of interest is rare, where accuracy is uninformative and the default 0.5 threshold is arbitrary.

## Core Techniques

### 1. Abandon Accuracy
At 99:1 imbalance, `predict(x) = majority` scores 99% accuracy and catches zero positives. Use metrics that ignore true negatives:

| Metric | Reads as | Use when |
|---|---|---|
| Precision | Of flagged, how many were real | Review capacity is limited |
| Recall | Of real, how many were caught | Misses are expensive |
| PR-AUC (average precision) | Ranking quality on the positive class | Strong imbalance |
| ROC-AUC | Ranking quality overall | Near-balanced classes |
| F1 / Fβ | Single-number blend | β>1 to weight recall |

ROC-AUC is optimistic under heavy imbalance: its x-axis is FPR, and with 99,000 negatives, 990 false positives is an FPR of 0.01 — visually negligible, yet those 990 swamp the 1,000 true positives. Precision-recall keeps that damage visible.

### 2. Reweight Before You Resample
```python
LogisticRegression(class_weight="balanced")   # weight = n / (n_classes * n_c)
```
`class_weight="balanced"` and XGBoost's `scale_pos_weight = n_neg / n_pos` are one-line, add no synthetic data, and are usually within noise of SMOTE. Try them first.

### 3. Resample Inside the Fold
```python
from imblearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE

pipe = Pipeline([("smote", SMOTE(random_state=0)), ("clf", RandomForestClassifier())])
```
SMOTE interpolates between a minority point and its k nearest neighbours. Applied before splitting, a synthetic point can be built from a validation row and placed in training — the model then partly memorizes the answer. `imblearn.pipeline.Pipeline` resamples on `fit` only, never on `transform`/`predict`.

### 4. Tune the Threshold, Not Just the Model
```python
p = model.predict_proba(X_val)[:, 1]
prec, rec, thr = precision_recall_curve(y_val, p)
```
`predict()` hardcodes 0.5, which is a decision, not a property of the model. Pick the threshold on validation data from the operating constraint — "review 200 cases/day" or "recall ≥ 0.90" — and report the precision that follows.

### 5. Keep Probabilities Calibrated
Resampling and class weighting distort predicted probabilities upward; the ranking survives but the numbers stop meaning anything. If downstream logic multiplies probability by loss amount, calibrate on unresampled data with `CalibratedClassifierCV(..., method="isotonic", cv=5)`.

## Warning Signs

- Accuracy quoted as the headline metric on skewed data
- `SMOTE().fit_resample(X, y)` called before `train_test_split`
- Resampling applied to the validation or test set
- Threshold left at the 0.5 default with no cost analysis
- ROC-AUC of 0.95 alongside precision of 0.04
- Confusion matrix never inspected — only aggregate scores
- Fewer than ~50 positive cases, yet a high-capacity model in use
