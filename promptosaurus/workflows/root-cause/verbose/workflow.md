---
name: root-cause
description: "Comprehensive root cause analysis using 5 Whys, Fishbone diagrams, and systematic investigation"
version: "1.0"
languages: ["python", "typescript", "sql"]
subagents: ["debug", "code"]
---

# Root Cause Analysis Workflow (Verbose)

## Purpose
Systematically identify the root cause of bugs, errors, and production incidents through evidence-based investigation. This workflow prevents jumping to conclusions and ensures fixes address causes, not symptoms.

## When to Use This Workflow
- Production incident occurred
- Bug reported but cause unclear
- Intermittent failures happening
- Performance degradation with unknown cause
- Post-mortem investigation

## Prerequisites
- Access to logs, monitoring, and error tracking systems
- Ability to reproduce the issue (or access to production data)
- Understanding of the system architecture
- Version control history (git)

---

## Steps

### 1. Gather Symptoms and Context

**Goal:** Understand exactly what is broken and under what conditions.

#### 1.1 Define the Symptom
Be precise about what is wrong:

**Good symptom descriptions:**
- "POST /api/orders returns 500 error when cart has >100 items"
- "User login succeeds but session expires after 30 seconds instead of 24 hours"
- "Memory usage grows 50MB/hour until OOM after 20 hours"

**Bad symptom descriptions (too vague):**
- "The app is broken"
- "Users can't log in"
- "Something is slow"

#### 1.2 Determine Expected Behavior
What should happen instead?

**Example:**
```
Symptom: POST /api/orders returns 500 error
Expected: POST /api/orders returns 201 with order ID
```

#### 1.3 Identify Environment
Where does this happen?

**Checklist:**
- [ ] Local development (developer machine)
- [ ] CI/CD pipeline
- [ ] Staging environment
- [ ] Production environment
- [ ] Specific region/datacenter
- [ ] Specific server/container

**Environmental factors:**
- OS version
- Runtime version (Python 3.11 vs 3.12)
- Database version
- Dependencies versions
- Configuration differences

#### 1.4 Determine Frequency Pattern
When does this happen?

**Frequency types:**

| Pattern | Description | Common Causes |
|---------|-------------|---------------|
| **Always** | Happens every time | Logic error, missing dependency |
| **Intermittent** | Happens sometimes | Race condition, timing issue |
| **Under Load** | Only with high traffic | Resource exhaustion, connection pool |
| **Time-based** | Specific time of day | Cron job, scheduled task, timezone issue |
| **Data-dependent** | Specific inputs | Edge case, boundary condition |

**Example:**
```
Frequency: Intermittent
- Happens ~5% of the time
- More frequent during peak hours
- No obvious pattern in failing requests
→ Suggests: Race condition or resource exhaustion
```

#### 1.5 Identify When It Started
Timeline analysis:

**Questions:**
- When was the first occurrence?
- What changed before the first occurrence?
- Did it happen before that change?

**Example:**
```
First occurrence: 2026-04-10 14:30 UTC
Last known working: 2026-04-10 14:15 UTC
Change deployed: 2026-04-10 14:20 UTC (commit abc123)
→ Suggests: Issue introduced in commit abc123
```

---

### 2. Collect Artifacts

**Goal:** Gather all relevant evidence before forming hypotheses.

#### 2.1 Error Messages and Stack Traces
Capture the full error, not just the summary:

**Good error capture:**
```python
Traceback (most recent call last):
  File "src/api/orders.py", line 45, in create_order
    order = Order.create(cart_items)
  File "src/models/order.py", line 23, in create
    total = sum(item.price for item in items)
  File "src/models/order.py", line 23, in <genexpr>
    total = sum(item.price for item in items)
AttributeError: 'NoneType' object has no attribute 'price'
```

**What to extract:**
- Exception type: `AttributeError`
- Message: `'NoneType' object has no attribute 'price'`
- Location: `src/models/order.py:23`
- Call stack: Shows it came from `create_order()` API handler
- Root error line: `sum(item.price for item in items)` assumes all items have price

#### 2.2 Relevant Code
Read the code where the error occurred:

```python
# src/models/order.py:20-30
@classmethod
def create(cls, items):
    # BUG: Assumes all items have 'price' attribute
    total = sum(item.price for item in items)
    order = cls(total=total)
    return order
```

**Questions to ask:**
- What assumptions does this code make?
- What could cause those assumptions to be violated?
- Are there any validations missing?

#### 2.3 Logs Before, During, and After Failure
Logs provide context:

