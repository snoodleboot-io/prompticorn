---
name: "data-pipeline"
description: "Comprehensive guide to designing, implementing, and optimizing data pipelines with idempotency, incremental processing, and monitoring"
version: "1.0"
languages: ["python", "sql", "hcl"]
subagents: ["data/pipeline", "data/quality", "orchestrator"]
---

# Data Pipeline Workflow (Verbose)

## Purpose
Design, build, and optimize ETL/ELT pipelines for moving and transforming data at enterprise scale with focus on reliability, performance, and maintainability.

## When to Use This Workflow
- Building new data pipelines from scratch
- Redesigning existing pipelines for scale
- Migrating data between systems
- Implementing real-time or streaming pipelines
- Optimizing pipeline performance and cost

## Prerequisites
- Understanding of source and destination systems
- Data volume and velocity expectations
- SLA requirements (freshness, availability, accuracy)
- Team expertise in pipeline tools and languages
- Infrastructure budget and constraints

---

## Steps

### 1. Define Data Flow & Requirements

**Goal:** Understand the complete data movement requirement.

#### 1.1 Analyze Source Systems
- What systems contain the source data?
- What are access patterns (databases, APIs, files, streams)?
- What is the data schema and volume?
- What are growth projections (10% monthly growth)?

**Example source analysis:**
```
Source 1: PostgreSQL database
- Table: orders (10M rows/month growth)
- Primary key: order_id
- Change frequency: Continuous (real-time transactions)
- Access: Direct JDBC connection available

Source 2: REST API (SaaS)
- Endpoint: /v2/analytics/events
- Volume: 100K events/day
- Rate limit: 1000 requests/min
- Incremental: Cursor-based pagination

Source 3: S3 CSV files
- Location: s3://uploads/daily/
- Format: CSV gzip compressed
- New file: Every 24 hours at 23:00 UTC
- Historical: 18 months of data available
```

#### 1.2 Define Destination Requirements
- Where does data need to go (warehouse, lake, cache)?
- What schema/partitioning strategy for analytics?
- What access patterns (OLAP queries, dashboards)?
- What latency requirements (real-time, hourly, daily)?

**Example destination:**
```
Destination: Snowflake Data Warehouse
- Database: ANALYTICS
- Schema: raw_data, transformed, reporting
- Partitioning: By date for time-series data
- Access: SQL queries, BI tools (Tableau, Looker)
- SLA: Data fresh within 1 hour (p95)
- Retention: 7 years of historical data
```

#### 1.3 Identify Transformations
What processing needs to happen between source and destination?

**Transformation categories:**
```
Cleansing:
- Remove duplicates (same customer ID, order_id)
- Handle missing values (null email → customer_id only)
- Standardize formats (dates, phone numbers)
- Filter invalid records

Enrichment:
- Join customer demographics from CRM
- Add geolocation from IP address
- Calculate derived metrics (customer lifetime value)
- Add reference data (product categories, tax rates)

Aggregation:
- Daily order totals per customer
- Monthly revenue by region
- Customer cohorts by signup date

Compliance:
- Mask PII (email, credit card numbers)
- Implement GDPR right to forget
- Anonymize for analytics (hash email)
```

#### 1.4 Set SLAs & Expectations
```
Availability: 99.5% (3.6 hours downtime/month acceptable)
Freshness: Daily (orders available by 8am UTC+1)
Accuracy: 99.9% (valid records should match source)
Latency: 95th percentile <30 minutes from source to warehouse
Cost: <$5K/month on cloud infrastructure
```

---

### 2. Choose Pipeline Architecture

**Goal:** Select the right tool and pattern for the workload.

#### 2.1 ETL vs ELT

**ETL (Extract-Transform-Load):**
- Transform happens outside target warehouse
- Best for: Complex transformations, sensitive data processing
- Tools: Apache Beam, Spark, Python/Pandas
- Cost: Separate transformation compute
- When to use: Sensitive data, complex rules, validation before warehouse

```
ETL Example:
PostgreSQL → Apache Spark (transform) → Snowflake (load)
- Spark validates data quality
- Spark masks PII
- Spark aggregates before warehouse
```

