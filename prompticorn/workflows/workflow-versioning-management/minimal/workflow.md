---
name: "workflow-versioning-management"
description: Manage multiple versions of workflows with compatibility
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Versioning Management Workflow

Running several versions at once without breaking in-flight runs, reproducibility,
or downstream consumers. `workflow-migration-patterns` moves between versions;
`workflow-rollback-strategies` goes back; this defines the rules that make both work.

## Core Concepts
Version three things **separately** — collapsing them causes "we changed nothing"
incidents:
- **Definition** (steps, graph, schedule) — affects in-flight runs
- **Step implementation** (code, image) — affects nobody if the contract holds
- **Output contract** (schema, semantics) — affects every consumer

## Compatibility
- Safe: adding an optional output field
- Breaking: adding a required input, removing or renaming an output
- **Breaking and silent:** changing a field's type, units, or meaning while keeping
  its name — passes every schema check and corrupts every consumer.
  **Rename on semantic change** so the break is loud

## Pattern Types
- **Bind at start:** a run keeps its version for its lifetime; never swap underneath
- **Concurrent versions:** active / draining / retired, with at least one prior
  version deployable so rollback stays available
- **State schema evolution:** additive with defaults, and **preserve unknown fields**
  — dropping them makes rollback silently lossy
- **Digest pinning:** definitions and images by digest, never tag
- **Deprecation with telemetry:** measure actual use before sunsetting

## When to Use
- Any workflow with downstream consumers or runs long enough to span a deploy

## Key Considerations
- Retain retired definitions for the audit period — you must be able to explain a
  historical run
- Mutable tags defeat audit, rollback scoping, and data repair simultaneously
- Consumer lists are always incomplete; usage telemetry is the only reliable evidence