**Example logs:**
```
2026-04-10 14:30:15 INFO [request] POST /api/orders user=123
2026-04-10 14:30:15 DEBUG [cart] Retrieved 3 items from cart
2026-04-10 14:30:15 DEBUG [cart] Item 1: product=456 price=29.99
2026-04-10 14:30:15 DEBUG [cart] Item 2: product=789 price=None  ← PROBLEM
2026-04-10 14:30:15 DEBUG [cart] Item 3: product=101 price=49.99
2026-04-10 14:30:16 ERROR [order] Failed to create order: AttributeError
```

**What this reveals:**
- Item 2 has `price=None`
- This is why `item.price` failed
- Need to investigate: Why is price None?

#### 2.4 Recent Changes
Check what changed recently:

```bash
# Show commits since last working state
git log --oneline --since="2026-04-09"

# Show specific commit that might be related
git show abc123

# Check if a file changed recently
git log -p src/models/order.py
```

**Example:**
```
commit abc123 "Add discount products feature"
- Modified: src/models/product.py
- Added: Optional 'discount_price' field
- Changed: price can now be None for free/discount items
→ Hypothesis: Code doesn't handle None prices
```

#### 2.5 Monitoring Data
Check resource usage and metrics:

**Metrics to review:**
- CPU usage (spike before crash?)
- Memory usage (memory leak?)
- Network traffic (DDoS?)
- Database connections (pool exhausted?)
- Error rate (gradual increase or sudden?)

---

### 3. Form Hypotheses

**Goal:** Generate ranked list of potential root causes based on evidence.

#### 3.1 Brainstorm Potential Causes
List all plausible explanations:

**Example (for AttributeError on item.price):**
1. Some items have price=None in database
2. Price field missing from API response
3. Type mismatch (price is string, not float)
4. Race condition (price deleted between queries)
5. Bad migration didn't backfill prices

#### 3.2 Rank by Likelihood
Consider evidence collected:

**Hypothesis 1: Items have price=None**
- **Likelihood:** High
- **Supporting evidence:** Logs show `price=None`, recent commit made price optional
- **Contradicting evidence:** None
- **How to test:** Query database for items where price IS NULL

**Hypothesis 2: Price field missing from API response**
- **Likelihood:** Low
- **Supporting evidence:** None
- **Contradicting evidence:** Logs show `price=None`, not missing field
- **How to test:** Check API response schema

**Hypothesis 3: Type mismatch**
- **Likelihood:** Low
- **Supporting evidence:** None
- **Contradicting evidence:** Error is AttributeError, not TypeError
- **How to test:** Check type of price field

**Ranked list:**
1. Items have price=None (High)
2. Bad migration didn't backfill (Medium)
3. Type mismatch (Low)
4. Race condition (Very Low)

#### 3.3 Apply RCA Methodologies

**5 Whys Technique:**
Keep asking "Why?" to find root cause:

```
Problem: Order creation fails
Why? → item.price is None
Why? → Some products have null price in database
Why? → Recent commit made price optional
Why? → Discount feature requires free items
Why? → No validation was added to handle None prices

Root cause: Code doesn't validate/handle None prices after schema change
```

**Fishbone Diagram (Categories):**

```
People:
- Developer didn't update order logic when changing schema

Process:
- No code review caught the missing validation
- No test for None prices

Technology:
- Database allows NULL for price field
- No database constraint requires price

Environment:
- Only happens in production (staging has no None prices)
```

---

### 4. Test Hypotheses

**Goal:** Confirm or rule out each hypothesis with experiments.

#### 4.1 Design Minimal Experiment
Test the most likely hypothesis first:

**Hypothesis:** Items have price=None in database

**Experiment:**
```sql
-- Check if any products have NULL price
SELECT id, name, price 
FROM products 
WHERE price IS NULL;
```

**Expected result if hypothesis is true:**
- Query returns rows

**Expected result if hypothesis is false:**
- Query returns 0 rows

#### 4.2 Execute Test
Run the experiment:

```
Result:
id  | name               | price
----|--------------------|-------
789 | Free Sample        | NULL
234 | Promotional Gift   | NULL
567 | Discount Coupon    | NULL
```

**Conclusion:** Hypothesis CONFIRMED - database has items with NULL prices.

#### 4.3 Observe Results
Compare to predictions:

```
Prediction: If price is NULL, order creation should fail
Observation: Order creation failed with AttributeError on item.price
Match: YES ✓

Root cause identified: Code doesn't handle NULL prices
```

#### 4.4 If Ruled Out, Test Next Hypothesis
If experiment contradicts hypothesis, move to next one:

