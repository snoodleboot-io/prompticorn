---
name: debug-root-cause-verbose
version: 1.0.0
description: Detailed root cause analysis methodology with examples
tags: [debug, root-cause, verbose]
tools: [bash]
---

# Debug Root Cause (Verbose)

Complete guide to systematic root cause analysis using the 5 Whys technique and hypothesis-driven debugging.

## Philosophy

Never jump to solutions. The first explanation is often wrong. Build hypotheses, gather evidence, and confirm the root cause before suggesting fixes.

## Complete Workflow

### Phase 1: Context Gathering

#### Step 1.1: Understand the Symptom

Ask these questions:

1. **What is the symptom vs expected behavior?**
   - Symptom: "Users getting 500 errors"
   - Expected: "Users successfully complete checkout"

2. **What environment?**
   - Local development?
   - Staging?
   - Production?

3. **Frequency:**
   - Always (100% of requests)?
   - Intermittent (10% of requests)?
   - Under load (only when traffic spikes)?
   - Time-based (only after 6 hours of uptime)?

4. **When did it start?**
   - After a deploy?
   - After a configuration change?
   - After a database migration?
   - Has it always existed?

#### Step 1.2: Request Artifacts

Don't guess. Ask for concrete evidence:

**Required artifacts:**
1. Error message or stack trace (exact text, not paraphrased)
2. Code that's failing (relevant files)
3. Logs around the time of failure (before + during + after)
4. Recent changes (git diff or description)

**Optional but helpful:**
5. Metrics/monitoring dashboards
6. Database query plans
7. Network traces
8. Memory dumps (for crashes)

### Phase 2: Hypothesis Generation

#### The 5 Whys Technique

Ask "why" repeatedly to drill down to root cause:

**Example:**

**Symptom:** Payment processing is failing

1. **Why is payment processing failing?**
   → Because the payment gateway API call is timing out

2. **Why is the API call timing out?**
   → Because the gateway is taking longer than our 5-second timeout

3. **Why is the gateway taking longer than 5 seconds?**
   → Because our requests are being rate-limited by the gateway

4. **Why are our requests being rate-limited?**
   → Because we're making 1000 requests/second, exceeding the 100/second limit

5. **Why are we making 1000 requests/second?**
   → Because each checkout spawns 10 parallel payment validation requests (bug)

**Root Cause:** Code is making 10x more API calls than necessary due to a loop bug.

#### Hypothesis Ranking

Generate 3 hypotheses ranked by likelihood:

**Example:**

```markdown
## Hypotheses (ranked by likelihood):

### 1. Database connection pool exhausted (70% confidence)

**Evidence supporting:**
- All errors show "timeout waiting for connection"
- Errors happen under load (>500 req/sec)
- Connection pool size = 10, active connections = 10 at time of error

**Evidence against:**
- No connection leak detected (connections do get released)
- Pool size hasn't changed recently

**How to rule out:**
- Increase pool size from 10 to 20
- If errors stop, confirms pool exhaustion
- If errors continue, look elsewhere

**Investigation steps:**
1. Check database metrics: active connections over time
2. Check application metrics: connection checkout duration
3. Run: `SHOW PROCESSLIST` on database to see active queries

---

### 2. Slow query causing connection starvation (20% confidence)

**Evidence supporting:**
- Some queries taking 5+ seconds
- These queries hold connections while running
- Could starve the pool

**Evidence against:**
- Slow query log shows only 2-3 slow queries per minute
- Not enough to exhaust 10-connection pool

**How to rule out:**
- Check query execution times
- If no queries > 1 second, rule out
- If queries > 5 seconds exist, optimize them

**Investigation steps:**
1. Enable slow query log (threshold: 1 second)
2. Check query execution plans: EXPLAIN SELECT ...
3. Look for missing indexes

---

### 3. Network latency to database (10% confidence)

**Evidence supporting:**
- Database is in different AWS region
- Network latency could cause timeouts

**Evidence against:**
- Latency has been stable at 5ms for months
- Other services using same database not affected

**How to rule out:**
- Check network metrics: latency, packet loss
- If latency < 10ms, rule out
- If latency > 100ms, investigate network

**Investigation steps:**
1. Run: ping database_host
2. Check AWS VPC metrics
3. Check for network congestion
```

### Phase 3: Systematic Investigation

