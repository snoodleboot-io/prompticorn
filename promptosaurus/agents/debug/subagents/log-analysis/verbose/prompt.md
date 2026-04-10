---
name: debug-log-analysis-verbose
version: 1.0.0
description: Detailed log analysis methodology with examples
tags: [debug, logs, verbose]
---

# Debug Log Analysis (Verbose)

Complete guide to analyzing logs, traces, and telemetry to identify root causes.

## Philosophy

Logs tell a story. Your job is to read that story, separate signal from noise, and identify what went wrong and why. The last error is often a symptom, not the cause.

## Complete Workflow

### Step 1: Identify Root Error

Don't stop at the last error in the log. Trace backward to find the original failure.

#### Example: Finding Root Cause

**Last error (symptom):**
```
ERROR [14:23:45.789] HTTP 500 Internal Server Error returned to client
```

**Root cause (actual problem - 10 seconds earlier):**
```
ERROR [14:23:35.123] Database connection pool exhausted (max: 10, active: 10)
WARN  [14:23:35.125] Connection request timed out after 5000ms
ERROR [14:23:40.125] Query execution failed: timeout waiting for connection
```

**Why this matters:**
- Fixing the 500 error doesn't solve the problem
- The root cause is connection pool exhaustion
- This might be caused by a connection leak or insufficient pool size

### Step 2: Trace Execution Path

Follow the request from entry to failure, noting all significant events.

#### Example: Request Timeline

```
Timeline for request_id=abc123:

00:00.000 - Request received: POST /api/users
00:00.012 - Auth middleware: validating token
00:00.045 - Auth successful: user_id=user456
00:00.050 - UserController.createUser() called
00:00.065 - Validation passed
00:00.070 - Database query started: INSERT INTO users...
00:05.678 - Database timeout (FAILURE)
00:05.680 - Retry attempt 1 started
00:10.890 - Database timeout (FAILURE)
00:10.892 - Circuit breaker opened
00:10.895 - HTTP 503 returned to client
```

**Key observations:**
- 5-second timeout on every database attempt
- Two retries before circuit breaker
- Total request duration: 10.895 seconds
- User waited ~11 seconds for a failure

### Step 3: Highlight Anomalies

Look for patterns that indicate problems:

#### Anomaly 1: Swallowed Errors

**Bad pattern:**
```
INFO  [14:23:35.123] Processing payment for order_id=12345
INFO  [14:23:35.150] Payment processed successfully
```

**Wait... what happened in between?**
```
INFO  [14:23:35.123] Processing payment for order_id=12345
ERROR [14:23:35.140] Payment gateway returned error: insufficient funds
WARN  [14:23:35.142] Retrying with fallback payment method
INFO  [14:23:35.150] Payment processed successfully (used fallback)
```

**Why this is a problem:**
- First error was caught and handled silently
- No visibility into payment failures
- Might indicate systemic issues with primary gateway

#### Anomaly 2: Unexpected Retry Patterns

**Normal:**
```
INFO  Request to external API failed (attempt 1/3)
INFO  Request to external API failed (attempt 2/3)
INFO  Request to external API succeeded (attempt 3/3)
```

**Anomaly:**
```
INFO  Request to external API failed (attempt 1/3)
INFO  Request to external API failed (attempt 2/3)
INFO  Request to external API failed (attempt 3/3)
INFO  Request to external API succeeded (attempt 1/3)
INFO  Request to external API succeeded (attempt 2/3)
```

**What's wrong?**
- Retry counter reset mid-sequence
- Suggests multiple parallel requests or race condition
- Might indicate duplicate request processing

#### Anomaly 3: Timing Anomalies

**Too fast (cached or mocked):**
```
INFO  [14:23:35.100] Database query started: SELECT * FROM large_table
INFO  [14:23:35.101] Query returned 1,000,000 rows (1ms)
```
This is impossibly fast for 1M rows - likely cached or the log is lying.

**Too slow (blocking):**
```
INFO  [14:23:35.100] Acquiring lock for resource_id=xyz
INFO  [14:23:50.100] Lock acquired (15 seconds later)
```
15-second lock wait suggests contention or deadlock.

### Step 4: Correlate with Other Signals

#### Correlation 1: Deployment Timeline

```
ERROR rate spike at 14:23:00
Deployment completed at 14:22:30
```
→ Likely caused by new deployment

#### Correlation 2: Load Patterns

```
ERROR rate: 0.1% at 14:00 (100 req/sec)
ERROR rate: 5.0% at 14:30 (1000 req/sec)
```
→ System degrading under load

#### Correlation 3: Related Services

**Service A logs:**
```
ERROR [14:23:35] Timeout calling Service B
```

**Service B logs:**
```
WARN  [14:23:30] CPU at 95%, request queue backing up
ERROR [14:23:32] OOM killer triggered, restarting...
```
→ Service B crashed, causing Service A failures

