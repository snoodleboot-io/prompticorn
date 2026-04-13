---
name: data-quality
description: "Comprehensive data quality framework including validation rules, testing, monitoring, and governance"
version: "1.0"
languages: ["python", "sql"]
subagents: ["data/quality", "data/pipeline", "observability/metrics"]
---

# Data Quality Workflow (Verbose)

## Purpose
Establish comprehensive data quality and testing framework to catch issues early, prevent bad data propagation, maintain user trust in analytics, and ensure compliance with data governance requirements.

## When to Use This Workflow
- Building new data pipelines
- Improving existing data quality practices
- Implementing compliance requirements (GDPR, CCPA)
- Responding to data quality incidents
- Setting up data governance program
- Preparing data for machine learning

## Prerequisites
- Understanding of data pipeline stages
- Knowledge of business logic and rules
- Access to data platforms (warehouse, testing tools)
- Team expertise in SQL, testing frameworks
- Stakeholder alignment on quality standards

---

## Steps

### 1. Define Quality Dimensions

**Goal:** Establish what "good data" means for your organization.

#### 1.1 The Six Quality Dimensions

**Completeness: Are all required fields present?**
```
Example rules:
- customer_id: REQUIRED (100% completion)
- email: REQUIRED for registered users (99%+ completion)
- phone: OPTIONAL (can be null)
- last_purchase_date: For customers with orders (100% if has_orders=true)

Acceptable thresholds:
- Critical fields: 100% (0 nulls allowed)
- Important fields: 99%+ (less than 1% nulls)
- Optional fields: Any (can be null)
```

**Accuracy: Does data match source of truth?**
```
Example rules:
- customer name matches CRM system (100% accuracy)
- order total = sum of line items (100% accuracy)
- user age >= 0 and <= 150 (100% valid)
- email format matches RFC 5322 standard

Validation approach:
- Audit join: Compare warehouse vs source system
  SELECT * FROM warehouse.customers w
  LEFT JOIN source_system.customers s 
    ON w.customer_id = s.id
  WHERE w.name != s.name OR w.email != s.email
  
- Business logic checks
  SELECT order_id FROM orders
  WHERE total != SUM(line_items.price)
  GROUP BY order_id
```

**Consistency: Are values consistent across tables?**
```
Example rules:
- customer appears in both orders and customers table
- order.customer_id exists in customers.id (referential integrity)
- revenue in reporting matches accounting system (±$0.01)

Validation:
- Referential integrity: Foreign key relationships valid
- Cross-system match: Different systems agree on facts
- Dimension consistency: Customer attributes same everywhere
```

**Timeliness: Is data fresh enough?**
```
Example rules:
- Orders available within 1 hour of transaction
- Customer profiles updated within 24 hours
- Historical data preserved for 7 years
- Real-time dashboards update every 5 minutes

SLA example:
- Data freshness: 95th percentile <1 hour
- Pipeline availability: 99.5%
- Maximum acceptable delay before alert: 2 hours
```

**Validity: Do values conform to format/range?**
```
Example rules:
- Email matches email pattern (user@domain.com)
- Phone numbers are 10 digits
- Dates in ISO 8601 format (YYYY-MM-DD)
- Currency values positive or zero
- Age between 0-150 years
- Discount percentage between 0-100%

Implementation:
- Type checks: Correct data type (string, int, date)
- Format validation: Regex patterns for strings
- Range validation: Min/max boundaries for numbers
- Enum validation: Value in allowed set (region in [US, EU, APAC])
- Cross-field validation: OrderDate <= ShipDate <= DeliveryDate
```

**Uniqueness: Is data properly deduplicated?**
```
Example rules:
- customer_id is unique in customers table
- (customer_id, order_date) is unique for daily snapshot
- email is unique (no duplicate account registrations)
- product_sku is unique in product catalog

Validation:
SELECT customer_id, COUNT(*) as cnt
FROM customers
GROUP BY customer_id
HAVING cnt > 1
-- Should return 0 rows
```

#### 1.2 Quality Dimensions Matrix

Create a matrix for all important tables:

