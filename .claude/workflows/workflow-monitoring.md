# Workflow Monitoring Workflow

Making workflow execution observable: what to measure, what to alert on, and how
to keep a run explainable afterwards.

Workflows fail differently from services. A service tells you it is down; a
workflow's most expensive failures are the run that quietly stops happening and the
run that succeeds while producing wrong output. Monitoring has to catch both.

---

## 1. The four signals that matter for workflows

Service monitoring (latency, traffic, errors, saturation) misses the two failure
modes specific to workflows: *did not run* and *ran but was wrong*.

| Signal | Question | Typical metric |
|--------|----------|----------------|
| **Liveness** | Did it run when it should have? | Time since last successful completion |
| **Duration** | Is it taking longer than it should? | p50 / p95 / p99 run and step duration |
| **Correctness** | Did it produce sane output? | Row counts, checksums, null rates, deltas |
| **Backlog** | Is work accumulating? | Queue depth, lag behind source, DLQ depth |

### Implementation:
```yaml
metrics:
  workflow_run_total:        {type: counter,   labels: [workflow, version, status]}
  workflow_duration_seconds: {type: histogram, labels: [workflow, step]}
  workflow_last_success_ts:  {type: gauge,     labels: [workflow]}
  workflow_output_rows:      {type: gauge,     labels: [workflow]}
  workflow_queue_depth:      {type: gauge,     labels: [workflow]}
```

Label by **version** as well as name. Without it a regression introduced by a new
version is invisible — it averages into the same series as the old one.

### Use Cases:
- Scheduled batch workflows, where absence is the primary failure
- Event-driven consumers, where lag matters more than instantaneous error rate

### Advantages & Disadvantages:
- **Advantage:** Catches silent stalls, which error-rate alerting never will
- **Disadvantage:** Correctness metrics are workflow-specific — no generic version exists

---

## 2. Alert on absence, not just on failure

The costliest failure is the run that never started. No error is emitted, so
error-based alerting stays silent indefinitely.

### Implementation:
```yaml
alerts:
  - name: workflow_stalled
    expr: time() - workflow_last_success_ts > 2 * expected_interval
    severity: page
    # A multiple of the schedule, not a constant — a 5-minute job and a nightly
    # job need very different absolute values.

  - name: workflow_backlog_growing
    expr: deriv(workflow_queue_depth[30m]) > 0 and workflow_queue_depth > 1000
    severity: page
    # Depth alone is noisy; depth *and* a rising trend is real.
```

### When to Use:
- Every scheduled workflow. The deadman is the single highest-value alert here.

---

## 3. Alert on symptoms, page on consequences

Every alert should name something a human can act on now. Most workflow alerts do
not deserve a page.

| Condition | Route |
|-----------|-------|
| One run failed, retries remain | Nothing — the retry is the handler |
| Retries exhausted, DLQ growing | Page |
| No successful run in 2 intervals | Page |
| p99 duration doubled, still succeeding | Ticket |
| Output row count outside historical band | Page — silent corruption |

```yaml
alert_policy:
  for: 10m                  # sustained, not instantaneous
  group_by: [workflow]      # one alert per workflow, not per failed unit
  inhibit: {when: workflow_stalled, suppress: [workflow_duration_high]}
```

**Group and inhibit.** A fan-out of 200 failing units must page once, not 200 times.
Alert storms are how real incidents get missed.

---

## 4. Structured run records

A metric says something is wrong. A run record says what happened.

### Implementation Strategy:
```yaml
run_record:
  run_id: uuid
  workflow: nightly_rollup
  version: 2026.7.14-3        # required to scope rollback and repair
  trigger: schedule | manual | upstream_event
  started_at / ended_at
  status: succeeded | failed | skipped | cancelled
  steps: [{name, status, duration, attempts, error}]
  inputs_digest / outputs_digest
  trace_id
```

- **Correlate by `trace_id`** across steps and services, or debugging a distributed
  workflow becomes grepping several systems by timestamp.
- **Record attempts per step,** not just final status. "Succeeded on attempt 4" is
  an early warning that a dependency is degrading.
- Emit heartbeats from long-running steps so a hung step is distinguishable from a
  merely slow one.

---

## 5. Correctness monitoring

The hardest failure to detect: the run succeeds and the output is wrong.

```yaml
data_quality_checks:
  - {metric: row_count,  expect: within_pct_of_trailing_7d, tolerance: 20}
  - {metric: null_rate,  column: customer_id, expect: "== 0"}
  - {metric: freshness,  expect: max_event_ts > now() - 2h}
  - {metric: duplicates, key: order_id, expect: "== 0"}
on_violation: fail_the_run     # not: log and continue
```

Fail the run on violation. A workflow that emits a quality warning and publishes
anyway has taught every downstream consumer to ignore the warning.

Compare against a **trailing band**, not a fixed constant. Fixed thresholds are
either too loose to catch anything or too tight to survive normal growth.

---

## Dashboards

Structure by question, not by which metrics happen to exist:

1. **Are the workflows healthy?** Last success, current status, backlog — one row each
2. **Is this workflow healthy?** Duration trend by step, attempts, recent runs
3. **What happened in this run?** Step timeline, errors, input/output digests

The step-level duration trend is what turns "the workflow got slower" into "step 4
got slower after version 2026.7.14-3".

---

## Best Practices

1. **Deadman-alert every scheduled workflow.** Absence is what error-rate alerting
   cannot see.
2. **Label metrics by version** so regressions are attributable.
3. **Group and inhibit alerts** — one page per workflow, never one per failed unit.
4. **Page only on what a human can act on now;** route the rest to tickets.
5. **Record version and trace id on every run** — rollback and repair need them.
6. **Track attempts per step** to see degradation before it becomes failure.
7. **Fail runs on data-quality violations** instead of warning and publishing.
8. **Compare against trailing bands,** not fixed thresholds.

---

## Common Pitfalls

- **Alerting only on errors.** A stalled scheduler emits none.
- **Fixed staleness thresholds.** Wrong for either the 5-minute job or the nightly one.
- **Per-unit alerting in a fan-out.** 200 pages, and the real incident is buried.
- **No version label.** A regression averages in with the previous release.
- **Warning on bad data and publishing anyway.** Trains everyone to ignore warnings.
- **Metrics without run records.** You know something failed, not why.
- **Paging on a single failed run** that still has retries left — alert fatigue.

---

## Related Patterns

- `workflow-error-handling-patterns` — what the run does with the failures you detect
- `workflow-performance-optimization` — acting on the duration signals
- `workflow-rollback-strategies` — the automated triggers these signals feed
- `workflow-scaling-patterns` — reading backlog and saturation for capacity