### Step 5: Produce Timeline

Create a chronological narrative:

#### Complete Example: Payment Processing Failure

**Symptom:**
```
User reports: "Payment failed with 500 error"
```

**Investigation:**

```
Timeline for transaction_id=txn789 (user_id=user456):

00:00.000 - User clicked "Pay Now" button
00:00.050 - Request received: POST /api/payments
00:00.100 - Auth validated: user_id=user456
00:00.150 - PaymentController.processPayment() called
00:00.200 - Validation passed: amount=$99.99, method=credit_card
00:00.250 - Database query: SELECT * FROM payment_methods WHERE user_id=user456
00:00.280 - Retrieved payment method: card_id=card123
00:00.300 - External API call started: POST https://gateway.example.com/charge
00:05.300 - External API timeout (FAILURE - 5 second timeout)
00:05.305 - Retry attempt 1: POST https://gateway.example.com/charge
00:10.305 - External API timeout (FAILURE - 5 second timeout again)
00:10.310 - Retry attempt 2: POST https://gateway.example.com/charge
00:15.310 - External API timeout (FAILURE - 5 second timeout again)
00:15.315 - Max retries exceeded
00:15.320 - Transaction marked as FAILED in database
00:15.325 - HTTP 500 returned to user
```

**Root Cause:**
External payment gateway (gateway.example.com) was unresponsive.

**Evidence:**
- All 3 attempts timed out after exactly 5 seconds
- No error response from gateway (just timeout)
- Gateway status page shows incident from 14:20-14:40

**Impact:**
- User waited 15 seconds for a failure
- Transaction was NOT charged (confirmed with gateway)
- User experience: poor (long wait + confusing error)

**Recommended Fix:**
1. Reduce timeout from 5s to 2s for faster failure
2. Implement circuit breaker to fail fast during outages
3. Return 503 (Service Unavailable) instead of 500
4. Show user-friendly message: "Payment provider temporarily unavailable"

## Log Sources and Tools

### Common Log Sources

**Docker:**
```bash
# View logs for specific container
docker logs container_name

# Follow logs in real-time
docker logs -f container_name

# Show only last 100 lines
docker logs --tail 100 container_name

# Filter by timestamp
docker logs --since "2024-01-01T14:00:00" container_name
```

**Kubernetes:**
```bash
# View pod logs
kubectl logs pod_name

# View logs from specific container in pod
kubectl logs pod_name -c container_name

# Follow logs
kubectl logs -f pod_name

# View previous container logs (after crash)
kubectl logs pod_name --previous
```

**CloudWatch (AWS):**
```bash
# Using AWS CLI
aws logs tail /aws/lambda/function-name --follow

# Filter by pattern
aws logs filter-log-events \
  --log-group-name /aws/lambda/function-name \
  --filter-pattern "ERROR"
```

### Parsing Tools

**grep - Search logs:**
```bash
# Find all errors
grep "ERROR" application.log

# Case-insensitive search
grep -i "error" application.log

# Show 5 lines before and after match
grep -A 5 -B 5 "ERROR" application.log

# Search multiple files
grep "ERROR" logs/*.log
```

**awk - Extract fields:**
```bash
# Extract timestamp and message
awk '{print $1, $2, $NF}' application.log

# Filter by log level
awk '/ERROR/ {print}' application.log

# Count errors by hour
awk -F'[: ]' '/ERROR/ {print $1":"$2}' application.log | sort | uniq -c
```

**jq - Parse JSON logs:**
```bash
# Pretty-print JSON logs
cat application.json | jq '.'

# Extract specific field
cat application.json | jq '.timestamp, .level, .message'

# Filter by log level
cat application.json | jq 'select(.level == "ERROR")'

# Extract correlation ID
cat application.json | jq -r '.correlation_id' | sort | uniq
```

### Correlation ID Tracking

**Example: Following a request across services:**

```bash
# Extract correlation_id from initial request
correlation_id="abc-123-def"

# Search all logs for this correlation_id
grep "$correlation_id" logs/service-a.log
grep "$correlation_id" logs/service-b.log
grep "$correlation_id" logs/service-c.log

# Using jq for JSON logs
jq "select(.correlation_id == \"$correlation_id\")" logs/*.json | jq -s 'sort_by(.timestamp)'
```

**Result:**
```
Service A [14:23:35.100] Received request (correlation_id=abc-123-def)
Service A [14:23:35.150] Calling Service B (correlation_id=abc-123-def)
Service B [14:23:35.200] Processing request (correlation_id=abc-123-def)
Service B [14:23:35.250] Calling Service C (correlation_id=abc-123-def)
Service C [14:23:35.300] Database query failed (correlation_id=abc-123-def)
Service C [14:23:35.350] Returning error (correlation_id=abc-123-def)
Service B [14:23:35.400] Error from Service C (correlation_id=abc-123-def)
Service A [14:23:35.450] Error from Service B (correlation_id=abc-123-def)
```