#### Investigation Pattern

**For each hypothesis (starting with most likely):**

1. **Gather evidence:**
   - Run diagnostic commands
   - Check metrics/logs
   - Reproduce the issue

2. **Confirm or rule out:**
   - If evidence confirms: proceed to root cause verification
   - If evidence rules out: move to next hypothesis

3. **Verify root cause:**
   - Make minimal change that should fix issue
   - Verify fix in isolated environment
   - Confirm fix resolves issue

#### Example Investigation: Database Connection Pool

**Hypothesis:** Connection pool exhausted

**Step 1: Gather evidence**
```bash
# Check database connection count
mysql -e "SHOW PROCESSLIST;" | wc -l

# Check application metrics
curl http://localhost:9090/metrics | grep "connection_pool"

# Check logs for connection errors
grep "connection" application.log | grep -i timeout
```

**Result:**
```
Database connections: 10 (matches pool size)
connection_pool_active: 10
connection_pool_idle: 0
connection_pool_waiting: 45 (requests waiting for connection!)
```

**Evidence confirms hypothesis.**

**Step 2: Verify root cause**
```yaml
# Increase pool size temporarily
database:
  connection_pool:
    max: 20  # was 10
```

**Step 3: Test**
- Deploy to staging with increased pool size
- Run load test
- Monitor error rate

**Result:**
- Error rate: 5% → 0%
- Connection pool usage: max 15/20 (peak load)

**Root cause confirmed:** Connection pool too small for current load.

### Phase 4: Intermittent Bug Analysis

Intermittent bugs require different strategies:

#### Strategy 1: Add Logging

**Bad logging:**
```python
logger.info("Processing payment")
# ... lots of code ...
logger.info("Payment processed")
```

**Good logging:**
```python
logger.info(f"Processing payment: transaction_id={txn_id}, amount={amount}")
logger.debug(f"Payment method: {payment_method}")
logger.debug(f"Calling gateway API: {gateway_url}")

try:
    response = gateway.charge(amount, payment_method)
    logger.info(f"Gateway response: status={response.status}, txn={txn_id}")
except GatewayError as e:
    logger.error(f"Gateway error: {e}, txn={txn_id}, method={payment_method}")
    raise
```

Now when bug occurs, logs show exactly what happened.

#### Strategy 2: Local Reproduction

**Reproduce intermittent bug locally:**

1. **Identify pattern:**
   - Does it happen after N requests?
   - Does it happen under concurrent load?
   - Does it happen with specific input?

2. **Create minimal reproduction:**
   ```python
   # test_intermittent_bug.py
   import concurrent.futures
   
   def test_concurrent_payment_processing():
       """Reproduce race condition in payment processing."""
       with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
           futures = [
               executor.submit(process_payment, user_id, amount)
               for _ in range(100)  # 100 concurrent payments
           ]
           results = [f.result() for f in futures]
           
           # Check for failures
           failures = [r for r in results if not r.success]
           assert len(failures) == 0, f"Found {len(failures)} failures"
   ```

3. **Run repeatedly until failure:**
   ```bash
   for i in {1..100}; do
       echo "Run $i"
       pytest test_intermittent_bug.py || break
   done
   ```

#### Strategy 3: Identify Bug Type

**Race Condition:**
- Symptoms: Intermittent, happens under load
- Investigation: Add thread dumps, check for shared mutable state
- Fix: Use locks, atomic operations, or eliminate shared state

**Memory Issue:**
- Symptoms: Happens after running for hours, gets worse over time
- Investigation: Monitor memory usage, take heap dumps
- Fix: Fix memory leak, increase memory, or add memory limits

**Environmental Flake:**
- Symptoms: Only happens in production, not in staging
- Investigation: Compare environment configs, check for external dependencies
- Fix: Replicate production config in staging, fix environment-specific code

### Phase 5: Solution Generation

Once root cause is confirmed, offer solutions:

**Format:**
```markdown
## Root Cause Confirmed

Database connection pool size (10) is too small for current load (500 req/sec).

## Solution Options

### Option 1: Increase connection pool size (Recommended)

**Description:** Increase max_connections from 10 to 30

**Pros:**
- Quick fix (config change only)
- Proven to work in staging
- No code changes required

**Cons:**
- Doesn't address underlying inefficiency
- More database connections = more memory used

**Risk:** Low
**Effort:** 5 minutes
**Treats:** Root cause

**Implementation:**
```yaml
database:
  connection_pool:
    max: 30
