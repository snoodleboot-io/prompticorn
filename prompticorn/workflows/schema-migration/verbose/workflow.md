---
name: "schema-migration"
description: "Comprehensive guide to zero-downtime schema migrations with backward compatibility and rollback planning"
version: "1.0"
languages: ["sql"]
subagents: ["data/pipeline", "orchestrator"]
---

# Schema Migration Workflow (Verbose)

## Purpose
Safely evolve database schemas while maintaining zero downtime, backward compatibility with existing code, and ability to rollback if issues discovered.

## When to Use This Workflow
- Adding new columns to tables
- Removing deprecated columns
- Changing column types or constraints
- Renaming tables or columns
- Creating new tables or indexes
- Splitting tables or normalizing schema
- Any change to production database schema

## Prerequisites
- Understanding of current schema and queries
- Knowledge of application code using schema
- Access to staging environment matching production
- Backup and disaster recovery procedures in place
- Team agreement on migration plan

---

## Steps

### 1. Plan the Change

**Goal:** Understand scope and impact before making changes.

#### 1.1 Current State Analysis

```sql
-- Document current table structure
DESCRIBE orders;
-- Output:
-- order_id INT PRIMARY KEY
-- customer_id INT NOT NULL
-- order_date DATE NOT NULL
-- total DECIMAL(10,2) NOT NULL
-- status VARCHAR(20) NOT NULL

-- Find all indexes
SHOW INDEXES FROM orders;

-- Find all foreign key references
SELECT * FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
WHERE TABLE_NAME = 'orders';

-- Find all views using this table
SELECT * FROM INFORMATION_SCHEMA.VIEWS 
WHERE TABLE_SCHEMA = 'production' 
AND VIEW_DEFINITION LIKE '%orders%';

-- Find all stored procedures
SELECT * FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_SCHEMA = 'production' 
AND ROUTINE_DEFINITION LIKE '%orders%';
```

#### 1.2 Design New Schema

Document the change clearly:

```
Migration: Add payment_method column to orders

BEFORE:
orders (
  order_id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  order_date DATE NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  status VARCHAR(20) NOT NULL
)

AFTER:
orders (
  order_id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  order_date DATE NOT NULL,
  total DECIMAL(10,2) NOT NULL,
  status VARCHAR(20) NOT NULL,
  payment_method VARCHAR(20)  -- NEW COLUMN
)

Affected objects:
- 3 views depend on this table
- 5 stored procedures query orders
- 2 indexes will need updates
- Payment processing app writes payment data

Data migration:
- Existing 5M orders: default payment_method = 'unknown'
- New orders: application must provide payment_method
```

#### 1.3 Impact Assessment

```
Checklist:
[ ] What tables are affected?
[ ] What indexes need updating?
[ ] What views read this table?
[ ] What applications depend on this schema?
[ ] What stored procedures need changes?
[ ] What queries will be affected?
[ ] What is the data volume?
[ ] How long will migration take?
[ ] Will production traffic continue during migration?
[ ] Can we lock the table if needed?
[ ] Do we need a rollback plan?

Risk assessment:
[ ] HIGH: Table is heavily queried (orders: 100K qps)
[ ] MEDIUM: Views/procedures need updating
[ ] LOW: No dependent application code
[ ] CRITICAL: Must support 24/7 uptime
[ ] NICE-TO-HAVE: Can tolerate brief maintenance window
```

---

### 2. Ensure Backward Compatibility

**Goal:** Enable zero-downtime migration by making schema changes non-breaking.

#### 2.1 Additive Changes Only

**Bad approach (causes downtime):**
```sql
-- WRONG: Remove old column, breaks running application
ALTER TABLE orders DROP COLUMN shipped_date;
-- Applications expecting shipped_date column CRASH
```

