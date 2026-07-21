# Feature Importance Analysis (Minimal)

## Purpose
Rank which inputs a model actually depends on, using methods whose biases you
can name — because every importance method answers a slightly different question.

## Core Techniques

### 1. Know What Each Method Measures
| Method | Measures | Main bias |
|---|---|---|
| Impurity (`feature_importances_`) | Training-set split gain | Inflates high-cardinality and continuous features |
| Permutation | Test-score drop when a column is shuffled | Misleads under correlated features |
| Drop-column (refit) | True marginal value of the feature | Costs one refit per feature |
| SHAP (mean abs) | Per-prediction attribution magnitude | Explains the model, not the world |

### 2. Distrust Impurity-Based Importance
```python
rf.feature_importances_    # fast, free, and biased
```
A random-noise column with 10,000 distinct float values gets many chances to
produce a spuriously good split, so it accumulates impurity gain and can outrank
a genuinely predictive binary flag. Add a pure-noise feature as a control: if it
lands mid-table, the ranking below it is meaningless. It is also computed on
training data, so it rewards overfitting.

### 3. Permutation Importance on Held-Out Data
```python
from sklearn.inspection import permutation_importance

r = permutation_importance(
    model, X_test, y_test, n_repeats=30, random_state=0, scoring="average_precision"
)
for i in r.importances_mean.argsort()[::-1]:
    print(f"{X_test.columns[i]:<24} {r.importances_mean[i]:.4f} +/- {r.importances_std[i]:.4f}")
```
Use `X_test`, not `X_train`. Report the std — features whose mean is under one
std are indistinguishable from zero.

### 4. Handle Correlated Features Deliberately
Permuting one of two correlated columns leaves the model the other, so both look
unimportant and their shared signal vanishes from the ranking. Worse, permuting
breaks the correlation and evaluates the model on impossible rows (income
$20k with a $2M mortgage), where predictions are unconstrained.

Fix by clustering on Spearman rank correlation and permuting whole groups:
```python
from scipy.cluster import hierarchy
from scipy.stats import spearmanr

corr = spearmanr(X_train).correlation
links = hierarchy.ward(hierarchy.distance.squareform(1 - abs(corr)))
groups = hierarchy.fcluster(links, 0.5, criterion="distance")
```

### 5. Use Drop-Column When the Decision Is "Can I Remove It?"
Permutation asks "does this fitted model use it." Removal asks "can the model
succeed without it." They differ when a substitute exists. If you plan to delete
a feature pipeline, refit without it and compare CV scores with intervals.

### 6. Require Stability Before Believing a Ranking
Recompute across seeds, folds, and bootstrap resamples. A top-10 that reshuffles
per seed is noise. Only features stable across all resamples belong in a report.

## Warning Signs

- `feature_importances_` quoted as ground truth, with no noise control
- Permutation importance computed on training data
- Importances reported without spread, so "0.012 vs 0.009" reads as a difference
- Correlated columns ranked individually and then pruned one at a time
- ID-like or high-cardinality columns near the top (usually leakage)
- Feature dropped on importance alone without a refit that confirms no loss
