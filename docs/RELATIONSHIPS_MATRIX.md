# prompticorn Agent Relationships Matrix

**Updated:** June 21, 2026
**Status:** Current

This document maps actual relationships in the codebase:

1. **Agent → Subagent** — derived from `prompticorn/agents/*/subagents/`
2. **Agent → Skills / Workflows** — derived from `prompticorn/configurations/agent_skill_mapping.yaml`

> Package version is dynamic (sourced from `prompticorn/__about__.py`, CI-injected); it
> is intentionally not pinned in this document.

---

## Agent → Subagent Mapping

### architect
**Location:** `prompticorn/agents/architect/subagents/`
- **data-model** - Database schema and data model design
- **scaffold** - Project scaffolding and architecture setup
- **task-breakdown** - Feature decomposition and planning

### ask
**Location:** `prompticorn/agents/ask/subagents/`
- **decision-log** - Recording architectural and technical decisions
- **docs** - Documentation generation and improvement
- **testing** - Testing strategies and approaches

### backend
**Location:** `prompticorn/agents/backend/subagents/`
- **api-design** - REST, GraphQL, gRPC API patterns
- **caching** - Multi-level caching strategies
- **microservices** - Service boundaries and communication
- **storage** - SQL/NoSQL database selection

### code
**Location:** `prompticorn/agents/code/subagents/`
- **boilerplate** - Code template generation
- **dependency-upgrade** - Dependency management and upgrades
- **feature** - Feature implementation guidance
- **house-style** - Code style enforcement
- **migration** - Framework/library migrations
- **refactor** - Code refactoring strategies

### compliance
**Location:** `prompticorn/agents/compliance/subagents/`
- **gdpr** - GDPR compliance guidance
- **review** - Compliance code review
- **soc2** - SOC 2 compliance requirements

### data
**Location:** `prompticorn/agents/data/subagents/`
- **governance** - Data governance and lineage
- **pipeline** - ETL/ELT pipeline design
- **quality** - Data quality frameworks
- **streaming** - Real-time stream processing
- **warehouse** - Data warehouse architecture

### debug
**Location:** `prompticorn/agents/debug/subagents/`
- **log-analysis** - Log parsing and analysis
- **root-cause** - Root cause analysis
- **rubber-duck** - Guided problem articulation

### devops
**Location:** `prompticorn/agents/devops/subagents/`
- **aws** - AWS infrastructure design
- **docker** - Container optimization and security
- **gitops** - GitOps deployment automation
- **kubernetes** - Orchestration and resource management
- **terraform-deployment** - Infrastructure as Code

### document
**Location:** `prompticorn/agents/document/subagents/`
- **strategy-for-applications** - Application documentation strategy

### enforcement
**Location:** `prompticorn/agents/enforcement/`
- **No subagents** - Core agent only

### explain
**Location:** `prompticorn/agents/explain/subagents/`
- **strategy** - Code explanation and walkthroughs

### frontend
**Location:** `prompticorn/agents/frontend/subagents/`
- **accessibility** - WCAG compliance and inclusive design
- **mobile** - React Native and mobile development
- **react-patterns** - React hooks and state management
- **vue-patterns** - Vue.js composition patterns

### incident
**Location:** `prompticorn/agents/incident/subagents/`
- **oncall** - On-call rotation and escalation
- **postmortem** - Blameless postmortem facilitation
- **runbook** - Incident runbook creation
- **triage** - Rapid incident severity assessment

### migration
**Location:** `prompticorn/agents/migration/subagents/`
- **strategy** - Migration planning and execution

### mlai
**Location:** `prompticorn/agents/mlai/subagents/`
- **data-preparation** - Feature engineering and cleaning
- **deployment** - Model serving and inference
- **ml-ethics-reviewer** - Ethical ML and responsible AI
- **ml-evaluation-expert** - Model evaluation and validation
- **mlops-engineer** - MLOps deployment and infrastructure
- **model-training** - Algorithm selection and tuning
- **model-training-specialist** - Advanced training techniques
- **monitoring** - Drift detection and retraining

### observability
**Location:** `prompticorn/agents/observability/subagents/`
- **alerting** - Alert design and tuning
- **dashboards** - Dashboard design and visualization
- **logging** - Log aggregation and analysis
- **metrics** - Prometheus and metrics collection
- **tracing** - Distributed tracing instrumentation

### orchestrator
**Location:** `prompticorn/agents/orchestrator/subagents/`
- **devops** - DevOps workflow coordination
- **maintenance** - Maintenance workflow management
- **meta** - Multi-step task coordination
- **pr-description** - Pull request description generation

### performance
**Location:** `prompticorn/agents/performance/subagents/`
- **benchmarking** - Performance baseline and comparison
- **bottleneck-analysis** - Hotspot identification
- **optimization-strategies** - Caching and algorithm optimization
- **profiling** - CPU and memory profiling

