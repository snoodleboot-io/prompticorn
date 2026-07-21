# Batch vs Realtime Scoring (Minimal)

## Purpose
Choose between precomputing predictions on a schedule and computing them per request — a decision driven by how fresh the *inputs* must be, not by how modern the architecture looks.

## Core Techniques

### 1. Ask What Changes Between Scoring and Use
The deciding question is whether the features can change between when you would precompute and when the prediction is consumed.

| Signal | Batch | Realtime |
|---|---|---|
| Entities to score | Known and enumerable | Arbitrary, unknown until the request |
| Input freshness needed | Hours–days | Seconds |
| Depends on in-session context | No | Yes |
| Cost per prediction | Very low (amortized) | 10–100× higher |
| Failure mode | Stale scores | User-visible latency or errors |

Churn scores for known users: batch. Fraud on a card-present transaction: realtime. Product recommendations: usually batch candidates plus a realtime re-rank.

### 2. Batch Is Usually Cheaper and Simpler — Prefer It
Precomputing overnight into a key-value store turns serving into a lookup: a few milliseconds, no model in the request path, no GPU autoscaling, and a failed run degrades to yesterday's scores rather than an outage.

```python
# Nightly: score all active users, write to the online store
scores = model.predict_proba(features_df)[:, 1]
redis.pipeline().mset({f"churn:{uid}": s for uid, s in zip(ids, scores)}).execute()
```
Set a TTL longer than one run interval so a single failed job does not blank the store.

### 3. Realtime Latency Budgets Force Feature Precomputation
A 50 ms p99 budget cannot contain a feature-engineering query. Model inference is often the cheap part.

```
p99 budget                 50 ms
  network + serialization   8 ms
  feature retrieval        ??? ← the whole problem
  inference                 6 ms
  business logic            5 ms
```
Aggregations like `orders_30d` or `avg_ticket_90d` cannot be computed from raw events per request. Precompute them into an online store (Redis, DynamoDB) via a streaming job, and let the request path do point lookups only. This is why feature stores exist: the online store is a latency artifact, not a storage convenience.

### 4. Split Features by Volatility
```
Precomputed nightly    account_age, lifetime_value, segment
Streaming (seconds)    orders_1h, failed_logins_5m
Request-time only      amount, merchant_id, device, hour_of_day
```
Only the last group is computed inline, and it must be pure arithmetic on the request payload — no I/O.

### 5. Use the Hybrid Where It Fits
Precompute an expensive stage offline, do a cheap realtime stage on top: retrieve 500 batch candidates, re-rank the top 20 with a small model plus session context. Most large recommendation systems are this shape.

## Warning Signs

- Realtime inference chosen for entities scored once a day anyway
- Feature aggregations computed with a SQL query inside the request path
- Latency budget stated as an average rather than p99
- Batch job with no TTL, so one failure empties the online store
- Batch and realtime paths computing the same feature two different ways
- No fallback prediction when the model or feature store is unavailable
