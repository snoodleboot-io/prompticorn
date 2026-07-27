# SQL Window Functions And CTEs (Minimal)

## Purpose
Compute per-row values across a set of related rows — rankings, running totals,
row-to-row deltas — without collapsing rows or writing self-joins. And name query
steps with CTEs.

## Core Techniques

### 1. A Window Keeps Every Row
Unlike `GROUP BY`, a window function returns one value per input row. `OVER`
defines the window; `PARTITION BY` resets it per group.
```sql
SELECT
  employee, department, salary,
  AVG(salary) OVER (PARTITION BY department) AS dept_avg
FROM employees;   -- every row kept, dept average attached
```

### 2. Ranking: ROW_NUMBER vs RANK vs DENSE_RANK
```sql
SELECT
  name, score,
  ROW_NUMBER() OVER (ORDER BY score DESC) AS rn,   -- 1,2,3,4 always unique
  RANK()       OVER (ORDER BY score DESC) AS rnk,  -- ties share, gaps: 1,1,3
  DENSE_RANK() OVER (ORDER BY score DESC) AS drnk  -- ties share, no gap: 1,1,2
FROM players;
```

### 3. LAG / LEAD For Row-To-Row Deltas
Read a value from a previous or next row — ideal for period-over-period change.
```sql
SELECT
  month, revenue,
  revenue - LAG(revenue) OVER (ORDER BY month) AS mom_change
FROM monthly_sales;
```

### 4. Frames For Running Totals And Moving Averages
A frame bounds which rows the aggregate sees within the ordered partition.
```sql
SELECT
  day, amount,
  SUM(amount) OVER (
    ORDER BY day
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total
FROM ledger;
```

### 5. CTEs Name The Steps
A `WITH` clause names a subquery so the main query reads top to bottom instead of
nesting inside-out.
```sql
WITH recent AS (
  SELECT * FROM orders WHERE created_at > '2026-01-01'
)
SELECT customer_id, COUNT(*) FROM recent GROUP BY customer_id;
```

### 6. Recursive CTEs Walk Hierarchies
An anchor plus a `UNION ALL` self-reference traverses trees and graphs.
```sql
WITH RECURSIVE tree AS (
  SELECT id, manager_id, 1 AS depth FROM employees WHERE manager_id IS NULL
  UNION ALL
  SELECT e.id, e.manager_id, t.depth + 1
  FROM employees e JOIN tree t ON e.manager_id = t.id
)
SELECT * FROM tree;
```

### 7. Prefer A Window To A Self-Join
"Top N per group" or "compare to the group's average" via a correlated self-join
scans the table repeatedly. One window pass is simpler and usually faster.

## Warning Signs

- A GROUP BY + join back to recover the detail rows a window would keep
- A correlated subquery per row for "rank within group"
- ROW_NUMBER used where ties should share a rank (want RANK/DENSE_RANK)
- Deeply nested subqueries a CTE would flatten
- A recursive CTE with no terminating condition (unbounded growth)

For EXPLAIN plans, indexing, and N+1 fixes, see the `sql-optimization` skill —
this one is about query shape, not execution tuning.