**Good approach (zero downtime):**
```sql
-- Step 1: Add new column
ALTER TABLE orders ADD COLUMN shipped_date_new DATE DEFAULT NULL;

-- Step 2: App dual-writes (writes to both old and new)
-- Step 3: App dual-reads (reads from new, fallback to old)

-- Step 4: Migrate data
UPDATE orders SET shipped_date_new = shipped_date;

-- Step 5: Remove old column (after app updated)
ALTER TABLE orders DROP COLUMN shipped_date;
```

#### 2.2 Type Changes (Careful)

**Changing column type (dangerous):**
```sql
-- RISKY: ALTER TYPE directly often fails
ALTER TABLE customers MODIFY COLUMN age SMALLINT;

-- SAFER: Create new column, migrate, then drop old
ALTER TABLE customers ADD COLUMN age_new SMALLINT;
UPDATE customers SET age_new = CAST(age AS SMALLINT);
ALTER TABLE customers DROP COLUMN age;
ALTER TABLE customers RENAME COLUMN age_new TO age;
```

#### 2.3 Dual Write Pattern

```python
# Application code during migration

class OrderService:
    def save_order(self, order_data):
        # Dual write: Write to both columns
        customer_order = CustomerOrder(
            customer_id=order_data['customer_id'],
            # Old column (deprecated)
            customer_num=order_data['customer_id'],
            # New column (preferred)
            customer_id_new=order_data['customer_id']
        )
        customer_order.save()
    
    def read_order(self, order_id):
        # Dual read: Read from new column, fallback to old
        order = Order.get(order_id)
        
        # Prefer new column
        customer_id = order.customer_id_new
        
        # Fallback to old column if new is null
        if customer_id is None:
            customer_id = order.customer_num
        
        return {
            'order_id': order.order_id,
            'customer_id': customer_id
        }
```

#### 2.4 Constraint Management

**Adding constraints safely:**
```sql
-- BAD: Adding NOT NULL constraint to column with nulls FAILS
ALTER TABLE orders MODIFY COLUMN status VARCHAR(20) NOT NULL;
-- Error: Column 'status' contains null values!

-- GOOD: Add nullable column first, populate, then add constraint
ALTER TABLE orders ADD COLUMN status_new VARCHAR(20);
UPDATE orders SET status_new = COALESCE(status, 'unknown');
ALTER TABLE orders MODIFY COLUMN status_new VARCHAR(20) NOT NULL;
-- Update views/procedures to use status_new
ALTER TABLE orders DROP COLUMN status;
ALTER TABLE orders RENAME COLUMN status_new TO status;
```

---

### 3. Pre-Migration Validation

**Goal:** Test thoroughly before running on production.

#### 3.1 Staging Environment Testing

```bash
# 1. Create staging environment with production data
backup_production_to_staging()

# 2. Run migration script on staging
./migrate_staging.sh

# 3. Verify schema changes
verify_schema_matches_expected()

# 4. Run test suite
pytest tests/  # All tests should pass

# 5. Performance test
run_performance_tests_on_staging()
# Before migration: 100ms avg query
# After migration: 100ms avg query (no regression)

# 6. Test rollback on staging
execute_rollback_script()
verify_schema_reverted()
```

#### 3.2 Migration Script Example

```sql
-- File: migrations/20260410_add_payment_method.sql
-- Description: Add payment_method column to orders table
-- Rollback: See migrations/20260410_rollback.sql

BEGIN TRANSACTION;

-- Add new column (non-blocking on modern databases)
ALTER TABLE orders 
ADD COLUMN payment_method VARCHAR(20) DEFAULT NULL;

-- Add index on new column for queries
CREATE INDEX idx_orders_payment_method ON orders(payment_method);

-- Update existing rows (can take time on large tables)
-- Use batch processing to avoid locking
UPDATE orders SET payment_method = 'unknown' WHERE payment_method IS NULL;

-- Add constraint (now that all values filled)
ALTER TABLE orders MODIFY COLUMN payment_method VARCHAR(20) NOT NULL DEFAULT 'unknown';

COMMIT;

-- Verify migration
SELECT COUNT(*) FROM orders WHERE payment_method IS NULL;  -- Should be 0
```