```
Hypothesis 2: Bad migration didn't backfill
Experiment: Check migration history
Result: All migrations ran successfully, no backfill needed
Conclusion: RULED OUT
```

---

### 5. Identify Root Cause

**Goal:** Confirm root cause with reproducible evidence.

#### 5.1 Reproduce the Issue
Create minimal reproduction:

```python
# Minimal reproduction
from src.models import Order

# Create item with None price
item = Item(id=1, name="Free Sample", price=None)

# Try to create order
order = Order.create([item])
# Result: AttributeError ✓ (reproduces the bug)
```

#### 5.2 Distinguish Root Cause from Symptoms

**Symptoms (effects):**
- HTTP 500 error returned
- Order not created
- Error logged

**Root cause (underlying problem):**
- Order.create() doesn't handle None prices
- No validation on price field
- Schema change wasn't reflected in business logic

**Fix must address root cause, not symptoms.**

#### 5.3 Apply "5 Whys" Verification
Verify you reached root cause:

```
1. Why did order creation fail?
   → item.price was None

2. Why was price None?
   → Database allows NULL prices for free items

3. Why doesn't code handle NULL prices?
   → Recent schema change made price optional

4. Why wasn't code updated?
   → Developer updated schema but not all consumers

5. Why wasn't this caught?
   → No test for None prices, code review didn't catch it

Root cause: Missing validation + incomplete schema change rollout
```

**When to stop:** When "Why?" leads to process/people, you've found root cause.

#### 5.4 Document Causal Chain

```
Timeline of causation:
1. Feature requirement: Support free promotional items
2. Schema change: Made price field nullable
3. Database update: Added products with price=NULL
4. Code not updated: Order.create() still assumes price exists
5. Production request: User adds free item to cart
6. Code execution: sum(item.price) tries to access None.price
7. Error: AttributeError raised
8. Result: HTTP 500 returned, order not created
```

---

### 6. Verify Fix

**Goal:** Ensure fix resolves issue without introducing new problems.

#### 6.1 Design Fix That Addresses Root Cause

**Symptom fix (WRONG):**
```python
# Just catch the error
try:
    total = sum(item.price for item in items)
except AttributeError:
    total = 0  # Silent failure, wrong behavior
```

**Root cause fix (CORRECT):**
```python
# Handle None prices explicitly
def create(cls, items):
    # Validate all items have prices
    for item in items:
        if item.price is None:
            raise ValueError(f"Item {item.id} has no price")
    
    total = sum(item.price for item in items)
    order = cls(total=total)
    return order
```

**Better fix (handle free items):**
```python
def create(cls, items):
    # Treat None price as 0 (free item)
    total = sum(item.price or 0 for item in items)
    order = cls(total=total)
    return order
```

#### 6.2 Test Fix Resolves Issue
Verify with same reproduction case:

```python
# Test with None price
item = Item(id=1, name="Free Sample", price=None)
order = Order.create([item])
# Result: Order created with total=0 ✓

# Test with normal prices
items = [
    Item(id=1, price=10.0),
    Item(id=2, price=None),  # Free item
    Item(id=3, price=20.0)
]
order = Order.create(items)
assert order.total == 30.0  # ✓
```

#### 6.3 Verify No Regressions
Run full test suite:

```bash
pytest tests/
# All tests pass ✓

# Check edge cases
pytest tests/test_orders.py -v
# test_order_with_free_items ✓
# test_order_all_paid_items ✓
# test_order_all_free_items ✓
```

#### 6.4 Add Test to Prevent Recurrence

```python
# tests/test_orders.py
def test_order_handles_none_prices():
    """Regression test for issue #789: AttributeError on None price"""
    items = [
        Item(id=1, price=10.0),
        Item(id=2, price=None),  # Free item
    ]
    order = Order.create(items)
    assert order.total == 10.0
```

---

## RCA Methodologies

### 5 Whys
Ask "Why?" repeatedly to drill down to root cause.

**Example:**
```
Problem: Server crashed
1. Why? → Out of memory
2. Why? → Memory leak in image processing
3. Why? → Images not released after processing
4. Why? → Forgot to close file handles
5. Why? → No code review enforcing resource cleanup

Root cause: Missing code review checklist item
```

### Fishbone (Ishikawa) Diagram
Categorize potential causes:

**Categories:**
- **People:** Training, expertise, communication
- **Process:** Procedures, reviews, testing
- **Technology:** Tools, frameworks, infrastructure
- **Environment:** Deployment, configuration, dependencies

