---
name: "workflow-monitoring"
description: Monitor workflow execution with metrics and alerting
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Monitoring Workflow

Making workflow execution observable. Workflows fail differently from services:
the costly failures are the run that quietly stops happening and the run that
succeeds while producing wrong output.

## Core Concepts — four signals
- **Liveness:** time since last successful completion — catches the silent stall
- **Duration:** p50/p95/p99 per run *and* per step
- **Correctness:** row counts, null rates, freshness, duplicates
- **Backlog:** queue depth, lag behind source, DLQ depth

Label every metric by **version** as well as name, or a regression averages in
with the previous release.

## Pattern Types
- **Deadman alert:** `now - last_success > 2 * expected_interval` — highest-value
  alert for any scheduled workflow, and the one error-rate alerting cannot replace
- **Trend-gated backlog alert:** depth alone is noisy; depth *and* rising is real
- **Grouping and inhibition:** one page per workflow, never one per failed unit
- **Structured run records:** run id, version, trigger, per-step status/attempts, trace id
- **Data-quality gates:** fail the run on violation rather than warning and publishing

## When to Use
- Every scheduled or event-driven workflow that anything downstream depends on

## Key Considerations
- **Page only on what a human can act on now.** A failed run with retries remaining
  is not a page; retries exhausted with a growing DLQ is
- Thresholds relative to the schedule, not absolute constants
- Compare correctness against a **trailing band**, not a fixed number
- Record attempts per step — "succeeded on attempt 4" is a degrading dependency
- Heartbeats from long steps distinguish hung from slow
