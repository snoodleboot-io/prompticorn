---
name: performance
description: "Comprehensive performance optimization workflow with profiling tools, strategies, and examples"
version: "1.0"
languages: ["python", "typescript", "sql"]
subagents: ["code", "debug", "architect"]
---

# Performance Workflow (Verbose)

## Purpose
Systematically identify and resolve performance bottlenecks through measurement, profiling, targeted optimization, and verification. Use this workflow when response times, throughput, or resource usage do not meet requirements.

## When to Use This Workflow
- API endpoint exceeds target latency (e.g., >200ms for user-facing endpoints)
- Database queries taking too long (>100ms)
- High CPU or memory usage
- Application feels slow to users
- Performance regression after code changes

## Prerequisites
- Access to profiling tools for your stack
- Representative test workload or production traffic
- Performance targets defined (latency, throughput, resource limits)
- Monitoring/observability in place

---

## Steps

### 1. Measure Baseline

**Goal:** Establish current performance metrics before optimization.

#### 1.1 Identify the Slow Operation
Be specific about what is slow:

**Good:**
- "GET /api/users endpoint takes 2.3s on average"
- "Database query for user orders takes 850ms"
- "Image processing function uses 4GB RAM per request"

**Bad (too vague):**
- "The app is slow"
- "Database is slow"
- "Users complaining about performance"

#### 1.2 Measure Current Performance
Use appropriate tools to get precise measurements:

**For HTTP endpoints:**
```bash
# Using Apache Bench
ab -n 1000 -c 10 http://localhost:8000/api/users
# Look for: Requests per second, Time per request (mean)

# Using wrk (better for sustained load)
wrk -t4 -c100 -d30s http://localhost:8000/api/users
# Look for: Latency distribution (50th, 95th, 99th percentile)
```

**For Python functions:**
```python
import time
start = time.perf_counter()
result = slow_function()
elapsed = time.perf_counter() - start
print(f"Took {elapsed:.3f}s")
```

**For database queries:**
```sql
-- PostgreSQL
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;
-- Look for: Execution time, Seq Scans, rows examined

-- Add timing
\timing on
SELECT * FROM orders WHERE user_id = 123;
```

#### 1.3 Document Baseline Metrics
Record specific numbers:

**Example:**
```
Operation: GET /api/users?page=1&limit=50
Baseline metrics (2026-04-10):
- Response time (avg): 2,340ms
- Response time (p95): 3,100ms
- Response time (p99): 4,500ms
- Throughput: 8.5 req/sec
- CPU usage: 85%
- Memory usage: 1.2GB
- Database queries per request: 47
```

#### 1.4 Set Target Performance Goal
Define what success looks like:

**Example targets:**
```
Target for GET /api/users:
- Response time (avg): <200ms (11x improvement)
- Response time (p95): <400ms
- Throughput: >100 req/sec
- Database queries per request: <5
```

---

### 2. Profile to Identify Bottlenecks

**Goal:** Find exactly where time is being spent.

#### 2.1 Choose Profiling Tool

**Python:**
- **py-spy** - Sampling profiler, low overhead, works on running processes
- **cProfile** - Deterministic profiler, function-level timing
- **line_profiler** - Line-by-line profiling
- **memory_profiler** - Memory usage per line

**TypeScript/Node.js:**
- **Chrome DevTools** - Built-in profiler
- **clinic.js** - Comprehensive Node.js profiler
- **0x** - Flamegraph profiler

**Database:**
- **EXPLAIN ANALYZE** - Query execution plan
- **pg_stat_statements** - PostgreSQL query stats
- **Slow query log** - MySQL slow queries

#### 2.2 Run Profiler Against Representative Workload
Use realistic data and load:

**Python example (py-spy):**
```bash
# Profile running server
py-spy record -o profile.svg --pid $(pgrep -f "uvicorn")

# Generate load while profiling
wrk -t4 -c100 -d30s http://localhost:8000/api/users

# Stop py-spy after 30s
# Opens profile.svg showing flamegraph
```

**Python example (cProfile):**
```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run your code
for _ in range(100):
    result = slow_function()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

**Database example:**
```sql
-- Enable query timing
\timing on

-- Profile slow query
EXPLAIN (ANALYZE, BUFFERS) 
SELECT u.*, COUNT(o.id) 
FROM users u 
LEFT JOIN orders o ON u.id = o.user_id 
GROUP BY u.id;

