# Feature Store Design (Minimal)

## Purpose
Serve the same feature values to training and to inference, computed by the same code, so a model that scored 0.89 offline does not score 0.71 in production.

## Core Techniques

### 1. The Problem Is Training/Serving Skew, Not Storage
A feature store is not "a database for features." Its reason to exist is that most teams compute features twice — a Spark job for training, a hand-written Python path for the online API — and the two definitions drift. A 7-day rolling average that excludes today offline but includes it online produces a model that is quietly broken and passes every unit test.

One definition, two materializations. Write the transformation once; the store materializes it to an offline table for training and an online store for serving.

### 2. Offline and Online Stores Have Different Jobs
| | Offline store | Online store |
|---|---|---|
| Access pattern | Scan millions of rows | Point lookup by entity key |
| Latency | Minutes acceptable | p99 under 10 ms |
| Backend | Parquet on S3, BigQuery, Snowflake | Redis, DynamoDB, Cassandra |
| Holds | Full history, every timestamp | Latest value per entity only |
| Serves | Training sets, backfills | Live inference |

The online store holds *only the current value*. Trying to serve training reads from Redis, or online reads from Parquet, is the usual first design mistake.

### 3. Point-in-Time Correct Joins Prevent Label Leakage
This is the technical heart of the thing. Given a label event at time T, every feature must be the value **as known at T** — not the current value, and not the value at end of day.

```sql
-- ✅ point-in-time correct: newest feature row at or before the label timestamp
select l.customer_id, l.event_ts, l.churned, f.orders_30d
from labels l
asof join features f
  on l.customer_id = f.customer_id
  and f.feature_ts <= l.event_ts
```

A plain `join ... on customer_id` picks up feature values computed *after* the outcome. Offline AUC jumps, everyone celebrates, and production is 15 points worse because at inference time the future is not available. If your training AUC is suspiciously high, this is the first thing to check.

### 4. Model the Entity, Then the Feature View
An entity is the join key (`customer_id`, `driver_id`, `merchant_id`). A feature view is a group of features sharing an entity, a source, and a freshness contract.

```python
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64

customer = Entity(name="customer", join_keys=["customer_id"])

customer_stats = FeatureView(
    name="customer_stats",
    entities=[customer],
    ttl=timedelta(days=7),
    schema=[
        Field(name="orders_30d", dtype=Int64),
        Field(name="avg_basket_usd", dtype=Float32),
    ],
    source=FileSource(path="s3://fs/customer_stats.parquet",
                      timestamp_field="event_ts"),
)
```

### 5. Set a TTL and Alert on Staleness
Every feature needs a maximum acceptable age. Without a TTL, a broken materialization job serves values from three weeks ago and inference happily continues at full throughput with no error. Stale features are the most common silent production failure in ML systems.

### 6. Know When You Do Not Need One
A feature store buys cross-team reuse and skew elimination. For one team with one model and batch scoring, a versioned table plus a shared transformation module gives you most of the benefit at a fraction of the operational cost. Adopt when you have several models, multiple consumers of the same feature, or real-time inference.

## Warning Signs

- Feature logic written twice — once in Spark, once in the serving path
- Training joins on entity key alone, without a timestamp condition
- Offline metrics far better than production performance
- Online store queried during training, or the warehouse queried at inference
- No TTL, no staleness alert on materialization jobs
- Feature names without owners, definitions, or version history
- Online-served values never compared against the offline values for the same entity and time
