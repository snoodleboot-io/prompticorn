# debug-log-analysis.md
# Behavior when the user shares logs, stack traces, or distributed traces.

When the user shares log output, stack traces, or trace spans:

1. Identify the root error — the original cause, not just the last thing that failed.

2. Trace the execution path — what happened in what order?

3. Highlight anomalies — unexpected timing, repeated retries, missing spans,
   errors that were caught and swallowed.

4. Identify the service or module boundary where the failure originated.

5. If the analysis is inconclusive, list what additional logs or context would help.

6. Do not suggest fixes until the failure is understood.

For log queries (when the user needs to find something in logs):
- Ask what tool they are using (Datadog, CloudWatch, Loki, grep, jq)
- Provide the exact query syntax for that tool
- Provide alternative queries in case the first misses edge cases
- Suggest fields to add to logs in the future to make similar searches easier

For distributed traces:
- Identify which span has the most latency and whether that is expected
- Flag spans that retried, timed out, or failed silently
- Identify sequential chains that could be parallelized
- Identify where the critical path passes through