```
Table: orders
┌─────────────┬─────────┬──────────┬─────────┬─────────┬────────────┐
│ Field       │ Complete│ Accurate │ Consisten│ Timely │ Valid      │
├─────────────┼─────────┼──────────┼──────────┼────────┼────────────┤
│ order_id    │ 100%    │ Yes      │ Yes      │ -      │ INT format │
│ customer_id │ 100%    │ Yes      │ FK→cust  │ -      │ INT format │
│ total       │ 100%    │ 100%     │ =Sum()   │ -      │ ≥ 0        │
│ status      │ 100%    │ Yes      │ -        │ <1m    │ ENUM       │
│ created_at  │ 100%    │ Yes      │ Yes      │ 1 hour │ ISO 8601   │
│ notes       │ 10%     │ -        │ -        │ -      │ TEXT       │
└─────────────┴─────────┴──────────┴──────────┴────────┴────────────┘
```

---

### 2. Design Quality Checks

**Goal:** Create specific, measurable checks to verify data quality.

#### 2.1 Row-Level Checks

```sql
-- Null/completeness checks
SELECT COUNT(*) as null_count
FROM orders
WHERE customer_id IS NULL  -- Should be 0

-- Data type checks
SELECT COUNT(*) as invalid_count
FROM orders
WHERE TYPEOF(total) != 'DECIMAL'

-- Range validation
SELECT COUNT(*) as invalid_range
FROM customers
WHERE age < 0 OR age > 150

-- Pattern/format validation
SELECT COUNT(*) as invalid_email
FROM customers
WHERE email NOT LIKE '%@%.%'  -- Simple email pattern

-- Enumeration validation
SELECT COUNT(*) as invalid_status
FROM orders
WHERE status NOT IN ('pending', 'processing', 'completed', 'cancelled')
```

#### 2.2 Aggregate Checks

```sql
-- Row count anomaly (significant deviation from normal)
SELECT COUNT(*) as row_count
FROM orders
WHERE created_date = CURRENT_DATE;
-- Alert if count < 10K (normal 50K daily)

-- Distribution anomaly
SELECT status, COUNT(*) as cnt
FROM orders
WHERE created_date = CURRENT_DATE
GROUP BY status;
-- Alert if any status drastically different (e.g., 99% cancelled)

-- Aggregation verification
SELECT 
  order_id,
  total,
  SUM(line_item_amount) as calculated_total
FROM orders o
JOIN order_lines ol ON o.order_id = ol.order_id
GROUP BY order_id, total
HAVING total != calculated_total;
-- Should return 0 rows
```

#### 2.3 Referential Integrity

```sql
-- Foreign key validation
SELECT COUNT(*) as orphaned_orders
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
-- Should be 0

-- Cardinality checks
SELECT 
  COUNT(DISTINCT customer_id) as unique_customers,
  COUNT(*) as total_orders
FROM orders;
-- Orders should be ≥ customers (one customer can have many orders)
```

#### 2.4 Business Logic Checks

```sql
-- Dates in correct order
SELECT COUNT(*) as invalid_dates
FROM orders
WHERE created_at > shipped_at  -- Creation before shipping!

-- Financial calculations
SELECT COUNT(*) as calculation_errors
FROM orders
WHERE subtotal + tax + shipping != total;

-- Business rule violation
SELECT COUNT(*) as invalid_discounts
FROM orders
WHERE discount_amount < 0 OR discount_amount > subtotal;
```

---

### 3. Implement Testing Framework

**Goal:** Automate quality checks into pipeline.

#### 3.1 dbt Testing (SQL-based)

```yaml
# models/orders.yml
models:
  - name: orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('customers')
              field: customer_id
      - name: status
        tests:
          - not_null
          - accepted_values:
              values: ['pending', 'processing', 'completed', 'cancelled']
      - name: total
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_of_type:
              column_type: decimal
```

**Run dbt tests in pipeline:**
```bash
dbt test  # Run all tests
dbt test --select orders  # Test specific model

# Fail pipeline if tests fail
if ! dbt test; then
  echo "Quality checks failed!"
  exit 1
fi
```

#### 3.2 Python Data Quality Framework

```python
from great_expectations.dataset import PandasDataset

# Load and validate data
df = pandas.read_csv('orders.csv')
ds = PandasDataset(df)

# Define expectations (Great Expectations library)
ds.expect_table_row_count_to_be_between(40_000, 60_000)
ds.expect_column_values_to_not_be_null('order_id')
ds.expect_column_values_to_be_in_set('status', 
    ['pending', 'processing', 'completed', 'cancelled'])
ds.expect_column_values_to_be_between('total', min_value=0)

# Validate and get report
validation_result = ds.validate()
if not validation_result['success']:
    send_alert(f"Quality validation failed: {validation_result}")
    raise DataQualityException(validation_result)
```

