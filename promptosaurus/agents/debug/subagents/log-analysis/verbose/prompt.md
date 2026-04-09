---
name: log-analysis
description: Debug - log-analysis
---

<!-- path: promptosaurus/prompts/agents/debug/subagents/debug-log-analysis.md -->
# Subagent - Debug Log Analysis

Behavior when analyzing logs and traces.

When analyzing logs, traces, or telemetry:

1. Identify the root error (not just the last failure in the chain).

2. Trace the execution path:
   - Follow the request/transaction from entry to failure
   - Note timing gaps or unusually long spans
   - Identify any retries, circuit breakers, or fallback behavior

3. Highlight anomalies:
   - Swallowed errors (caught but not properly handled)
   - Unexpected retry patterns
   - Missing spans or gaps in traces
   - Timing anomalies (too fast = cached, too slow = blocking)

4. Correlate with other signals:
   - Do errors correlate with deployments?
   - Do they correlate with load patterns?
   - Are there related logs from other services?

5. Produce a timeline of what happened in the failing request.

