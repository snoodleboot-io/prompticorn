# Phase 1: Data Engineering & SRE/Observability - Execution Plan

**Status:** 🎯 READY TO START  
**Branch:** `feat/phase1-data-sre-observability`  
**Priority:** HIGHEST  
**Estimated Duration:** 2-3 weeks  
**Target Completion:** April 30, 2026  

---

## Executive Summary

Phase 1 addresses the **most critical gaps** in prompticorn coverage:
1. **Data Engineering** (completely missing)
2. **SRE/Observability** (limited coverage)
3. **Incident Management** (missing)

These additions will unlock massive value for data teams, SRE teams, and production reliability practices.

---

## Deliverables

### 🎯 New Agents (3)

1. **`data` Agent** - Data engineering specialist
2. **`observability` Agent** - Monitoring and alerting specialist
3. **`incident` Agent** - Incident management specialist

### 🔧 New Subagents (14)

**data agent (5 subagents):**
- `pipeline` - ETL/ELT pipeline design and optimization
- `warehouse` - Data warehouse design and modeling
- `quality` - Data validation, testing, and monitoring
- `governance` - Data lineage, catalog, compliance
- `streaming` - Real-time data processing

**observability agent (5 subagents):**
- `metrics` - Prometheus, StatsD, custom metrics
- `logging` - Structured logging, aggregation
- `tracing` - Distributed tracing (OpenTelemetry, Jaeger)
- `alerting` - Alert design, tuning, escalation
- `dashboards` - Grafana, visualization best practices

**incident agent (4 subagents):**
- `triage` - Incident detection and initial response
- `postmortem` - Blameless postmortems, learning
- `runbook` - Operational procedure creation
- `oncall` - On-call rotation, escalation policies

### 📋 New Workflows (8)

**Data Engineering (3):**
1. `data-pipeline-workflow` - Design ETL/ELT pipelines
2. `data-quality-workflow` - Implement validation and monitoring
3. `schema-migration-workflow` - Safe database schema evolution

**SRE/Observability (3):**
4. `observability-workflow` - Setup monitoring stack
5. `slo-sli-workflow` - Define and track SLOs/SLIs
6. `capacity-planning-workflow` - Resource forecasting

**Incident Management (2):**
7. `incident-response-workflow` - Triage, escalation, communication
8. `postmortem-workflow` - Incident analysis and learning

### 🎓 New Skills (11)

**Data Engineering (5):**
1. `sql-optimization` - Query performance tuning patterns
2. `dimensional-modeling` - Star/snowflake schema design
3. `data-partitioning` - Partitioning strategies for scale
4. `idempotency-patterns` - Safe retry mechanisms
5. `slowly-changing-dimensions` - SCD type 1/2/3 handling

**SRE/Observability (4):**
6. `prometheus-query-patterns` - PromQL best practices
7. `distributed-tracing-instrumentation` - OpenTelemetry patterns
8. `slo-sli-definition` - Service level objective design
9. `grafana-dashboard-design` - Effective visualization

**Incident Management (2):**
10. `incident-timeline-creation` - Structured incident logging
11. `root-cause-five-whys` - Root cause analysis technique

### 🌐 New Language Support (4)

1. **PostgreSQL** - PostgreSQL-specific SQL conventions
2. **BigQuery** - BigQuery SQL dialect and best practices
3. **Snowflake** - Snowflake SQL and warehouse conventions
4. **dbt** - dbt project structure and conventions

---

## Execution Checklist

### ✅ Pre-Work (COMPLETED - April 10, 2026)

- [x] Repository cleanup
- [x] Commit all changes from core conventions work
- [x] Create PR for `bugfix/yaml-parser-body-extraction` → `main`
- [x] Create new feature branch `feat/phase1-data-sre-observability`
- [x] Coverage gap analysis completed (`docs/COVERAGE_GAP_ANALYSIS.md`)
- [x] Execution plan documented (this file)

