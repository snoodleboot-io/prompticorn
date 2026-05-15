# prompticorn Agent → Subagent Relationships

**Updated:** April 13, 2026  
**Version:** 0.1.0

This document maps actual agent-to-subagent relationships in the codebase.

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

## Version History

| Version | Date | Agents | Subagents | Notes |
|---------|------|--------|-----------|-------|
| 0.1.0 | 2026-04-13 | 25 | 86 | Initial baseline with accurate counts |

