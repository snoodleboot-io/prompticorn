# Workflow Performance Optimization Workflow

Making an existing workflow finish sooner and cost less, without changing what it
produces.

Distinct from `workflow-scaling-patterns`, which is about absorbing more load. A
workflow can be slow at trivial volume (a serialized graph) or fast but unable to
scale (a bottlenecked shared resource). The diagnoses differ.

---

## 1. Measure the critical path before changing anything

Total duration is set by the longest dependency chain, not by the slowest step.
Optimizing a slow step that is not on the critical path changes nothing.

### Characteristics:
```
A(2m) ──> B(10m) ──┐
C(1m) ──> D(3m) ───┴──> E(1m)      total = 13m
        ^^^^ optimizing D to 0 saves nothing; B is the critical path
```

### Implementation:
```yaml
profile:
  per_step: [duration_p50, duration_p99, attempts, wait_time, exec_time]
  critical_path: true
  breakdown: [queue_wait, dependency_wait, execution, io_wait]
```

Separate **wait** from **execution**. A step showing 10 minutes that spent 9 of them
queued behind a concurrency limit is a scheduling problem, not a code problem, and
optimizing its code is wasted effort.

### Advantages & Disadvantages:
- **Advantage:** Points at the change that actually moves total duration
- **Disadvantage:** Requires per-step instrumentation to exist first — see
  `workflow-monitoring`

---

## 2. Shorten the critical path

The highest-leverage change is usually structural, not algorithmic.

| Technique | Effect |
|-----------|--------|
| **Remove stale ordering edges** | Widens the ready set; the graph flattens |
| **Split a serial step** | A long step becomes several parallel ones |
| **Move work off the path** | Non-blocking work (notifications, exports) runs async |
| **Start earlier** | Prefetch inputs during an unrelated step's execution |

### Implementation:
```yaml
- id: send_notifications
  depends_on: [publish_results]
  blocking: false          # off the critical path — no downstream waits on it
```

Auditing dependency edges is the cheapest optimization available and is almost
never done. Most "must run after" edges are historical accidents — see
`workflow-dependency-management`.

---

## 3. Eliminate the barrier

Barriers between stages are the most common structural cause of a slow "parallel"
workflow.

```
BARRIER                          PIPELINE
A1 ══╗          A2               A1 ──> A2 ──> A3
B1 ══╬═ wait ══ B2               B1 ────> B2 ──> B3
C1 ══╝          C2               C1 ─> C2 ──> C3
total = sum of slowest-per-stage total = slowest single chain
```

A barrier is justified only when the next stage needs cross-unit context. See
`async-workflow-execution` for the full decision. If the code between stages only
maps, flattens, or filters, the barrier is pure waste.

---

## 4. Batch and chunk deliberately

Per-item overhead dominates at small batch sizes; memory and retry cost dominate at
large ones.

### Implementation Strategy:
```yaml
batching:
  size: 500                  # tune empirically — the curve is U-shaped
  flush_interval: 30s        # bound latency for partial batches
  on_failure: retry_batch    # or split_and_retry to isolate a poison record
```

- A batch of 1 pays full round-trip overhead per item
- A batch of 100,000 re-does 100,000 items when one record fails
- `split_and_retry` (bisect the failed batch) isolates a poison record without
  re-running the whole batch

---

## 5. Cut redundant work

| Pattern | Applies when |
|---------|--------------|
| **Incremental processing** | Only changed partitions need reprocessing |
| **Memoize by input digest** | Same inputs recur across runs |
| **Push filters down** | Filtering at the source beats transferring then discarding |
| **Skip unchanged** | Digest matches the previous run — do nothing |

```yaml
- id: transform
  cache_key: "{{ inputs_digest }}:{{ code_version }}"
  skip_if_unchanged: true
```

Include the **code version** in the cache key. Keying on inputs alone serves stale
results after a logic change — a correctness bug introduced by an optimization.

---

## 6. Resource right-sizing

Faster is not always more parallel; often it is less contention.

```yaml
resources:
  worker_concurrency: 8       # matched to the real constraint, not to cores
  db_pool: 10                 # concurrency above pool size just queues
  memory: 4Gi                 # under-provisioned memory causes spill-to-disk
```

Match concurrency to the actual bottleneck — connection pool, API rate limit, or
CPU. Concurrency beyond the constraint adds queueing and context-switching without
adding throughput, and often makes p99 worse.

---

## Verify the optimization

```yaml
verification:
  compare: [total_duration_p95, cost_per_run, output_checksum]
  require: output_checksum_unchanged     # non-negotiable
  soak: 7d
```

An optimization that changes output is not an optimization. Pin the output
checksum, and measure over enough runs that normal variance does not read as
improvement.

---

## Best Practices

1. **Profile the critical path first.** Optimizing off-path steps changes nothing.
2. **Separate wait time from execution time** before touching any code.
3. **Audit dependency edges** — the cheapest speedup available.
4. **Replace barriers with pipelines** unless cross-unit context is genuinely needed.
5. **Tune batch size empirically;** the cost curve is U-shaped.
6. **Include the code version in every cache key.**
7. **Match concurrency to the real constraint,** not to core count.
8. **Require an unchanged output checksum** for every optimization.

---

## Common Pitfalls

- **Optimizing the slowest step** when it is not on the critical path.
- **Confusing queue wait with execution time.** Leads to rewriting fast code.
- **Adding concurrency past the bottleneck.** Throughput flat, p99 worse.
- **Caching on inputs without the code version.** Stale results after a logic change.
- **Huge batches.** One bad record forces a re-run of the whole batch.
- **Barriers kept for tidiness.** Discards most of the available parallelism.
- **Declaring victory from one fast run.** Normal variance, not improvement.

---

## Related Patterns

- `workflow-scaling-patterns` — absorbing more load, as opposed to going faster
- `async-workflow-execution` — the barrier-versus-pipeline decision in full
- `workflow-dependency-management` — the edges whose removal flattens the graph
- `workflow-monitoring` — the per-step instrumentation this depends on