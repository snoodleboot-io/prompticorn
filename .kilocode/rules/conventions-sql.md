# Core Conventions SQL

Language: SQL (PostgreSQL, MySQL, BigQuery, Snowflake)
Database: PostgreSQL (unless specified)
Style: Mostly uppercase keywords, lowercase identifiers

## Naming

Tables: snake_case (orders, customer_orders)
Columns: snake_case (customer_id, order_date)
Indexes: idx_{table}_{column} (idx_orders_customer_id)
Constraints: fk_{table}_{ref} (fk_orders_customer)

## Queries

### Formatting
```sql
SELECT 
  customer_id,
  SUM(amount) as total
FROM orders
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY customer_id
ORDER BY total DESC;
```

### Type Safety
- Always specify types in CREATE TABLE
- Use appropriate types (INT vs BIGINT, DATE vs TIMESTAMP)
- Use constraints (NOT NULL, UNIQUE, FOREIGN KEY)

### Performance
- Always use indexes on filtered/joined columns
- Avoid functions in WHERE (breaks indexes)
- Use EXPLAIN ANALYZE for complex queries
- Partition large tables by date/region

### Error Handling
- Use transactions (BEGIN/COMMIT) for multi-step operations
- Test migrations on staging before production
- Include rollback scripts
- Monitor slow query logs

## Testing
- Write tests for complex queries (CTEs, window functions)
- Use dbt or similar for SQL testing
- Test migrations thoroughly (data integrity)

## Anti-Patterns
❌ SELECT * (specify columns)
❌ Wildcards at start of LIKE ('%john%')
❌ Functions in WHERE clause
❌ No indexes on large tables
❌ Hardcoded dates (use NOW(), CURRENT_DATE)
