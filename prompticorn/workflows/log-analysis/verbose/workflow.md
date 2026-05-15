---
name: "log-analysis"
languages: ["bash", "python", "typescript"]
subagents: ["debug", "ask"]
---

# Log Analysis Workflow (Comprehensive)

## Overview

Log analysis is the process of examining application and system logs to diagnose issues, understand system behavior, and identify root causes of failures.

**Common use cases:**
- Debugging production incidents
- Performance analysis
- Security incident response
- Compliance auditing
- Understanding user behavior

**Key principles:**
- Find the root cause, not just the last error
- Correlate events across services
- Distinguish cause from symptoms
- Timeline reconstruction

---

## Phase 1: Log Collection

### 1.1 Identify Log Sources

**Application logs:**
- Structured logs (JSON, logfmt)
- Unstructured logs (plain text)
- Application server logs (Gunicorn, Uvicorn, Node.js)

**System logs:**
- Operating system logs (syslog, journalctl)
- Container logs (Docker, Kubernetes)
- Cloud platform logs (CloudWatch, Stackdriver, Azure Monitor)

**Infrastructure logs:**
- Load balancer logs
- Reverse proxy logs (Nginx, HAProxy)
- CDN logs (CloudFront, Fastly)
- Database logs

**Third-party logs:**
- Authentication providers (Auth0, Okta)
- Payment processors (Stripe, PayPal)
- External APIs

### 1.2 Define Timeframe

**Narrow the search window:**
```bash
# When did the issue start?
# Example: User reported error at 12:45 PM

# Check logs from 10 minutes before to 5 minutes after
--since "2026-04-10 12:35:00"
--until "2026-04-10 12:50:00"
```

**If timeframe is unknown:**
```bash
# Find when error first appeared
grep -i "specific error message" app.log | head -1 | awk '{print $1, $2}'

# Find when error stopped
grep -i "specific error message" app.log | tail -1 | awk '{print $1, $2}'
```

### 1.3 Collect Logs

**Local files:**
```bash
# Tail recent logs
tail -n 1000 /var/log/app.log

# Search specific timeframe
grep "2026-04-10 12:4" /var/log/app.log

# Compressed logs (gzip)
zgrep "error" /var/log/app.log.1.gz
```

**systemd/journalctl:**
```bash
# Service logs
journalctl -u myapp.service --since "2026-04-10 12:00" --until "2026-04-10 13:00"

# Follow live logs
journalctl -u myapp.service -f

# Filter by priority (0=emerg, 3=err, 6=info)
journalctl -u myapp.service -p 3  # errors only
```

**Docker containers:**
```bash
# Recent logs
docker logs mycontainer --tail 500

# Logs since timestamp
docker logs mycontainer --since 2026-04-10T12:00:00

# Follow live logs
docker logs mycontainer -f

# Container no longer running (use docker ps -a to find ID)
docker logs <stopped-container-id>
```

**Kubernetes:**
```bash
# Pod logs
kubectl logs mypod --namespace=production --tail=500

# Previous container (if pod restarted)
kubectl logs mypod --previous

# Multiple pods (deployment)
kubectl logs -l app=myapp --tail=100 --all-containers

# Follow live logs
kubectl logs -f mypod
```

**AWS CloudWatch:**
```bash
# Tail logs
aws logs tail /aws/lambda/my-function --since 1h --follow

# Filter pattern
aws logs filter-log-events \
  --log-group-name /aws/lambda/my-function \
  --start-time $(date -d '1 hour ago' +%s)000 \
  --filter-pattern "ERROR"

# Export to file
aws logs filter-log-events \
  --log-group-name /aws/lambda/my-function \
  --start-time $(date -d '2 hours ago' +%s)000 \
  > logs_export.json
```

**GCP Cloud Logging:**
```bash
# Tail logs
gcloud logging tail --limit 100

# Filter by severity
gcloud logging read "severity>=ERROR" --limit 50

# Filter by resource
gcloud logging read \
  "resource.type=k8s_container AND resource.labels.pod_name=mypod" \
  --limit 100
```

### 1.4 Centralize Logs (if distributed)

**If logs are spread across multiple sources:**

