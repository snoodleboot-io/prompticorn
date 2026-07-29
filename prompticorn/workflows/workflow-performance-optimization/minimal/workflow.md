---
name: "workflow-performance-optimization"
description: Optimize workflow execution for speed and efficiency
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Performance Optimization Workflow

Making an existing workflow finish sooner and cost less without changing its
output. Distinct from `workflow-scaling-patterns` (absorbing more load) — a
workflow can be slow at trivial volume, or fast but unable to scale.

## Core Concepts
- **Total duration is set by the critical path,** not the slowest step. Optimizing
  an off-path step changes nothing
- **Separate wait time from execution time.** A step queued 9 of its 10 minutes is
  a scheduling problem, not a code problem

## Pattern Types
- **Audit dependency edges:** removing stale ordering edges flattens the graph —
  the cheapest speedup available
- **Replace barriers with pipelines:** a barrier is justified only when the next
  stage needs cross-unit context
- **Batch tuning:** the cost curve is U-shaped; use `split_and_retry` so one poison
  record does not re-run the whole batch
- **Cut redundant work:** incremental processing, skip-if-unchanged, push filters
  down to the source
- **Right-size resources:** match concurrency to the real constraint (pool, rate
  limit), not to core count

## When to Use
- A workflow whose duration or cost has become a problem, with per-step metrics available

## Key Considerations
- **Include the code version in every cache key** — keying on inputs alone serves
  stale results after a logic change
- Concurrency beyond the bottleneck adds queueing, not throughput, and worsens p99
- **Require an unchanged output checksum.** An optimization that changes output is
  not an optimization
- Soak over enough runs that normal variance is not mistaken for improvement
