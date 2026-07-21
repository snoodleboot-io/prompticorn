# Time Series Preprocessing (Minimal)

## Purpose
Prepare temporal data for modeling without letting information from the future reach a model that will only ever see the past.

## Core Techniques

### 1. Build Lag Features Causally
```python
# ✅ Row at time t sees only t-1 and earlier
df["sales_lag_1"] = df["sales"].shift(1)
df["sales_lag_7"] = df["sales"].shift(7)

# ✅ Rolling mean must be shifted — the window ends at t-1
df["sales_ma_7"] = df["sales"].shift(1).rolling(7).mean()

# ❌ Includes the current value you are trying to predict
df["sales_ma_7"] = df["sales"].rolling(7).mean()
```
`rolling(7)` in pandas is right-aligned by default: the window at row `t` spans `t-6 .. t`, so it contains `sales[t]` itself. Every rolling, expanding, or `ewm` feature needs a `.shift(1)` in front of it, or the target sits inside its own predictor and validation error comes back implausibly low.

### 2. Resample First — and Recognize the Target Changed
```python
daily = df.resample("D", on="ts").agg({"sales": "sum", "price": "mean"})
```
Resampling redefines the prediction problem. Hourly-to-daily `sum` turns "units in the next hour" into "units in the next day" — different variance, different seasonality, a different baseline to beat. `mean` and `last` are not interchangeable either: `last` keeps the endpoint (right for prices), `mean` smooths away intra-period extremes (wrong for peak-load forecasting). Pick the aggregation from what the downstream decision needs, then re-derive the baseline.

### 3. Split by Time, Never at Random
```python
from sklearn.model_selection import TimeSeriesSplit
tscv = TimeSeriesSplit(n_splits=5, gap=24)   # gap ≥ forecast horizon
```
Random `KFold` trains on Wednesday to predict Tuesday. `gap` matters whenever the target spans a horizon: forecasting 24 hours ahead with no gap leaves the final training rows overlapping the validation target window.

### 4. Treat Gaps as Gaps
```python
df = df.set_index("ts").asfreq("h")          # missing timestamps become explicit NaN
df["value"] = df["value"].ffill(limit=3)     # bounded, causal fill
df["was_imputed"] = df["value"].isna() | ...
```
`interpolate()` is bidirectional — it pulls future values backwards, which is leakage in a training set. Forward fill is causal; cap the limit so a three-day outage does not become three days of flat, plausible-looking data. Keep an `was_imputed` flag so the model can learn those regions are less trustworthy.

### 5. Test Stationarity, Difference If Needed
```python
from statsmodels.tsa.stattools import adfuller
stat, pvalue = adfuller(series)[:2]          # p > 0.05: cannot reject a unit root
df["diff_1"] = df["value"].diff()
```
ARIMA-family models require stationarity. Tree and boosting models do not, but they cannot extrapolate a trend at all — a boosted tree on a rising series flatlines at the largest value it saw in training. Difference, or model the ratio to a rolling baseline, before handing a trending series to trees.

### 6. Fit Scalers on the Past Only
```python
scaler.fit(train)                            # statistics from history alone
train_s, test_s = scaler.transform(train), scaler.transform(test)
```
A `StandardScaler` fitted on the full series encodes the future's mean and variance into every training row. The same holds for target encoding, quantile binning, and PCA — put them in a `Pipeline` so they refit inside each fold.

## Warning Signs

- Validation error far better than any published baseline for the problem
- A rolling, expanding, or `ewm` feature with no `.shift(1)`
- `train_test_split(shuffle=True)` on temporal data
- `interpolate()` or `bfill()` applied before the split
- Feature importance dominated by a column only knowable after the fact
- Strong backtest, immediate degradation in production
- Timestamps in local time across a DST boundary — duplicated or missing hours