**ELT (Extract-Load-Transform):**
- Load raw data first, transform in warehouse
- Best for: Scalable analytics, flexible transformations
- Tools: dbt, SQL, Snowflake, BigQuery
- Cost: Warehouse compute handles transformations
- When to use: Analytics, data lake, exploratory analysis

```
ELT Example:
PostgreSQL → Snowflake raw → dbt transforms → Snowflake analytics
- Raw data preserved for audit trail
- dbt models handle all transformations
- Warehouse scales with transformations
```

#### 2.2 Batch vs Streaming

**Batch Processing:**
- Fixed time intervals (daily, hourly)
- Tools: Apache Spark, AWS Glue, dbt
- Latency: Minutes to hours
- Cost: Compute only when running
- When to use: Most analytical workloads, cost-sensitive

```
Batch schedule:
- 2am UTC: Daily customer snapshot refresh
- Hourly: Event aggregation every hour
- Weekly: Deep historical reprocessing
```

**Streaming (Real-time):**
- Continuous data processing
- Tools: Kafka, Spark Streaming, Flink, Kinesis
- Latency: Seconds to milliseconds
- Cost: Constant compute + storage
- When to use: Real-time dashboards, fraud detection, alerting

```
Streaming pipeline:
Events → Kafka → Spark Streaming → Redis/Druid
- Event arrives in <100ms
- Aggregations updated in real-time
- Dashboard shows latest within 5 seconds
```

#### 2.3 Orchestration Tool Selection

| Tool | Best For | Complexity | Cost | Learning Curve |
|------|----------|-----------|------|-----------------|
| **dbt** | SQL transformations | Low | Low | Very low |
| **Apache Airflow** | Complex DAGs | High | Medium | Medium-High |
| **Prefect** | Modern Python pipelines | Medium | Medium | Low-Medium |
| **Dagster** | Data-aware pipelines | High | Medium | Medium-High |
| **Dataflow (Beam)** | Large-scale processing | High | Medium-High | High |

**Recommendation checklist:**
- Pure SQL transformations? → Use **dbt**
- Python-heavy transformations? → Use **Prefect** or **Dagster**
- Complex dependencies/monitoring? → Use **Airflow** or **Dagster**
- Streaming + batch mixed? → Use **Apache Beam** or **Spark**

---

### 3. Implement Idempotency (Critical for Reliability)

**Goal:** Design pipelines that produce identical results regardless of how many times they run.

#### 3.1 Exactly-Once Semantics

**Problem:** Without idempotency, retrying a failed pipeline can duplicate data.

```
Bad (non-idempotent):
1. Extract 1000 orders
2. Insert into warehouse (500 inserted)
3. Pipeline fails
4. Retry extracts 1000 orders again
5. Insert all 1000 → 1500 total (duplicate 500)

Good (idempotent):
1. Extract 1000 orders with IDs 1000-1999
2. INSERT OR REPLACE WHERE order_id IN (1000-1999)
3. Pipeline fails
4. Retry extracts same orders
5. INSERT OR REPLACE → still 1000 total (no duplicates)
```

#### 3.2 Natural Keys & Deduplication

Use business keys instead of synthetic IDs for idempotency.

```sql
-- Bad: Dependent on sequence
INSERT INTO orders (order_id, customer_id, amount)
VALUES (nextval('seq_order_id'), 123, 99.99);
-- On retry, gets different order_id!

-- Good: Natural key (customer + timestamp)
MERGE INTO orders o
USING source_data s
ON o.customer_id = s.customer_id 
   AND o.order_timestamp = s.order_timestamp
WHEN NOT MATCHED THEN
  INSERT (customer_id, order_timestamp, amount)
  VALUES (s.customer_id, s.order_timestamp, s.amount)
WHEN MATCHED THEN
  UPDATE SET amount = s.amount;
```

#### 3.3 Checkpointing for Recovery

```python
# Save progress so retries don't restart from beginning
def process_stream(source):
    checkpoint = load_checkpoint('process_stream')
    
    # Resume from last successful record
    for record in source.records_after(checkpoint.last_id):
        process(record)
        checkpoint.update(record.id)
        checkpoint.save()  # Save after each batch
```