### plan
**Location:** `prompticorn/agents/plan/`
- **No subagents** - Core agent only

### product
**Location:** `prompticorn/agents/product/subagents/`
- **metrics-analytics-lead** - KPIs, OKRs, analytics
- **requirements-analyst** - Requirements gathering and user stories
- **roadmap-planner** - Strategic roadmap planning

### qa-tester
**Location:** `prompticorn/agents/qa-tester/subagents/`
- **e2e-testing** - End-to-end user journey testing
- **integration-testing** - Multi-component testing
- **load-testing** - Performance and stress testing
- **unit-testing** - Unit test strategies and patterns

### refactor
**Location:** `prompticorn/agents/refactor/subagents/`
- **strategy** - Code refactoring strategy

### review
**Location:** `prompticorn/agents/review/subagents/`
- **accessibility** - Accessibility code review
- **code** - General code review
- **performance** - Performance code review

### security
**Location:** `prompticorn/agents/security/subagents/`
- **compliance-auditor** - OWASP, GDPR, HIPAA compliance
- **review** - Security code review
- **security-architecture-reviewer** - Architecture security review
- **threat-model** - Threat modeling
- **threat-modeling-expert** - Advanced threat modeling (STRIDE)
- **vulnerability-assessment-specialist** - Vulnerability scanning and remediation

### test
**Location:** `prompticorn/agents/test/subagents/`
- **strategy** - Testing strategy and approach

---

## Summary Statistics

| Agent | Subagent Count |
|-------|----------------|
| architect | 3 |
| ask | 3 |
| backend | 4 |
| code | 6 |
| compliance | 3 |
| data | 5 |
| debug | 3 |
| devops | 5 |
| document | 1 |
| enforcement | 0 |
| explain | 1 |
| frontend | 4 |
| incident | 4 |
| migration | 1 |
| mlai | 8 |
| observability | 5 |
| orchestrator | 4 |
| performance | 4 |
| plan | 0 |
| product | 3 |
| qa-tester | 4 |
| refactor | 1 |
| review | 3 |
| security | 6 |
| test | 1 |
| **TOTAL** | **82** |

---

## Agent → Skills & Workflows

Source of truth: `prompticorn/configurations/agent_skill_mapping.yaml` (language-agnostic
base mappings; rare language-specific overrides live in `language_skill_mapping.yaml`).

> Note: the mapping file keys agents by name. The `plan` universal agent is keyed as
> `planning` in the mapping file, and `enforcement` (which has no subagents) still has
> skill/workflow mappings.

### architect
- **Skills:** architecture-documentation, data-model-discovery, feature-planning, mermaid-erd-creation, post-implementation-checklist, problem-decomposition, technical-communication, technical-decision-making
- **Workflows:** architecture-documentation, data-model, decision-log, scaffold, strategy, task-breakdown

### ask
- **Skills:** documentation-best-practices, technical-communication, test-aaa-structure, test-mocking-rules, testing-strategies
- **Workflows:** decision-log, docs, testing

### backend
- **Skills:** architecture-documentation, code-review-practices, data-model-discovery, data-validation-pipelines, incremental-implementation, performance-optimization
- **Workflows:** api-design, code, data-model, performance, review

### code
- **Skills:** code-review-practices, feature-planning, incremental-implementation, post-implementation-checklist, quality-assurance, technical-debt-management, test-coverage-categories
- **Workflows:** boilerplate, code, feature, house-style, refactor, testing

### compliance
- **Skills:** documentation-best-practices, quality-assurance, technical-communication
- **Workflows:** compliance-audit, security-hardening-checklist, workflow-compliance-patterns

### data
- **Skills:** architecture-documentation, data-model-discovery, data-validation-pipelines, data-versioning-reproducibility, feature-store-design
- **Workflows:** data-model, data-quality-monitoring, experiment-tracking-setup, workflow-versioning-management

### debug
- **Skills:** debugging-methodology, problem-decomposition, technical-communication
- **Workflows:** debugging-methodology, log-analysis, root-cause

### devops
- **Skills:** continuous-improvement, documentation-best-practices, technical-decision-making
- **Workflows:** dependency-scanning, secret-management, workflow-monitoring, workflow-orchestration-patterns, workflow-rollback-strategies

### document
- **Skills:** architecture-documentation, documentation-best-practices, mermaid-erd-creation, technical-communication
- **Workflows:** docs, strategy-for-applications, workflow-documentation-patterns

### enforcement
- **Skills:** code-review-practices, quality-assurance, technical-debt-management
- **Workflows:** code, house-style, review

### explain
- **Skills:** architecture-documentation, documentation-best-practices, technical-communication
- **Workflows:** docs, strategy

### frontend
- **Skills:** code-review-practices, incremental-implementation, performance-optimization, testing-strategies
- **Workflows:** accessibility, code, testing, ux-validation

