---
name: data-pipeline
description: "Design and implement ETL/ELT data pipelines"
version: "1.0"
languages: ["python", "sql", "hcl"]
subagents: ["data/pipeline", "data/quality", "orchestrator"]
---

# Data Pipeline Workflow (Minimal)

## Purpose
Design, build, and optimize ETL/ELT pipelines for moving and transforming data at scale.

## Steps

### 1. Define Data Flow
- What are the source systems (databases, APIs, files)?
- What is the destination (warehouse, lake, cache)?
- What transformations are needed?
- What is the expected volume and velocity?

### 2. Choose Pipeline Architecture
- ETL (extract-transform-load) vs ELT (extract-load-transform)
- Batch vs streaming vs hybrid
- Orchestration tool (Airflow, dbt, Prefect, Beam)
- Scheduling frequency (hourly, daily, real-time)

### 3. Implement Idempotency
- Design for safe retries (exactly-once semantics)
- Use natural keys for deduplication
- Handle late-arriving data and out-of-order events
- Implement checkpointing for recovery

### 4. Add Incremental Processing
- Capture changed data (CDC)
- Use timestamps or sequence numbers
- Partition data for efficient incremental loads
- Handle backfills for historical corrections

### 5. Design Error Handling
- Validate source data quality
- Log transformation failures with context
- Implement dead letter queues for bad records
- Alert on pipeline failures

### 6. Optimize Performance
- Parallelize extraction and transformation
- Use appropriate data formats (Parquet, ORC)
- Index and partition for query performance
- Monitor pipeline latency and resource usage

### 7. Monitor & Maintain
- Track data freshness (time since last successful run)
- Monitor volume, latency, and error rates
- Set up alerts for SLA violations
- Document lineage for data governance