---

### 4. Design Incremental Processing

**Goal:** Process only changed data, not entire dataset each time.

#### 4.1 Change Data Capture (CDC)

**Full Load (expensive):**
```
Every run:
1. Read entire source table (100M rows)
2. Transform all data
3. Replace warehouse table
Problem: 99% of data unchanged, waste of compute
```

**Incremental with CDC (efficient):**
```
Every run:
1. Read only changed rows since last run (100K rows)
2. Transform changes only
3. MERGE into warehouse (upsert changed rows)
Benefit: 1000x faster, 1000x cheaper
```

#### 4.2 Timestamp-Based Incremental

```sql
-- Track last extraction timestamp
SELECT * FROM source_table 
WHERE updated_at > :last_extraction_time
ORDER BY updated_at

-- For next run
last_extraction_time = '2026-04-10 14:30:00'
```

**Challenges:**
- Clocks may not be synchronized
- Server timezone conversions
- Records arriving out of order
- Backfill requirements

**Solution: Add buffer window**
```sql
-- Reprocess last 24 hours to catch late arrivals
SELECT * FROM source_table 
WHERE updated_at > CURRENT_TIMESTAMP - INTERVAL 24 HOUR
```

#### 4.3 Partitioning for Performance

```sql
-- Partition by date for efficient incremental processing
CREATE TABLE orders (
  order_id INT,
  customer_id INT,
  order_date DATE,
  amount DECIMAL
)
PARTITION BY DATE(order_date);

-- Only scan relevant partition
SELECT * FROM orders 
WHERE order_date = '2026-04-10'  -- Single partition scan!
```

**Partition key selection:**
- **By time** (daily, hourly): Best for time-series, freshness SLAs
- **By region** (US, EU, APAC): For compliance data residency
- **By customer** (customer_id): For multi-tenant data isolation

---

### 5. Design Error Handling

**Goal:** Catch problems early, fail gracefully, provide debugging info.

#### 5.1 Data Quality Validation

```python
# Validate before loading
class DataValidator:
    def validate(self, batch):
        errors = []
        
        # Schema validation
        if 'order_id' not in batch:
            errors.append("Missing required column: order_id")
        
        # Type validation
        for row in batch:
            if not isinstance(row['amount'], (int, float)):
                errors.append(f"Invalid amount type: {row['amount']}")
        
        # Business logic validation
        for row in batch:
            if row['amount'] < 0:
                errors.append(f"Negative amount: {row['amount']}")
            if row['customer_id'] not in valid_customers:
                errors.append(f"Unknown customer: {row['customer_id']}")
        
        # Too many errors = fail fast
        if len(errors) > 0.01 * len(batch):  # >1% error rate
            raise ValueError(f"Quality check failed: {errors[:10]}")
        
        return errors  # Return for logging
```

#### 5.2 Dead Letter Queue Pattern

```
Good records → Warehouse ✓
Bad records → Dead Letter Queue → Manual review → Fix source
        ↓
    Log error details
    Alert on threshold
    Track by error type
```

#### 5.3 Graceful Failure & Alerts

```python
def run_pipeline():
    try:
        extract()
        transform()
        load()
        log_success()
    except DataQualityError as e:
        # Expected error (bad data in source)
        alert_level = "WARNING"
        send_alert(f"Quality check failed: {e}", level=alert_level)
        # Don't fail pipeline, continue with good records
    except DatabaseError as e:
        # Unexpected error (infrastructure issue)
        alert_level = "CRITICAL"
        send_alert(f"Database unavailable: {e}", level=alert_level)
        # Fail pipeline, retry later
        raise
```

---

### 6. Optimize Performance

**Goal:** Reduce latency, cost, and resource usage.

#### 6.1 Parallelization

```python
# Sequential: 1 hour total
for source in sources:
    extract(source)
    transform(source)
    load(source)

# Parallel: 10 minutes total (if 6 sources)
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(process, source) for source in sources]
    for future in futures:
        future.result()
```

#### 6.2 Data Format Selection

