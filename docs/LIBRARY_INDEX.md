# prompticorn Library Index

**Last Updated:** June 21, 2026
**Status:** Current

Complete searchable catalog of all prompticorn agents, subagents, workflows, and skills.

> **Versioning:** prompticorn has no hardcoded version. The package version is sourced
> from `prompticorn/__about__.py` and injected by CI/CD at build time
> (see `.github/scripts/calculate_version.py` and `.github/workflows/ci-cd.yml`).
> Local and editable installs use the `0.0.0.dev0` placeholder.

---

## Quick Navigation

- [Agents](#agents) - 25 primary agents
- [Personas](#personas) - 12 personas (including 3 software-engineer specializations + 1 deprecated alias)
- [Universal Agents](#universal-agents) - Always available
- [Workflows](#workflows) - 100 workflows
- [Skills](#skills) - 95 skills
- [By Domain](#by-domain) - Organized by technical domain
- [Component Counts](#component-counts) - Verified inventory

---

## Agents

### All Primary Agents (25 total)

Located in `prompticorn/agents/[agent-name]/`

| Agent | Purpose | Persona Affinity |
|-------|---------|------------------|
| **architect** | System design and architecture planning | Architect |
| **ask** | General Q&A and research | Universal |
| **backend** | Backend systems, APIs, microservices | Backend/Fullstack SWE, Architect |
| **code** | Code implementation | Backend/Frontend/Fullstack SWE, DevOps Engineer, Data Engineer, Data Scientist |
| **compliance** | Compliance audits (SOC 2, GDPR, HIPAA, etc.) | Security Engineer |
| **data** | Data pipelines, warehouses, quality systems | Data Engineer, Data Scientist, Architect |
| **debug** | Troubleshooting and error resolution | Universal |
| **devops** | CI/CD, infrastructure, deployment automation | DevOps Engineer |
| **document** | Documentation generation and improvement | Technical Writer |
| **enforcement** | Code quality / standards enforcement | Backend/Frontend/Fullstack SWE, QA/Tester, Security Engineer |
| **explain** | Code walkthroughs and onboarding | Universal |
| **frontend** | Frontend architecture and UI development | Frontend/Fullstack SWE, Architect |
| **incident** | Incident response and management | DevOps Engineer, Security Engineer |
| **migration** | Dependency upgrades and framework migrations | Backend/Frontend/Fullstack SWE |
| **mlai** | ML/AI pipelines, model training, deployment | Data Scientist, DevOps Engineer |
| **observability** | Monitoring, logging, tracing, alerting | DevOps Engineer, Data Engineer, Data Scientist |
| **orchestrator** | Multi-step workflow coordination | Universal |
| **performance** | Performance optimization and benchmarking | SWE, QA/Tester, Data Engineer, Data Scientist, Architect |
| **plan** | Strategic planning and work planning | Universal |
| **product** | Product strategy, requirements, roadmaps | Product Manager |
| **qa-tester** | Quality assurance and testing strategies | QA/Tester |
| **refactor** | Code refactoring and restructuring | Backend/Frontend/Fullstack SWE |
| **review** | Code, performance, accessibility review | SWE, QA/Tester, Security Engineer |
| **security** | Security reviews, threat modeling | Security Engineer |
| **test** | Testing and QA | SWE, QA/Tester, Data Scientist |

---

## Universal Agents

**Always available** to all personas, regardless of selection:

- **ask** - General Q&A and research
- **debug** - Troubleshooting and error resolution
- **explain** - Code walkthroughs and onboarding
- **plan** - Strategic planning and work planning
- **orchestrator** - Multi-step workflow coordination

---

## Personas

**12 persona definitions** for agent/workflow/skill filtering (3 software-engineer
specializations plus a deprecated `software_engineer` alias):

| Persona | Focus | Primary Agents |
|---------|-------|----------------|
| **Software Engineer (Fullstack)** _(deprecated alias)_ | Alias for Fullstack Software Engineer | code, test, refactor, migration |
| **Backend Software Engineer** | Scalable backend systems, APIs, data persistence | code, test, refactor, migration |
| **Frontend Software Engineer** | Performant, accessible UIs for web and mobile | code, test, refactor, migration |
| **Fullstack Software Engineer** | Complete apps from UI to API to database | code, test, refactor, migration |
| **Architect** | System design, architecture, trade-offs | architect, backend, frontend, data |
| **QA / Tester** | Quality assurance, testing strategy, automation | test, review |
| **DevOps Engineer** | Infrastructure as code, deployment, CI/CD | code, devops, observability, incident |
| **Security Engineer** | Security hardening, threat modeling, compliance | security, compliance |
| **Product Manager** | Requirements, prioritization, roadmap planning | product |
| **Data Engineer** | Data pipelines, data quality, data infrastructure | code, data |
| **Data Scientist** | ML, model development, optimization | code, mlai |
| **Technical Writer** | Documentation and technical communication | document |

For detailed persona information, see: [PERSONAS.md](./PERSONAS.md)

---

## Workflows

**100 workflows** located in `prompticorn/workflows/[workflow-name]/`. Workflows are
mapped to agents via `prompticorn/configurations/agent_skill_mapping.yaml` and to
personas via `prompticorn/personas/personas.yaml`.

Representative groupings (see the source directory for the complete list):

- **Implementation:** code, feature, boilerplate, house-style, refactor, migration, scaffold
- **Testing & quality:** testing, testing-strategy, automated-testing, coverage-improvement-maintenance, code-quality-maintenance, review
- **Architecture & data:** api-design, component-architecture, microservices-architecture, database-selection, caching-strategy, data-model, data-pipeline, data-quality, schema-migration
- **DevOps & reliability:** cicd-pipeline, infrastructure-as-code, container-orchestration, deployment-automation, disaster-recovery, observability, incident-response, postmortem, capacity-planning
- **Security & compliance:** security-code-review, security-testing, vulnerability-scanning, vulnerability-assessment, threat-modeling, penetration-testing-guide, compliance-audit, data-encryption, authentication-authorization
- **ML/AI:** model-evaluation, model-serving, model-retraining-strategy, production-ml-deployment, mlops-pipeline-setup, experiment-tracking-setup, hyperparameter-tuning, ml-monitoring-observability, model-governance
- **Product:** requirements-gathering, feature-prioritization, roadmap-planning, user-research-guide, a-b-testing, analytics-setup, ux-validation, feature-launch-checklist
- **Documentation & planning:** docs, strategy, strategy-for-applications, decision-log, task-breakdown, meta, multi-agent-coordination
- **Workflow meta-patterns:** workflow-orchestration-patterns, workflow-testing-patterns, workflow-security-in-workflows, workflow-rollback-strategies, workflow-monitoring, workflow-versioning-management, and related `workflow-*` guides

```bash
# List all workflows
ls -1 prompticorn/workflows/
```

---

## Skills

**95 skills** located in `prompticorn/skills/[skill-name]/`. Skills are mapped to agents
via `prompticorn/configurations/agent_skill_mapping.yaml` (language-agnostic) with optional
language overrides in `prompticorn/configurations/language_skill_mapping.yaml`.

Representative groupings (see the source directory for the complete list):

- **Engineering practice:** incremental-implementation, code-review-practices, technical-debt-management, quality-assurance, problem-decomposition, post-implementation-checklist, feature-planning
- **Testing:** testing-strategies, test-aaa-structure, test-mocking-rules, test-coverage-categories, test-data-strategies, flaky-test-remediation, mutation-testing, load-testing
- **Architecture & data modeling:** architecture-documentation, data-model-discovery, mermaid-erd-creation, dimensional-modeling, slowly-changing-dimensions, nosql-database-selection, data-partitioning, distributed-caching-design
- **ML/AI:** feature-importance-analysis, mlops-pipeline-design, model-interpretability, model-evaluation, model-monitoring, model-performance-debugging, hyperparameter-optimization, cross-validation-strategies, imbalanced-classification, ensemble-methods, dimensionality-reduction, anomaly-detection-techniques, batch-vs-realtime-scoring, time-series-preprocessing, feature-engineering, feature-store-design
- **Security:** secure-code-review, security-architecture-review, threat-modeling, threat-identification, vulnerability-assessment, api-security, api-security-hardening, authentication-design, authorization-patterns, cryptography-fundamentals, key-management, container-security-hardening, secret-management
- **DevOps & observability:** iac-best-practices, infrastructure-drift-detection, deployment-rollback-strategies, kubernetes-resource-management, slo-sli-definition, prometheus-query-patterns, grafana-dashboard-design, distributed-tracing-instrumentation, incident-automation, incident-response-planning, incident-timeline-creation
- **Frontend:** component-design-systems, responsive-design-patterns, state-management-architecture, css-performance-optimization, ux-writing-guidelines
- **Product:** requirements-specification, roadmap-prioritization, success-metrics-definition, user-needs-discovery, user-testing-methods, competitor-analysis, product-analytics-setup, launch-readiness-checklist, stakeholder-communication
- **Communication & continuous improvement:** technical-communication, technical-decision-making, documentation-best-practices, team-collaboration, continuous-improvement, debugging-methodology, root-cause-five-whys, performance-optimization

```bash
# List all skills
ls -1 prompticorn/skills/
```

---

## Supported Languages

prompticorn renders language-standard source-tree layouts and conventions for
**29 languages** (defined in `prompticorn/configurations/source_layouts.yaml`,
rendered to `.claude/conventions/languages/`):

c, clojure, cpp, csharp, dart, elixir, elm, fsharp, golang, groovy, haskell, html,
java, javascript, julia, kotlin, lua, objc, php, python, r, ruby, rust, scala,
shell, sql, swift, terraform, typescript

> Note: `prompticorn/configurations/languages.yaml` lists the 26 languages exposed for
> CLI language selection/validation; the 29-language set above reflects every language
> with a rendered source-tree layout and convention file.

---

## Supported AI Tools

prompticorn generates assistant configurations for **5 AI coding tools**:

- **Kilo** (`.kilo/`)
- **Cline** (`.cline/`)
- **Claude** (`.claude/`)
- **Cursor** (`.cursor/`)
- **Copilot** (`.github/copilot` / Copilot config)

---

## By Domain

### Backend & APIs
- **Agents:** backend, code, performance
- **Use Cases:** REST APIs, GraphQL, microservices, caching, database selection

### Frontend & UI
- **Agents:** frontend, code, performance
- **Use Cases:** React, Vue.js, mobile apps, accessibility, state management

### DevOps & Infrastructure
- **Agents:** devops, observability, incident, code
- **Use Cases:** CI/CD, Docker, Kubernetes, Terraform, monitoring, incident response

### Data Engineering
- **Agents:** data, code, performance, observability
- **Use Cases:** ETL pipelines, data quality, data warehouses, streaming

### ML & AI
- **Agents:** mlai, data, code
- **Use Cases:** Model training, feature engineering, model deployment, monitoring

### Security & Compliance
- **Agents:** security, compliance, review, incident
- **Use Cases:** Threat modeling, vulnerability assessment, code review, audits

### Testing & QA
- **Agents:** test, qa-tester, review, performance
- **Use Cases:** Unit testing, integration testing, load testing, quality assurance

### Documentation
- **Agents:** document, explain
- **Use Cases:** Technical writing, code walkthroughs, API documentation

---

## Component Counts

| Type | Count | Source of Truth |
|------|-------|-----------------|
| **Primary Agents** | 25 | `prompticorn/agents/` (excluding `core/`) |
| **Subagents** | 82 | `prompticorn/agents/*/subagents/*` |
| **Workflows** | 100 | `prompticorn/workflows/` |
| **Skills** | 95 | `prompticorn/skills/` |
| **Personas** | 12 | `prompticorn/personas/personas.yaml` |
| **Languages** | 29 | `prompticorn/configurations/source_layouts.yaml` |
| **AI Tools** | 5 | Kilo, Cline, Claude, Cursor, Copilot |

```bash
# Reproduce the counts
ls -1 prompticorn/agents/ | grep -v '^core$' | wc -l                          # 25 agents
find prompticorn/agents -mindepth 3 -maxdepth 3 -type d -path '*/subagents/*' | wc -l   # 82 subagents
ls -1 prompticorn/workflows/ | wc -l                                          # 100 workflows
ls -1 prompticorn/skills/ | wc -l                                             # 95 skills
grep -c 'display_name:' prompticorn/personas/personas.yaml                    # 12 personas
```

---

## How to Use This Index

### Search by Agent Name
Find the agent in the [Agents](#agents) table above and check its location:
`prompticorn/agents/[agent-name]/`

### Search by Persona
1. Find your role in [Personas](#personas)
2. Check which agents are available
3. Browse those agent directories

### Search by Domain
1. Find your domain in [By Domain](#by-domain)
2. Check recommended agents
3. Explore agent subdirectories for subagents

### Find Subagents
- Subagents located in: `prompticorn/agents/[agent-name]/subagents/[subagent-name]/`
- Each subagent provides `minimal/` and `verbose/` variants

---

## File Locations

### Agent Prompts
- Location: `prompticorn/agents/[agent-name]/`
- Example: `prompticorn/agents/backend/`

### Subagents
- Location: `prompticorn/agents/[agent-name]/subagents/[subagent-name]/[minimal|verbose]/`
- Example: `prompticorn/agents/backend/subagents/api-design/minimal/`

### Persona Configuration
- Location: `prompticorn/personas/personas.yaml`
- Defines which agents/workflows/skills are available per persona

### Agent → Skill / Workflow Mapping
- Location: `prompticorn/configurations/agent_skill_mapping.yaml`

---

## Related Documentation

- **PERSONAS.md** - Persona-based filtering system
- **RELATIONSHIPS_MATRIX.md** - Agent → subagent and agent → skill/workflow relationships
- **ARCHITECTURE.md** - System architecture overview
