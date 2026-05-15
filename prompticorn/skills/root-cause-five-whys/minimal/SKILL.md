# Root Cause Analysis: Five Whys (Minimal)

## Process

Start with surface symptom, ask "Why?" 5 times:

```
1. What happened?
   "API timeout on every request"

2. Why?
   "Database connection pool exhausted"

3. Why?
   "New query doesn't release connections"

4. Why?
   "No timeout on query, runs forever"

5. Why?
   "No connection pool monitoring/alerting"

Root Cause: Lack of connection pool monitoring
Solution: Add alert when pool > 80% used
```

## Key Rules

✅ DO:
- Ask "why?" multiple times (usually 3-5)
- Focus on system failure, not human error
- Find preventable failure

❌ DON'T:
- Stop at "Engineer made a mistake"
- Blame individuals
- Make it about the person

## Bad vs Good RCA

❌ Bad: "Query has bug" (who cares, fix it)
✅ Good: "No monitoring for slow queries" (prevent future)

❌ Bad: "Engineer didn't test" (blame)
✅ Good: "No automated testing in CI/CD" (prevent)

## Root Cause vs Contributing Factor

**Root Cause:** The issue that enables failure
- Missing monitoring
- Missing tests
- Missing validation

**Contributing Factor:** Secondary issue
- Bad communication
- Slow response time
- Incomplete runbook

Address ROOT CAUSE, not just factors.

## Prevention Through RCA

```
RCA Finding: "No monitoring for pool exhaustion"

Prevention:
1. Add alert: Connection pool > 80%
2. Add runbook: "Connection pool exhausted"
3. Add test: Verify pool cleanup on query timeout
4. Documentation: Connection pool best practices
```
