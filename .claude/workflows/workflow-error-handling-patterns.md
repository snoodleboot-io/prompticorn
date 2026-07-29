# Workflow Error Handling Patterns Workflow

What a workflow does when a step fails: classification, retry, compensation, and
how failure is surfaced.

Companion to `async-workflow-execution` (cancellation, timeouts, join policies for
concurrent steps) and `workflow-rollback-strategies` (reverting an already-deployed
workflow version). This workflow is about failure *during a run*.

---

## 1. Classify the failure first

Every retry decision follows from the classification. Getting this wrong causes
both wasted retries and lost work.

| Class | Example | Retry? |
|-------|---------|--------|
| **Transient** | Connection reset, 503, lock timeout, throttling | Yes, with backoff |
| **Permanent** | 400, schema violation, missing required field | Never — a retry repeats the same error |
| **Poison** | Input that reliably crashes the step | Never — quarantine it |
| **Ambiguous** | Timeout with no response | Only if the step is idempotent |

The ambiguous class is the dangerous one: you do not know whether the work
happened. Treat it as *possibly succeeded* and retry only when a repeat is safe.

### Implementation:
```yaml
error_classification:
  transient: [ConnectionError, TimeoutError, 429, 502, 503, 504]
  permanent: [ValidationError, 400, 401, 403, 404, 422]
  default: permanent          # unknown errors do NOT retry
```

Default unknown errors to **permanent**. An unrecognized error retried five times
is five times the damage plus a delayed, confusing failure report.

---

## 2. Retry with backoff and jitter

### Characteristics:
- Bounded attempts — an unbounded retry is an outage that never reports
- Exponential backoff — constant-interval retries synchronize into a thundering herd
- Jitter — without it, N failed clients retry in lockstep and re-trigger the failure

### Implementation:
```yaml
retry:
  max_attempts: 4              # 1 initial + 3 retries
  backoff: exponential
  base_delay: 1s
  max_delay: 30s
  jitter: full                 # delay = random(0, computed_delay)
  retry_on: transient
```

```
attempt 1 ──fail──> wait ~1s
attempt 2 ──fail──> wait ~2s
attempt 3 ──fail──> wait ~4s
attempt 4 ──fail──> give up, escalate
```

### Use Cases:
- Any network call, storage write, or external API step
- Lock contention and throttling, where the next attempt genuinely may succeed

### Advantages & Disadvantages:
- **Advantage:** Absorbs the large majority of real failures, which are transient
- **Disadvantage:** Multiplies load on a struggling dependency — pair with a circuit breaker
- **Disadvantage:** Extends wall-clock; bound `max_delay` so one step cannot stall a run

---

## 3. Idempotency is the precondition for retry

A retry is safe only if repeating the step is safe. Without this, retry turns a
transient failure into duplicate charges, duplicate emails, or double-applied
migrations.

### Implementation:
```yaml
step:
  name: charge_customer
  idempotency_key: "{{ order_id }}"
  # Derived from the business identity of the work — NOT the attempt number,
  # which would make every retry a fresh operation.
```

### When to Use:
- Always, before enabling automatic retry on a step with side effects
- If a step cannot be made idempotent, it must not be retried automatically —
  escalate instead

---

## 4. Circuit Breaker

Stop calling a dependency that is failing, so it can recover.

### Characteristics:
```
CLOSED ──failures exceed threshold──> OPEN
  ^                                     │
  │                              cool-down elapses
  │                                     v
  └────probe succeeds──────────── HALF_OPEN
                                        │
                                  probe fails
                                        v
                                      OPEN
```

### Implementation Strategy:
```yaml
circuit_breaker:
  failure_threshold: 5         # consecutive failures to open
  cool_down: 60s
  half_open_probes: 1          # single trial request before closing
```

### Use Cases:
- A shared downstream service under load, where retries make it worse
- Fan-out where 200 units would otherwise each retry independently

---

## 5. Compensation (Saga)

A workflow that has already committed several steps cannot roll back a distributed
transaction. Instead each step declares how to undo itself, and failure runs those
in reverse.

### Flow:
```
reserve_stock ──> charge_card ──> book_courier ──✗ FAILS
      │                 │
      └─ release_stock <┴─ refund_card          (reverse order)
```

### Implementation:
```yaml
steps:
  - name: reserve_stock
    compensate: release_stock
  - name: charge_card
    compensate: refund_card
  - name: book_courier
    compensate: cancel_courier
on_failure: compensate_completed_steps_in_reverse
```

### Rules that make sagas work:
- **Compensations must be idempotent** — they are themselves retried
- **Compensations must not fail silently.** A failed compensation is a data-integrity
  incident and must escalate
- **Not everything is compensable.** A sent email cannot be unsent — order the
  workflow so irreversible steps come last

### Advantages & Disadvantages:
- **Advantage:** The only workable consistency model across services without a
  distributed transaction coordinator
- **Disadvantage:** Intermediate states are visible to other readers
- **Disadvantage:** Doubles the step count you must write and test

---

## 6. Dead Letter Queue

Work that cannot succeed must leave the pipeline without stopping it.

### Implementation:
```yaml
on_exhausted_retries:
  action: dead_letter
  include: [input_payload, error, attempt_history, trace_id]
  alert: workflow-dlq-nonzero
```

- Capture the **input**, not just the error — a DLQ entry you cannot replay is a log line
- Alert on DLQ depth; an unwatched DLQ is silent data loss
- Support replay after the fix, and make replay idempotent

---

## Partial Failure

In a fan-out, some units succeed and some fail. Decide the aggregate policy up
front — see `async-workflow-execution` for join policies.

- Never let a failed unit's `null` flow into a downstream gate unfiltered
- Report *which* units failed, not just a count
- Decide explicitly whether 90% success is an overall success or a rollback trigger

---

## Escalation

Automated recovery has a limit. Past it, a human is the correct handler.

```yaml
escalate_when:
  - retries_exhausted
  - compensation_failed        # always — data integrity at risk
  - circuit_open_beyond: 15m
  - dlq_depth_above: 100
```

Escalate with the trace id, the input, the attempt history, and what was already
compensated. An escalation lacking those is a page nobody can act on.

---

## Best Practices

1. **Classify before retrying.** Unknown errors default to permanent.
2. **Bound every retry loop** — attempts and total elapsed time.
3. **Jitter every backoff.** Lockstep retries recreate the outage.
4. **No retry without idempotency.** State the key explicitly.
5. **Make compensations idempotent, and never swallow their failures.**
6. **Order irreversible steps last** so the compensable prefix stays compensable.
7. **Alert on DLQ depth**, not only on step failure.
8. **Log the error with its step and trace id** — "failed" alone is unactionable.

---

## Common Pitfalls

- **Retrying a non-idempotent step.** The classic duplicate-charge bug.
- **Catching broad exceptions and continuing.** Turns a failure into corrupt output.
- **Unbounded retries.** The workflow never completes and never alerts.
- **Constant-interval retries.** Synchronized load spikes on a recovering service.
- **Compensation that fails silently.** Leaves a half-applied state nobody knows about.
- **A DLQ nobody watches.** Indistinguishable from dropping the work.
- **Retrying an ambiguous timeout with no idempotency key.** The work may already
  have succeeded.

---

## Related Patterns

- `async-workflow-execution` — cancellation, timeouts, join policies
- `workflow-rollback-strategies` — reverting a deployed workflow version
- `workflow-monitoring` — the signals that make failures visible
- `multi-agent-coordination` — agent-failure detection and task reassignment