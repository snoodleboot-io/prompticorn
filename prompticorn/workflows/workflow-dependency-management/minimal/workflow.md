---
name: "workflow-dependency-management"
description: Manage dependencies between workflow tasks
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Dependency Management Workflow

Declaring what each task needs, and deriving execution order from that instead of
hand-maintaining it. Companion to `async-workflow-execution` (how ready tasks run)
and `workflow-orchestration-patterns` (phase shaping).

## Core Concepts
- Tasks are nodes, "must finish before" is an edge; the graph must be acyclic
- **Declare, don't order** — each task states its needs, the scheduler derives the sequence
- The **ready set** is every task whose dependencies are satisfied; launch it all at once
- Re-evaluate readiness on **each completion**, not at phase boundaries

## Dependency Kinds
- **Data:** B consumes A's output — a hard edge
- **Ordering:** B follows A but uses nothing from it — often removable
- **Resource:** contention for a lock or pool — mutual exclusion, not ordering
- **External:** a file landing, an upstream partition, an approval — always bounded by a timeout

## When to Use
- Build/deploy pipelines, multi-service migrations, any fan-out where units feed others

## Key Considerations
- **Validate before running:** cycles, unknown ids, orphans. Report the cycle path,
  not just "cycle detected"
- **Failure propagation:** `skip_dependents` is usually right — let independent
  branches finish; report skipped separately from failed
- **Delete stale ordering edges** — each one removed widens the ready set
- **Never treat resource contention as an ordering edge** — it serializes needlessly
- Render the graph; a 40-node DAG is unreadable as YAML