```bash
# Collect from multiple servers
for server in server1 server2 server3; do
  ssh $server "grep '2026-04-10 12:4' /var/log/app.log" > logs_${server}.txt
done

# Merge and sort by timestamp
sort -t' ' -k1,2 logs_*.txt > merged_logs.txt
```

**Using log aggregation tools:**
- Elasticsearch (query via Kibana or curl)
- Splunk (SPL query language)
- Datadog (log explorer)
- Grafana Loki (LogQL)

---

## Phase 2: Pattern Recognition

### 2.1 Error Identification

**Find all errors:**
```bash
# Case-insensitive error search
grep -i "error" app.log

# Multiple error keywords
grep -iE "error|exception|fail|fatal" app.log

# Exclude known false positives
grep -i "error" app.log | grep -v "error_count=0"
```

**Count error frequency:**
```bash
# Count total errors
grep -i "error" app.log | wc -l

# Count by error type
grep "ERROR" app.log | awk -F: '{print $3}' | sort | uniq -c | sort -rn

# Count by hour
grep "ERROR" app.log | awk '{print $1, $2}' | cut -d: -f1-2 | uniq -c
```

**Example output:**
```
45 2026-04-10 12:00  ← Spike at 12:00
38 2026-04-10 12:01
42 2026-04-10 12:02
3 2026-04-10 12:03   ← Resolved at 12:03
```

### 2.2 Stack Trace Extraction

**Capture full stack traces:**
```bash
# Extract error with following 10 lines (stack trace)
grep -A 10 "Exception" app.log

# Extract error with preceding 2 lines (context)
grep -B 2 -A 10 "Exception" app.log

# Save to file
grep -A 20 "Traceback" app.log > stack_traces.txt
```

**Python stack trace example:**
```python
2026-04-10 12:45:15 ERROR Traceback (most recent call last):
  File "app/controllers/user.py", line 42, in get_user
    user = db.query(User).filter_by(id=user_id).one()
  File "sqlalchemy/orm/query.py", line 2892, in one
    raise NoResultFound()
sqlalchemy.orm.exc.NoResultFound: No row was found for one()
```

**TypeScript/JavaScript stack trace example:**
```
2026-04-10 12:45:15 ERROR Error: User not found
    at UserService.getUser (/app/src/services/UserService.ts:45:11)
    at UserController.getById (/app/src/controllers/UserController.ts:23:28)
    at processTicksAndRejections (node:internal/process/task_queues:96:5)
```

### 2.3 Structured Log Parsing

**For JSON logs:**
```bash
# Pretty print JSON logs
cat app.log | jq '.'

# Filter by log level
cat app.log | jq 'select(.level == "error")'

# Extract specific fields
cat app.log | jq '{timestamp: .timestamp, message: .message, user_id: .user_id}'

# Count errors by type
cat app.log | jq -r 'select(.level == "error") | .error_type' | sort | uniq -c
```

**Example JSON log:**
```json
{
  "timestamp": "2026-04-10T12:45:15Z",
  "level": "error",
  "message": "Database connection timeout",
  "request_id": "abc123",
  "user_id": 456,
  "duration_ms": 13000,
  "error_type": "DatabaseTimeoutError"
}
```

**Parse with jq:**
```bash
# Find all slow requests (>5s)
cat app.log | jq 'select(.duration_ms > 5000)'

# Average duration by endpoint
cat app.log | jq -r '[.endpoint, .duration_ms] | @tsv' | awk '{sum[$1]+=$2; count[$1]++} END {for (e in sum) print e, sum[e]/count[e]}'
```

---

## Phase 3: Request Tracing

### 3.1 Correlation IDs

**Follow a single request through the system:**

```bash
# Extract request ID from error
grep "Database timeout" app.log | grep -oP 'request_id=\K\w+'

# Follow request through logs
grep "request_id=abc123" app.log | sort

# Extract request flow
grep "request_id=abc123" app.log | awk '{print $1, $2, $5, $6, $7}'
```

