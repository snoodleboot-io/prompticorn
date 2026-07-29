# Async Workflow Execution Workflow

How a workflow's steps run *concurrently* rather than one-at-a-time: how work is
launched, how results are awaited, and how completion unblocks the next step.

Companion to `multi-agent-coordination` (who does the work, how they talk) and
`workflow-orchestration-patterns` (how phases are shaped). This workflow covers
only the execution model. Do not re-derive the coordinator pattern here.

---

## 1. Future / Promise

Launch work, hold a handle, await the value later.

### Characteristics:
- Launching returns immediately with a handle, not a result
- The handle resolves exactly once — to a value or an error
- The caller chooses *when* to block

### Implementation:
```yaml
step:
  name: fetch_inventory
  mode: async
  returns: future        # handle, not value
  await_at: aggregation  # blocking deferred to the gate
```

```
launch ──> [ pending ] ──> [ resolved: value ]
                      └──> [ rejected: error ]
```

### Use Cases:
- Independent I/O-bound steps (fetches, builds, test shards)
- Any step whose result is not needed until a later gate

### Advantages & Disadvantages:
- **Advantage:** Latency of N steps becomes the slowest, not the sum
- **Advantage:** Straight-line, readable control flow
- **Disadvantage:** A handle awaited too early collapses back to sequential
- **Disadvantage:** An un-awaited handle silently swallows its error

---

## 2. Callback / Continuation

Register what happens on completion; do not hold a handle at all.

### Characteristics:
- Completion pushes to the continuation instead of the caller pulling
- No central place where results are collected — the continuation owns that
- Naturally suits streaming and progress reporting

### Implementation:
```yaml
step:
  name: run_test_shard
  mode: async
  on_complete: record_shard_result
  on_error: quarantine_shard
  on_progress: emit_heartbeat
```

### When to Use:
- Work whose results are consumed incrementally, not in a batch
- Long-running steps that must report progress before they finish
- Fire-and-observe steps with no downstream dependency

### Advantages & Disadvantages:
- **Advantage:** No blocking anywhere; lowest-latency reaction to completion
- **Disadvantage:** Control flow fragments across handlers (callback sprawl)
- **Disadvantage:** Error paths are easy to leave unhandled — always set `on_error`

---

## 3. Fan-Out / Fan-In

Split into independent units, run them all, join the results.

### Implementation Strategy:
```
                 ┌──> unit A ──┐
dispatch ────────┼──> unit B ──┼──> join ──> aggregated result
                 └──> unit C ──┘
```

```yaml
fan_out:
  over: changed_packages
  step: build_and_test
  max_concurrency: 8      # bound the fan — see Backpressure
fan_in:
  policy: all_settled     # or: first_error
  on_partial: report_and_continue
```

### Join policies — pick deliberately:

| Policy | Waits for | Use when |
|--------|-----------|----------|
| `all_settled` | Every unit, success or failure | You need the full picture (audits, reviews) |
| `all_success` | Every unit; aborts on first failure | Downstream is meaningless if any unit failed |
| `first_error` | Cancels siblings on first failure | Failure is fatal and compute is expensive |
| `first_success` | Cancels siblings on first success | Racing redundant strategies |

---

## 4. Barrier vs. Pipeline — the decision that matters most

Both run units concurrently. They differ in *when* a unit may advance.

### Barrier (synchronized stages)
Every unit must finish stage N before any unit starts stage N+1.

```
A1 ══╗            A2
B1 ══╬══ barrier ══ B2
C1 ══╝  (waits)    C2
```

**Correct only when stage N+1 needs cross-unit context** — deduplicating across
all results, aborting when the total count is zero, or comparing units against
each other.

### Pipeline (independent chains)
Each unit flows through every stage on its own; no unit waits on a sibling.

```
A1 ──> A2 ──> A3
B1 ────> B2 ──> B3
C1 ─> C2 ──> C3
```