### 📝 Step 1: Create Agent Scaffolding (Week 1, Days 1-2)

**Deliverable:** Agent directory structure and base prompt files

#### 1.1 Data Agent Structure
- [ ] Create `prompticorn/agents/data/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/pipeline/minimal/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/pipeline/verbose/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/warehouse/minimal/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/warehouse/verbose/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/quality/minimal/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/quality/verbose/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/governance/minimal/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/governance/verbose/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/streaming/minimal/prompt.md`
- [ ] Create `prompticorn/agents/data/subagents/streaming/verbose/prompt.md`

#### 1.2 Observability Agent Structure
- [ ] Create `prompticorn/agents/observability/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/metrics/minimal/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/metrics/verbose/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/logging/minimal/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/logging/verbose/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/tracing/minimal/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/tracing/verbose/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/alerting/minimal/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/alerting/verbose/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/dashboards/minimal/prompt.md`
- [ ] Create `prompticorn/agents/observability/subagents/dashboards/verbose/prompt.md`

#### 1.3 Incident Agent Structure
- [ ] Create `prompticorn/agents/incident/prompt.md`
- [ ] Create `prompticorn/agents/incident/subagents/triage/minimal/prompt.md`
- [ ] Create `prompticorn/agents/incident/subagents/triage/verbose/prompt.md`
- [ ] Create `prompticorn/agents/incident/subagents/postmortem/minimal/prompt.md`
- [ ] Create `prompticorn/agents/incident/subagents/postmortem/verbose/prompt.md`
- [ ] Create `prompticorn/agents/incident/subagents/runbook/minimal/prompt.md`
- [ ] Create `prompticorn/agents/incident/subagents/runbook/verbose/prompt.md`
- [ ] Create `prompticorn/agents/incident/subagents/oncall/minimal/prompt.md`
- [ ] Create `prompticorn/agents/incident/subagents/oncall/verbose/prompt.md`

**Verification:**
```bash
# Count agent files created
find prompticorn/agents/data -name "prompt.md" | wc -l  # Should be 11 (1 agent + 10 subagent variants)
find prompticorn/agents/observability -name "prompt.md" | wc -l  # Should be 11
find prompticorn/agents/incident -name "prompt.md" | wc -l  # Should be 9

# Total should be 31 new agent/subagent files
```

---

### 📚 Step 2: Write Agent Content (Week 1, Days 3-5)

**Guidelines:**
- Follow `docs/VARIANT_DIFFERENTIATION_STRATEGY.md` for minimal vs verbose
- Minimal: 20-50 lines, concise bullets, quick reference
- Verbose: 150-350 lines, detailed examples, anti-patterns, code snippets
- Reference existing subagents as examples
- Include real-world scenarios and common pitfalls

#### 2.1 Write Data Agent Content
- [ ] `data/prompt.md` - Main data agent description
- [ ] `data/subagents/pipeline/*` - ETL/ELT pipeline patterns
- [ ] `data/subagents/warehouse/*` - Data warehouse design
- [ ] `data/subagents/quality/*` - Data validation and testing
- [ ] `data/subagents/governance/*` - Lineage, catalog, compliance
- [ ] `data/subagents/streaming/*` - Real-time processing patterns

#### 2.2 Write Observability Agent Content
- [ ] `observability/prompt.md` - Main observability agent
- [ ] `observability/subagents/metrics/*` - Prometheus, StatsD patterns
- [ ] `observability/subagents/logging/*` - Structured logging
- [ ] `observability/subagents/tracing/*` - OpenTelemetry, distributed tracing
- [ ] `observability/subagents/alerting/*` - Alert design and tuning
- [ ] `observability/subagents/dashboards/*` - Grafana best practices

#### 2.3 Write Incident Agent Content
- [ ] `incident/prompt.md` - Main incident agent
- [ ] `incident/subagents/triage/*` - Incident detection and response
- [ ] `incident/subagents/postmortem/*` - Blameless postmortems
- [ ] `incident/subagents/runbook/*` - Runbook creation
- [ ] `incident/subagents/oncall/*` - On-call best practices