**Example request flow:**
```
2026-04-10 12:45:01 [INFO] Request received: GET /api/users/456
2026-04-10 12:45:01 [DEBUG] Authenticating user token
2026-04-10 12:45:02 [DEBUG] Starting database query
2026-04-10 12:45:15 [ERROR] Database timeout after 13s
2026-04-10 12:45:15 [INFO] Returning 503 to client
```

### 3.2 Distributed Tracing

**If using OpenTelemetry or Jaeger:**

```bash
# Query traces by trace ID
curl "http://jaeger:16686/api/traces/abc123"

# Find slow traces
curl "http://jaeger:16686/api/traces?service=my-app&minDuration=5s"
```

**Manual correlation across services:**
```bash
# Service A logs
grep "trace_id=xyz789" service_a.log

# Service B logs
grep "trace_id=xyz789" service_b.log

# Service C logs
grep "trace_id=xyz789" service_c.log

# Merge by timestamp
cat service_a.log service_b.log service_c.log | grep "trace_id=xyz789" | sort
```

### 3.3 Timeline Reconstruction

**Build chronological view:**

```bash
# Extract timestamps and messages
grep "request_id=abc123" app.log | awk '{print $1, $2, $0}' | sort

# Calculate time deltas between steps
grep "request_id=abc123" app.log | awk '{
  if (prev) {
    cmd = "date -d \""$1" "$2"\" +%s.%N"
    cmd | getline current
    close(cmd)
    
    cmd = "date -d \""prev_date"\" +%s.%N"
    cmd | getline previous
    close(cmd)
    
    delta = current - previous
    print $0, "  [+" delta "s]"
  }
  prev_date = $1" "$2
  prev = $0
}'
```

**Output:**
```
2026-04-10 12:45:01.123 Request received  [+0s]
2026-04-10 12:45:01.145 Auth check passed  [+0.022s]
2026-04-10 12:45:02.001 DB query started  [+0.856s]
2026-04-10 12:45:15.234 DB timeout ERROR  [+13.233s]  ← Problem here
2026-04-10 12:45:15.250 Response sent  [+0.016s]
```

---

## Phase 4: Root Cause Analysis

### 4.1 Distinguish Root Cause from Symptoms

**Common symptom patterns:**

**Cascading failures (symptom):**
```
12:45:15 ERROR DatabaseTimeoutError  ← Root cause
12:45:16 ERROR CacheUpdateFailed     ← Symptom (cache update depends on DB)
12:45:17 ERROR UserNotificationFailed ← Symptom (notification depends on cache)
```

**Retry loops (symptom):**
```
12:45:15 ERROR Connection refused
12:45:16 ERROR Connection refused (retry 1)
12:45:17 ERROR Connection refused (retry 2)
12:45:18 ERROR Connection refused (retry 3)
```

**Root cause identification:**
1. Find the FIRST error in the sequence
2. Check what happened immediately before
3. Verify this error triggered subsequent failures

### 4.2 Look for Missing Context

**What's NOT in the logs:**

**Silent failures:**
```python
# Bad: Swallowed exception
try:
    db.query(User).filter_by(id=user_id).one()
except Exception:
    pass  # ← No log entry, invisible in logs
```

**Fix: Add logging:**
```python
try:
    db.query(User).filter_by(id=user_id).one()
except Exception as e:
    logger.error(f"Database query failed for user {user_id}: {e}")
    raise
```

**Gaps in request flow:**
```
12:45:01 Request received
12:45:15 Database timeout  ← What happened in 14 seconds?
```

**Investigate the gap:**
- Check for missing log statements
- Check for blocking operations (network, file I/O)
- Check for deadlocks or race conditions

### 4.3 Timing Anomalies

**Too fast (unexpected):**
```
12:45:01 Request received
12:45:01.002 Response sent  ← 2ms is suspiciously fast for DB query
```

**Possible causes:**
- Cached response (check cache logs)
- Early return (error handling, validation failure)
- Timing bug (logged response before actually sending)

**Too slow (expected):**
```
12:45:01 Request received
12:45:15 Response sent  ← 14s is very slow
```

**Possible causes:**
- Network latency
- Database query timeout
- Blocking synchronous operation
- Resource exhaustion (CPU, memory, connections)

---

