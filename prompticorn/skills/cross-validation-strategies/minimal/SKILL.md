# Cross Validation Strategies (Minimal)

## Purpose
Estimate how a model will perform on data it has not seen, without letting information from the validation fold leak into training.

## Core Techniques

### 1. Match the Splitter to the Data Structure
| Data shape | Splitter | Why |
|---|---|---|
| i.i.d., balanced | `KFold(shuffle=True)` | Plain random partition |
| Skewed class ratio | `StratifiedKFold` | Preserves class proportions per fold |
| Time-ordered | `TimeSeriesSplit` | Never trains on the future |
| Repeated subjects/users | `GroupKFold` | Keeps one entity wholly in one fold |
| Grouped *and* skewed | `StratifiedGroupKFold` | Both constraints at once |

The default `cross_val_score` uses `StratifiedKFold` for classifiers and `KFold` for regressors — including on time series, where it is wrong.

### 2. Never Shuffle Time Series
```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5, test_size=30, gap=7)
```
Random k-fold trains on Thursday and Saturday to predict Friday. That is impossible at inference time, and the resulting score can be wildly optimistic — often near-perfect on autocorrelated series. `gap` drops rows between train and test so a lagged feature computed on day *t-1* cannot bleed across the boundary.

### 3. Fit Preprocessing Inside the Fold
```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# ✅ scaler refit on each training fold only
pipe = make_pipeline(StandardScaler(), LogisticRegression())
scores = cross_val_score(pipe, X, y, cv=5)

# ❌ scaler saw the whole dataset — validation mean/std leaked into training
X_scaled = StandardScaler().fit_transform(X)
cross_val_score(LogisticRegression(), X_scaled, y, cv=5)
```
The same rule governs imputation, target encoding, feature selection, and resampling. Anything that *learns* from data belongs inside a `Pipeline`.

### 4. Nest CV When You Tune
A single CV loop that both selects hyperparameters and reports the score is biased upward — you picked the configuration that best fits those folds. Wrap it:

```python
inner = GridSearchCV(pipe, grid, cv=5)
scores = cross_val_score(inner, X, y, cv=5)   # outer loop reports honestly
```
Cost is `n_outer × n_inner` fits. Expect the nested estimate to land 1–3 points below the naive one; that gap is the selection bias you were otherwise shipping.

### 5. Choose k for the Bias–Variance Trade
k=5 and k=10 are the practical range. Larger k means more training data per fold (less pessimistic bias) but higher variance and linear cost growth. Leave-one-out is high-variance and rarely worth it. Below ~1000 rows, use `RepeatedStratifiedKFold(n_splits=5, n_repeats=10)` and report mean ± std.

## Warning Signs

- CV score far above the held-out test or production score
- `fit_transform` called on `X` before any splitting
- Random `KFold` on data with a timestamp column
- Same user, patient, or device appearing in both train and validation
- Hyperparameters tuned and performance reported from the same folds
- Fold-to-fold standard deviation larger than the difference between candidate models
