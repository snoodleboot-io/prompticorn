# SQL Window Functions And CTEs (Verbose)

## Core Patterns

### Window Functions Keep Every Row

A window function computes an aggregate or ranking *over a set of rows related to
the current row*, without collapsing them the way `GROUP BY` does. The `OVER`
clause defines the window; `PARTITION BY` splits rows into independent groups, and
`ORDER BY` orders rows within each partition.

```sql
SELECT
  region,
  salesperson,
  amount,
  SUM(amount) OVER (PARTITION BY region)                 AS region_total,
  amount * 100.0 / SUM(amount) OVER (PARTITION BY region) AS pct_of_region
FROM sales;
```

Every detail row is preserved, with the region total attached — impossible with a
plain `GROUP BY` without joining the aggregate back.

### Ranking Functions

```sql
SELECT
  category, product, revenue,
  ROW_NUMBER() OVER (PARTITION BY category ORDER BY revenue DESC) AS rn,
  RANK()       OVER (PARTITION BY category ORDER BY revenue DESC) AS rnk,
  DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC) AS drnk
FROM products;
```

- `ROW_NUMBER` — always unique (1, 2, 3, 4), arbitrary among ties.
- `RANK` — ties share a rank, then a gap (1, 1, 3).
- `DENSE_RANK` — ties share a rank, no gap (1, 1, 2).

Use `ROW_NUMBER` to deduplicate ("keep the newest row per key"); use `RANK` /
`DENSE_RANK` when ties should genuinely tie.

### Top-N Per Group

The canonical use: number rows within each partition, then filter in an outer
query. You cannot filter on a window function in `WHERE` — it is computed after
`WHERE`, so wrap it in a CTE or subquery.

```sql
WITH ranked AS (
  SELECT
    department, employee, salary,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) AS rn
  FROM employees
)
SELECT department, employee, salary
FROM ranked
WHERE rn <= 3;               -- top 3 earners per department
```

### LAG And LEAD

`LAG` reads a column from a previous row in the ordered partition; `LEAD` reads
from a following row. They replace awkward self-joins for period-over-period math.

```sql
SELECT
  product_id,
  month,
  revenue,
  LAG(revenue) OVER (PARTITION BY product_id ORDER BY month)             AS prev_month,
  revenue - LAG(revenue) OVER (PARTITION BY product_id ORDER BY month)   AS mom_delta
FROM monthly_revenue;
```

Provide a default for the boundary row: `LAG(revenue, 1, 0)` returns 0 instead of
NULL for the first month.

### Frames: Running Totals And Moving Averages

Within an ordered partition, a frame restricts which rows the aggregate sees. When
you specify `ORDER BY` without an explicit frame, the default is `RANGE BETWEEN
UNBOUNDED PRECEDING AND CURRENT ROW` — often what you want for a running total, but
be explicit to avoid surprises.

```sql
SELECT
  day, amount,
  SUM(amount) OVER w                                      AS running_total,
  AVG(amount) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
                                                          AS avg_7day
FROM ledger
WINDOW w AS (ORDER BY day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW);
```

`ROWS` counts physical rows; `RANGE` groups peers with equal `ORDER BY` values.
The distinction matters when the ordering column has duplicates. A named `WINDOW`
clause avoids repeating the same specification across several columns.

### CTEs: Naming The Steps

A `WITH` clause (Common Table Expression) names a subquery so a complex query reads
top-to-bottom instead of nesting inside-out. Chain several to build a pipeline.

```sql
WITH paid AS (
  SELECT * FROM invoices WHERE status = 'paid'
),
by_customer AS (
  SELECT customer_id, SUM(total) AS revenue
  FROM paid
  GROUP BY customer_id
)
SELECT c.name, b.revenue
FROM by_customer b
JOIN customers c ON c.id = b.customer_id
ORDER BY b.revenue DESC;
```

CTEs are primarily about readability. On some engines they were once an
optimization fence; on modern PostgreSQL non-recursive CTEs are inlined, so treat
them as a structuring tool rather than a performance lever.

### Recursive CTEs

A recursive CTE has an *anchor* member and a *recursive* member joined by
`UNION ALL`; the recursive part references the CTE itself and runs until it
produces no new rows. It walks hierarchies and generates sequences.

```sql
WITH RECURSIVE subordinates AS (
  SELECT id, name, manager_id, 1 AS level
  FROM employees
  WHERE id = 42                       -- anchor: the starting manager
  UNION ALL
  SELECT e.id, e.name, e.manager_id, s.level + 1
  FROM employees e
  JOIN subordinates s ON e.manager_id = s.id   -- recurse down the tree
)
SELECT * FROM subordinates ORDER BY level;
```

Always ensure the recursion terminates — a cycle in the data (or a missing
stopping condition) produces unbounded rows. Guard with a depth cap or cycle
detection where the graph may contain loops.

### When A Window Beats A Self-Join

"Compare each row to its group's aggregate" and "find the top row per group"
traditionally used correlated subqueries or self-joins that re-scan the table once
per group. A window function does it in a single ordered pass — fewer scans,
clearer intent.

```sql
-- ❌ self-join: scans orders again for every customer
SELECT o.*
FROM orders o
JOIN (
  SELECT customer_id, MAX(created_at) AS latest
  FROM orders GROUP BY customer_id
) m ON m.customer_id = o.customer_id AND m.latest = o.created_at;

-- ✅ window: one pass
SELECT * FROM (
  SELECT o.*,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn
  FROM orders o
) t
WHERE rn = 1;
```

## Common Anti-Patterns

❌ **GROUP BY then join back to recover detail**
```sql
SELECT o.*, t.dept_avg
FROM orders o
JOIN (SELECT dept, AVG(amount) AS dept_avg FROM orders GROUP BY dept) t
  ON t.dept = o.dept;
```
✅ **Attach the aggregate with a window**
```sql
SELECT o.*, AVG(amount) OVER (PARTITION BY dept) AS dept_avg FROM orders o;
```

❌ **Filtering on a window function in WHERE**
```sql
SELECT *, ROW_NUMBER() OVER (ORDER BY score DESC) AS rn
FROM players WHERE rn <= 10;         -- error: rn not available in WHERE
```
✅ **Wrap in a CTE or subquery, filter outside**
```sql
WITH r AS (SELECT *, ROW_NUMBER() OVER (ORDER BY score DESC) AS rn FROM players)
SELECT * FROM r WHERE rn <= 10;
```

❌ **ROW_NUMBER when ties should tie**
```sql
ROW_NUMBER() OVER (ORDER BY score DESC)   -- two equal scores get 1 and 2
```
✅ **RANK / DENSE_RANK for shared standings**
```sql
RANK() OVER (ORDER BY score DESC)
```

❌ **Recursive CTE with no termination on cyclic data** — grows without bound.
✅ **Cap depth or detect cycles** (`WHERE level < 100`, or track visited ids).

## Window Functions And CTEs Checklist

- [ ] Window used (not GROUP BY + join back) when detail rows must survive
- [ ] Correct ranking function chosen: ROW_NUMBER unique, RANK/DENSE_RANK for ties
- [ ] Window functions filtered in an outer query/CTE, never in WHERE
- [ ] Frame made explicit (`ROWS` / `RANGE`) for running totals and moving averages
- [ ] LAG/LEAD (with a default) used for row-to-row deltas instead of self-joins
- [ ] CTEs used to structure multi-step queries readably
- [ ] Recursive CTEs have a guaranteed termination / cycle guard
- [ ] Execution tuning (indexes, EXPLAIN, N+1) deferred to the sql-optimization skill
