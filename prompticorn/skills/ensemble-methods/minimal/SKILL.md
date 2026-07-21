# Ensemble Methods (Minimal)

## Purpose
Combine multiple models so their errors cancel, choosing the combination scheme
from which part of the error — variance or bias — you actually need to reduce.

## Core Techniques

### 1. Diagnose Before You Combine
| Symptom | Error type | Ensemble that helps |
|---|---|---|
| Train score >> test score | Variance | Bagging / random forest |
| Train and test both poor | Bias | Boosting |
| Several decent, dissimilar models | Neither alone | Stacking / blending |

Bagging cannot fix an underfit base learner; averaging ten identical shallow
stumps gives you a shallow stump. Boosting on an already-overfit deep tree makes
it worse.

### 2. Bagging Reduces Variance
```python
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(
    n_estimators=500, max_features="sqrt", n_jobs=-1, random_state=0
)
```
Averaging `n` estimators with pairwise correlation `rho` leaves variance
proportional to `rho + (1 - rho)/n`. The `rho` term does not shrink with `n`, so
past a few hundred trees `max_features` matters more than `n_estimators` —
decorrelation buys what count cannot.

### 3. Boosting Reduces Bias
```python
from sklearn.ensemble import HistGradientBoostingClassifier

hgb = HistGradientBoostingClassifier(
    learning_rate=0.05, max_iter=1000, early_stopping=True,
    validation_fraction=0.1, random_state=0,
)
```
Each tree fits the previous ensemble's residual, so bias falls sequentially and
overfitting is a real risk. Lower `learning_rate` needs more iterations; pair a
small rate with early stopping rather than guessing `max_iter`.

### 4. Stacking Needs Out-of-Fold Predictions
```python
from sklearn.ensemble import StackingClassifier
from sklearn.linear_model import LogisticRegression

stack = StackingClassifier(
    estimators=[("rf", rf), ("hgb", hgb), ("lr", lr_pipeline)],
    final_estimator=LogisticRegression(),
    cv=5,            # base models produce out-of-fold predictions -- essential
    passthrough=False,
)
```
If the meta-learner trains on in-sample base predictions, an overfit base model
looks near-perfect on the rows it memorized, and the meta-learner learns to trust
it completely. Test performance collapses. `cv=5` is what prevents that; never
hand-roll stacking by calling `predict` on the training set.

### 5. Diversity Beats Individual Strength
Five gradient-boosting models with different seeds ensemble to roughly one
gradient-boosting model. A forest, a boosted model, a regularized linear model
and a k-NN gain more: their error patterns differ. Check base-model residual
correlation — above ~0.95 there is nothing left to gain.

### 6. Weigh the Cost
Ensembles multiply latency, memory, and retraining complexity, and make every
explanation indirect. If one tuned `HistGradientBoosting` sits within noise of a five-model stack, ship it.

## Warning Signs

- Stacking implemented with in-fold base predictions (guaranteed leak)
- Base models all from one family, all with the same features
- Ensemble CV score reported without an interval, on a fraction-of-a-point gain
- Boosting with `learning_rate` high and no early stopping
- Meta-learner more complex than the base models
- Preprocessing fitted outside the ensemble's CV, leaking across folds