**Quality Checklist (for each subagent):**
- [ ] Real code examples (not pseudocode)
- [ ] Common anti-patterns documented
- [ ] Tool recommendations (e.g., Prometheus, Grafana, dbt)
- [ ] Links to official documentation
- [ ] Tested patterns that actually work

---

### 🎨 Step 3: Create Workflows (Week 2, Days 1-3)

**Deliverable:** 8 new workflows with minimal/verbose variants

#### 3.1 Data Engineering Workflows
- [ ] Create `prompticorn/workflows/data-pipeline-workflow/minimal/workflow.md`
- [ ] Create `prompticorn/workflows/data-pipeline-workflow/verbose/workflow.md`
- [ ] Create `prompticorn/workflows/data-quality-workflow/minimal/workflow.md`
- [ ] Create `prompticorn/workflows/data-quality-workflow/verbose/workflow.md`
- [ ] Create `prompticorn/workflows/schema-migration-workflow/minimal/workflow.md`
- [ ] Create `prompticorn/workflows/schema-migration-workflow/verbose/workflow.md`

#### 3.2 SRE/Observability Workflows
- [ ] Create `prompticorn/workflows/observability-workflow/minimal/workflow.md`
- [ ] Create `prompticorn/workflows/observability-workflow/verbose/workflow.md`
- [ ] Create `prompticorn/workflows/slo-sli-workflow/minimal/workflow.md`
- [ ] Create `prompticorn/workflows/slo-sli-workflow/verbose/workflow.md`
- [ ] Create `prompticorn/workflows/capacity-planning-workflow/minimal/workflow.md`
- [ ] Create `prompticorn/workflows/capacity-planning-workflow/verbose/workflow.md`

#### 3.3 Incident Management Workflows
- [ ] Create `prompticorn/workflows/incident-response-workflow/minimal/workflow.md`
- [ ] Create `prompticorn/workflows/incident-response-workflow/verbose/workflow.md`
- [ ] Create `prompticorn/workflows/postmortem-workflow/minimal/workflow.md`
- [ ] Create `prompticorn/workflows/postmortem-workflow/verbose/workflow.md`

**Content Guidelines:**
- Step-by-step procedures
- Decision trees for common scenarios
- Templates and checklists
- Integration with existing tools

**Verification:**
```bash
# Count workflow files created
find prompticorn/workflows/*-workflow -name "workflow.md" | grep -E "(data-pipeline|data-quality|schema-migration|observability|slo-sli|capacity-planning|incident-response|postmortem)" | wc -l
# Should be 16 files (8 workflows × 2 variants)
```

---

### 🎓 Step 4: Create Skills (Week 2, Days 4-5)

**Deliverable:** 11 new skills with minimal/verbose variants

#### 4.1 Data Engineering Skills
- [ ] Create `prompticorn/skills/sql-optimization/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/sql-optimization/verbose/SKILL.md`
- [ ] Create `prompticorn/skills/dimensional-modeling/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/dimensional-modeling/verbose/SKILL.md`
- [ ] Create `prompticorn/skills/data-partitioning/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/data-partitioning/verbose/SKILL.md`
- [ ] Create `prompticorn/skills/idempotency-patterns/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/idempotency-patterns/verbose/SKILL.md`
- [ ] Create `prompticorn/skills/slowly-changing-dimensions/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/slowly-changing-dimensions/verbose/SKILL.md`

#### 4.2 SRE/Observability Skills
- [ ] Create `prompticorn/skills/prometheus-query-patterns/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/prometheus-query-patterns/verbose/SKILL.md`
- [ ] Create `prompticorn/skills/distributed-tracing-instrumentation/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/distributed-tracing-instrumentation/verbose/SKILL.md`
- [ ] Create `prompticorn/skills/slo-sli-definition/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/slo-sli-definition/verbose/SKILL.md`
- [ ] Create `prompticorn/skills/grafana-dashboard-design/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/grafana-dashboard-design/verbose/SKILL.md`

