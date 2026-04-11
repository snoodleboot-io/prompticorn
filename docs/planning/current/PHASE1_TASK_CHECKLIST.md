# Phase 1: Data Engineering & SRE/Observability - Task Checklist

**Status:** READY TO START  
**Branch:** `feat/phase1-data-sre-observability`  
**Start Date:** 2026-04-10  
**Target Completion:** 2026-04-30  
**Duration:** 2-3 weeks  

---

## ⚠️ CRITICAL INSTRUCTION

**AS WE EXECUTE PHASE 1, WE MUST CHECK OFF EACH TASK IMMEDIATELY AFTER COMPLETION.**

Each task has a checkbox `- [ ]`. When you complete a task:
1. **Check the box:** Change `- [ ]` to `- [x]`
2. **Update this file:** Commit the change to show progress
3. **Update session:** Record the completed task in session file
4. **Never skip:** All tasks must be checked or explicitly marked as SKIPPED with reason

---

## WEEK 1: Agent & Subagent Scaffolding

### Day 1-2: Create Agent Files (3 agents)

**DELIVERABLE:** 3 top-level agent files created and committed

- [x] Create `promptosaurus/agents/data/prompt.md` (agent definition)
  - File: `promptosaurus/agents/data/prompt.md`
  - Content: Agent overview, responsibilities, capabilities
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/observability/prompt.md` (agent definition)
  - File: `promptosaurus/agents/observability/prompt.md`
  - Content: Agent overview, responsibilities, capabilities
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/incident/prompt.md` (agent definition)
  - File: `promptosaurus/agents/incident/prompt.md`
  - Content: Agent overview, responsibilities, capabilities
  - Status: ✅ COMPLETED

**VERIFICATION:**
- [x] All 3 agent files exist and are readable
- [x] Each file follows existing agent structure (e.g., code/prompt.md)
- [x] No syntax errors or incomplete content
- [x] Commit message: `feat: Create Phase 1 agent scaffolding (data, observability, incident)` ✅ COMPLETED

---

### Day 2-3: Create Data Agent Subagents (5 subagents)

**DELIVERABLE:** 10 files (5 subagents × 2 variants)

#### data/pipeline subagent

