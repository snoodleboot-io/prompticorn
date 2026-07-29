---
name: "workflow-error-handling-patterns"
description: Handle errors in workflows with retries and compensation
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Error Handling Patterns Workflow

What a workflow does when a step fails. Companion to `async-workflow-execution`
(timeouts, cancellation, join policies) and `workflow-rollback-strategies`
(reverting a deployed version).

## Classify First
- **Transient** (503, reset, throttling) — retry with backoff
- **Permanent** (400, schema violation) — never retry, the error repeats
- **Poison** (input that always crashes) — quarantine
- **Ambiguous** (timeout, no response) — retry only if the step is idempotent
- Unknown errors default to **permanent**

## Pattern Types
- **Retry with backoff:** bounded attempts, exponential delay, always jittered
- **Idempotency:** the precondition for any retry; key off business identity, not attempt
- **Circuit breaker:** stop calling a failing dependency so it can recover
- **Compensation (saga):** each step declares its undo; failure runs them in reverse
- **Dead letter queue:** unprocessable work leaves the pipeline without stopping it

## When to Use
- Any step crossing a network or service boundary
- Multi-step flows with side effects that cannot share a transaction

## Key Considerations
- **No retry without idempotency** — otherwise retry means duplicate charges
- **Bound every retry loop**, attempts and total elapsed time
- **Compensations are idempotent and must never fail silently** — a failed
  compensation is a data-integrity incident, escalate it
- **Order irreversible steps last** so the compensable prefix stays compensable
- **Alert on DLQ depth** — an unwatched DLQ is silent data loss
- Escalate with trace id, input, attempt history, and what was compensated