#### 3.3 Pandas Assertions

```python
def validate_orders(df):
    assert df['order_id'].is_unique, "Duplicate order_ids"
    assert df['customer_id'].notna().all(), "Null customer_ids"
    assert (df['total'] >= 0).all(), "Negative totals"
    assert df['status'].isin(['pending', 'processing', 'completed', 'cancelled']).all(), \
        "Invalid status values"
    assert len(df[df['created_at'] > df['shipped_at']]) == 0, \
        "Orders shipped before creation"
    
    return True  # All checks passed
```

#### 3.4 Quality Gates in Pipeline

```python
def run_data_pipeline():
    # Extract
    raw_data = extract_from_source()
    
    # Quality gate 1: Completeness
    if raw_data.isna().sum() / len(raw_data) > 0.05:  # >5% nulls
        raise DataQualityException("High null rate in source")
    
    # Transform
    transformed = transform(raw_data)
    
    # Quality gate 2: Uniqueness
    if not transformed['order_id'].is_unique:
        raise DataQualityException("Duplicate order_ids after transform")
    
    # Load
    load_to_warehouse(transformed)
    
    # Quality gate 3: Freshness
    verify_data_freshness()
```

---

### 4. Set Up Monitoring & Alerts

**Goal:** Detect quality issues in real-time, notify team.

#### 4.1 Dashboards

```
Data Quality Dashboard
┌─────────────────────────────────────────────────────────┐
│ Table: orders (Last 24 Hours)                            │
├────────────────────────┬────────────┬──────────┬─────────┤
│ Metric                 │ Value      │ Trend    │ Status  │
├────────────────────────┼────────────┼──────────┼─────────┤
│ Completeness           │ 99.8%      │ ↑ +0.1%  │ ✓ PASS  │
│ Accuracy               │ 99.97%     │ ↔ Stable │ ✓ PASS  │
│ Null customer_id       │ 0          │ ↓        │ ✓ PASS  │
│ Duplicates             │ 0          │ ↑ Stable │ ✓ PASS  │
│ Invalid status         │ 2          │ ↑ NEW    │ ⚠ WARN  │
│ Total-calc mismatch    │ 0          │ ↔ Stable │ ✓ PASS  │
│ Data latency (p95)     │ 28 min     │ ↑ +3min  │ ✓ PASS  │
└────────────────────────┴────────────┴──────────┴─────────┘

Top Issues (Last 7 Days):
1. Invalid status values (15 records) - Not null, but wrong value
2. Late arrivals (2% of records) - Arrived >1 hour after timestamp
3. Orphaned order_ids (0 records) - FK violations resolved
```

#### 4.2 Alert Rules

```yaml
Alerts:
  - name: high_null_rate
    threshold: >0.01  # >1% nulls
    severity: CRITICAL
    on_field: customer_id
    notify: [data-platform, analysts]
  
  - name: duplicate_detected
    threshold: >0
    severity: CRITICAL
    on_field: order_id
    notify: [data-platform]
  
  - name: data_late
    threshold: >60 minutes
    severity: WARNING
    metric: pipeline_latency
    notify: [data-platform]
  
  - name: accuracy_declining
    threshold: <99%
    severity: WARNING
    metric: validation_pass_rate
    notify: [data-platform, analysts]
```

---

### 5. Create SLAs

**Goal:** Define and track service level agreements for data quality.

#### 5.1 Sample SLAs

```
Orders Table SLA

Availability:
- Target: 99.5%
- Acceptable downtime: 3.6 hours/month
- Current: 99.72% (exceeding)

Freshness:
- Target: Data available within 1 hour (p95)
- Current: 28 minutes avg, 45 minutes p95 (exceeding)

Accuracy:
- Target: 99.9% valid records
- Current: 99.97% (exceeding)

Completeness:
- Target: 99%+ for required fields
- Current: 99.8% (meeting)

Row Count:
- Target: 45K-55K orders/day
- Current: 51,234 orders/day (within range)
```

#### 5.2 SLA Reporting

```
Weekly Quality Report
Reporting Period: Apr 4-10, 2026

Table: customers
- Availability: 99.8% ✓
- Freshness: 12min avg ✓
- Accuracy: 99.98% ✓
- No incidents

Table: orders
- Availability: 99.6% ✓
- Freshness: 28min avg ✓
- Accuracy: 99.97% ✓
- 1 incident: 15 invalid status values (resolved)

Overall: 99.7% availability, all SLAs met
```

