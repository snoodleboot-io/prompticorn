---
name: multiagent-orchestration
description: Run a genuinely-parallel multiagent implementation - plan, gate on environment, spawn subagents concurrently, aggregate
when_to_use: Load before planning ANY work with independently executable units - the request names parallel/multiagent/concurrent execution, asks to orchestrate or fan out agents, or decomposes into lanes that would otherwise run one at a time
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
   independent units run in parallel by default. Spawn a subagent per independently
   executable unit, briefing each with its agent prompt, the loaded conventions, its
   task scope, and the interfaces it shares with others. A unit with parallelisable
   subtasks spawns its own subagents rather than working through them serially.
   Define the aggregator that validates across outputs and gates the next phase. See
   the `multi-agent-coordination` and `workflow-orchestration-patterns` workflows
   for the coordinator pattern.
4. **Environment-readiness gate (HARD).** The `environment-setup` subagent
   identifies, starts, and health-checks every required service — dev server, test
   runner, database, broker, mocks, watchers — before any other lane is unblocked.
   Assume nothing is already up. Confirm ports and health checks; document how to
   verify and stop each cleanly. The pipeline owns setup — never tell the human to
   start services. An unstartable service is a surfaced blocker, not a silent
   failure.
5. **Present the plan for approval (HARD gate).** Deliver a markdown document
   showing: conventions loaded, agent roster, environment manifest, a Mermaid
   execution map (env gate → parallel lanes → subagent spawn points → aggregation →
   sequential gates → debug/retry loop), subagent specs, convention-enforcement
   checkpoints, test strategy (ATDD before coding, TDD concurrent), gap report, and
   debug/retry logic. Wait for approval.
6. **Execute concurrently on approval.** Spawn all unblocked subagents at once —
   never wait for one to return before launching the next; unblock downstream the
   moment dependencies resolve; surface progress from all streams as it happens;
   aggregate at each gate; debug/retry/escalate on failure.

If the roster, conventions, environment state, or plan change materially mid-run,
pause every lane and re-present for approval.
