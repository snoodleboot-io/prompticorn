# Workflow Scaling Patterns Workflow

Absorbing more work — more items, more runs, more concurrent workflows — without
the system degrading.

Distinct from `workflow-performance-optimization`, which makes a single run finish
sooner. Scaling is about throughput and headroom under growth. A workflow can be
fast and unscalable, or slow and perfectly scalable.

---

## 1. Find the binding constraint

Scaling anything other than the actual bottleneck adds cost and no throughput.

### Characteristics:
| Constraint | Symptom | Response |
|------------|---------|----------|
| **Worker capacity** | Queue depth grows, workers at 100% CPU | Add workers |
| **Connection pool** | Workers idle waiting on connections | Raise pool, or pool per shard |
| **Downstream rate limit** | 429s rise with added concurrency | Throttle, do not scale |
| **Single coordinator** | Scheduling lag grows, workers idle | Shard the coordinator |
| **Hot partition** | One unit runs far longer than its peers | Re-key the partitioning |

### Implementation:
```yaml
saturation_signals:
  - {metric: queue_depth,        rising: scale_out}
  - {metric: worker_utilization, threshold: 0.7}
  - {metric: downstream_429_rate, rising: throttle}   # NOT scale_out
```

Adding workers against a rate-limited downstream converts a slow workflow into a
failing one. Read the constraint before scaling.

---

## 2. Horizontal scaling and partitioning

The default scaling axis: more workers over a partitioned work set.

### Implementation:
```yaml
partitioning:
  key: customer_id            # not: date, unless volume per date is even
  strategy: hash
  partitions: 64              # over-partition relative to workers
  rebalance: on_worker_change
```

```
work ──> [p0][p1][p2][p3]...[p63]
            │   │   │   │
          w1  w2  w3  w4        each worker owns several partitions
```

- **Over-partition.** More partitions than workers lets you add workers without
  re-partitioning.
- **Choose the key for even distribution,** not for convenience. Keying on date
  concentrates a backfill into one partition.
- **Watch for hot keys.** One customer with 40% of the volume defeats hash
  partitioning; those need dedicated handling or a composite key.

### Advantages & Disadvantages:
- **Advantage:** Near-linear throughput while the constraint is worker capacity
- **Disadvantage:** Skew converts a parallel run into a serial one plus overhead
- **Disadvantage:** Rebalancing mid-run needs careful checkpointing

---

## 3. Autoscaling on the right signal

### Implementation Strategy:
```yaml
autoscale:
  metric: queue_depth_per_worker      # not CPU
  target: 100
  min_workers: 2
  max_workers: 50                     # a hard ceiling is mandatory
  scale_up_cooldown: 1m
  scale_down_cooldown: 10m            # asymmetric — down slowly
```

- **Scale on backlog, not CPU.** A worker blocked on I/O shows low CPU while the
  queue grows.
- **Asymmetric cooldowns.** Scale up fast, down slowly — aggressive scale-down
  causes thrash, and re-warming workers costs more than the idle capacity saved.
- **Always set `max_workers`.** Unbounded autoscaling turns a stuck-consumer bug
  into an unbounded bill and a downstream outage.

---

## 4. Backpressure

When intake outpaces processing, something must give. Choose it deliberately.

| Strategy | Behaviour | Use when |
|----------|-----------|----------|
| **Block the producer** | Intake slows to processing rate | Producer can wait |
| **Bounded buffer + reject** | Excess rejected with a retryable error | Producer can retry |
| **Load shed** | Drop low-priority work | Some work is genuinely optional |
| **Degrade** | Reduce per-item work under pressure | A cheaper result beats none |

```yaml
backpressure:
  queue_max: 10000
  on_full: reject_with_retry_after    # never: unbounded growth
```

An unbounded queue does not remove backpressure; it defers it until memory runs
out, converting a slowdown into an outage.

---

## 5. Isolation: keep one workload from starving another

Shared capacity means the noisiest workflow degrades all the others.

```yaml
isolation:
  queues: {critical: {workers: 10}, bulk: {workers: 4}}
  quota: {per_tenant_max_inflight: 50}
  priority: {critical: 0, standard: 5, backfill: 9}
```

- Separate queues per priority class; a backfill must never starve the live path
- Per-tenant quotas prevent one tenant consuming the entire pool
- Give backfills their own lower-priority capacity — this single change prevents
  most self-inflicted incidents

---

## 6. State is what usually stops scaling

Stateless workers scale trivially. The constraint is nearly always shared state.

- **Avoid a global lock per item.** Partition the lock by key.
- **Batch the writes** — per-item transactions serialize on the database.
- **Idempotent workers** let you scale, retry, and rebalance without coordination.
- **Beware the coordinator** becoming the bottleneck: at some worker count, the
  scheduler's own bookkeeping dominates. Shard it.

---

## Best Practices

1. **Identify the binding constraint before scaling anything.**
2. **Never scale out against a rate limit** — throttle instead.
3. **Over-partition** so workers can be added without re-partitioning.
4. **Choose partition keys for even distribution,** and monitor for skew.
5. **Autoscale on backlog, not CPU,** with asymmetric cooldowns.
6. **Set a hard `max_workers`.** Always.
7. **Bound every queue** and pick an explicit on-full policy.
8. **Give backfills their own low-priority capacity.**

---

## Common Pitfalls

- **Scaling workers against a rate-limited dependency.** Slow becomes failing.
- **Autoscaling on CPU.** I/O-bound workers look idle while the backlog grows.
- **No `max_workers`.** One stuck consumer scales to the account limit.
- **Partitioning by date.** A backfill lands entirely in one partition.
- **Ignoring hot keys.** One tenant serializes the whole run.
- **Unbounded queues.** Turns a slowdown into an out-of-memory outage.
- **Backfills sharing the live path's capacity.** A routine reprocess pages the on-call.
- **Symmetric scale-down.** Thrash, and re-warm cost exceeding the savings.

---

## Related Patterns

- `workflow-performance-optimization` — making a single run finish sooner
- `workflow-monitoring` — the backlog and saturation signals scaling decisions need
- `async-workflow-execution` — concurrency limits and backpressure within a run
- `workflow-dependency-management` — the graph that determines what can run in parallel