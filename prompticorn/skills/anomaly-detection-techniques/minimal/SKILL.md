# Anomaly Detection Techniques (Minimal)

## Purpose
Find rare, unexpected observations in data where labels are scarce or absent, and evaluate the result in a way that survives extreme class imbalance.

## Core Techniques

### 1. Start With Robust Statistics
```python
import numpy as np
med = np.median(x)
mad = np.median(np.abs(x - med))
robust_z = 0.6745 * (x - med) / mad          # |robust_z| > 3.5 flags an outlier
```
Mean and standard deviation are computed *from* the data you are screening, so a handful of extreme points inflate σ and mask themselves — this is masking, and it is why 3-sigma rules miss the very outliers they target. Median and MAD have a 50% breakdown point. The `0.6745` factor rescales MAD to be comparable to a standard deviation under normality.

### 2. Isolation Forest for Tabular Data
```python
from sklearn.ensemble import IsolationForest
iso = IsolationForest(n_estimators=200, contamination=0.01, random_state=0)
scores = -iso.fit(X_train).score_samples(X_test)   # higher = more anomalous
```
Isolates points by random splits: anomalies need fewer splits to separate, so path length is the score. Linear in `n`, no distance metric, handles mixed scales tolerably. `contamination` only sets the threshold on the score — it does not change the ranking, so keep the raw scores and pick your own cutoff.

### 3. Match the Method to the Anomaly's Shape
| Method | Detects | Cost | Weakness |
|---|---|---|---|
| Robust z / MAD | Univariate extremes | O(n) | Blind to combinations |
| Isolation Forest | Global, sparse-region | O(n log n) | Weak on local density |
| Local Outlier Factor | Locally low density | O(n²) naive | Needs `novelty=True` to score new data |
| One-Class SVM | Boundary of a dense region | O(n²)–O(n³) | Kernel/`nu` tuning is fiddly |
| Autoencoder residual | High-dim, nonlinear | GPU | Can learn to reconstruct anomalies |

A fraudulent transaction is rarely extreme on any single column; it is an unusual *combination*. Univariate screening cannot see that.

### 4. Evaluate on Precision@k, Not Accuracy
At 0.1% anomaly rate, predicting "normal" for everything scores 99.9% accurate and finds nothing. What the operator actually experiences is the top of the ranked list:
```python
from sklearn.metrics import average_precision_score
order = np.argsort(-scores)
precision_at_100 = y_true[order[:100]].mean()      # of 100 alerts, how many real?
pr_auc = average_precision_score(y_true, scores)   # threshold-free, imbalance-aware
```
Use PR-AUC (average precision), not ROC-AUC: ROC-AUC is dominated by the negative class and stays flattering — 0.95 or better — for a detector whose alerts are 95% false positives. Set `k` to the alerts per day the team can genuinely triage.

### 5. Seasonality Before Thresholding on Time Series
Traffic at 3am is not an anomaly. Decompose or model the expectation first, then score the residual:
```python
import numpy as np
from scipy.stats import median_abs_deviation
from statsmodels.tsa.seasonal import STL

res = STL(series, period=24, robust=True).fit()
mad = median_abs_deviation(res.resid)          # raw MAD, no scaling
resid_z = 0.6745 * (res.resid - np.median(res.resid)) / mad
```
The `0.6745` factor is the modified z-score constant, putting MAD on the same
scale as a standard deviation for normally distributed residuals.
`robust=True` keeps the fitted seasonal component from absorbing the anomalies you are hunting.

### 6. Fit on Clean Data When You Can
Semi-supervised beats unsupervised whenever a known-good period exists: fit on that window, score everything after. An unsupervised model fitted on contaminated data learns the anomalies as part of the normal region and stops flagging them.

## Warning Signs

- Accuracy or ROC-AUC reported as the headline metric
- Alert volume far above what the on-call rotation can triage
- Threshold picked once and never revisited as the data drifts
- 3-sigma rules on skewed or heavy-tailed distributions
- Model refit nightly on data that includes yesterday's undetected anomalies
- No feedback loop capturing which alerts operators dismissed
- Detector fitted on scaled features where the scaler saw the anomalies
