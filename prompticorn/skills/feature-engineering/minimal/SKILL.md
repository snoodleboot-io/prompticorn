# Feature Engineering (Minimal)

## Purpose
Turn raw columns into inputs that expose the signal a model can actually use, without smuggling in information unavailable at prediction time.

## Core Techniques

### 1. Encode Categoricals by Cardinality
| Cardinality | Encoding | Caveat |
|---|---|---|
| 2–15 | `OneHotEncoder(handle_unknown="ignore")` | Column blowup above ~50 |
| Ordered levels | `OrdinalEncoder` with explicit `categories=` | Never let it infer order |
| 50+ (zip, SKU, user) | Target encoding (cross-fitted) | Leaks badly if done naively |
| Any, tree model | `HistGradientBoostingClassifier(categorical_features=...)` | Native, no expansion |

`handle_unknown="ignore"` is not optional in production: a category unseen in training will otherwise raise at inference.

### 2. Cross-Fit Target Encoding
```python
from sklearn.preprocessing import TargetEncoder
enc = TargetEncoder(smooth="auto", cv=5)   # internal cross-fitting on fit_transform
```
Replacing a category with the mean target computed over all rows means each row's own label contributes to its own feature. Training accuracy soars, validation does not move. Cross-fitting computes each fold's encoding from the other folds; smoothing shrinks rare categories toward the global mean so a category with n=1 does not become a perfect predictor.

### 3. Scale Only When the Model Cares
Linear models, SVMs, k-NN, neural nets, PCA, and any distance- or penalty-based method need scaling. Decision trees and gradient boosting are invariant to monotone transforms — scaling them is harmless but pointless. Use `StandardScaler` by default, `RobustScaler` when outliers dominate, `QuantileTransformer` for heavy-tailed features.

### 4. Decompose Dates Instead of Ordinal-Encoding Them
```python
df["hour"] = ts.dt.hour
df["dow"] = ts.dt.dayofweek
df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
```
A raw epoch timestamp forces the model to learn periodicity from a monotone number, which trees can only approximate with many splits. Sine/cosine pairs make 23:00 and 00:00 adjacent, which they are.

### 5. Make Missingness a Feature
```python
SimpleImputer(strategy="median", add_indicator=True)
```
Nulls are often informative — an unfilled income field correlates with the outcome. Imputing silently destroys that signal; the indicator column preserves it. Compute the fill value inside the fold, never over the full dataset.

### 6. Aggregate Over Entities With a Time Cutoff
Counts, means, and recencies per user or account are usually stronger than any raw column. Every aggregate must be windowed strictly before the label timestamp, or you have built a feature that knows the future.

## Warning Signs

- A single feature with implausibly high importance — usually leakage
- Target encoding computed over the full dataset before splitting
- Scaler or imputer fitted outside the CV fold
- Timestamps fed to the model as raw integers
- One-hot encoding a 10,000-level id column
- Features derived from data recorded after the prediction moment
- Engineered features that cannot be reproduced from live inputs at serve time