#### 3.3 Rollback Script

```sql
-- File: migrations/20260410_rollback.sql
-- Rollback: Remove payment_method column

BEGIN TRANSACTION;

-- Drop index first
DROP INDEX idx_orders_payment_method;

-- Drop the column
ALTER TABLE orders DROP COLUMN payment_method;

COMMIT;

-- Verify rollback
DESCRIBE orders;  -- payment_method should not exist
```

#### 3.4 Testing Checklist

```
Pre-migration Testing:
[ ] Staging environment matches production
[ ] Migration script tested on staging
[ ] All data migrated successfully
[ ] Indexes created and performing
[ ] Views and procedures still work
[ ] Test suite passes 100%
[ ] Performance regression tests pass
[ ] Rollback tested and verified
[ ] Team notified and ready
[ ] Monitoring/alerts prepared
[ ] Runbook documented
```

---

### 4. Execute Migration (Zero Downtime)

**Goal:** Apply changes with no application downtime.

#### 4.1 Pre-Execution Checklist

```
30 minutes before:
[ ] Notify team via Slack/email
[ ] Check staging status and recent changes
[ ] Review monitoring/alerting setup
[ ] Ensure backup of production taken
[ ] Team on standby for rollback

5 minutes before:
[ ] Stop application deployments
[ ] Verify no locks on table
[ ] Start detailed monitoring
[ ] Have rollback script ready
[ ] Test database connection works
```

#### 4.2 Execution Steps

```
Timeline:
T+0: Execute migration script
T+1: Verify schema changes applied
T+2: Run post-migration tests
T+3: Update application (if needed)
T+4: Start dual-write phase
T+5: Validate dual-write working
T+10: Monitor for issues
```

#### 4.3 During Execution

```bash
#!/bin/bash

set -e  # Exit on error

echo "Starting schema migration at $(date)"

# 1. Execute migration
mysql production < migrations/20260410_add_payment_method.sql
if [ $? -ne 0 ]; then
    echo "Migration failed! Rolling back..."
    mysql production < migrations/20260410_rollback.sql
    exit 1
fi

# 2. Verify changes
RESULT=$(mysql production -e "SELECT COUNT(*) FROM orders WHERE payment_method IS NOT NULL;")
if [ "$RESULT" -lt 5000000 ]; then  # Expected 5M+ orders
    echo "Verification failed! Data not migrated!"
    exit 1
fi

# 3. Rebuild indexes if needed
ANALYZE TABLE orders;

# 4. Notify team
echo "Migration successful at $(date)"
send_alert("Schema migration completed successfully")
```

---

### 5. Dual Write / Dual Read Period

**Goal:** Run new and old code paths in parallel to validate correctness.

#### 5.1 Dual Write Duration

```
Timeline for column addition:

Week 1: New column added, code deployed
- Application writes to both old and new columns
- Database: Old column for legacy code, new column for validation
- Monitoring: Check data consistency

Week 2-3: Data consistency validation
- Run nightly job comparing old vs new columns
- Spot check rows for correctness
- Monitor query performance

Week 4: Deprecation phase
- Stop writing to old column
- Continue reading from new column
- Monitor for any issues

Week 5: Cleanup
- Remove old column once confident
- Clean up old indexes
```

#### 5.2 Data Consistency Monitoring

```sql
-- Daily check: Validate old and new columns match
SELECT 
  COUNT(*) as mismatched_rows,
  COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders) as pct_mismatch
FROM orders
WHERE customer_id != customer_id_new
  AND customer_id_new IS NOT NULL;
  
-- If >0 mismatches: Investigate root cause!
```

#### 5.3 Application Code Changes