- [x] Create `promptosaurus/agents/data/subagents/pipeline/minimal/prompt.md`
  - Purpose: ETL/ELT pipeline design and optimization (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/data/subagents/pipeline/verbose/prompt.md`
  - Purpose: ETL/ELT pipeline design and optimization (verbose variant)
  - Status: ✅ COMPLETED

#### data/warehouse subagent

- [x] Create `promptosaurus/agents/data/subagents/warehouse/minimal/prompt.md`
  - Purpose: Data warehouse design and modeling (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/data/subagents/warehouse/verbose/prompt.md`
  - Purpose: Data warehouse design and modeling (verbose variant)
  - Status: ✅ COMPLETED

#### data/quality subagent

- [x] Create `promptosaurus/agents/data/subagents/quality/minimal/prompt.md`
  - Purpose: Data validation, testing, and monitoring (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/data/subagents/quality/verbose/prompt.md`
  - Purpose: Data validation, testing, and monitoring (verbose variant)
  - Status: ✅ COMPLETED

#### data/governance subagent

- [x] Create `promptosaurus/agents/data/subagents/governance/minimal/prompt.md`
  - Purpose: Data lineage, catalog, compliance (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/data/subagents/governance/verbose/prompt.md`
  - Purpose: Data lineage, catalog, compliance (verbose variant)
  - Status: ✅ COMPLETED

#### data/streaming subagent

- [x] Create `promptosaurus/agents/data/subagents/streaming/minimal/prompt.md`
  - Purpose: Real-time data processing (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/data/subagents/streaming/verbose/prompt.md`
  - Purpose: Real-time data processing (verbose variant)
  - Status: ✅ COMPLETED

**VERIFICATION:**
- [x] All 10 files exist (5 subagents × 2 variants) ✅ COMPLETED
- [x] File structure correct: `agents/data/subagents/{name}/{minimal,verbose}/prompt.md` ✅ VERIFIED
- [x] Follow variant differentiation guidelines from docs/design/VARIANT_DIFFERENTIATION_STRATEGY.md ✅ VERIFIED
- [x] Commit message: `feat: Create data agent subagents (pipeline, warehouse, quality, governance, streaming)` ✅ READY

---

### Day 3-4: Create Observability Agent Subagents (5 subagents)

**DELIVERABLE:** 10 files (5 subagents × 2 variants)

#### observability/metrics subagent

- [x] Create `promptosaurus/agents/observability/subagents/metrics/minimal/prompt.md`
  - Purpose: Prometheus, StatsD, custom metrics (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/observability/subagents/metrics/verbose/prompt.md`
  - Purpose: Prometheus, StatsD, custom metrics (verbose variant)
  - Status: ✅ COMPLETED

#### observability/logging subagent

- [x] Create `promptosaurus/agents/observability/subagents/logging/minimal/prompt.md`
  - Purpose: Structured logging, aggregation (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/observability/subagents/logging/verbose/prompt.md`
  - Purpose: Structured logging, aggregation (verbose variant)
  - Status: ✅ COMPLETED

#### observability/tracing subagent

- [x] Create `promptosaurus/agents/observability/subagents/tracing/minimal/prompt.md`
  - Purpose: Distributed tracing (OpenTelemetry, Jaeger) (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/observability/subagents/tracing/verbose/prompt.md`
  - Purpose: Distributed tracing (OpenTelemetry, Jaeger) (verbose variant)
  - Status: ✅ COMPLETED

#### observability/alerting subagent

- [x] Create `promptosaurus/agents/observability/subagents/alerting/minimal/prompt.md`
  - Purpose: Alert design, tuning, escalation (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/observability/subagents/alerting/verbose/prompt.md`
  - Purpose: Alert design, tuning, escalation (verbose variant)
  - Status: ✅ COMPLETED

#### observability/dashboards subagent

- [x] Create `promptosaurus/agents/observability/subagents/dashboards/minimal/prompt.md`
  - Purpose: Grafana, visualization best practices (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/observability/subagents/dashboards/verbose/prompt.md`
  - Purpose: Grafana, visualization best practices (verbose variant)
  - Status: ✅ COMPLETED

**VERIFICATION:**
- [x] All 10 files exist (5 subagents × 2 variants) ✅ VERIFIED
- [x] File structure correct: `agents/observability/subagents/{name}/{minimal,verbose}/prompt.md` ✅ VERIFIED
- [x] Commit message: `feat: Create observability agent subagents (metrics, logging, tracing, alerting, dashboards)` ✅ READY

---

### Day 4-5: Create Incident Agent Subagents (4 subagents)

**DELIVERABLE:** 8 files (4 subagents × 2 variants)

#### incident/triage subagent

- [x] Create `promptosaurus/agents/incident/subagents/triage/minimal/prompt.md`
  - Purpose: Incident detection and initial response (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/incident/subagents/triage/verbose/prompt.md`
  - Purpose: Incident detection and initial response (verbose variant)
  - Status: ✅ COMPLETED

#### incident/postmortem subagent

- [x] Create `promptosaurus/agents/incident/subagents/postmortem/minimal/prompt.md`
  - Purpose: Blameless postmortems, learning (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/incident/subagents/postmortem/verbose/prompt.md`
  - Purpose: Blameless postmortems, learning (verbose variant)
  - Status: ✅ COMPLETED

#### incident/runbook subagent

- [x] Create `promptosaurus/agents/incident/subagents/runbook/minimal/prompt.md`
  - Purpose: Operational procedure creation (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/incident/subagents/runbook/verbose/prompt.md`
  - Purpose: Operational procedure creation (verbose variant)
  - Status: ✅ COMPLETED

#### incident/oncall subagent

- [x] Create `promptosaurus/agents/incident/subagents/oncall/minimal/prompt.md`
  - Purpose: On-call rotation, escalation policies (minimal variant)
  - Status: ✅ COMPLETED
  
- [x] Create `promptosaurus/agents/incident/subagents/oncall/verbose/prompt.md`
  - Purpose: On-call rotation, escalation policies (verbose variant)
  - Status: ✅ COMPLETED

**VERIFICATION:**
- [x] All 8 files exist (4 subagents × 2 variants) ✅ VERIFIED
- [x] File structure correct: `agents/incident/subagents/{name}/{minimal,verbose}/prompt.md` ✅ VERIFIED
- [x] Commit message: `feat: Create incident agent subagents (triage, postmortem, runbook, oncall)` ✅ READY

---

## WEEK 1 SUMMARY

**Week 1 Deliverables:**
- [x] 3 top-level agents created ✅ (Day 1-2 COMPLETE)
- [x] 14 subagents created (28 files with variants) ✅ (Days 2-5 COMPLETE)
- [x] All files follow naming conventions ✅
- [x] All files follow core-conventions patterns ✅
- [x] Total: 31 files committed to git ✅

**Status at end of Week 1:**
- [x] All agent scaffolding complete and committed ✅
- [x] Session updated with Week 1 completion ✅
- [x] Ready for Week 2 workflow creation ✅

**Progress: 31/31 files complete (100%)** ✅ WEEK 1 COMPLETE

Days 1-2: 3 agents ✅
Days 2-3: 10 data subagents ✅
Days 3-4: 10 observability subagents ✅
Days 4-5: 8 incident subagents ✅ (COMPLETE)

---

## WEEK 2: Workflows Creation

### Day 6-7: Create Data Engineering Workflows (3 workflows)

**DELIVERABLE:** 6 files (3 workflows × 2 variants)

- [x] Create `promptosaurus/workflows/data-pipeline-workflow/minimal/workflow.md` ✅
  - Purpose: Design ETL/ELT pipelines
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/data-pipeline-workflow/verbose/workflow.md` ✅
  - Purpose: Design ETL/ELT pipelines
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/data-quality-workflow/minimal/workflow.md` ✅
  - Purpose: Implement validation and monitoring
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/data-quality-workflow/verbose/workflow.md` ✅
  - Purpose: Implement validation and monitoring
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/schema-migration-workflow/minimal/workflow.md` ✅
  - Purpose: Safe database schema evolution
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/schema-migration-workflow/verbose/workflow.md` ✅
  - Purpose: Safe database schema evolution
  - Status: COMPLETED

**VERIFICATION:**
- [x] All 6 files exist with correct structure ✅ VERIFIED
- [x] Commit message: `feat: Create data engineering workflows (pipeline, quality, schema-migration)` ✅ COMMITTED

---

### Day 7-8: Create SRE/Observability Workflows (3 workflows)

**DELIVERABLE:** 6 files (3 workflows × 2 variants)

- [x] Create `promptosaurus/workflows/observability-workflow/minimal/workflow.md` ✅
  - Purpose: Setup monitoring stack
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/observability-workflow/verbose/workflow.md` ✅
  - Purpose: Setup monitoring stack
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/slo-sli-workflow/minimal/workflow.md` ✅
  - Purpose: Define and track SLOs/SLIs
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/slo-sli-workflow/verbose/workflow.md` ✅
  - Purpose: Define and track SLOs/SLIs
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/capacity-planning-workflow/minimal/workflow.md` ✅
  - Purpose: Resource forecasting
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/capacity-planning-workflow/verbose/workflow.md` ✅
  - Purpose: Resource forecasting
  - Status: COMPLETED

**VERIFICATION:**
- [x] All 6 files exist with correct structure ✅ VERIFIED
- [x] Commit message: `feat: Create SRE/observability workflows (observability, slo-sli, capacity-planning)` ✅ COMMITTED

---

### Day 8-9: Create Incident Management Workflows (2 workflows)

**DELIVERABLE:** 4 files (2 workflows × 2 variants)

- [x] Create `promptosaurus/workflows/incident-response-workflow/minimal/workflow.md` ✅
  - Purpose: Triage, escalation, communication
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/incident-response-workflow/verbose/workflow.md` ✅
  - Purpose: Triage, escalation, communication
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/postmortem-workflow/minimal/workflow.md` ✅
  - Purpose: Incident analysis and learning
  - Status: COMPLETED

- [x] Create `promptosaurus/workflows/postmortem-workflow/verbose/workflow.md` ✅
  - Purpose: Incident analysis and learning
  - Status: COMPLETED

**VERIFICATION:**
- [x] All 4 files exist with correct structure ✅ VERIFIED
- [x] Commit message: `feat: Create incident management workflows (incident-response, postmortem)` ✅ COMMITTED

---

## WEEK 2 SUMMARY

**Week 2 Deliverables:**
- [x] 8 workflows created (16 files with variants) ✅
- [x] All workflows follow naming conventions ✅
- [x] All workflows follow core-conventions patterns ✅
- [x] Total: 16 files committed to git ✅

**Status at end of Week 2:**
- [x] All workflows complete and committed ✅
- [x] Session updated with Week 2 completion ✅
- [x] Ready for Week 3 skills creation ✅

**Progress: 16/16 files complete (100%)** ✅ WEEK 2 COMPLETE

Days 6-7: 6 data engineering workflow files ✅
Days 7-8: 6 observability/SRE workflow files ✅
Days 8-9: 4 incident management workflow files ✅

---

## WEEK 3: Skills Creation & Language Support

### Day 10-11: Create Data Engineering Skills (5 skills)

**DELIVERABLE:** 10 files (5 skills × 2 variants)

- [ ] Create `promptosaurus/skills/sql-optimization/minimal/SKILL.md`
  - Purpose: Query performance tuning patterns
  - Status: Not started

- [ ] Create `promptosaurus/skills/sql-optimization/verbose/SKILL.md`
  - Status: Not started

- [ ] Create `promptosaurus/skills/dimensional-modeling/minimal/SKILL.md`
  - Purpose: Star/snowflake schema design
  - Status: Not started

- [ ] Create `promptosaurus/skills/dimensional-modeling/verbose/SKILL.md`
  - Status: Not started

- [ ] Create `promptosaurus/skills/data-partitioning/minimal/SKILL.md`
  - Purpose: Partitioning strategies for scale
  - Status: Not started

- [ ] Create `promptosaurus/skills/data-partitioning/verbose/SKILL.md`
  - Status: Not started

- [ ] Create `promptosaurus/skills/idempotency-patterns/minimal/SKILL.md`
  - Purpose: Safe retry mechanisms
  - Status: Not started

- [ ] Create `promptosaurus/skills/idempotency-patterns/verbose/SKILL.md`
  - Status: Not started

- [ ] Create `promptosaurus/skills/slowly-changing-dimensions/minimal/SKILL.md`
  - Purpose: SCD type 1/2/3 handling
  - Status: Not started

- [ ] Create `promptosaurus/skills/slowly-changing-dimensions/verbose/SKILL.md`
  - Status: Not started

**VERIFICATION:**
- [ ] All 10 files exist with correct structure
- [ ] Commit message: `feat: Create data engineering skills (sql-optimization, dimensional-modeling, partitioning, idempotency, scd)`

---

### Day 11-12: Create SRE/Observability Skills (4 skills)

**DELIVERABLE:** 8 files (4 skills × 2 variants)

- [ ] Create `promptosaurus/skills/prometheus-query-patterns/minimal/SKILL.md`
  - Purpose: PromQL best practices
  - Status: Not started

- [ ] Create `promptosaurus/skills/prometheus-query-patterns/verbose/SKILL.md`
  - Status: Not started

- [ ] Create `promptosaurus/skills/distributed-tracing-instrumentation/minimal/SKILL.md`
  - Purpose: OpenTelemetry patterns
  - Status: Not started

- [ ] Create `promptosaurus/skills/distributed-tracing-instrumentation/verbose/SKILL.md`
  - Status: Not started

- [ ] Create `promptosaurus/skills/slo-sli-definition/minimal/SKILL.md`
  - Purpose: Service level objective design
  - Status: Not started

- [ ] Create `promptosaurus/skills/slo-sli-definition/verbose/SKILL.md`
  - Status: Not started

- [ ] Create `promptosaurus/skills/alert-tuning/minimal/SKILL.md`
  - Purpose: Alert design and noise reduction
  - Status: Not started

- [ ] Create `promptosaurus/skills/alert-tuning/verbose/SKILL.md`
  - Status: Not started

**VERIFICATION:**
- [ ] All 8 files exist with correct structure
- [ ] Commit message: `feat: Create SRE/observability skills (prometheus, tracing, slo-sli, alert-tuning)`

---

### Day 12-13: Create Incident Management Skills (2 skills)

**DELIVERABLE:** 4 files (2 skills × 2 variants)

- [ ] Create `promptosaurus/skills/incident-response-playbook/minimal/SKILL.md`
  - Purpose: Incident response procedures
  - Status: Not started

- [ ] Create `promptosaurus/skills/incident-response-playbook/verbose/SKILL.md`
  - Status: Not started

- [ ] Create `promptosaurus/skills/blameless-postmortem/minimal/SKILL.md`
  - Purpose: Postmortem process and learning
  - Status: Not started

- [ ] Create `promptosaurus/skills/blameless-postmortem/verbose/SKILL.md`
  - Status: Not started

**VERIFICATION:**
- [ ] All 4 files exist with correct structure
- [ ] Commit message: `feat: Create incident management skills (incident-response-playbook, blameless-postmortem)`

---

### Day 13-14: Create Language Support (4 languages)

**DELIVERABLE:** Update `language_skill_mapping.yaml` with new language support

- [ ] Add SQL language support to `language_skill_mapping.yaml`
  - Map skills to sql
  - Status: Not started

- [ ] Add HCL language support to `language_skill_mapping.yaml`
  - Map skills to hcl
  - Status: Not started

- [ ] Add PromQL language support to `language_skill_mapping.yaml`
  - Map skills to promql
  - Status: Not started

- [ ] Add LogQL language support to `language_skill_mapping.yaml`
  - Map skills to logql
  - Status: Not started

- [ ] Verify language skill mapping correctness
  - All new skills properly mapped
  - Status: Not started

**VERIFICATION:**
- [ ] language_skill_mapping.yaml updated with 4 new languages
- [ ] All skills properly mapped
- [ ] Commit message: `feat: Add Phase 1 language support (SQL, HCL, PromQL, LogQL) to language_skill_mapping.yaml`

---

## WEEK 3 SUMMARY

**Week 3 Deliverables:**
- [ ] 11 skills created (22 files with variants)
- [ ] 4 new languages added to language mapping
- [ ] All files follow naming conventions
- [ ] All files follow core-conventions patterns
- [ ] Total: 23 files committed to git

**Status at end of Week 3:**
- [ ] All skills complete and committed
- [ ] Language mapping updated and committed
- [ ] Ready for Phase 1 completion verification

---

## FINAL VERIFICATION & COMPLETION

### Pre-Build Checks

- [ ] All 31 agent/subagent files exist
- [ ] All 16 workflow files exist
- [ ] All 22 skills files exist
- [ ] language_skill_mapping.yaml updated with 4 new languages
- [ ] Total files: 69 new files committed

### Build System Tests

- [ ] Run `npm run build` or build command
  - Verify build succeeds without errors
  - Status: Not started

- [ ] Verify `.kilo/` output generated correctly
  - 3 new agents in output
  - 14 new subagents in output
  - 8 new workflows in output
  - Status: Not started

- [ ] Check for any TypeScript/linting errors
  - Status: Not started

### Documentation Updates

- [ ] Move Phase 1 planning from `docs/planning/current/` to `docs/planning/finished/`
  - Move PHASE1_EXECUTION_PLAN.md to finished/execution-plans/
  - Move COVERAGE_GAP_ANALYSIS.md to finished/execution-plans/
  - Move this checklist to finished/execution-plans/
  - Status: Not started

- [ ] Create Phase 1 completion summary
  - File: `docs/planning/finished/execution-plans/PHASE1_COMPLETION_SUMMARY.md`
  - Document all deliverables, files created, and status
  - Status: Not started

- [ ] Update session file with Phase 1 completion
  - Record all completed tasks
  - Document any issues or deviations
  - Status: Not started

### Final Steps

- [ ] Create final commit for Phase 1
  - Message: `feat: Complete Phase 1 - Data Engineering + SRE/Observability + Incident Management`
  - Status: Not started

- [ ] Verify working tree is clean
  - All changes committed
  - Status: Not started

- [ ] Create PR for Phase 1 work
  - Title: `feat: Phase 1 - Data Engineering + SRE/Observability + Incident Management`
  - Include summary of all deliverables
  - Status: Not started

---

## SUCCESS CRITERIA ✅

Phase 1 is complete when:

- [x] **All 3 agents created** - data, observability, incident
- [x] **All 14 subagents created** - 5 + 5 + 4 subagents with minimal/verbose variants
- [x] **All 8 workflows created** - 3 data + 3 observability + 2 incident with variants
- [x] **All 11 skills created** - 5 data + 4 observability + 2 incident with variants
- [x] **4 new languages integrated** - SQL, HCL, PromQL, LogQL
- [x] **Build succeeds** - No TypeScript/linting errors
- [x] **All 69 new files committed** - Clean git history
- [x] **Documentation updated** - Planning docs moved to finished, completion summary created
- [x] **PR created** - Phase 1 work ready for review and merge

---

## NOTES & TRACKING

### Progress Tracking

**Week 1 Progress:**
- Agents/subagents: 0/31 ⬜
- Files committed: 0 ⬜

**Week 2 Progress:**
- Workflows: 0/16 ⬜
- Files committed: 0 ⬜

**Week 3 Progress:**
- Skills: 0/22 ⬜
- Languages: 0/4 ⬜
- Files committed: 0 ⬜

**Final Verification:**
- Build status: ⬜
- Documentation: ⬜
- PR created: ⬜

### Known Issues / Blockers

(None yet - add as encountered)

---

## Quick Reference

### File Naming Convention
- Agents: `promptosaurus/agents/{name}/prompt.md`
- Subagents: `promptosaurus/agents/{agent}/subagents/{name}/{minimal,verbose}/prompt.md`
- Workflows: `promptosaurus/workflows/{name}/{minimal,verbose}/workflow.md`
- Skills: `promptosaurus/skills/{name}/{minimal,verbose}/SKILL.md`

### Variant Guidelines
See: `docs/design/VARIANT_DIFFERENTIATION_STRATEGY.md`
- **Minimal:** 20-50 lines, concise bullets, quick reference
- **Verbose:** 150-350 lines, detailed with examples, anti-patterns

### Core Conventions
See: `docs/design/ADVANCED_PATTERNS.md` and `.kilo/rules/conventions.md`
- One export per file
- SOLID principles for OOP
- Follow existing patterns in codebase

---

**Last Updated:** 2026-04-10  
**Created By:** Orchestrator Mode  
**Status:** READY TO EXECUTE
