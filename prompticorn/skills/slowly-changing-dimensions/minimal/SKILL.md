# Slowly Changing Dimensions (Minimal)

## Types

### Type 1: Overwrite
Customer name changes → Just update
```sql
UPDATE dim_customer SET name = 'John Smith' 
WHERE customer_id = 123;
```
Pros: Simple | Cons: Lose history

### Type 2: Add New Row
Customer name changes → Add new record with effective dates
```sql
-- Old record: end_date = 2026-04-10
INSERT INTO dim_customer 
(customer_id, name, start_date, end_date)
VALUES (123, 'John Smith', '2026-04-11', NULL);
```
Pros: Keep history | Cons: More rows

### Type 3: Add Column
```sql
ALTER TABLE dim_customer ADD previous_name VARCHAR;
UPDATE dim_customer SET previous_name = name 
WHERE customer_id = 123;
UPDATE dim_customer SET name = 'John Smith' 
WHERE customer_id = 123;
```
Pros: Keep previous + current | Cons: Only 2 versions

## When to Use

**Type 1 (Overwrite):** Not important (email, phone)
**Type 2 (New Row):** Important for analytics (address, price)
**Type 3 (Column):** Need previous + current (status change)

## Implementation Pattern

```sql
SELECT fact_id, customer_id, amount
FROM fact_sales fs
JOIN dim_customer dc 
  ON fs.customer_id = dc.customer_id
  AND fs.date_id BETWEEN dc.start_date AND dc.end_date
```