---

### 6. Establish Remediation Process

**Goal:** Handle quality issues systematically.

#### 6.1 Issue Triage

```
When quality check fails:

1. Severity Assessment
   CRITICAL: Bad data already propagated to reports
   → Alert team immediately, plan correction
   
   HIGH: Quality gate caught bad data before warehouse
   → Alert team, prevent load, investigate
   
   MEDIUM: Anomaly detected but within threshold
   → Log for trend analysis, monitor
   
   LOW: Minor issue in non-critical field
   → Document, include in weekly report

2. Root Cause Analysis
   Data issue → Fix at source
   Pipeline bug → Fix transformation
   System issue → Fix infrastructure
   Configuration → Update rules

3. Remediation
   Option A: Fix at source (preferred)
     - Fix underlying issue in source system
     - Prevents future issues
     - Usually slower
   
   Option B: Fix in pipeline (common)
     - Add validation step
     - Transform problematic values
     - Effective immediately
   
   Option C: Fix in warehouse (rare)
     - Backfill corrected values
     - Only for approved corrections
     - Requires audit trail

4. Prevention
   - Add quality check to catch in future
   - Update documentation
   - Review related data
   - Train team on prevention
```

#### 6.2 Backfill Procedure

```sql
-- Correct historical data with audit trail
CREATE TABLE orders_corrections (
  correction_id SERIAL PRIMARY KEY,
  order_id INT,
  field_name VARCHAR,
  old_value TEXT,
  new_value TEXT,
  reason VARCHAR,
  corrected_by VARCHAR,
  corrected_at TIMESTAMP DEFAULT NOW()
);

-- Record the correction
INSERT INTO orders_corrections (order_id, field_name, old_value, new_value, reason)
SELECT order_id, 'status', status, 'completed', 'Backfill for incident #12345'
FROM orders
WHERE order_id IN (SELECT order_id FROM orders_corrections_needed);

-- Apply correction
UPDATE orders
SET status = 'completed'
WHERE order_id IN (SELECT order_id FROM orders_corrections_needed);

-- Audit trail preserved in orders_corrections table
```

---

### 7. Governance & Compliance

**Goal:** Track ownership, document rules, maintain audit trail.

#### 7.1 Data Ownership & Documentation

```
Table: orders
Owner: Payment Platform team (john.smith@company.com)
Steward: Data Platform team

Quality Rules (5 defined):
1. order_id uniqueness
2. customer_id not null + valid FK
3. status in {pending, processing, completed, cancelled}
4. total >= 0
5. created_at < shipped_at

Compliance Mappings:
- GDPR: customer_id is PII
  → Masked in analytics environments
  → Purged after 7 years
- CCPA: customer consent tracked
  → Only load if customer_id in consent list
- SOC 2: Data integrity
  → Validated via quality checks above
```

#### 7.2 Audit Trail

```
Quality Events Log
┌─────────┬─────────────┬──────────┬────────────┬─────────────────┐
│ Date    │ Table       │ Check    │ Result     │ Action          │
├─────────┼─────────────┼──────────┼────────────┼─────────────────┤
│ Apr 10  │ orders      │ Null FKs │ 0 (pass)   │ None            │
│ Apr 10  │ orders      │ Dups     │ 0 (pass)   │ None            │
│ Apr 9   │ orders      │ Status   │ 15 invalid │ Alert + backfill│
│ Apr 9   │ orders      │ Nulls    │ 3 (pass)   │ None            │
└─────────┴─────────────┴──────────┴────────────┴─────────────────┘
```

---

## Common Pitfalls

- **Catching issues too late:** Validation only in warehouse, not pipeline
- **No root cause fix:** Applying band-aid in pipeline instead of fixing source
- **Alert fatigue:** Too many alerts, team ignores them
- **Orphaned rules:** Quality checks that nobody maintains
- **Silent failures:** Pipeline succeeds with bad data loaded
- **No prioritization:** Treating all quality issues equally

## Success Criteria

- ✓ 100% of critical field nulls caught before warehouse load
- ✓ Data quality issues detected within 5 minutes of occurrence
- ✓ <1% of data rows fail quality checks
- ✓ All SLAs met (freshness, accuracy, availability)
- ✓ 99%+ of pipeline runs without quality failures
- ✓ Root cause analysis completed within 24 hours of incident
- ✓ Team responds to alerts within 30 minutes
- ✓ Quality remediation prevents recurrence
