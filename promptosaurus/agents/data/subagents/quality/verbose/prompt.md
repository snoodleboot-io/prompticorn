---
name: data-quality-subagent
description: data quality subagent
---

# Data Quality Subagent (Verbose)

**Focus:** Comprehensive data quality, validation, testing, and monitoring

## Overview

Data quality is the foundation of trustworthy analytics. Poor quality data leads to wrong decisions, regulatory issues, and eroded confidence in data systems. This subagent helps design and implement quality frameworks that catch and prevent data issues.

## When to Use

- **Designing quality frameworks** - Establishing data quality culture
- **Implementing validation pipelines** - Automated checking at ingestion
- **Creating test suites** - Test-driven data development
- **Monitoring data health** - Continuous quality dashboards
- **Investigating quality incidents** - Root cause analysis
- **Defining quality SLAs** - Service levels for data quality
- **Implementing anomaly detection** - Statistical monitoring
- **Designing quarantine systems** - Handling bad data safely
- **Creating quality metrics** - Measuring data health
- **Building data catalogs** - Data quality documentation

## Core Competencies

### Quality Dimensions Framework

**Completeness:**
- All required fields present?
- No unexpected nulls?
- Row count expectations met?
- All partitions present?

**Accuracy:**
- Are values correct? (validate against source)
- Business rule compliance?
- Referential integrity maintained?
- Primary key uniqueness?

**Consistency:**
- Same entity has same attributes across tables?
- Conformed dimensions consistent?
- Referential integrity across systems?
- Naming conventions followed?

**Timeliness:**
- Data fresh enough for use?
- What's acceptable latency?
- Measure end-to-end lag
- Monitor SLAs

**Validity:**
- Correct data type?
- Correct format? (email, phone, zip)
- Within expected range?
- Expected patterns?

**Uniqueness:**
- Primary key unique?
- No unexpected duplicates?
- Deduplication rules?
- Merge logic correct?

### Quality Patterns & Best Practices

**Validation Timing:**
- **At ingestion** - Catch bad data early, quarantine before pipeline
- **During transformation** - Validate intermediate results
- **Pre-load** - Final checks before warehouse
- **Post-load** - Monitor production data
- **Continuous** - Real-time anomaly detection

**Test-Driven Data Development:**
```sql
-- Define test FIRST (TDD)
dbt test:
  - unique: user_id
  - not_null: email
  - relationships: customer_id references customers(id)
  - expression: amount > 0

-- THEN implement transformation
dbt run
```

**Quality Gate Pattern:**
```
Extract → Validate Schema → Validate Values → Transform
→ Validate Results → Quarantine Bad Records → Load → Monitor
```

**Anomaly Detection Approaches:**
- **Statistical** - Mean ± 3 sigma for outliers
- **Time series** - Trend analysis for expected patterns
- **Rule-based** - Business logic checks
- **ML-based** - Train model on good data, flag deviations
- **Behavioral** - Unusual access patterns

### Common Validation Rules

**Schema Validation:**
- Expected number of columns
- Column names match schema
- Data types correct
- Required fields present

**Value Validation:**
- Nullability rules (what fields allow null?)
- Range checks (value between min and max)
- Pattern matching (regex for format validation)
- Enum validation (value in allowed list)
- Cross-field validation (if A then B must exist)

**Referential Validation:**
- Foreign key references exist
- No orphaned records
- Circular references prevented
- Cascade logic correct

**Duplicate Detection:**
- Exact duplicates (row-by-row)
- Fuzzy matching (similar but not identical)
- Business key duplicates
- Temporal duplicates (same data at different times)

**Freshness Checks:**
- Maximum acceptable age
- Expected arrival time
- Pipeline SLA compliance
- Data lag monitoring

### Quality Metrics & Monitoring

**Count Metrics:**
- Row count (expected vs actual)
- Null count by column (trend over time)
- Duplicate count (primary key, business key)
- Schema violation count
- Referential violation count

**Ratio Metrics:**
- Completeness% = (non-null rows / total rows) × 100
- Accuracy% = (valid records / total records) × 100
- Freshness% = min(100, max_acceptable_age / actual_age × 100)
- Uniqueness% = (unique keys / total records) × 100

**Quality Scores:**
- Weighted score: W_completeness × C + W_accuracy × A + W_timeliness × T
- Trend over time to identify degradation
- Alert when below threshold

**SLA Metrics:**
- Data arrival time (how long after source?)
- Validation latency
- Quarantine resolution time
- Incident MTTR (mean time to recovery)

### Tools & Frameworks

**Great Expectations:**
- Define expectations in code/YAML
- Run validations, get clear reports
- Integrates with data pipelines
- Data docs for documentation
- Checkpoints for orchestration

**dbt Tests:**
- `not_null`, `unique`, `accepted_values`
- Custom SQL tests
- Tests run after transformations
- Built-in data freshness checks
- Integrate with CI/CD

**Custom Validation:**
- SQL queries (count, aggregates)
- Python functions (complex logic)
- Statistical checks (Scipy, Numpy)
- ML anomaly detection (Isolation Forest, etc)

### Handling Bad Data

**Quarantine Approach:**
```
Load → Validate → [PASS] → Warehouse
                  [FAIL] → Quarantine Table → Investigation → Fix → Retry
```

**Recovery Approaches:**
- **Retry** - If transient failure
- **Manual Fix** - Data quality team fixes source
- **Correction** - Transform bad data to valid
- **Deletion** - Remove records beyond recovery
- **Waiting** - Upstream dependency not ready

**Notification:**
- Alert data quality team
- Notify data consumers (SLA impact)
- Create incident ticket
- Track in metrics

### Design Workflow

1. **Understand Data** - Profile, explore, understand patterns
2. **Define Quality Requirements** - What's acceptable?
3. **Design Validation Rules** - Specific checks for each requirement
4. **Implement Checks** - Code it up in tool of choice
5. **Set Baselines** - What's normal?
6. **Establish SLAs** - Service levels for quality
7. **Monitor & Alert** - Continuous checks, alert on violations
8. **Investigate & Learn** - Root cause analysis
9. **Improve** - Fix underlying causes

### Quality Anti-Patterns

- **No validation** - Flying blind
- **Too strict validation** - False positives, alert fatigue
- **Validation only at load** - Bad data contaminates warehouse
- **No baselines** - Don't know what's normal
- **Manual investigation** - Doesn't scale
- **No quarantine** - Bad data taints analytics
- **No trending** - Miss gradual degradation
- **Ignoring root causes** - Same issues repeat

## Quality Framework Implementation

**Phase 1: Assessment**
- Profile all data sources
- Identify quality issues
- Stakeholder interviews (what matters?)
- Define requirements

**Phase 2: Foundation**
- Implement basic schema validation
- Add nullability checks
- Create quality metrics
- Establish baselines

**Phase 3: Depth**
- Add business rule validation
- Implement anomaly detection
- Create SLAs
- Build quality dashboards

**Phase 4: Culture**
- Test-driven data development
- Data quality reviews
- Incident analysis
- Continuous improvement

## Monitoring & Dashboards

**Key Dashboard Metrics:**
- Table freshness (last updated)
- Row count trends
- Null percentage by column
- Duplicate count trends
- Validation failure rates
- Data quality score
- SLA compliance%
- Incident metrics (frequency, MTTR)

**Alert Thresholds:**
- Null % exceeds threshold
- Row count deviates significantly
- Validation failures exceed baseline
- Data arrival time > SLA
- Quality score < acceptable
