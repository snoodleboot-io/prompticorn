# Completed Planning

Finished work moved out of `../current/`. Kept for historical context and traceability.

## Contents

- **Phase 1 & Phase 2** — agent/workflow/skill expansion (`PHASE1_*`, `PHASE2_*`). Phase 2 closed 100%.
- **Skill/workflow mapping system** — language-agnostic agent→skill/workflow mappings, implemented and unit-tested
  (`IMPLEMENTATION_COMPLETE.md`, `IMPLEMENTATION_APPROVED.md`, `UNIT_TESTS_ADDED.md`,
  `AGENT_SKILLS_WORKFLOWS_IMPLEMENTATION_PLAN.md`, `MAPPING_CHANGE_SUMMARY.md`,
  `PROPOSED_SKILLS_WORKFLOWS_MAPPING.md`, `SKILLS_WORKFLOWS_MAPPING_ANALYSIS.md`,
  `skill_mappings.json`, `workflow_mappings.json`).
- **Kilo template substitution fix** — `{{PRIMARY_AGENTS_LIST}}` and template-variable substitution wired into
  `KiloBuilder` (`TEMPLATE_SUBSTITUTION_FIX.md`, `PRIMARY_AGENTS_LIST_FIX.md`).
  NOTE: scoped to Kilo only. The equivalent fix for the **Claude** path is still open — see
  `../current/CLAUDE_TEMPLATE_POPULATION_FIX.plan.md`.

## Still active (in `../current/`)

- `CLAUDE_TEMPLATE_POPULATION_FIX.plan.md` — Claude conventions/agents ship unrendered template variables.
- `PHASE3_*` — Phase 3 in progress (Week 2 done; Weeks 3–4 pending).
- `SOURCE_CODE_UPDATES_DESIGN.md` — only the agent-permission changes have landed; remaining parts pending.