## Phase 5: Correlation Analysis

### 5.1 Correlate with Deployments

**Check if error started after deployment:**

```bash
# Find deploy time
git log --since="2026-04-10 12:00" --until="2026-04-10 13:00" --oneline

# Check CI/CD logs
# Jenkins, CircleCI, GitHub Actions, etc.

# Compare error rate before/after deploy
# Before deploy (11:00-12:00):
grep -c "ERROR" app.log.1  # 5 errors

# After deploy (12:00-13:00):
grep -c "ERROR" app.log    # 45 errors ← 9x increase!
```

**If error rate spiked after deploy:**
- Check what changed in the deploy
- Review git diff for relevant changes
- Consider rollback

### 5.2 Correlate with Load Patterns

**Check if error correlates with traffic:**

```bash
# Count requests per minute
awk '{print $1, $2}' app.log | cut -d: -f1-2 | uniq -c

# Count errors per minute
grep ERROR app.log | awk '{print $1, $2}' | cut -d: -f1-2 | uniq -c

# Compare side-by-side
paste <(awk '{print $1, $2}' app.log | cut -d: -f1-2 | uniq -c) \
      <(grep ERROR app.log | awk '{print $1, $2}' | cut -d: -f1-2 | uniq -c)
```

**Output:**
```
100 2026-04-10 12:00  |  3 2026-04-10 12:00   (3% error rate)
500 2026-04-10 12:01  |  45 2026-04-10 12:01  (9% error rate) ← Spike
600 2026-04-10 12:02  |  54 2026-04-10 12:02  (9% error rate)
150 2026-04-10 12:03  |  5 2026-04-10 12:03   (3% error rate) ← Normal
```

**Interpretation:** Error rate increased during traffic spike (load-related issue).

### 5.3 Correlate with Infrastructure Events

**Check for infrastructure changes:**

**Pod restarts (Kubernetes):**
```bash
kubectl get pods --namespace=prod -o wide

# Check events
kubectl get events --namespace=prod --sort-by='.lastTimestamp'
```

**Auto-scaling events:**
```bash
# AWS Auto Scaling
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name my-asg \
  --max-records 20

# Kubernetes HPA
kubectl describe hpa my-app-hpa
```

**Resource exhaustion:**
```bash
# Memory usage at time of failure
grep "2026-04-10 12:4" /var/log/syslog | grep -i "memory"

# OOM killer logs
dmesg | grep -i "out of memory"

# Kubernetes pod eviction
kubectl get events --all-namespaces | grep Evict
```

### 5.4 Correlate with Dependencies

**Check downstream service health:**

```bash
# Database logs
grep "2026-04-10 12:4" /var/log/postgresql/postgresql.log

# Redis logs
grep "2026-04-10 12:4" /var/log/redis/redis.log

# Third-party API status
curl https://status.stripe.com/api/v2/status.json
```

**Connection pool exhaustion:**
```bash
# Find connection pool warnings
grep "connection pool" app.log

# Count active connections
grep "active_connections" app.log | tail -1
```

**Example:**
```
2026-04-10 12:45:15 WARN Connection pool exhausted: 0/10 available
```

---

## Phase 6: Anomaly Detection

### 6.1 Unexpected Retry Patterns

**Find retry logic:**
```bash
# Search for retry keywords
grep -iE "retry|attempt" app.log

# Count retries per request
grep "request_id=" app.log | grep -i retry | awk '{print $4}' | sort | uniq -c
```

**Example:**
```
1 request_id=abc123 retry_attempt=1
1 request_id=abc123 retry_attempt=2
1 request_id=abc123 retry_attempt=3
```

**Exponential backoff check:**
```bash
# Extract retry timestamps
grep "request_id=abc123" app.log | grep retry | awk '{print $1, $2}'

# Calculate time between retries
2026-04-10 12:45:15.000  (initial attempt)
2026-04-10 12:45:16.000  (retry 1, +1s)
2026-04-10 12:45:18.000  (retry 2, +2s)
2026-04-10 12:45:22.000  (retry 3, +4s)  ← Exponential backoff working
```

### 6.2 Swallowed Errors

**Find error handling without logging:**