-- Look for:
-- Seq Scan (bad - missing index)
-- Nested Loop (can be slow for large datasets)
-- High buffer reads
```

#### 2.3 Identify Top Bottlenecks
Look for operations consuming >10% of total time:

**Example profiler output:**
```
Total time: 2,340ms

Top time consumers:
1. Database query (fetch orders): 1,200ms (51%)
2. JSON serialization: 680ms (29%)
3. Authorization check: 280ms (12%)
4. Response formatting: 120ms (5%)
5. Everything else: 60ms (3%)
```

#### 2.4 Categorize Bottleneck Type

**Common bottleneck types:**

| Type | Symptoms | Common Causes |
|------|----------|---------------|
| **Database** | High query time, many queries | N+1 queries, missing indexes, slow queries |
| **CPU** | High CPU %, slow computation | Complex algorithms, unnecessary work |
| **Memory** | High RAM usage, GC pressure | Large objects, memory leaks, no pagination |
| **I/O** | Slow file/network operations | Sync I/O in async code, large file reads |
| **Network** | High latency, many API calls | Missing batching, no caching, remote calls |

---

### 3. Prioritize Bottlenecks

**Goal:** Focus on highest-impact optimizations first.

#### 3.1 Calculate Impact Score
For each bottleneck:

**Formula:** Impact = Time Saved × Frequency

**Example:**
```
Bottleneck 1: Database query
- Time saved: 1,200ms → 50ms (if optimized) = 1,150ms
- Frequency: Every request = 100%
- Impact: 1,150ms × 1.0 = 1,150ms per request

Bottleneck 2: JSON serialization
- Time saved: 680ms → 200ms (if optimized) = 480ms
- Frequency: Every request = 100%
- Impact: 480ms × 1.0 = 480ms per request

Bottleneck 3: Authorization check
- Time saved: 280ms → 10ms (if cached) = 270ms
- Frequency: Only for authenticated requests = 80%
- Impact: 270ms × 0.8 = 216ms per request
```

**Priority order:** 1 > 2 > 3

#### 3.2 Consider Implementation Effort
Estimate difficulty:

```
Bottleneck 1 (database):
- Effort: Medium (add index, optimize query)
- Impact: 1,150ms saved
- ROI: High

Bottleneck 2 (serialization):
- Effort: High (switch to faster library, rewrite)
- Impact: 480ms saved
- ROI: Medium

Bottleneck 3 (auth):
- Effort: Low (add caching)
- Impact: 216ms saved
- ROI: High (quick win)
```

**Optimized priority:** Bottleneck 3 (quick win) → 1 (high impact) → 2 (if needed)

---

### 4. Optimize

**Goal:** Apply targeted fixes for each bottleneck type.

#### 4.1 Common Optimization Strategies by Type

**Database Bottlenecks:**

**N+1 Queries** (most common):
```python
# ❌ BEFORE (N+1 problem)
users = User.query.all()  # 1 query
for user in users:
    orders = user.orders.all()  # N queries (one per user)

# ✓ AFTER (eager loading)
users = User.query.options(joinedload(User.orders)).all()  # 1 query
for user in users:
    orders = user.orders  # No additional query
```

**Missing Indexes:**
```sql
-- Check for slow query
EXPLAIN ANALYZE 
SELECT * FROM orders WHERE user_id = 123;
-- Shows: Seq Scan on orders (cost=0.00..1234.56)

-- Add index
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Re-check
EXPLAIN ANALYZE 
SELECT * FROM orders WHERE user_id = 123;
-- Shows: Index Scan using idx_orders_user_id (cost=0.29..8.31)
```

**Slow Aggregations:**
```sql
-- ❌ BEFORE (slow count)
SELECT COUNT(*) FROM orders WHERE status = 'pending';

-- ✓ AFTER (materialized view updated periodically)
CREATE MATERIALIZED VIEW order_stats AS
SELECT status, COUNT(*) as count
FROM orders
GROUP BY status;

-- Query is instant
SELECT count FROM order_stats WHERE status = 'pending';
```

**CPU Bottlenecks:**

**Unnecessary Computation:**
```python
# ❌ BEFORE (computes on every request)
@app.get("/stats")
def get_stats():
    # Expensive: processes all users every time
    return {
        "total": User.query.count(),
        "active": User.query.filter_by(active=True).count()
    }

