---
name: "async-workflow-execution"
description: Execute workflow steps asynchronously with callbacks and futures
type: workflow
category: workflow-patterns
minimal: true
---

# Async Workflow Execution Workflow

How workflow steps run concurrently: launching work, awaiting results, and
unblocking what comes next. Companion to `multi-agent-coordination` (who does the
work) and `workflow-orchestration-patterns` (how phases are shaped).

## Execution Models
- **Future/Promise:** Launch returns a handle; block only where the value is needed
- **Callback/Continuation:** Completion pushes to a handler; nothing blocks
- **Fan-Out/Fan-In:** Split into independent units, run all, join the results
- **Event-Driven:** A unit starts the moment its last dependency resolves

## Barrier vs. Pipeline
- **Pipeline (default):** Each unit flows through all stages independently.
  Wall-clock is the slowest chain, not the sum of slowest-per-stage.
- **Barrier:** All units finish stage N before any starts N+1. Correct *only*
  when the next stage needs cross-unit context (dedupe, compare, abort-on-empty).
- If the code between stages only maps, flattens, or filters, no barrier is needed.

## Join Policies
- `all_settled` — every unit, success or failure; use when you need the full picture
- `all_success` — abort if any unit fails
- `first_error` / `first_success` — cancel siblings once the outcome is decided

## Key Considerations
- **Bound every await:** timeout on waits, `max_concurrency` on fan-out
- **Idempotent units:** retry and cancellation are only safe if re-running is safe
- **Attach the error path at launch:** an un-awaited rejection is a lost error
- **Filter failed units before aggregating:** a `null` in a gate's input is a defect
- **Emit progress heartbeats** from long-running units so status is observable

## Common Pitfalls
- Awaiting inside the launch loop — sequential code in async syntax
- A barrier where a pipeline belongs — the usual cause of slow "parallel" runs
- Unbounded fan-out — fine at 3 units, exhausts resources at 300
