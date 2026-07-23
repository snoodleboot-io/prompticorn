# Data Validation Pipelines (Minimal)

## Purpose
Catch bad data at the point it enters your system, so downstream tables, dashboards, and models fail loudly instead of quietly producing wrong numbers.

## Core Techniques

### 1. Validate at the Boundary, Not Everywhere
Every place data crosses a trust line — an API response, an uploaded CSV, a Kafka topic, a vendor drop — gets one validation gate that parses raw input into a typed object. Past that gate, code assumes the data is good.

```python
from pydantic import BaseModel, Field, field_validator

class Reading(BaseModel):
    sensor_id: str = Field(pattern=r"^S-\d{6}$")
    celsius: float = Field(ge=-90, le=60)
    recorded_at: datetime

    @field_validator("recorded_at")
    @classmethod
    def not_future(cls, v: datetime) -> datetime:
        if v > datetime.now(tz=timezone.utc):
            raise ValueError("recorded_at is in the future")
        return v
```

Defensive `if x is None` checks sprinkled through business logic are the failure mode this replaces: they are never complete, they never agree with each other, and none of them tell you which file the bad row came from.

### 2. A Schema Check Is Not a Data-Quality Check
Types passing says nothing about values being sane. All of these satisfy a schema:

| Column | Type says | Reality |
|---|---|---|
| `age` | int64 | `-4`, `999` |
| `revenue_usd` | float64 | `0.0` for every row since the upstream rename |
| `country` | string | `"US"`, `"usa"`, `"United States"` |
| `updated_at` | timestamp | frozen three days ago |

Structural validation is table stakes. Add semantic checks: ranges, cardinality, referential integrity, freshness, and row-count deltas against recent history.

### 3. Assert on Volume and Freshness
The most common silent failure is not malformed data — it is *missing* data. A partition that lands with 12 rows instead of 4 million passes every type check.

```sql
-- Fail the build if today's load is below 70% of the recent median
with daily as (
  select load_date, count(*) as n from analytics.orders
  where load_date >= dateadd('day', -28, current_date) group by 1
)
select * from daily
where load_date = current_date
  and n < 0.7 * (select median(n) from daily where load_date < current_date)
```

### 4. Quarantine Rows, Don't Drop the Batch
Rejecting a whole file over one bad row means a single vendor typo halts the pipeline at 3am. Split instead: valid rows proceed, invalid rows land in a rejects table with the failing rule and the raw payload, and the job fails only when the reject *rate* crosses a threshold (e.g. > 1%).

### 5. Separate Warn From Fail
Not every check should stop the pipeline. Give each check a severity: `error` blocks publication, `warn` files a ticket. If everything is an error, on-call learns to rerun jobs with validation disabled — and then you have no validation at all.

### 6. Push the Contract to the Producer
The strongest validation is an upstream schema contract — Avro/Protobuf with a registry on `BACKWARD` compatibility, or a dbt model contract — that rejects an incompatible producer at deploy time, before a bad row exists. Runtime validation is the safety net for what contracts cannot express.

## Warning Signs

- Null-and-type checks scattered across transformation code instead of one gate
- Validation that only checks types and column presence
- No row-count or freshness assertion on any table
- One bad row failing an entire load
- Every check severity set to `error`
- Rejected rows discarded without the raw payload or the rule that fired
- Checks running only in the warehouse, so bad data is caught six hours after it lands
- Hard-coded thresholds nobody has revisited since the table was a tenth its size
