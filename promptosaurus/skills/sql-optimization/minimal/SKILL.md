---
name: sql-optimization
type: skill
category: technical-skill
minimal: true
---
# SQL Optimization (Minimal)

## Purpose
Techniques for diagnosing and optimizing slow SQL queries.

## Core Techniques

### 1. EXPLAIN ANALYZE
```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 123;
```
Shows execution plan and actual vs. estimated rows. Look for:
- Seq Scan (full table scan) = slow for large tables
- Index Scan = good, uses index
- High Filter rows = indexes not selective enough

### 2. Add Indexes
```sql
-- Create index on frequently filtered columns
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Multi-column index for common filters
CREATE INDEX idx_orders_customer_date ON orders(customer_id, created_at);
```

### 3. Avoid N+1 Queries
Bad: Loop calling query for each row
```python
orders = db.query("SELECT * FROM orders")
for order in orders:
    customer = db.query("SELECT * FROM customers WHERE id = ?", order.customer_id)
    # 1 + N queries!
```

Good: Single join
```sql
SELECT o.*, c.* FROM orders o
JOIN customers c ON o.customer_id = c.id
-- 1 query!
```

### 4. Limit & Pagination
```sql
-- Don't fetch 1M rows, fetch what you need
SELECT * FROM orders LIMIT 100 OFFSET 0;
```

### 5. Use Appropriate Data Types
- Avoid TEXT for everything - use INT, DATE, etc.
- Smaller types = faster indexes
- VARCHAR(10) vs VARCHAR(1000)

## Warning Signs

- Query > 1 second
- Seq Scan on large table
- High filter ratio (estimated 1M, actual 100)
- Deadlocks in logs