```bash
# Search for generic error handling
grep -n "except:" *.py  # Python
grep -n "catch (e)" *.ts  # TypeScript

# Check if errors are logged
grep -A 3 "except:" *.py | grep -i "log"
```

**Example violation:**
```python
# Bad: Silent failure
try:
    result = api.call()
except Exception:
    return None  # ← Error swallowed, no log

# Good: Logged failure
try:
    result = api.call()
except Exception as e:
    logger.error(f"API call failed: {e}", exc_info=True)
    raise
```

### 6.3 Log Gaps

**Find missing log entries:**

```bash
# Check for sequential request IDs
grep "request_id=" app.log | awk -F= '{print $2}' | awk '{print $1}' | sort -n

# Output:
abc120
abc121
abc122
abc125  ← Where are abc123 and abc124?
abc126
```

**Possible causes:**
- Logs lost (buffer overflow, disk full)
- Requests not logged (crashed before logging)
- Log rotation during collection

---

## Phase 7: Reporting

### 7.1 Timeline Format

**Create incident timeline:**

```markdown
## Incident Timeline: Database Timeout Storm

**Incident ID:** INC-2026-04-10-001
**Start:** 2026-04-10 12:45:01 UTC
**End:** 2026-04-10 12:50:15 UTC
**Duration:** 5 minutes 14 seconds
**Impact:** 45% of requests failed (127 failed / 282 total)

### Timeline

**12:45:01** - Traffic spike detected (500 req/min, normal is 100 req/min)
**12:45:02** - Database connection pool exhausted (0/10 available)
**12:45:15** - First timeout errors appear (13s timeout)
**12:45:16** - Error rate reaches 50%
**12:45:30** - Auto-scaling triggered (2 → 5 instances)
**12:46:00** - New instances healthy, connection pool restored
**12:46:15** - Error rate drops to 10%
**12:50:15** - Error rate back to normal (<1%)

### Root Cause

Database connection pool size (10) was insufficient for traffic spike (5x normal load).
Connection pool exhaustion caused requests to wait for available connections.
Timeout threshold (15s) was reached, causing request failures.

### Contributing Factors

1. Auto-scaling delay (30s from spike to new instances)
2. No connection pool monitoring/alerting
3. Connection pool size not tuned for peak load

### Evidence

- Connection pool logs: 0 available connections from 12:45:02-12:46:00
- Request latency: p95 jumped from 200ms to 15s
- Database server logs: No database-side errors (pool exhaustion was client-side)

### Resolution

1. Immediate: Manual scaling (2 → 10 instances) resolved issue
2. Short-term: Increased connection pool size (10 → 50)
3. Long-term: Add connection pool monitoring, tune auto-scaling threshold
```

### 7.2 Root Cause Documentation

**5 Whys technique:**

```markdown
## Root Cause Analysis (5 Whys)

**Problem:** Requests timed out at 12:45:15

**Why?** Database queries exceeded 15s timeout
**Why?** Queries waited for available connection pool slots
**Why?** Connection pool was exhausted (0/10 available)
**Why?** Traffic spiked 5x but pool size stayed constant
**Why?** Auto-scaling has 30s delay and pool size wasn't tuned for bursts

**Root Cause:** Connection pool size (10) was inadequate for traffic bursts
```

---

## Tools and Resources

**Log collection:**
- Tail: Built-in Unix tool
- journalctl: systemd journal
- Docker logs: docker logs
- kubectl logs: Kubernetes logs
- AWS CLI: CloudWatch Logs
- gcloud: GCP Cloud Logging

**Log parsing:**
- grep: Pattern matching
- awk: Text processing
- jq: JSON parsing
- sed: Stream editing
- rg (ripgrep): Fast search

**Log aggregation:**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Grafana Loki
- Splunk
- Datadog
- New Relic

**Distributed tracing:**
- OpenTelemetry
- Jaeger
- Zipkin
- AWS X-Ray
- Google Cloud Trace

**Log analysis tools:**
- goaccess: Real-time log analyzer
- Logwatch: Automated log analysis
- Fail2ban: Security log analysis
- mtail: Extract metrics from logs