| Format | Compression | Query Speed | Tool Support | When to Use |
|--------|------------|-------------|--------------|------------|
| **CSV** | Optional | Slow | Excellent | Small files, one-time |
| **Parquet** | Excellent | Fast | Great | Analytics, columnar queries |
| **ORC** | Excellent | Fast | Good | Hive/Spark ecosystems |
| **Avro** | Good | Medium | Great | Schema evolution, Kafka |
| **JSON** | Poor | Slow | Excellent | APIs, semi-structured |

```python
# Benchmark: 1GB data processing
CSV:     60 seconds (full scan)
Parquet: 5 seconds  (columnar, compression)
ORC:     4 seconds  (better compression)

# Cost impact: $0.06/GB scanned in BigQuery
CSV:     $0.06
Parquet: $0.005 (90% cheaper!)
```

#### 6.3 Partitioning & Indexing

```sql
-- Without index: Scan 100M rows to find 1000
SELECT * FROM orders WHERE customer_id = 123  → 30 seconds

-- With index: Direct lookup
CREATE INDEX idx_orders_customer ON orders(customer_id);
SELECT * FROM orders WHERE customer_id = 123  → 0.1 seconds
```

#### 6.4 Monitor Metrics

```
Track for each pipeline:
- Latency (runtime from start to finish)
- Throughput (records/second)
- Cost (compute + storage + data transfer)
- Resource usage (CPU, memory, disk)
- Quality (error rates, data completeness)

Example dashboard:
Daily Orders Pipeline
├─ Status: ✓ Success
├─ Duration: 3.2 minutes (vs avg 3.1m)
├─ Records: 142,531 orders loaded
├─ Quality: 99.97% valid (35 rejected)
├─ Cost: $0.48 for this run
└─ Alerts: None
```

---

### 7. Monitor & Maintain

**Goal:** Ensure pipelines stay healthy, fresh, and compliant.

#### 7.1 Data Freshness Monitoring

```
What gets tracked:
- Last successful run: 2026-04-10 14:30:00
- Expected run: 2026-04-11 03:00:00
- Freshness: 12 hours 30 minutes (within 24h SLA) ✓
- Next run: 2026-04-11 03:00:00 in 12.5 hours

Alert if:
- No successful run in last 25 hours → CRITICAL
- Last run failed → WARNING
- Latency >50% worse than normal → WARNING
```

#### 7.2 Volume & Anomaly Detection

```
Order volume monitoring:
- Normal daily: 50K-55K orders
- Today: 3K orders (94% below normal!)
- Status: CRITICAL alert
- Investigation: Check if source outage or data pipeline failure

Automated detection:
- 3-sigma rule: Anything >3x std dev is anomaly
- Trend analysis: Sudden changes in growth rate
- Seasonal patterns: Account for day-of-week, holidays
```

#### 7.3 Data Lineage & Governance

```
Order table lineage:
Source: PostgreSQL orders
  ↓
Pipeline: extract_orders (daily 03:00 UTC)
  ↓
Transform: dbt stg_orders (flatten, validate)
  ↓
Warehouse: analytics.orders_raw (Snowflake)
  ↓
Downstream: daily_revenue (aggregation)
         : customer_value (enrichment)
         : billing_report (export)

Ownership: Data Platform team
SLA: 99.5% availability, <1h freshness
DQ Rules: 5 checks (uniqueness, not null, range, etc)
```

---

## Common Pitfalls

- **No idempotency:** Retries cause duplicate data
- **Tight SLA without buffer:** Pipeline failures impact downstream users
- **No monitoring:** Discover data issues days later
- **Big bang rewrites:** Migrate incrementally, keep old + new in parallel
- **Ignoring cost:** Unoptimized pipelines become expensive at scale
- **No data quality checks:** Bad data propagates downstream

## Success Criteria

- ✓ Pipeline runs successfully 99%+ of the time
- ✓ Data available within SLA (1 hour, 1 day, etc)
- ✓ Can handle 10x data growth with same infrastructure
- ✓ Failures detected and alerted within 5 minutes
- ✓ Data quality issues identified at ingestion
- ✓ Pipeline costs track and optimize monthly
- ✓ Team can troubleshoot failures in <30 minutes
