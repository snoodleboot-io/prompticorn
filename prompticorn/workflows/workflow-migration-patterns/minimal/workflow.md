---
name: "workflow-migration-patterns"
description: Migrate workflows between versions and systems safely
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Migration Patterns Workflow

Moving workflow definitions and their in-flight state to a new version, engine, or
platform without losing runs.

## Core Concepts
Two migrations get conflated and carry different risks:
- **Version migration** — same engine, new definition. The hard part is in-flight runs
- **Platform migration** — new engine. The hard part is that semantics do not map

## Pattern Types
- **Drain (default):** old runs finish on the old definition, new runs use the new one
- **Abort and restart:** cancel in-flight, compensate, re-run — only if steps are compensable
- **State translation:** map in-flight state onto the new definition; highest cost,
  needed only for long-lived (multi-day) runs
- **Expand → migrate → switch → contract:** reversible at every step; contract is a
  separate, much later deploy
- **Shadow run:** run both, compare outputs with a deliberate ignore list, then promote

## When to Use
- Schema changes to workflow state, splitting or merging workflows, engine changes

## Key Considerations
- **Contracting early is the one-way door** — keep the old path until the new one
  survives a full retention window
- **Enumerate engine semantics before porting:** retry scope, timeout scope,
  delivery guarantees, missed-window handling, overlapping runs, state on restart
- Shadow comparisons need an ignore list (timestamps, ids) or every run mismatches
- **Backfills must be checkpointed, throttled, and verified** — unthrottled backfills
  take down the dependencies they share
- Never silently kill in-flight runs at a drain deadline; escalate