#### 4.3 Incident Management Skills
- [ ] Create `prompticorn/skills/incident-timeline-creation/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/incident-timeline-creation/verbose/SKILL.md`
- [ ] Create `prompticorn/skills/root-cause-five-whys/minimal/SKILL.md`
- [ ] Create `prompticorn/skills/root-cause-five-whys/verbose/SKILL.md`

**Content Focus:**
- Reusable techniques and patterns
- Code examples and templates
- Tool-specific guidance
- Common mistakes to avoid

**Verification:**
```bash
# Count skill files created
find prompticorn/skills -name "SKILL.md" | grep -E "(sql-optimization|dimensional-modeling|data-partitioning|idempotency-patterns|slowly-changing-dimensions|prometheus-query|distributed-tracing|slo-sli|grafana-dashboard|incident-timeline|root-cause-five)" | wc -l
# Should be 22 files (11 skills × 2 variants)
```

---

### 🌐 Step 5: Add Language Support (Week 3, Days 1-2)

**Deliverable:** 4 new language convention files

#### 5.1 SQL Dialect Conventions
- [ ] Create `prompticorn/agents/core/conventions-postgresql.md`
  - PostgreSQL-specific features (CTEs, window functions, JSONB)
  - Performance optimization (EXPLAIN ANALYZE, indexes)
  - Best practices (transactions, constraints)

- [ ] Create `prompticorn/agents/core/conventions-bigquery.md`
  - BigQuery SQL dialect differences
  - Partitioning and clustering strategies
  - Cost optimization techniques
  - Best practices for large-scale analytics

- [ ] Create `prompticorn/agents/core/conventions-snowflake.md`
  - Snowflake SQL features and syntax
  - Virtual warehouse sizing
  - Time travel and cloning
  - Performance optimization

#### 5.2 Data Tools Conventions
- [ ] Create `prompticorn/agents/core/conventions-dbt.md`
  - dbt project structure
  - Model organization (staging, intermediate, marts)
  - Testing strategies
  - Jinja templating best practices
  - Documentation patterns

**Verification:**
```bash
# Verify new language files
ls -la prompticorn/agents/core/ | grep -E "(postgresql|bigquery|snowflake|dbt)"
# Should show 4 new files
```

---

### 🔗 Step 6: Update Language Skill Mapping (Week 3, Day 3)

**Deliverable:** Updated `language_skill_mapping.yaml`

#### 6.1 Add Language Entries
- [ ] Add `postgresql` entry with data-related skills/workflows
- [ ] Add `bigquery` entry with data-related skills/workflows
- [ ] Add `snowflake` entry with data-related skills/workflows
- [ ] Add `dbt` entry with data pipeline skills/workflows

#### 6.2 Update Existing Language Entries
- [ ] Update `python` entry - add data engineering skills
- [ ] Update `sql` entry - reference dialect-specific conventions
- [ ] Update `all` entry - add observability/incident skills (universal)

**Example Mapping:**
```yaml
postgresql:
  skills:
    - sql-optimization
    - dimensional-modeling
    - data-partitioning
  workflows:
    - data-pipeline-workflow
    - data-quality-workflow
    - schema-migration-workflow

dbt:
  skills:
    - sql-optimization
    - dimensional-modeling
    - idempotency-patterns
    - slowly-changing-dimensions
  workflows:
    - data-pipeline-workflow
    - data-quality-workflow

all:
  skills:
    - prometheus-query-patterns
    - distributed-tracing-instrumentation
    - slo-sli-definition
    - incident-timeline-creation
  workflows:
    - observability-workflow
    - incident-response-workflow
    - postmortem-workflow
```

---

