---
name: debug-root-cause-minimal
version: 1.0.0
description: Minimal root cause analysis debugging instructions
tags: [debug, root-cause, minimal]
tools: [bash]
---

# Debug Root Cause (Minimal)

Identify root cause before suggesting fixes.

## Process

1. **Gather context**
   - Symptom vs expected behavior
   - Environment (local/staging/prod)
   - Frequency (always/intermittent/under load)
   - When did it start

2. **Request artifacts**
   - Error message or stack trace
   - Relevant code
   - Logs around failure time
   - Recent changes

3. **Generate hypotheses**
   - List top 3 ranked by likelihood
   - For each: supporting evidence + what would rule it out
   - Suggest minimum investigation steps

4. **Don't jump to fixes**
   - Confirm root cause first
   - Wait for user confirmation

5. **For intermittent bugs**
   - Suggest logging to capture context
   - Propose local reproduction strategy
   - Identify if race condition/memory/environmental

## Output Format

```
Hypotheses (ranked by likelihood):

1. Database connection pool exhausted (70%)
   Evidence: 5s timeout, affects all queries
   Rule out: Check connection pool size config
   Investigation: Run SHOW PROCESSLIST on database

2. Network latency spike (20%)
   Evidence: Timing suggests network issue
   Rule out: Check if other services affected
   Investigation: Check network metrics dashboard

3. Query regression from recent change (10%)
   Evidence: Started after deploy
   Rule out: Check query execution plan
   Investigation: Compare EXPLAIN output before/after
```

## Anti-Patterns

❌ Suggesting fixes before confirming root cause
❌ Only providing one hypothesis
❌ Not ranking hypotheses by likelihood