```python
# During dual-write phase

class OrderRepository:
    def save(self, order):
        # Write to BOTH columns
        query = """
        UPDATE orders 
        SET 
          status = :status,           # Old column
          status_new = :status        # New column
        WHERE order_id = :order_id
        """
        db.execute(query, {
            'status': order.status,
            'status_new': order.status,
            'order_id': order.order_id
        })
    
    def get(self, order_id):
        # Read from NEW column, fallback to OLD
        result = db.query("""
        SELECT 
          order_id,
          COALESCE(status_new, status) as status,
          customer_id,
          amount
        FROM orders
        WHERE order_id = :order_id
        """, {'order_id': order_id})
        
        return result[0]
```

---

### 6. Deprecation Phase

**Goal:** Stop using old code path, prepare for cleanup.

#### 6.1 Remove from Dual Write

```python
# After validation period, stop writing to old column

class OrderRepository:
    def save(self, order):
        # Write to NEW column ONLY
        query = """
        UPDATE orders 
        SET status_new = :status
        WHERE order_id = :order_id
        """
        db.execute(query, {
            'status': order.status,
            'order_id': order.order_id
        })
```

#### 6.2 Final Validation

```sql
-- Confirm no code still reading old column
-- (Usually done via code review, not SQL)

-- Verify all data in new column
SELECT 
  COUNT(*) as total_rows,
  SUM(CASE WHEN status_new IS NULL THEN 1 ELSE 0 END) as null_count,
  ROUND(100.0 * SUM(CASE WHEN status_new IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_null
FROM orders;
-- Should show: pct_null = 0
```

---

### 7. Cleanup & Finalization

**Goal:** Remove old column and documentation.

#### 7.1 Remove Old Column

```sql
-- Only after confident new column is working
ALTER TABLE orders DROP COLUMN status;

-- Drop old indexes
DROP INDEX idx_orders_status_old;

-- Rebuild statistics for query optimizer
ANALYZE TABLE orders;
```

#### 7.2 Update Documentation

```markdown
# Schema Change Log

## 2026-04-10: Add payment_method to orders

**What changed:**
- Added `payment_method VARCHAR(20)` column to orders table
- Migrated payment data from external system

**Impact:**
- Application code no longer needs external payment lookup
- Queries can filter/group by payment_method directly

**Timeline:**
- 2026-04-10: Column added
- 2026-04-10 to 2026-04-24: Dual-write period
- 2026-04-24: Deprecated old external lookup
- 2026-04-30: Old column removed

**Testing:**
- Staging tested: ✓
- Performance impact: None
- Rollback tested: ✓
```

#### 7.3 Lessons Learned

```
Post-migration retrospective:

What went well:
- Staging testing caught index name collision
- Dual-write phase validated 100% data consistency
- Zero downtime achieved (0 seconds unavailable)

What to improve:
- Communication could have been earlier to app team
- Performance testing revealed query plan change (benign)
- Documentation took longer than expected

For next time:
- Schedule schema changes in QA period, not Friday
- Add application team to pre-migration review
- Document expected vs actual performance metrics
```

---

## Common Pitfalls

- **Removing old column too quickly:** Application still uses it → crash
- **Large table migration without batching:** Locks table for hours
- **No rollback plan:** Can't recover if migration fails
- **Changing type without intermediate column:** Data loss or conversion errors
- **No monitoring:** Don't realize performance regression until users complain
- **Skipping staging test:** Bug found in production (too late)

## Migration Tools by Database

| Database | Zero-Downtime Tool | Cost | Complexity |
|----------|-------------------|------|------------|
| PostgreSQL | pg_online_migrations | Free | Low |
| MySQL | Percona pt-online-schema-change | Paid | Medium |
| PostgreSQL | pg_repack | Free | Medium |
| MySQL 8.0+ | Online DDL | Built-in | Low |

## Success Criteria

- ✓ Zero downtime achieved (0 seconds unavailable)
- ✓ All data migrated correctly
- ✓ No performance regression
- ✓ Rollback tested and documented
- ✓ Team comfortable with process
- ✓ All dependent applications working
- ✓ Old schema fully removed
- ✓ Team learned for future migrations
