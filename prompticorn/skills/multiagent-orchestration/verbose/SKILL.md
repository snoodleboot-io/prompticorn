---
name: multiagent-orchestration
description: Run a genuinely-parallel multiagent implementation with detailed guidance - plan, gate on environment, spawn subagents concurrently, aggregate, and debug/retry
languages: [all]
subagents: [all]
tools_needed: [read, glob]
---

## Instructions

Invoke this on demand ("run the multiagent implementation"). **You (the host
assistant) perform the orchestration using your own subagent-spawning primitives.**
prompticorn is a prompt/config generator, not an agent runtime — the parallelism is
realized by you, the capable host, not by prompticorn. This skill composes (does not
duplicate) the existing `multi-agent-coordination`, `workflow-orchestration-patterns`,
and `async-workflow-execution` workflows; read those for the coordinator pattern,
diagrams, and async model.

Two gates are non-negotiable: the **environment-readiness gate** (Step 4) and the
**plan-before-work approval gate** (Step 5). Never spawn implementation lanes before
both pass.

### Step 1: Load conventions

**Purpose:** Every subagent must implement against the same rules.

- Locate and read all governing docs: coding standards, ADRs, naming, directory
  structure, security guidance, and test patterns.
- Confirm explicitly which docs loaded (list them).
- Flag gaps: any convention area with no doc is a risk to call out in the plan.

### Step 2: Discover agents

**Purpose:** Know your roster before designing the pipeline.

- Enumerate the available agent prompts.
- Map each to a pipeline role: code, ATDD, TDD, verify, enforce, security, debug,
  PM/architect.
- Flag any role with no matching agent (a coverage gap for the plan's gap report).

### Step 3: Design the execution model

**Purpose:** Maximize safe parallelism.

- **Explicit dependencies:** each agent/subagent declares what it depends on.
- **Parallel by default:** independent units run concurrently.
- **Aggregator per phase:** define the aggregator that collects a phase's outputs
  and gates the next phase. Reuse the coordinator pattern from
  `multi-agent-coordination` / `workflow-orchestration-patterns` rather than
  reinventing it.

### Step 4: Environment-readiness gate (HARD)

**Purpose:** No lane starts against a dead dependency.

- A **dedicated setup subagent** identifies, starts, and health-checks every
  required service (DBs, queues, caches, external stubs) before any other lane is
  unblocked.
- **The pipeline owns setup.** Never instruct the human to start services.
- An **unstartable service is a surfaced blocker** — stop and report it, don't
  silently proceed with a degraded environment.

### Step 5: Present the plan for approval (HARD gate)

**Purpose:** The human approves the shape of the run before any work happens.

Present, in one plan:
- Conventions loaded (from Step 1).
- Agent roster and role mapping (Step 2).
- Environment manifest (services + health checks, Step 4).
- A **Mermaid execution map**: `env gate → parallel lanes → subagent spawn points →
  aggregation → sequential gates → debug/retry loop`.
- Subagent specs (each unit's inputs, outputs, dependencies, owning agent).
- Convention-enforcement checkpoints (where the enforce/verify roles gate).
- Test strategy: **ATDD before coding, TDD concurrent with coding**.
- Gap report (roles/conventions/services with no coverage).
- Debug / retry / escalate logic.

**Wait for explicit approval before Step 6.**

### Step 6: Concurrent execution on approval

**Purpose:** Realize the parallelism.

- Spawn all currently-unblocked subagents **simultaneously**.
- Unblock a downstream unit the moment its dependencies resolve — do not wait for a
  whole phase if a unit is ready.
- **Aggregate at each gate**; a gate advances only when its inputs are complete and
  pass enforcement.
- On failure, run the debug/retry loop; escalate a persistently-failing unit as a
  blocker rather than looping indefinitely.

Delegated background/isolated subagents must emit progress heartbeats per the core
"Subagent Progress Heartbeats" convention so their status is observable.
