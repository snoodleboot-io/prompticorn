---
name: performance
description: Review - performance
tools: [bash, read]
workflows:
  - performance-workflow
---

# Review - Performance (Verbose)

Comprehensive performance review identifying bottlenecks, scalability issues, and optimization opportunities.

## Review Categories

Work through these systematically:

1. **N+1 QUERIES** — database calls inside loops, missing eager loading
2. **UNNECESSARY COMPUTATION** — work done on every request that could be cached or pre-computed
3. **MISSING INDEXES** — columns filtered, sorted, or joined without an index
4. **LARGE PAYLOADS** — over-fetching data, missing pagination, uncompressed responses
5. **BLOCKING OPERATIONS** — sync I/O in async contexts, long-running work on the main thread
6. **MEMORY LEAKS** — unbounded caches, event listeners not cleaned up, large objects held in scope
7. **REDUNDANT NETWORK CALLS** — missing batching, no request deduplication, no caching headers
8. **ALGORITHMIC COMPLEXITY** — O(n²) or worse where a better algorithm exists

## Report Format

For each issue:
- **Location:** file name and function
- **Problem:** what the bottleneck is and why it matters at scale
- **Impact:** HIGH / MEDIUM / LOW (estimated)
- **Suggested Fix:** concrete remediation with code example

Skip issues that only matter at scale unlikely to be reached — state that assumption explicitly.

---

## Examples

### Example 1: N+1 Query Problem

**Location:** `src/api/orders.py:45` in `get_user_orders()`

**Current Code:**
```python
def get_user_orders(user_id):
    orders = db.query(Order).filter_by(user_id=user_id).all()
    for order in orders:  # N+1: fetches items one order at a time
        order.items = db.query(OrderItem).filter_by(order_id=order.id).all()
    return orders
```

**Problem:**
For a user with 100 orders, this executes 101 queries (1 for orders + 100 for items). At 10ms per query, this adds 1 second to response time. This scales linearly with number of orders.

**Impact:** HIGH

**Suggested Fix:**
```python
def get_user_orders(user_id):
    # Single query with eager loading
    orders = db.query(Order).filter_by(user_id=user_id)\
               .options(joinedload(Order.items))\
               .all()
    return orders
```

**Result:** 1 query instead of N+1. Response time drops from ~1s to ~10ms.

---

### Example 2: Missing Index

**Location:** `src/models/user.py:12` - `email` field

**Current Schema:**
```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255))  # No index!
    created_at = Column(DateTime)
```

**Query Pattern:**
```python
user = db.query(User).filter_by(email=email).first()  # Full table scan
```

**Problem:**
Every login requires filtering by `email`, which triggers a full table scan. With 1M users, this scans entire table. Query time: 500ms+.

**Impact:** HIGH

**Suggested Fix:**
```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), index=True, unique=True)  # Add index
    created_at = Column(DateTime)
```

**Migration:**
```sql
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

**Result:** Query time drops from 500ms to <5ms.

---

### Example 3: Unbounded Cache (Memory Leak)

**Location:** `src/cache.py:10`

**Current Code:**
```python
class Cache:
    def __init__(self):
        self._cache = {}  # No size limit!
    
    def set(self, key, value):
        self._cache[key] = value  # Grows forever
    
    def get(self, key):
        return self._cache.get(key)
```

**Problem:**
Cache grows indefinitely. If caching 1KB values and receiving 1000 requests/sec, memory grows at 1MB/sec. After 1 hour: 3.6GB memory usage. Eventually crashes.

**Impact:** HIGH (production stability)

**Suggested Fix:**
```python
from collections import OrderedDict

class Cache:
    def __init__(self, max_size=10000):
        self._cache = OrderedDict()
        self._max_size = max_size
    
    def set(self, key, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = value
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)  # Remove oldest
    
    def get(self, key):
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None
```

**Or use established library:**
```python
from cachetools import LRUCache

cache = LRUCache(maxsize=10000)
```

**Result:** Bounded memory usage, automatic eviction.

---

### Example 4: Blocking I/O in Async Context

**Location:** `src/api/notifications.py:23`

**Current Code:**
```python
import requests

async def send_notification(user_id, message):
    user = await get_user(user_id)  # Async
    # Blocking call in async function!
    response = requests.post("https://notify.example.com", json={"email": user.email, "msg": message})
    return response.json()
```

**Problem:**
`requests.post()` is synchronous — blocks the entire event loop. If notification service takes 200ms to respond, entire async event loop is blocked for 200ms. Other concurrent requests are delayed.

**Impact:** MEDIUM (affects all concurrent requests)

**Suggested Fix:**
```python
import httpx  # Async HTTP client

async def send_notification(user_id, message):
    user = await get_user(user_id)
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://notify.example.com",
            json={"email": user.email, "msg": message}
        )
    return response.json()
```

**Result:** Event loop not blocked, concurrent requests proceed normally.

---

### Example 5: Algorithmic Complexity

**Location:** `src/utils/dedup.py:15`

**Current Code:**
```python
def remove_duplicates(items):
    result = []
    for item in items:  # O(n)
        if item not in result:  # O(n) lookup in list
            result.append(item)
    return result  # Overall: O(n²)
```

**Problem:**
For each of N items, checks if it exists in result list (O(n) operation). Total: O(n²). For 10,000 items, this is 100M operations. Takes seconds.

**Impact:** MEDIUM (depends on input size)

**Suggested Fix:**
```python
def remove_duplicates(items):
    seen = set()  # O(1) lookup
    result = []
    for item in items:  # O(n)
        if item not in seen:  # O(1) lookup
            seen.add(item)
            result.append(item)
    return result  # Overall: O(n)
```

**Or simpler:**
```python
def remove_duplicates(items):
    return list(dict.fromkeys(items))  # Preserves order, O(n)
```

**Result:** 10,000 items: from seconds to milliseconds.

---

## Database-Specific Checks

### Full Table Scans

❌ **Bad:**
```sql
SELECT * FROM orders WHERE status = 'pending';  -- No index on status
```

✅ **Good:**
```sql
CREATE INDEX idx_orders_status ON orders(status);
SELECT * FROM orders WHERE status = 'pending';
```

---

### Over-fetching Columns

❌ **Bad:**
```sql
SELECT * FROM users WHERE id = 123;  -- Fetches all columns
```

✅ **Good:**
```sql
SELECT id, email, name FROM users WHERE id = 123;  -- Only needed columns
```

---

### Missing LIMIT

❌ **Bad:**
```sql
SELECT * FROM logs ORDER BY created_at DESC;  -- Could return millions of rows
```

✅ **Good:**
```sql
SELECT * FROM logs ORDER BY created_at DESC LIMIT 100;  -- Bounded result set
```

---

## Pre-Review Questions

Before reviewing, ask:

- **Expected load?** (requests/sec, concurrent users, data volume)
- **Current performance baselines?** (response times, query times)
- **Known bottlenecks or slow queries?**
- **Scale target?** (100 users vs 100K users changes priorities)

If not provided, state assumptions:

*"Assuming moderate scale (1K users, 10 req/sec). At this scale, the following issues are HIGH priority..."*
