---
name: "workflow-documentation-patterns"
description: Document workflows for understanding and maintenance
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Documentation Patterns Workflow

Documenting a workflow for the person who meets it at 3am. Workflow docs decay
fast because the definition changes without the prose, so: **generate what can be
generated, author only what cannot.**

## Core Concepts
- **Generated:** step list, dependency graph, schedule, input/output schemas
- **Authored:** owner, SLA, escalation, why it exists, failure modes and remedies
- Store authored metadata **in the definition**, not a wiki — then it is reviewed in
  the same pull request as the change

## Pattern Types
- **Generated diagram:** regenerate from the definition in CI and fail on drift; a
  hand-drawn diagram is wrong within two sprints and people trust it anyway
- **Runbook by symptom:** organised as "run did not start", "failed at step X" —
  not as a narrative
- **Decision records:** why the retry limit is 2, why this is one workflow and not
  three — recorded next to the constraint
- **Automated doc checks:** owner present, runbook links resolve, diagram matches,
  no orphaned runbooks

## When to Use
- Any workflow with an on-call rotation or a downstream consumer

## Key Considerations
- **Answer the two questions on-call actually asks:** "is it safe to re-run?" and
  "what breaks if I do nothing?" — explicitly, near the top
- Document rationale, not mechanics; the definition already says what happens, and
  an unexplained constraint gets "tidied up" into an incident
- Name a human owner and escalation path, not a dead alias
- **Fail CI on doc checks** — a warn-only check is ignored