### 🧪 Step 7: Testing & Validation (Week 3, Days 4-5)

**Deliverable:** Verified build output and quality checks

#### 7.1 Build Verification
- [ ] Run `rm -rf .kilo/ && uv run prompticorn init --language python`
- [ ] Verify all 3 new agents appear in `.kilo/agents/`
- [ ] Verify all 14 new subagents appear in `.kilo/agents/{agent}/{subagent}.md`
- [ ] Verify all 8 new workflows appear in `.kilo/commands/`
- [ ] Verify all 11 new skills appear in `.kilo/skills/`
- [ ] Verify new language conventions appear in `.kilo/rules/`

#### 7.2 Content Quality Checks
- [ ] All minimal variants are 20-50 lines
- [ ] All verbose variants are 150-350 lines
- [ ] No placeholder content (e.g., "TODO", "[EXAMPLE]")
- [ ] All code examples are real and tested
- [ ] All links to external docs are valid
- [ ] Markdown formatting is correct (no broken tables, lists)

#### 7.3 Language Filtering Tests
- [ ] Test `postgresql` language - data skills/workflows included
- [ ] Test `bigquery` language - BigQuery-specific conventions loaded
- [ ] Test `python` language - data + observability skills included
- [ ] Test `typescript` language - observability/incident skills included (universal)

**Test Commands:**
```bash
# Test PostgreSQL build
rm -rf .kilo/
uv run prompticorn init
# Select language: postgresql
# Verify .kilo/rules/conventions-postgresql.md exists
# Verify data skills appear in .kilo/skills/

# Test Python build with data skills
rm -rf .kilo/
uv run prompticorn init
# Select language: python
# Verify data agent has data skills assigned
# Verify observability agent has SRE skills

# Test minimal vs verbose
rm -rf .kilo/
uv run prompticorn init --variant minimal
wc -l .kilo/agents/data/pipeline.md  # Should be ~20-50 lines

rm -rf .kilo/
uv run prompticorn init --variant verbose
wc -l .kilo/agents/data/pipeline.md  # Should be ~150-350 lines
```

---

### 📖 Step 8: Documentation (Week 3, Day 5)

**Deliverable:** Updated documentation

#### 8.1 Update Core Docs
- [ ] Update `README.md` - Add data, observability, incident agents to list
- [ ] Update `CHANGELOG.md` - Document Phase 1 additions
- [ ] Update `docs/COVERAGE_GAP_ANALYSIS.md` - Mark Phase 1 as complete

#### 8.2 Create Phase 1 Summary
- [ ] Create `docs/PHASE1_COMPLETION_REPORT.md`
  - Summary of deliverables
  - Test results
  - Known limitations
  - Recommendations for Phase 2

---

### 🚀 Step 9: Commit & PR (Week 3, Day 5)

**Deliverable:** Pull request to main

#### 9.1 Final Commit
- [ ] Run final build test
- [ ] Stage all changes: `git add -A`
- [ ] Create commit with comprehensive message

**Commit Message Template:**
```
feat: Phase 1 - Data Engineering & SRE/Observability

## Summary
Adds comprehensive support for data engineering, SRE practices, 
and incident management - the most critical gaps identified in 
coverage analysis.

## New Agents (3)
- data - Data engineering specialist
- observability - Monitoring and alerting specialist  
- incident - Incident management specialist

## New Subagents (14)
Data: pipeline, warehouse, quality, governance, streaming
Observability: metrics, logging, tracing, alerting, dashboards
Incident: triage, postmortem, runbook, oncall

## New Workflows (8)
- data-pipeline-workflow, data-quality-workflow, schema-migration-workflow
- observability-workflow, slo-sli-workflow, capacity-planning-workflow
- incident-response-workflow, postmortem-workflow

## New Skills (11)
Data: sql-optimization, dimensional-modeling, data-partitioning,
      idempotency-patterns, slowly-changing-dimensions
SRE: prometheus-query-patterns, distributed-tracing-instrumentation,
     slo-sli-definition, grafana-dashboard-design
Incident: incident-timeline-creation, root-cause-five-whys

## New Languages (4)
- PostgreSQL, BigQuery, Snowflake (SQL dialects)
- dbt (data build tool)

## Impact
- Unlocks data engineering workflows for data teams
- Enables SRE best practices for production systems
- Provides structured incident management
- 100% real content, NO placeholders

## Testing
- ✅ All builds tested (python, postgresql, bigquery, dbt)
- ✅ Language filtering verified
- ✅ Variant differentiation validated
- ✅ Content quality checked (no placeholders)
```

