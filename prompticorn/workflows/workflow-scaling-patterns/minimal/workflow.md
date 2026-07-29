---
name: "workflow-scaling-patterns"
description: Scale workflows to handle increased load and complexity
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Scaling Patterns Workflow

Absorbing more work without degrading. Distinct from
`workflow-performance-optimization` (making one run finish sooner) — a workflow can
be fast and unscalable, or slow and perfectly scalable.

## Core Concepts
Find the **binding constraint** first; scaling anything else adds cost, not throughput.

| Constraint | Symptom | Response |
|---|---|---|
| Worker capacity | Queue grows, CPU pinned | Add workers |
| Connection pool | Workers idle on connections | Raise pool |
| Downstream rate limit | 429s rise with concurrency | **Throttle, do not scale** |
| Hot partition | One unit far slower than peers | Re-key partitioning |

## Pattern Types
- **Partitioning:** over-partition relative to workers; key for even distribution,
  not convenience — keying on date concentrates a backfill into one partition
- **Autoscaling on backlog, not CPU:** I/O-bound workers look idle while the queue
  grows. Asymmetric cooldowns — up fast, down slowly
- **Backpressure:** bounded queue with an explicit on-full policy (block, reject,
  shed, degrade)
- **Isolation:** separate queues and quotas so backfills never starve the live path
- **Stateless workers:** shared state is what usually stops scaling — partition
  locks, batch writes, keep workers idempotent

## When to Use
- Growth in volume, run frequency, or tenant count is stressing the workflow

## Key Considerations
- **Always set a hard `max_workers`** — unbounded autoscaling turns a stuck consumer
  into an unbounded bill and a downstream outage
- **Unbounded queues defer backpressure until OOM** — a slowdown becomes an outage
- Watch for hot keys; one tenant with 40% of volume defeats hash partitioning
- At some worker count the coordinator itself becomes the bottleneck — shard it