# ✓ AFTER (cached for 5 minutes)
from functools import lru_cache
import time

@lru_cache(maxsize=1)
def compute_stats(cache_key: int):
    return {
        "total": User.query.count(),
        "active": User.query.filter_by(active=True).count()
    }

@app.get("/stats")
def get_stats():
    # Cache key changes every 5 minutes
    cache_key = int(time.time() / 300)
    return compute_stats(cache_key)
```

**Algorithmic Complexity:**
```python
# ❌ BEFORE (O(n²) - nested loops)
def find_duplicates(items):
    duplicates = []
    for i, item in enumerate(items):
        for j, other in enumerate(items):
            if i != j and item == other:
                duplicates.append(item)
    return duplicates

# ✓ AFTER (O(n) - using set)
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

**Memory Bottlenecks:**

**Large Payloads:**
```python
# ❌ BEFORE (loads all users into memory)
@app.get("/users")
def get_users():
    users = User.query.all()  # 1,000,000 users = OOM
    return [u.to_dict() for u in users]

# ✓ AFTER (pagination)
@app.get("/users")
def get_users(page: int = 1, limit: int = 50):
    users = User.query.paginate(page=page, per_page=limit)
    return {
        "items": [u.to_dict() for u in users.items],
        "total": users.total,
        "pages": users.pages
    }
```

**I/O Bottlenecks:**

**Blocking Operations:**
```python
# ❌ BEFORE (blocking sync I/O in async context)
async def get_user_data(user_id):
    user = db.get_user(user_id)  # Blocks event loop
    return user

# ✓ AFTER (async I/O)
async def get_user_data(user_id):
    user = await db.get_user_async(user_id)  # Non-blocking
    return user
```

**Network Bottlenecks:**

**Missing Batching:**
```typescript
// ❌ BEFORE (N requests)
async function getUsersWithOrders(userIds: number[]) {
  const results = []
  for (const id of userIds) {
    const orders = await fetch(`/api/orders?user=${id}`)
    results.push(await orders.json())
  }
  return results
}

// ✓ AFTER (batched request)
async function getUsersWithOrders(userIds: number[]) {
  const response = await fetch(`/api/orders?users=${userIds.join(',')}`)
  return response.json()
}
```

#### 4.2 Make Smallest Change That Addresses Bottleneck
Don't over-optimize:

```
Bottleneck: Database query takes 1,200ms

Option 1 (minimal): Add index (5 min)
- Result: 1,200ms → 50ms ✓

Option 2 (complex): Rewrite with Redis cache, denormalization (2 days)
- Result: 1,200ms → 10ms
- Not worth the effort when index solves it
```

---

### 5. Measure Improvement

**Goal:** Verify optimization worked and didn't cause regressions.

#### 5.1 Re-run Profiler with Same Workload
Use identical test conditions:

```bash
# Same load test as baseline
wrk -t4 -c100 -d30s http://localhost:8000/api/users
```

#### 5.2 Compare New Metrics to Baseline

**Before optimization:**
```
Response time (avg): 2,340ms
Response time (p95): 3,100ms
Throughput: 8.5 req/sec
Database queries: 47 per request
```

**After adding index + fixing N+1:**
```
Response time (avg): 180ms (13x faster ✓)
Response time (p95): 250ms (12x faster ✓)
Throughput: 115 req/sec (13.5x faster ✓)
Database queries: 2 per request (23.5x fewer ✓)
```

#### 5.3 Verify Improvement Meets Target Goal
Check against targets from Step 1.4:

```
Target: <200ms avg → 180ms ✓ PASS
Target: <400ms p95 → 250ms ✓ PASS
Target: >100 req/sec → 115 ✓ PASS
Target: <5 queries → 2 ✓ PASS
```

#### 5.4 Check for Regressions
Verify optimization didn't break anything:

```bash
# Run full test suite
pytest tests/

# Check for new errors in logs
tail -f logs/app.log | grep ERROR

# Monitor memory usage
ps aux | grep python
# Verify no memory spike

# Check correctness
# Compare response from old vs new implementation
diff old_response.json new_response.json
# Should be identical (only performance changed)
```

---

### 6. Document

**Goal:** Record what was done for future reference and learning.

#### 6.1 Document Performance Optimization

