---
languages: ["bash", "python", "typescript"]
subagents: ["debug", "ask"]
---

# Log Analysis Workflow (Minimal)

## 1. Collect Relevant Logs
Identify and gather logs for the timeframe:
```bash
# Application logs
tail -n 1000 /var/log/app.log

# System logs
journalctl -u myservice --since "2026-04-10 12:00" --until "2026-04-10 13:00"

# Container logs
docker logs mycontainer --since 1h --tail 500

# Cloud logs (AWS CloudWatch, GCP Logging)
aws logs tail /aws/lambda/my-function --since 1h
```

## 2. Identify Error Patterns
Search for errors and warnings:
```bash
# Find all errors
grep -i "error" app.log

# Count error types
grep "ERROR" app.log | awk '{print $5}' | sort | uniq -c | sort -rn

# Find stack traces
grep -A 10 "Exception" app.log
```

## 3. Extract Request Timeline
For failing requests, trace execution path:
```bash
# Follow request ID through logs
grep "request_id=abc123" app.log | sort

# Extract timestamps
grep "request_id=abc123" app.log | awk '{print $1, $2, $5}'
```

## 4. Find Root Cause (Not Last Error)
Distinguish between:
- **Root cause:** First error that triggered failure
- **Symptoms:** Cascading errors that followed

```bash
# Find first error in sequence
grep "request_id=abc123" app.log | grep -i "error" | head -1

# Check what happened before
grep "request_id=abc123" app.log | head -20
```

## 5. Correlate with External Events
Check for external factors:
- Deployment times (git log, CI/CD logs)
- Infrastructure changes (scaling events, restarts)
- Load patterns (traffic spikes, batch jobs)
- Dependency issues (database, API, network)

```bash
# Check deploy times
git log --since="2026-04-10 12:00" --until="2026-04-10 13:00" --oneline

# Check pod restarts (Kubernetes)
kubectl get pods --namespace=prod | grep Restart
```

## 6. Identify Anomalies
Look for unusual patterns:
- Swallowed errors (caught but not handled)
- Unexpected retries
- Missing log entries (gaps in request flow)
- Timing anomalies (too fast = cached, too slow = blocking)

## 7. Create Timeline
Document what happened:
```markdown
## Timeline for request_id=abc123

12:45:01 - Request received from user 456
12:45:02 - Database query started
12:45:15 - Database timeout (13s, expected <1s) ← ROOT CAUSE
12:45:15 - Retry attempt 1
12:45:28 - Database timeout again
12:45:28 - Retry attempt 2
12:45:41 - Database timeout (3rd time)
12:45:41 - Error returned to user: "Service unavailable"

**Root cause:** Database connection pool exhausted
**Evidence:** Connection pool logs show 0 available connections
**Fix:** Increase pool size from 10 to 50
```