```

---

### Option 2: Optimize queries to reduce connection hold time

**Description:** Add indexes and optimize slow queries

**Pros:**
- Reduces load on database
- Improves overall performance
- Sustainable long-term fix

**Cons:**
- Takes time to implement
- Requires code changes
- Needs testing

**Risk:** Medium (could introduce bugs)
**Effort:** 2-3 days
**Treats:** Root cause

**Implementation:**
1. Identify slow queries using slow query log
2. Add missing indexes
3. Rewrite N+1 queries to use JOIN
4. Test thoroughly

---

### Option 3: Implement connection pooling at application level

**Description:** Use connection pooling library (e.g., HikariCP)

**Pros:**
- Better connection management
- Built-in monitoring
- Automatic recovery

**Cons:**
- Requires code refactoring
- Learning curve
- Could introduce new bugs

**Risk:** High (significant changes)
**Effort:** 1 week
**Treats:** Symptom (makes pool more efficient, doesn't fix root cause)

---

## Recommendation

**Immediate (next 1 hour):** Option 1 - Increase pool size to 30
**Short-term (next 1 week):** Option 2 - Optimize queries
**Long-term (next 1 month):** Option 3 - Implement better pooling

This staged approach fixes the immediate issue while addressing the root cause sustainably.
```

## Complete Investigation Example

**User Report:**
"Application crashes after running for 6 hours in production"

### Step 1: Gather Context

**Questions:**
- Symptom: Application process exits with code 137
- Environment: Production only (not in staging)
- Frequency: Consistently after ~6 hours
- Started: After v2.5.0 deploy (2 weeks ago)

**Artifacts:**
```bash
# Get container logs before crash
kubectl logs pod_name --previous

# Last 100 lines before crash
kubectl logs pod_name --previous --tail=100
```

**Result:**
```
WARN  [05:45:23] Memory usage: 1.8GB / 2GB (90%)
WARN  [05:50:45] Memory usage: 1.9GB / 2GB (95%)
ERROR [05:55:12] OutOfMemoryError: Java heap space
FATAL [05:55:13] Application terminated (exit code 137)
```

Exit code 137 = SIGKILL = OOM killer killed the process.

### Step 2: Generate Hypotheses

**1. Memory leak (80% confidence)**
- Evidence: Memory increases steadily over 6 hours
- Pattern: Consistent timeline (always ~6 hours)
- Recent change: v2.5.0 introduced new caching logic

**2. Memory limit too low (15% confidence)**
- Evidence: Application uses 1.9GB before crash
- Limit: 2GB might be too small
- Counter-evidence: Worked fine before v2.5.0

**3. Traffic spike causing memory surge (5% confidence)**
- Evidence: None
- Counter-evidence: Traffic patterns unchanged

### Step 3: Investigate Memory Leak

**Take heap dump before crash:**
```bash
# Configure pod to take heap dump on OOM
kubectl set env deployment/app JAVA_OPTS="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=/tmp/heapdump.hprof"
```

**Analyze heap dump:**
```bash
# Download heap dump
kubectl cp pod_name:/tmp/heapdump.hprof ./heapdump.hprof

# Analyze with Eclipse MAT or jhat
jhat heapdump.hprof
# Browse to http://localhost:7000
```

**Finding:**
```
Largest objects in heap:
1. ConcurrentHashMap (1.2GB) - holds cached user sessions
2. ArrayList (400MB) - holds cached product data
3. String[] (200MB) - various strings

ConcurrentHashMap has 1.2 million entries!
```

**Root cause found:** Cache is unbounded and never evicts entries.

### Step 4: Confirm Root Cause

**Review v2.5.0 changes:**
```bash
git diff v2.4.0 v2.5.0 -- src/cache/
```

**Finding:**
```java
// v2.4.0 (working)
CacheBuilder.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(1, TimeUnit.HOURS)
    .build();

// v2.5.0 (broken)
new ConcurrentHashMap<>();  // No size limit!
```

**Root cause confirmed:** v2.5.0 replaced bounded cache with unbounded HashMap.

### Step 5: Offer Solutions