**Template:**
```markdown
## Performance Optimization: GET /api/users

**Date:** 2026-04-10
**Developer:** Alice

### Baseline
- Response time: 2,340ms avg
- Bottleneck: N+1 database queries (47 queries per request)

### Root Cause
- Fetching users, then fetching orders for each user in a loop
- Missing index on orders.user_id

### Fix
1. Added eager loading: `User.query.options(joinedload(User.orders))`
2. Added index: `CREATE INDEX idx_orders_user_id ON orders(user_id)`

### Results
- Response time: 180ms avg (13x improvement)
- Database queries: 2 per request (23.5x fewer)
- All tests passing, no regressions

### Files Changed
- src/api/users.py:45 (added eager loading)
- migrations/20260410_add_orders_index.sql (added index)
```

#### 6.2 Note Tradeoffs
Document any costs:

**Example:**
```
Tradeoffs:
- Index adds 50MB to database size
- Eager loading uses 20% more memory per request
- Worth it for 13x speed improvement
```

#### 6.3 Add Performance Test
Prevent regression:

```python
# tests/performance/test_api_performance.py
import time

def test_get_users_performance():
    """Ensure GET /api/users responds in <200ms"""
    start = time.perf_counter()
    response = client.get("/api/users?page=1&limit=50")
    elapsed = time.perf_counter() - start
    
    assert response.status_code == 200
    assert elapsed < 0.2, f"Too slow: {elapsed:.3f}s (limit: 0.2s)"
```

---

## Common Performance Mistakes

### Mistake 1: Optimizing Without Measuring
**Problem:** Guessing where the bottleneck is instead of profiling.

**Example:**
```
Developer: "I bet the JSON serialization is slow"
[Rewrites serializer, takes 2 days]
Result: 5% improvement (actual bottleneck was database)
```

**Fix:** Always profile first. Data beats intuition.

---

### Mistake 2: Premature Optimization
**Problem:** Optimizing code that isn't slow.

**Example:**
```
Developer: "This function could be faster with caching"
Reality: Function called once per day, takes 50ms
Result: Wasted time, added complexity
```

**Fix:** Only optimize code that is provably slow and runs frequently.

---

### Mistake 3: Micro-Optimizations
**Problem:** Focusing on tiny improvements instead of big wins.

**Example:**
```
Optimized: String concatenation (saved 2ms)
Ignored: N+1 database queries (would save 1,200ms)
```

**Fix:** Use the 80/20 rule - fix bottlenecks that account for >10% of time.

---

### Mistake 4: Breaking Correctness for Speed
**Problem:** Optimization introduces bugs.

**Example:**
```python
# Caching breaks when data changes
@lru_cache(maxsize=128)
def get_user(user_id):
    return User.query.get(user_id)

# Problem: Cache never invalidated, shows stale data
```

**Fix:** Always verify correctness after optimization. Add tests.

---

### Mistake 5: Not Considering Real-World Load
**Problem:** Testing with unrealistic data.

**Example:**
```
Test: 10 users, 50 orders → fast
Production: 1M users, 10M orders → slow
```

**Fix:** Profile with production-like data volume.

---

### Mistake 6: Ignoring Memory for Speed
**Problem:** Faster but uses too much memory.

**Example:**
```python
# Fast but loads 1GB into memory
users = User.query.all()
user_map = {u.id: u for u in users}

# Better: Query on demand (slower but bounded memory)
user = User.query.get(user_id)
```

**Fix:** Balance speed, memory, and complexity.

---

## Example: Optimizing Email Sending Endpoint

**Baseline:**
```
Operation: POST /api/send-bulk-email (1,000 recipients)
Response time: 45 seconds
Bottleneck: Unknown
```

**Step 1: Profile**
```python
# Profiler shows:
- Email send (sync): 44.5s (99%)
- Validation: 0.3s
- DB query: 0.2s
```

**Step 2: Identify bottleneck**
- Type: I/O (blocking network calls)
- Cause: Sending emails synchronously in a loop

**Step 3: Optimize**
```python
# ❌ BEFORE (blocking)
for recipient in recipients:
    send_email(recipient)  # Blocks for 45ms per email

# ✓ AFTER (async background job)
job_id = queue.enqueue(send_bulk_email_task, recipients)
return {"job_id": job_id, "status": "processing"}

# Background worker sends emails
```

**Step 4: Measure**
```
Response time: 120ms (API returns immediately)
Email sending: Happens in background
Throughput: 100 emails/sec (background worker)
```

**Result:** 375x faster API response, emails still sent reliably.
