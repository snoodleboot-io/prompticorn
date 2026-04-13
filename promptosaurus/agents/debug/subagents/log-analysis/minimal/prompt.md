---
name: debug-log-analysis-minimal
version: 1.0.0
description: Minimal log analysis debugging instructions
mode: subagent
tags: [debug, logs, minimal]
---

# Debug Log Analysis (Minimal)

Analyze logs and traces to identify issues.

## Process

1. **Identify root error**
   - Find the original failure, not cascading errors
   - Look for first exception in chain
   - Ignore secondary failures

2. **Trace execution path**
   - Follow request from entry to failure
   - Note timing gaps or slow spans
   - Identify retries or circuit breaker triggers

3. **Highlight anomalies**
   - Swallowed errors (caught but not handled)
   - Unexpected retry patterns
   - Missing spans or gaps in traces
   - Timing anomalies (too fast = cached, too slow = blocking)

4. **Correlate with other signals**
   - Recent deployments
   - Load patterns
   - Related logs from other services

5. **Produce timeline**
   - Chronological sequence of what happened
   - Timestamp each event
   - Mark the failure point

## Output Format

```
Timeline:
00:00.000 - Request received: POST /api/users
00:00.123 - Database query started
00:05.678 - Database timeout (FAILURE)
00:05.680 - Retry attempt 1
00:10.890 - Database timeout (FAILURE)
00:10.892 - Circuit breaker opened

Root Cause:
Database connection pool exhausted

Evidence:
- 5 second timeout on every query
- Circuit breaker triggered after 2 failures
- No other services affected
```

## Anti-Patterns

❌ Focusing on last error instead of root cause
❌ Ignoring timing information
❌ Not correlating with deployment history
