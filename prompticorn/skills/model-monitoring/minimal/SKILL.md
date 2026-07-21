# Model Monitoring (Minimal)

## Purpose
Detect a model degrading in production before the business notices — despite ground-truth labels arriving days or weeks after the prediction.

## Core Techniques

### 1. Monitor Four Layers, In This Order of Usefulness
| Layer | Signal | Latency to detect | Actionable? |
|---|---|---|---|
| Operational | p99 latency, error rate, throughput | Seconds | Always |
| Input data | Schema, null rate, range violations | Minutes | Usually a real bug |
| Prediction drift | Score distribution shift | Hours | Often |
| Model quality | AUC, precision against labels | Days–weeks | Definitive but late |

Most teams build only the last layer, then discover it cannot alert them for three weeks.

### 2. Prefer Prediction Drift Over Feature Drift for Alerting
Feature drift alerts fire constantly. With 200 features and a p < 0.05 test per feature per day, you get ~10 false alarms daily, and the team mutes the channel within a week.

Prediction drift is one distribution, it is the model's own summary of every input, and a shift in it means the model's *behavior* changed — which is what you actually care about.

```promql
# Alert when today's mean score departs from the trailing 7-day baseline
abs(
  avg_over_time(model_prediction_score[1h])
  - avg_over_time(model_prediction_score[7d] offset 1h)
) > 0.05
```
Keep feature drift as a *diagnostic* you consult after a prediction-drift alert, not as a pager.

### 3. Handle Delayed Ground Truth Explicitly
Labels for a churn or fraud model arrive 30–90 days later. Two consequences:

- Compute quality metrics on a **lagged window** and label the chart with it — "AUC as of 60 days ago" is honest; a live-looking number is not.
- Build **proxy labels** that arrive fast: click-through within the hour, chargeback within 24h, refund within 7 days. They are biased but timely, and a proxy collapsing today beats an AUC drop discovered in November.

### 4. Watch Segments, Not Just the Aggregate
Aggregate AUC is remarkably stable while a segment rots. Break every quality metric down by the dimensions that matter — tenure bucket, region, device, traffic source — and alert on the segments.

### 5. Distinguish Drift From Decay
Drift means inputs moved. Decay means predictions got worse. They are not the same: a model can face large input drift with no accuracy loss (the shift is in features it barely uses), or decay with no visible drift (the *relationship* between features and target changed — concept drift). Never auto-retrain on a drift signal alone.

### 6. Log Every Prediction With Its Inputs
```json
{"ts":"2026-07-19T10:03:11Z","request_id":"a1b2","model_version":"1.4.2",
 "features":{"orders_30d":4,"age_days":812},"score":0.73,"label":null}
```
Sample if volume demands it, but keep the raw features. Without them you cannot join labels later, cannot reproduce a bad prediction, and cannot compute drift retrospectively.

## Warning Signs

- Model quality measured only offline at training time
- Drift alerting configured per-feature across hundreds of features
- Retraining triggered automatically by a drift alarm alone
- No prediction logging, or logging scores without inputs
- Quality dashboards that hide the label delay
- Only aggregate metrics, no segment breakdown
- No alert on the fraction of inputs hitting the "unknown category" bucket