#### 9.2 Create Pull Request
- [ ] Push branch: `git push origin feat/phase1-data-sre-observability`
- [ ] Create PR on GitHub
- [ ] Link to `docs/COVERAGE_GAP_ANALYSIS.md` in PR description
- [ ] Link to `docs/PHASE1_EXECUTION_PLAN.md` (this file)
- [ ] Request review

---

## Success Criteria

### Quantitative
- [ ] 3 new agents created
- [ ] 14 new subagents created (all with minimal + verbose variants = 28 files)
- [ ] 8 new workflows created (minimal + verbose = 16 files)
- [ ] 11 new skills created (minimal + verbose = 22 files)
- [ ] 4 new language convention files
- [ ] 100% of content is real (no "TODO" or placeholders)
- [ ] All builds pass without errors
- [ ] Language filtering works correctly

### Qualitative
- [ ] Content is actionable and practical
- [ ] Real-world examples included
- [ ] Common pitfalls documented
- [ ] Tool recommendations provided
- [ ] External docs linked
- [ ] Follows variant differentiation strategy
- [ ] Consistent voice and quality with existing agents

---

## Risk Mitigation

### Risk: Scope Creep
**Mitigation:** Stick strictly to Phase 1 deliverables. Phase 2 items go in backlog.

### Risk: Quality Issues
**Mitigation:** 
- Use existing subagents as quality benchmarks
- Run quality checks before each commit
- Peer review before final PR

### Risk: Time Overrun
**Mitigation:**
- Track progress daily against checklist
- If behind schedule by Day 10, cut verbose variants to 100-200 lines
- Prioritize data agent > observability > incident if time runs short

### Risk: Integration Failures
**Mitigation:**
- Test builds after each major component
- Verify language mapping after each addition
- Keep build scripts running in background

---

## Progress Tracking

### Week 1 Summary
**Target:** Scaffolding + Content writing  
**Checklist Items:** Steps 1-2 (40 items)  
**Deliverables:** 31 agent files + content  

### Week 2 Summary
**Target:** Workflows + Skills  
**Checklist Items:** Steps 3-4 (38 items)  
**Deliverables:** 16 workflow files + 22 skill files  

### Week 3 Summary
**Target:** Languages + Testing + Documentation + PR  
**Checklist Items:** Steps 5-9 (35 items)  
**Deliverables:** 4 language files + docs + PR  

---

## Post-Phase 1

After Phase 1 completion, the next priorities are:

**Phase 2: Infrastructure & DevOps (1-2 weeks)**
- `infrastructure` agent
- `ci-cd` agent
- HCL language support

**Phase 3: API & Testing Enhancements (1 week)**
- `api` agent
- Contract testing, chaos engineering workflows

**Phase 4: Product Management (1 week)**
- `product` agent
- A/B testing, feature flags

---

## Notes

- All file paths are relative to repository root
- Follow existing patterns in `prompticorn/agents/code/subagents/` for examples
- Use `docs/VARIANT_DIFFERENTIATION_STRATEGY.md` as guide for content length
- Test builds frequently to catch issues early
- Commit after each major component completion

---

**Document Version:** 1.0  
**Last Updated:** 2026-04-10  
**Author:** Coverage Gap Analysis Team  
**Status:** Ready for Execution