```markdown
## Root Cause

v2.5.0 replaced bounded cache (max 10k entries) with unbounded ConcurrentHashMap.
Over 6 hours, cache grows to 1.2M entries, consuming all available memory.

## Solution Options

### Option 1: Revert to bounded cache (Recommended)

**Implementation:**
```java
// Restore bounded cache
CacheBuilder.newBuilder()
    .maximumSize(100_000)  // Increased from 10k
    .expireAfterWrite(1, TimeUnit.HOURS)
    .build();
```

**Pros:** Proven fix, simple change
**Cons:** Need to test cache eviction behavior
**Risk:** Low
**Effort:** 1 hour

### Option 2: Increase memory limit

**Pros:** Quick fix
**Cons:** Treats symptom, not cause - will eventually run out again
**Risk:** High (kicks can down road)
**Effort:** 5 minutes

**Not recommended** - doesn't fix root cause

---

## Recommendation

Deploy Option 1 immediately. Bounded cache with 100k entries should handle current load while preventing unbounded growth.
```

## Debugging Strategies by Bug Type

### Race Conditions

**Symptoms:**
- Intermittent failures
- Happens under concurrent load
- "impossible" state (e.g., balance went negative)

**Investigation:**
1. Add thread dumps: `kill -3 <pid>` or `jstack <pid>`
2. Check for shared mutable state
3. Add logging around critical sections
4. Run with concurrency stress test

**Fix strategies:**
- Use locks (`synchronized`, `Lock`)
- Use atomic operations (`AtomicInteger`, `compareAndSet`)
- Eliminate shared state (use immutable data)

### Deadlocks

**Symptoms:**
- Application hangs
- Thread dumps show threads waiting for locks
- Always happens in same scenario

**Investigation:**
1. Take thread dump: `jstack <pid>`
2. Look for "waiting to lock" + "locked by"
3. Identify lock ordering issues

**Example thread dump:**
```
Thread-1: waiting to lock <0x123> (held by Thread-2)
Thread-2: waiting to lock <0x456> (held by Thread-1)
```

**Fix:** Enforce consistent lock ordering across all code.

### Memory Leaks

**Symptoms:**
- Memory usage grows over time
- Eventually crashes with OOM
- Garbage collection taking longer

**Investigation:**
1. Monitor heap usage over time
2. Take heap dump before crash
3. Analyze largest objects in heap
4. Look for unbounded collections

**Fix strategies:**
- Add bounds to collections (max size)
- Add eviction policies (LRU, TTL)
- Fix object retention (remove strong references)

### Performance Degradation

**Symptoms:**
- Slow requests (seconds instead of milliseconds)
- Degradation under load
- Database CPU high

**Investigation:**
1. Profile code: find hot paths
2. Check database: slow query log
3. Check network: latency, packet loss
4. Check for N+1 query problems

**Fix strategies:**
- Add indexes to database
- Use connection pooling
- Cache frequently accessed data
- Batch requests instead of N separate requests

## Anti-Patterns

### ❌ Anti-Pattern 1: Solution First, Root Cause Later

**Wrong:**
User: "App is slow"
You: "Try adding an index on user_id column"

**Correct:**
1. Gather evidence: slow query log, execution plans
2. Confirm root cause: missing index on user_id
3. Then suggest adding index

### ❌ Anti-Pattern 2: Only One Hypothesis

**Wrong:**
"The problem is definitely the database."

**Correct:**
"Three possible causes: (1) database (60%), (2) network (30%), (3) application (10%). Let's investigate in that order."

### ❌ Anti-Pattern 3: Not Measuring Before/After

**Wrong:**
Make change, assume it fixed the issue.

**Correct:**
1. Measure baseline: error rate 5%, p95 latency 500ms
2. Make change
3. Measure again: error rate 0%, p95 latency 200ms
4. Confirm fix with data

## Checklist

```markdown
- [ ] Gathered context: symptom, environment, frequency, timeline
- [ ] Requested artifacts: errors, logs, code, recent changes
- [ ] Generated 3 hypotheses ranked by likelihood
- [ ] For each hypothesis: listed evidence for/against
- [ ] Suggested investigation steps for most likely hypothesis
- [ ] Confirmed root cause with evidence
- [ ] Offered multiple solution options with tradeoffs
- [ ] Recommended specific action with justification
- [ ] Did NOT jump to solution before confirming root cause
```
