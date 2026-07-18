---
name: multiagent-orchestration
description: Run a genuinely-parallel multiagent implementation - plan, gate on environment, spawn subagents concurrently, aggregate
languages: [all]
subagents: [all]
tools_needed: [read, glob]
---

## Instructions

Use this when asked to run a multiagent implementation. You (the host assistant)
perform the orchestration using your own subagent-spawning primitives — this is a
procedure, not a runtime. Do not skip the two hard gates (environment readiness,
plan approval).

1. **Load conventions.** Locate and read every governing doc (coding standards,
   ADRs, naming, structure, security, test patterns). Confirm what loaded; flag gaps.
2. **Discover agents.** Enumerate the available agent prompts and map each to a
   pipeline role (code, ATDD, TDD, verify, enforce, security, debug, PM/architect).
   Flag any role with no matching agent.
3. **Design the execution model.** Declare each unit's dependencies explicitly;
   independent units run in parallel by default. Define the aggregator that gates
   the next phase. See the `multi-agent-coordination` and
   `workflow-orchestration-patterns` workflows for the coordinator pattern.
4. **Environment-readiness gate (HARD).** A dedicated setup subagent identifies,
   starts, and health-checks every required service before any other lane is
   unblocked. The pipeline owns setup — never tell the human to start services. An
   unstartable service is a surfaced blocker, not a silent failure.
5. **Present the plan for approval (HARD gate).** Show: conventions loaded, agent
   roster, environment manifest, a Mermaid execution map (env gate → parallel lanes
   → subagent spawn points → aggregation → sequential gates → debug/retry loop),
   subagent specs, convention-enforcement checkpoints, test strategy (ATDD before
   coding, TDD concurrent), gap report, and debug/retry logic. Wait for approval.
6. **Execute concurrently on approval.** Spawn all unblocked subagents at once;
   unblock downstream the moment dependencies resolve; aggregate at each gate;
   debug/retry/escalate on failure.