**Example:**
```
Problem: Payment processing fails

People:
├─ New developer unfamiliar with payment API
└─ No documentation on error handling

Process:
├─ No integration tests for payment flow
└─ No staging environment to test

Technology:
├─ Payment API rate limits not handled
└─ No retry logic for transient failures

Environment:
├─ Production API keys different from dev
└─ Firewall blocking outbound HTTPS
```

### Fault Tree Analysis
Work backwards from failure:

```
Order creation fails (top event)
    ├─ AND: Request received AND processing failed
    │   ├─ OR: Validation error OR Database error OR Logic error
    │   │   ├─ Logic error (item.price is None)
    │   │   │   ├─ AND: Code assumes price exists AND price is None
    │   │   │   │   ├─ Schema allows NULL ✓
    │   │   │   │   └─ Code not updated ✓
```

---

## Common RCA Mistakes

### Mistake 1: Stopping at Symptoms
**Problem:** Fixing the visible error without understanding cause.

**Example:**
```
Symptom: HTTP 500 error
Bad fix: Return 200 with empty response
Root cause: Database connection pool exhausted (not fixed)
```

**Fix:** Keep asking "Why?" until you reach process/system level.

---

### Mistake 2: Blaming People Instead of Process
**Problem:** "Developer X made a mistake" is not a root cause.

**Example:**
```
Bad: "Developer forgot to update code"
Good: "No automated check enforces schema/code consistency"
```

**Fix:** Find the process gap that allowed the error.

---

### Mistake 3: Jumping to Conclusions
**Problem:** Assuming cause without evidence.

**Example:**
```
Developer: "It's probably the cache"
[Clears cache, doesn't help]
Actual cause: Database index missing
```

**Fix:** Form hypothesis, then gather evidence. Don't skip steps.

---

### Mistake 4: Confirming Bias
**Problem:** Only looking for evidence that supports your theory.

**Example:**
```
Hypothesis: "It's a race condition"
[Only looks at multi-threaded code, ignores logs showing sequential execution]
Actual cause: Input validation bug
```

**Fix:** Actively try to disprove your hypothesis.

---

### Mistake 5: Not Documenting the Investigation
**Problem:** Lose track of what was tested.

**Fix:** Keep an RCA log:
```
2026-04-10 14:45 - Hypothesis: Database connection pool exhausted
2026-04-10 14:50 - Test: Checked connection count - 10/100 used
2026-04-10 14:50 - Result: RULED OUT

2026-04-10 14:55 - Hypothesis: Slow query blocking requests
2026-04-10 15:00 - Test: Ran EXPLAIN ANALYZE on suspect query
2026-04-10 15:00 - Result: CONFIRMED - missing index
```

---

## Example: Intermittent Login Failures

**Symptom:**
Users report login fails ~10% of the time with "Invalid credentials" even with correct password.

**Step 1: Gather Context**
```
Environment: Production only
Frequency: ~10% of login attempts
Pattern: No obvious pattern (random times, random users)
Started: 2026-04-08 after deployment
```

**Step 2: Collect Artifacts**
```
Logs show:
- Successful login: Password hash matches ✓
- Failed login: Password hash doesn't match ✗
- Same user, same password, different results

Code review:
- Recent change: Added bcrypt salt rounds from 10 to 12
```

**Step 3: Hypothesis**
```
Hypothesis 1: Race condition in auth check (Medium likelihood)
Hypothesis 2: Inconsistent password hashes (High likelihood)
Hypothesis 3: Database replication lag (Low likelihood)
```

**Step 4: Test Hypothesis 2**
```sql
-- Check for users with multiple password hashes
SELECT user_id, COUNT(DISTINCT password_hash)
FROM users
GROUP BY user_id
HAVING COUNT(DISTINCT password_hash) > 1;

Result: 0 rows (ruled out)
```

**Test Hypothesis 1:**
```python
# Check if multiple auth requests happen simultaneously
# Add logging for concurrent requests
# Result: 10% of requests have concurrent auth checks

Root cause: Race condition when multiple tabs login simultaneously
- First request: Validates password ✓
- Second request: Validates password ✓
- Both requests: Try to update last_login timestamp
- Database deadlock: One request fails, returns "Invalid credentials"
```

**Step 5: Fix**
```python
# Add lock to prevent concurrent auth
with user_lock(user_id):
    if validate_password(user, password):
        update_last_login(user)
        return success
```

**Step 6: Verify**
```
Test: Login with same user from 10 tabs simultaneously
Result: All succeed ✓
Production: Error rate 0% for 48 hours ✓
```

**Lessons:**
- Intermittent = often race condition
- Same input, different output = concurrency issue
- Always test concurrent scenarios