**The default.** Wall-clock is the slowest single chain, not the sum of
slowest-per-stage. A barrier chosen for tidiness alone wastes exactly the
parallelism it was set up to gain.

### Smell test:
If the code between two barriers only maps, flattens, or filters, there is no
cross-unit dependency — it belongs inside a pipeline stage.

---

## 5. Event-Driven Continuation

Units are unblocked by dependency-resolution events rather than by stage
boundaries.

### Characteristics:
- Each unit declares its dependencies explicitly
- A completion event re-evaluates the ready set
- A unit starts the moment its last dependency resolves

### Implementation:
```yaml
units:
  - id: migrate_schema
    depends_on: [env_ready]
  - id: build_api
    depends_on: [env_ready]
  - id: integration_tests
    depends_on: [migrate_schema, build_api]
```

### Use Cases:
- Dependency graphs that are not cleanly layered
- Long tails where one slow unit would otherwise stall a whole phase

---

## Cancellation and Timeouts

Every await needs a bound. An unbounded await is a hang with extra steps.

```yaml
step:
  timeout: 300s
  on_timeout: cancel_and_escalate
  cancellation: cooperative   # unit checks a cancel signal at safe points
```

- **Cooperative cancellation:** the unit polls for a cancel signal and unwinds
  cleanly. Preferred — leaves no partial state.
- **Hard cancellation:** the unit is dropped. Only safe for idempotent,
  side-effect-free work.
- **Cancel siblings** on `first_error` / `first_success` joins, or they run on
  producing results nobody will read.

---

## Backpressure and Concurrency Limits

Unbounded fan-out is a self-inflicted outage.

- Cap in-flight units (`max_concurrency`); queue the excess
- Size the cap to the real constraint — CPU, connection pool, or API rate limit
- Prefer a bounded queue that blocks the producer over an unbounded one that
  exhausts memory
- Surface the cap in output: silent truncation reads as full coverage

---

## Error Handling

### Partial Failure
Some units succeed, some fail. Decide *before* the run whether the aggregate is
a success. Never let a `null` from a failed unit flow into a gate unfiltered.

### Error Propagation
- A rejected handle that is never awaited is a lost error — await or attach
  `on_error` to every launched unit
- Wrap unit errors with the unit's identity; "failed" without a unit id is
  unactionable in a fan-out of 50

### Retry
- Retry only idempotent units
- Bound attempts and back off between them
- Escalate a persistently-failing unit as a blocker rather than looping

---

## Best Practices

1. **Pipeline by default; justify every barrier.** State the cross-unit
   dependency that requires it.
2. **Bound everything:** timeout on every await, cap on every fan-out.
3. **Make units idempotent** so retry and cancellation are safe.
4. **Attach an error path at launch,** not at await.
5. **Emit progress heartbeats** from long-running units so status is observable.
6. **Filter failed units before aggregating** — `null` in a gate's input is a
   defect, not a data point.
7. **Tag every result with its unit id** so aggregation is traceable.

---

## Common Pitfalls

- **Awaiting inside the launch loop.** `for u in units: await run(u)` is
  sequential code wearing async syntax. Launch all, then await.
- **A barrier where a pipeline belongs.** The most common cause of a
  "parallel" run that is barely faster than a serial one.
- **Unbounded fan-out.** Works on 3 units, exhausts connections on 300.
- **Swallowed rejections.** A launched-and-forgotten unit fails silently and the
  gate reports success.
- **Unbounded await.** No timeout means one hung unit hangs the workflow.
- **Aggregating unfiltered results.** Failed units arrive as `null` and corrupt
  the aggregate.

---

## Related Patterns

- `multi-agent-coordination` — agent roles, messaging, and shared-state mechanics
- `workflow-orchestration-patterns` — phase shaping and gate design
- `multiagent-orchestration` skill — the end-to-end procedure that applies this
  execution model to a real parallel run