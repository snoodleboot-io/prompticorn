---
name: "workflow-security-in-workflows"
description: Implement security controls in workflow execution
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Security In Workflows Workflow

Securing the orchestration layer: what a run may do, what it carries, what it
leaves behind. Workflows hold broad long-lived credentials, run unattended, and
touch many systems in one pass — so one compromised step reaches further than a
compromised service would.

## Core Concepts
- **Identity per step, not per workflow.** One account with the union of every
  permission means any compromise yields all of it
- Short-lived credentials issued at step start, expiring before the run ends

## Pattern Types
- **Secrets by reference:** never in definitions (versioned, diffed, readable) and
  never in run parameters (logged, displayed, retained)
- **Boundary redaction:** apply to logs, run records, traces, and error messages —
  the error path is where payloads leak
- **Input allow-listing:** a trigger is an entry point; validate shape and size,
  never interpolate parameters into a shell command
- **Approval gates:** bind the approval to the run id *and* inputs digest, or it
  can be replayed against different inputs
- **Immutable audit trail:** record the triggering principal, not just "scheduler"

## When to Use
- Any workflow touching production data, credentials, or externally-triggered input

## Key Considerations
- **Never put user data in metric labels** — high cardinality and permanent
  retention in a weakly-controlled store
- Treat path parameters as hostile; `../` traversal via a parameter is a recurring finding
- **Pin step images by digest,** not tag — otherwise the reviewed step is not the
  step that ran
- Review definition changes as strictly as application code; one line can exfiltrate
  a database