### incident
- **Skills:** continuous-improvement, debugging-methodology, problem-decomposition, technical-communication
- **Workflows:** incident-response-security, log-analysis, root-cause

### migration
- **Skills:** incremental-implementation, problem-decomposition, technical-debt-management, technical-decision-making
- **Workflows:** dependency-upgrade, migration, strategy, workflow-migration-patterns

### mlai
- **Skills:** anomaly-detection-techniques, batch-vs-realtime-scoring, cross-validation-strategies, data-validation-pipelines, data-versioning-reproducibility, dimensionality-reduction, ensemble-methods, feature-importance-analysis, feature-store-design, hyperparameter-optimization, imbalanced-classification, mlops-pipeline-design, model-interpretability, model-performance-debugging, time-series-preprocessing
- **Workflows:** experiment-tracking-setup, feature-engineering-guide, hyperparameter-tuning, ml-monitoring-observability, mlops-pipeline-setup, model-evaluation, model-governance, model-interpretability-guide, model-retraining-strategy, model-serving, production-ml-deployment

### observability
- **Skills:** anomaly-detection-techniques, continuous-improvement, debugging-methodology, performance-optimization
- **Workflows:** analytics-setup, log-analysis, ml-monitoring-observability, performance, workflow-monitoring

### orchestrator
- **Skills:** feature-planning, problem-decomposition, team-collaboration, technical-decision-making
- **Workflows:** meta, multi-agent-coordination, task-breakdown, workflow-orchestration-patterns

### performance
- **Skills:** continuous-improvement, debugging-methodology, performance-optimization, problem-decomposition
- **Workflows:** performance, workflow-performance-optimization, workflow-scaling-patterns

### plan (mapped as `planning`)
- **Skills:** architecture-documentation, feature-planning, problem-decomposition, technical-communication, technical-decision-making
- **Workflows:** decision-log, feature-prioritization, requirements-gathering, roadmap-planning, task-breakdown

### product
- **Skills:** feature-planning, problem-decomposition, team-collaboration, technical-communication
- **Workflows:** a-b-testing, analytics-setup, feature-launch-checklist, feature-prioritization, requirements-gathering, roadmap-planning, user-research-guide

### qa-tester
- **Skills:** code-review-practices, quality-assurance, test-aaa-structure, test-coverage-categories, test-mocking-rules, testing-strategies
- **Workflows:** review, testing, workflow-testing-patterns

### refactor
- **Skills:** code-review-practices, continuous-improvement, incremental-implementation, quality-assurance, technical-debt-management
- **Workflows:** code, refactor, strategy

### review
- **Skills:** code-review-practices, performance-optimization, quality-assurance, technical-communication, technical-debt-management
- **Workflows:** accessibility, performance, review, security-code-review

### security
- **Skills:** code-review-practices, problem-decomposition, quality-assurance, technical-decision-making
- **Workflows:** penetration-testing-guide, security-code-review, security-hardening-checklist, security-testing, threat-modeling, vulnerability-scanning, workflow-security-in-workflows

### test
- **Skills:** incremental-implementation, quality-assurance, test-aaa-structure, test-coverage-categories, test-mocking-rules, testing-strategies
- **Workflows:** strategy, testing, workflow-testing-patterns

---

## Subagent Variants

**All subagents provide two variants:**
- **minimal/** - Quick reference, concise guidance
- **verbose/** - Comprehensive details, examples, anti-patterns

**Location Pattern:**
```
prompticorn/agents/[agent-name]/subagents/[subagent-name]/[minimal|verbose]/prompt.md
```

**Example:**
```
prompticorn/agents/backend/subagents/api-design/minimal/prompt.md
prompticorn/agents/backend/subagents/api-design/verbose/prompt.md
```

---

## How to Use This Reference

### Find Subagents for an Agent
1. Locate agent name in the list above
2. Check its subagent list
3. Navigate to: `prompticorn/agents/[agent-name]/subagents/[subagent-name]/`

### Verify Subagent Existence
```bash
# List all subagents for an agent
ls -1 prompticorn/agents/backend/subagents/

# List all agents with subagents
find prompticorn/agents -type d -name "subagents"
```

### Count Total Subagents
```bash
# Count all subagent directories
find prompticorn/agents -type d -mindepth 3 -maxdepth 3 -path "*/subagents/*" | wc -l
# Output: 82
```

---

## Related Documentation

- **PERSONAS.md** - Persona-based agent filtering
- **LIBRARY_INDEX.md** - Complete agent catalog
- **ARCHITECTURE.md** - System architecture overview

---

## Inventory History

| Date | Agents | Subagents | Skills | Workflows | Notes |
|------|--------|-----------|--------|-----------|-------|
| 2026-06-21 | 25 | 82 | 95 | 100 | Refreshed to current reality; added agent → skills/workflows mappings |