This shows the full request flow and where it failed.

## Distributed Tracing

For microservices, use distributed tracing tools:

**Tools:**
- Jaeger
- Zipkin
- AWS X-Ray
- Datadog APM
- New Relic

**What tracing shows:**
- Full request path across services
- Duration of each service call
- Where time was spent
- Error propagation

**Example trace:**
```
API Gateway (5ms)
  → Auth Service (20ms)
  → User Service (150ms)
      → Database Query (145ms) ← SLOW
  → Notification Service (timeout) ← FAILED
```

Immediately see: Database query is slow, Notification Service timed out.

## Root Cause vs Symptom Identification

### Symptom:
"Users getting 500 errors"

### Possible Root Causes:

**1. Database Connection Pool Exhausted**
Evidence:
- Errors: "Timeout waiting for connection"
- Timing: 5-second delays on all queries
- Pattern: Happens under load

**2. Memory Leak**
Evidence:
- Errors: "OutOfMemoryError" or OOM killer logs
- Pattern: Gradual degradation over hours
- Metrics: Memory usage climbing steadily

**3. External Service Degradation**
Evidence:
- Errors: "Timeout calling external API"
- Timing: Coincides with external service incident
- Scope: Only affects features using that service

**4. Recent Deployment Bug**
Evidence:
- Timing: Errors started immediately after deploy
- Code: New code has obvious bug
- Rollback: Rolling back fixes the issue

### How to Distinguish:

1. **Check timing:** When did errors start?
2. **Check scope:** Which endpoints/features affected?
3. **Check pattern:** Constant rate or increasing?
4. **Check metrics:** CPU, memory, connections, etc.
5. **Check recent changes:** Any deploys, config changes, or migrations?

## Complete Investigation Example

**User Report:**
"Checkout is broken - getting errors when trying to complete purchase"

**Step 1: Identify Error**
```bash
# Search for checkout errors in last hour
grep "checkout" application.log | grep ERROR | tail -20
```

**Finding:**
```
ERROR [14:45:23] CheckoutController: Payment processing failed
ERROR [14:45:23] PaymentService: Connection timeout to gateway.example.com
```

**Step 2: Trace Execution**
```bash
# Find all logs for this checkout session
grep "session_id=sess_abc123" application.log
```

**Timeline:**
```
14:45:15 User added item to cart
14:45:18 User proceeded to checkout
14:45:20 Payment info submitted
14:45:23 Payment gateway call started
14:45:28 Payment gateway timeout (5s)
14:45:28 Error returned to user
```

**Step 3: Correlate with Gateway Logs**
```bash
# Check if gateway was down
curl https://status.example.com/api/incidents
```

**Result:**
```json
{
  "incidents": [
    {
      "service": "payment-gateway",
      "start": "2024-01-01T14:40:00Z",
      "end": "2024-01-01T14:50:00Z",
      "status": "resolved"
    }
  ]
}
```

**Step 4: Report Findings**

```markdown
## Investigation Summary

**Symptom:** Checkout failing with payment errors

**Root Cause:** External payment gateway (gateway.example.com) was down

**Evidence:**
- All payment attempts timing out after 5 seconds
- Gateway status page shows incident 14:40-14:50
- No successful payments during this window
- Issue resolved automatically when gateway recovered

**Impact:**
- ~50 failed checkout attempts
- Users affected: ~30 unique users
- Revenue impact: $4,500 in failed transactions

**Recommended Actions:**
1. Immediate: None (gateway recovered)
2. Short-term: Implement circuit breaker to fail faster
3. Long-term: Add secondary payment gateway for redundancy
4. Monitoring: Alert when payment success rate drops below 95%
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Stopping at Last Error

**Wrong:**
```
ERROR [14:45:28] HTTP 500 returned to user
```
This is the symptom, not the root cause.

**Correct:**
Look 10-30 seconds earlier for the original error.

### ❌ Anti-Pattern 2: Ignoring Timestamps

**Wrong:**
Reading logs in order they appear, ignoring timing.

**Correct:**
Pay attention to gaps and delays - they reveal blocking operations.

### ❌ Anti-Pattern 3: Not Correlating with External Signals

**Wrong:**
Only looking at application logs.

**Correct:**
Check deployment history, infrastructure metrics, external service status.

## Checklist

```markdown
- [ ] Identified root error (not just last error)
- [ ] Created timeline from request entry to failure
- [ ] Noted all timing anomalies
- [ ] Checked for swallowed errors
- [ ] Correlated with deployment timeline
- [ ] Correlated with load patterns
- [ ] Checked external service status
- [ ] Identified whether issue is systemic or isolated
- [ ] Provided evidence for root cause theory
```
