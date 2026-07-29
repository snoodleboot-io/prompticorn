---
name: "workflow-rollback-strategies"
description: Implement safe rollback mechanisms for failed workflows
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Rollback Strategies Workflow

Returning to a known-good workflow *definition* after a bad one ships. Distinct
from `workflow-error-handling-patterns`, which compensates for a step that failed
inside a run — here the runs succeed but do the wrong thing.

## Core Concepts
- Design for **time-to-restore**, not for a rollback button
- **Immutable, digest-pinned versions** — never edit a deployed definition in place
- Every run records the version it executed under; rollback and repair both need it
- The hard decision is **in-flight runs**: `drain`, `abort`, or `let_finish`

## Pattern Types
- **Version pinning:** rollback becomes a pointer change, not a rebuild
- **Progressive exposure:** 1% → 10% → 50% → 100% with soak time; rolling back at
  10% costs 10% of runs
- **Automated triggers:** error rate, p99 duration, DLQ growth — not a human watching
- **Forward-fix:** correct when schema has already migrated non-reversibly
- **Data repair:** a separate idempotent, verified job scoped by recorded version

## When to Use
- Any change to a workflow with side effects or data output

## Key Considerations
- **Rollback does not undo writes.** It stops the bleeding; repair is separate
- **Never roll back the definition while leaving migrated state** — the old version
  then runs against a schema it does not understand
- Keep schema changes backward-compatible for one version so rollback stays available
- Retain several versions; two bad releases in a row leave nothing to restore
- Rehearse on a schedule and measure actual time-to-restore
- Cause unknown? Restore first, diagnose after
