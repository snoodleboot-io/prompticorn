# Quick Reference by Persona

Find the right resources for your role based on your actual persona configuration.

---

## 🏗️ Architect

**Display Name:** Architect  
**Focus:** Designing scalable systems and making architectural trade-offs

**Start here:**
1. [PERSONAS.md](./PERSONAS.md) - Understand persona-based filtering
2. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Search for architecture-related content

**Primary Agents:**
- `architect` - System design and architecture planning
- `backend` - Backend systems and APIs
- `frontend` - Frontend architecture
- `data` - Data architecture and pipelines

**Secondary Agents:**
- `performance` - Performance optimization

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- scaffold, data-model, strategy, decision-log
- component-architecture, microservices-architecture
- api-design, database-selection, caching-strategy
- capacity-planning

**Key Skills:**
- architecture-documentation
- technical-decision-making
- problem-decomposition
- mermaid-erd-creation
- data-model-discovery

**Agent Locations:**
- `prompticorn/agents/architect/`
- `prompticorn/agents/backend/`
- `prompticorn/agents/frontend/`
- `prompticorn/agents/data/`

---

## 👨‍💻 Software Engineer

**Display Name:** Software Engineer (Fullstack)  
**Focus:** Building complete applications from UI to API to database

> This section covers the four software-engineer personas, which share one curated
> workflow and skill list and differ only in agent selection:
> `backend_software_engineer` (`backend`), `frontend_software_engineer`
> (`frontend`), `fullstack_software_engineer` (both), and `software_engineer` — a
> deprecated alias of the fullstack persona.

**Start here:**
1. [QUICKSTART.md](./QUICKSTART.md) - Get started quickly
2. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find code/test/refactor resources

**Primary Agents:**
- `code` - Code implementation
- `test` - Testing and QA
- `refactor` - Code refactoring
- `migration` - Dependency upgrades and migrations

**Secondary Agents:**
- `review` - Code review
- `backend` - Backend development
- `frontend` - Frontend development
- `performance` - Performance optimization
- `enforcement` - Code quality enforcement
- `atdd` - Executable acceptance criteria

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- code, testing, feature, refactor
- dependency-upgrade, boilerplate
- code-quality-maintenance, coverage-improvement-maintenance
- automated-testing

**Key Skills:**
- incremental-implementation
- code-review-practices
- testing-strategies
- debugging-methodology
- technical-debt-management
- test-aaa-structure, test-mocking-rules, test-coverage-categories

**Agent Locations:**
- `prompticorn/agents/code/`
- `prompticorn/agents/test/`
- `prompticorn/agents/refactor/`
- `prompticorn/agents/migration/`

---

## 🧪 QA / Tester

**Display Name:** QA / Tester  
**Focus:** Ensuring quality through comprehensive testing

**Start here:**
2. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find testing resources

**Primary Agents:**
- `qa-tester` - Testing strategy and automated test suites
- `test` - Testing and QA
- `review` - Code review
- `atdd` - Executable acceptance criteria

**Secondary Agents:**
- `performance` - Performance testing
- `enforcement` - Quality enforcement

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- testing, testing-strategy, performance-testing
- automated-testing, coverage-improvement-maintenance
- review, accessibility

**Key Skills:**
- testing-strategies
- test-coverage-categories
- test-aaa-structure
- test-mocking-rules
- code-review-practices
- quality-assurance

**Agent Locations:**
- `prompticorn/agents/test/`
- `prompticorn/agents/review/`
- `prompticorn/agents/qa-tester/` (specialized QA agent)

---

## 🔧 DevOps Engineer

**Display Name:** DevOps Engineer  
**Focus:** Building infrastructure as code and maintaining systems

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find DevOps/infrastructure resources
2. [ARCHITECTURE.md](./ARCHITECTURE.md) - Understand system architecture

**Primary Agents:**
- `code` - Infrastructure-as-Code
- `devops` - DevOps practices and automation
- `observability` - Monitoring, logging, tracing
- `incident` - Incident response and management

**Secondary Agents:**
- `security` - Security practices

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- cicd-pipeline, secret-management, infrastructure-as-code
- disaster-recovery, container-orchestration
- observability, incident-response, postmortem
- capacity-planning

**Key Skills:**
- performance-optimization
- debugging-methodology
- technical-communication
- continuous-improvement

**Agent Locations:**
- `prompticorn/agents/devops/`
- `prompticorn/agents/observability/`
- `prompticorn/agents/incident/`

---

## 🔐 Security Engineer

**Display Name:** Security Engineer  
**Focus:** Securing systems and meeting compliance requirements

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find security/compliance resources

**Primary Agents:**
- `security` - Security reviews and threat modeling
- `compliance` - Compliance audits (SOC2, GDPR, etc.)

**Secondary Agents:**
- `incident` - Incident response
- `review` - Security code review
- `enforcement` - Security policy enforcement

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- security-code-review, security-testing
- vulnerability-scanning, vulnerability-assessment
- threat-modeling, compliance-audit
- penetration-testing-guide
- data-encryption, authentication-authorization
- incident-response-security

**Key Skills:**
- technical-communication
- code-review-practices
- problem-decomposition

**Agent Locations:**
- `prompticorn/agents/security/`
- `prompticorn/agents/compliance/`

---

## 📊 Product Manager

**Display Name:** Product Manager  
**Focus:** Defining what to build and why

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find product/planning resources

**Primary Agents:**
- `product` - Product strategy and requirements

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- requirements-gathering, feature-prioritization
- roadmap-planning, user-research-guide
- feature-launch-checklist
- a-b-testing, analytics-setup, ux-validation

**Key Skills:**
- feature-planning
- technical-communication
- problem-decomposition

**Agent Locations:**
- `prompticorn/agents/product/`

---

## 📊 Data Engineer

**Display Name:** Data Engineer  
**Focus:** Building reliable data systems and ETL pipelines

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find data pipeline resources

**Primary Agents:**
- `code` - ETL and pipeline code
- `data` - Data pipelines, quality, infrastructure

**Secondary Agents:**
- `devops` - Data infrastructure ops
- `observability` - Data monitoring
- `performance` - Data performance

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- data-pipeline, data-quality, data-quality-monitoring
- data-model, database-selection, schema-migration
- observability, performance-testing

**Key Skills:**
- data-validation-pipelines
- data-versioning-reproducibility
- technical-decision-making
- performance-optimization
- debugging-methodology

**Agent Locations:**
- `prompticorn/agents/data/`

---

## 🤖 Data Scientist

**Display Name:** Data Scientist  
**Focus:** Building and improving ML/AI systems

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find ML/AI resources

**Primary Agents:**
- `code` - ML model code
- `mlai` - ML/AI agent for model development

**Secondary Agents:**
- `data` - Data pipelines for ML
- `test` - ML testing
- `performance` - ML performance
- `devops` - MLOps
- `observability` - ML monitoring

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- model-evaluation, hyperparameter-tuning
- model-retraining-strategy, model-serving
- production-ml-deployment
- ml-monitoring-observability, mlops-pipeline-setup
- experiment-tracking-setup
- feature-engineering-guide
- model-interpretability-guide, model-governance

**Key Skills:**
- feature-importance-analysis
- mlops-pipeline-design
- model-interpretability
- batch-vs-realtime-scoring
- hyperparameter-optimization
- cross-validation-strategies
- imbalanced-classification
- ensemble-methods, dimensionality-reduction
- anomaly-detection-techniques
- model-performance-debugging
- feature-engineering, feature-store-design
- data-validation-pipelines, time-series-preprocessing

**Agent Locations:**
- `prompticorn/agents/mlai/`
- `prompticorn/agents/data/`

---

## ✍️ Technical Writer

**Display Name:** Technical Writer  
**Focus:** Creating clear, comprehensive documentation

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find documentation resources

**Primary Agents:**
- `document` - Documentation generation and improvement

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- docs, decision-log

**Key Skills:**
- documentation-best-practices
- technical-communication

**Agent Locations:**
- `prompticorn/agents/document/`

---

## 🧭 Discipline Personas — how to read the next nine

The nine sections below cover the discipline personas added in PRO-155. They carry
three extra blocks the nine sections above do not, because selection has
consequences a persona definition does not show:

- **Subagents inherited.** `personas.yaml` never lists subagents. Subagents inherit
  their parent agent's enabled status — the build keeps "only top-level agents that
  are enabled (subagents inherit parent status)"
  (`prompticorn/prompt_builder.py`) — so selecting one agent selects *every*
  subagent underneath it, and there is no way to take the agent without them. The
  counts below are the directory listings of `prompticorn/agents/<agent>/subagents/`.
  Where that pulls in prompts a project will not use, it is said so rather than
  hidden.
- **What it generates / When to select / When NOT to.** Persona selection is
  multi-select with union semantics, so the useful question is never "is this
  persona relevant" but "does it add anything the persona next to it does not".
- **Pairs well with.** Agents shared between two personas are generated once, so
  pairing is cheap; what it costs is the subagents of the agents only one of them
  selects.

Reachable counts quoted below are the skills and workflows the persona's own agents
map in `prompticorn/configurations/agent_skill_mapping.yaml`. They are larger than
the curated "Key Skills"/"Key Workflows" lists, which name the role's core rather
than its full surface, and they exclude whatever the five universal agents add.

---

## 🚨 Site Reliability Engineer

**Display Name:** Site Reliability Engineer  
**Persona Key:** `sre`  
**Focus:** Keeping production within its error budget, and learning from it when it is not

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find reliability, incident, and observability resources
2. [PERSONAS.md](./PERSONAS.md) - Understand persona-based filtering

**Primary Agents:**
- `incident` - Incident response, triage, postmortems, and on-call processes
- `observability` - Monitoring, logging, tracing, and alerting systems
- `performance` - Bottleneck analysis and benchmarking

**Secondary Agents:**
- `devops` - Deployment, infrastructure, and cloud operations

**Subagents inherited (18):**
- `incident/` - oncall, postmortem, runbook, triage
- `observability/` - alerting, dashboards, logging, metrics, tracing
- `performance/` - benchmarking, bottleneck-analysis, optimization-strategies, profiling
- `devops/` - aws, docker, gitops, kubernetes, terraform-deployment
- **Cost:** the five `devops` subagents arrive because of one secondary agent, and
  two of them are tool-specific — `aws` and `terraform-deployment`. On GCP, or with
  Pulumi, they are dead weight you cannot deselect without giving up
  `disaster-recovery-planning` and the `capacity-planning` workflow.

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- incident-response, postmortem, slo-sli
- observability, disaster-recovery, capacity-planning
- root-cause, log-analysis
- metrics-tracking-maintenance, performance-monitoring-maintenance

**Key Skills:**
- slo-sli-definition
- incident-response-planning, incident-timeline-creation, incident-automation
- root-cause-five-whys, disaster-recovery-planning
- prometheus-query-patterns, grafana-dashboard-design
- distributed-tracing-instrumentation
- continuous-improvement, load-testing

**What it generates:** four agents plus 18 subagents, and the 33 skills and 28
workflows those four agents map. In practice: runbook and on-call prompts, an
alerting/dashboards/logging/metrics/tracing set, Prometheus and Grafana skills, and
the postmortem and root-cause workflows.

**When to select it:** you carry a pager, own SLOs and error budgets, write runbooks,
and run postmortems.

**When NOT to select it:** if you build the paved road rather than answer for the
service running on it, `platform_engineer` is the closer fit. If your reliability
work is almost entirely latency tuning, `performance_engineer` is narrower and
cheaper. If you want one combined ops role, `devops_engineer` adds `code` and
`security` and drops `performance`. Note that `sre` selects no implementation
agent — there is no `code` or `test` here — so if the same people also fix the
service, pair it with a software-engineer persona.

**Pairs well with:** `platform_engineer` (the two together are still not
`devops_engineer`: they add `performance` and `architect`, and lack `security`),
`appsec_engineer`, which supplies the `security` half of a security incident this
persona cannot reach on its own, and `ml_engineer`, which shares `devops` and
`observability`.

**Agent Locations:**
- `prompticorn/agents/incident/`
- `prompticorn/agents/observability/`
- `prompticorn/agents/performance/`
- `prompticorn/agents/devops/`

---

## ☁️ Platform Engineer

**Display Name:** Platform Engineer  
**Persona Key:** `platform_engineer`  
**Focus:** Making the paved road faster than going around it

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find infrastructure and CI/CD resources
2. [ARCHITECTURE.md](./ARCHITECTURE.md) - Understand system architecture

**Primary Agents:**
- `devops` - Deployment, infrastructure, CI/CD pipelines, and cloud operations
- `architect` - System design and technical decision making

**Secondary Agents:**
- `code` - Infrastructure-as-Code and tooling changes

**Subagents inherited (14):**
- `devops/` - aws, docker, gitops, kubernetes, terraform-deployment
- `architect/` - data-model, scaffold, task-breakdown
- `code/` - boilerplate, dependency-upgrade, feature, house-style, migration, refactor
- **Cost:** `code` is a single secondary agent that brings six subagents, all of them
  application-development prompts (`feature`, `house-style`, `boilerplate`), and
  `architect` adds `data-model` — schema design a platform team rarely owns. Nine of
  the 14 subagents are there for the two agents that are not `devops`.

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- cicd-pipeline, infrastructure-as-code, container-orchestration
- release-cycle-maintenance, secret-management
- disaster-recovery, capacity-planning
- decision-log

**Key Skills:**
- iac-best-practices, infrastructure-drift-detection
- kubernetes-resource-management, container-security-hardening
- cloud-provider-tradeoffs, cloud-iam-design, cloud-networking-design
- cloud-cost-optimization, multi-cloud-strategy
- serverless-architecture, autoscaling-strategies
- deployment-rollback-strategies, secret-management

**What it generates:** three agents plus 14 subagents, and the 38 skills and 25
workflows those agents map. It is the only persona in the library that reaches all
six cloud-strategy skills: `devops` maps `cloud-iam-design`,
`cloud-networking-design` and `cloud-cost-optimization`, while `architect` maps
`cloud-provider-tradeoffs`, `multi-cloud-strategy` and `cloud-migration-strategy`.
Every other persona reaches at most four.

**When to select it:** you own CI/CD, infrastructure as code, clusters, and the
internal developer platform other teams build on.

**When NOT to select it:** if you are paged for a service's SLOs, `sre` owns that
(`incident`, `observability`) and this persona has neither. If you want both halves
in one selection, `devops_engineer` covers `devops` + `observability` + `incident` +
`security` but has no `architect` and so loses the `cloud-provider-tradeoffs`,
`multi-cloud-strategy` and `serverless-architecture` skills.

**Pairs well with:** `sre` (shares only `devops`, so the pairing genuinely adds
reliability coverage), `ml_engineer` (shares `devops`; the Kubernetes work is the
same work), and `database_engineer` (shares `architect`).

**Agent Locations:**
- `prompticorn/agents/devops/`
- `prompticorn/agents/architect/`
- `prompticorn/agents/code/`

---

## 🛡️ Application Security Engineer

**Display Name:** Application Security Engineer  
**Persona Key:** `appsec_engineer`  
**Focus:** Finding the flaw before it ships, not after it is exploited

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find security and compliance resources

**Primary Agents:**
- `security` - Secure design, threat modeling, and vulnerability assessment
- `review` - Code, performance, and accessibility reviews

**Secondary Agents:**
- `enforcement` - Coding-standard enforcement and change requests
- `compliance` - SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS compliance

**Subagents inherited (12):**
- `security/` - compliance-auditor, review, security-architecture-reviewer, threat-model, threat-modeling-expert, vulnerability-assessment-specialist
- `review/` - accessibility, code, performance
- `compliance/` - gdpr, review, soc2
- `enforcement/` - none
- **Cost:** `security` alone brings six, with two overlapping pairs —
  `threat-model` and `threat-modeling-expert`, plus a `security/review` and a
  `compliance/review` sitting alongside the `review` agent itself. Expect
  near-duplicate prompts to choose between. `compliance` also brings `gdpr` and
  `soc2` whether or not you are in scope for either, and `review/accessibility` has
  nothing to do with security.

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- threat-modeling, security-code-review, security-testing
- vulnerability-scanning, vulnerability-assessment
- penetration-testing-guide, security-hardening-checklist
- authentication-authorization, data-encryption
- security-audit-maintenance

**Key Skills:**
- threat-identification, secure-code-review, security-architecture-review
- vulnerability-assessment
- authentication-design, authorization-patterns
- api-security, api-security-hardening
- cryptography-fundamentals, key-management
- security-testing-strategies, secret-management
- container-security-hardening

**What it generates:** four agents plus 12 subagents, and the 27 skills and 19
workflows those agents map. The curated list here is 13 skills against
`security_engineer`'s three, which is the real difference between the two: same
territory, far more of it named.

**When to select it:** your security work happens in the codebase and the pipeline —
threat models for features, secure code review, dependency and container findings,
authentication and crypto decisions.

**When NOT to select it:** this persona's agent set
(`security`, `review`, `enforcement`, `compliance`) is a **strict subset** of
`security_engineer`'s, which adds `incident`. Selecting both is identical to
selecting `security_engineer` alone, so pick one: `appsec_engineer` when the work is
code-level, `security_engineer` when you also run security incident response.

**Pairs well with:** any software-engineer persona (they already share `review` and
`enforcement`, so the pairing costs only the `security` and `compliance` subagents),
and `sre` when security incidents are handled by the on-call rotation.

**Agent Locations:**
- `prompticorn/agents/security/`
- `prompticorn/agents/review/`
- `prompticorn/agents/enforcement/`
- `prompticorn/agents/compliance/`

---

## ⚡ Performance Engineer

**Display Name:** Performance Engineer  
**Persona Key:** `performance_engineer`  
**Focus:** Making it measurably faster, with the measurement first

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find profiling and load-testing resources

**Primary Agents:**
- `performance` - Profiling, bottleneck analysis, and benchmarking

**Secondary Agents:**
- `backend` - Backend systems, APIs, and distributed architectures
- `frontend` - User interfaces for web and mobile
- `observability` - Monitoring, logging, tracing, and alerting

**Subagents inherited (17):**
- `performance/` - benchmarking, bottleneck-analysis, optimization-strategies, profiling
- `backend/` - api-design, caching, microservices, storage
- `frontend/` - accessibility, mobile, react-patterns, vue-patterns
- `observability/` - alerting, dashboards, logging, metrics, tracing
- **Cost:** `frontend` is here for a single curated skill
  (`css-performance-optimization`, which no other agent maps) and brings four
  subagents with it, including both `react-patterns` and `vue-patterns` and an
  `accessibility` prompt. The `frontend-performance` workflow does *not* depend on
  it — that is mapped to `performance` as well. On a backend-only service all four
  subagents are noise, and there is no narrower way to reach the CSS skill.

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- performance, performance-testing, frontend-performance
- performance-monitoring-maintenance
- caching-strategy
- slo-sli, observability

**Key Skills:**
- performance-optimization, load-testing
- css-performance-optimization
- distributed-caching-design
- distributed-tracing-instrumentation, prometheus-query-patterns
- sql-optimization
- slo-sli-definition
- object-storage-patterns

**What it generates:** four agents plus 17 subagents, and the 37 skills and 26
workflows those agents map. It is one of only two personas where `performance` is a
primary agent (`sre` is the other, and both arrived in PRO-155). Before them the
agent was secondary to eight personas and primary to none, so its subagents
(`profiling`, `benchmarking`, `bottleneck-analysis`, `optimization-strategies`) only
ever arrived as a side effect of some other role.

**When to select it:** someone owns latency and throughput as a brief — load tests,
flame graphs, p99 budgets — rather than as a side task during feature work.

**When NOT to select it:** if the slow thing is the database, `database_engineer`
carries the deeper set (`sql-optimization` plus `data-partitioning`,
`dimensional-modeling`, `nosql-database-selection`). If the concern is error budgets
and alerting rather than optimisation, that is `sre`. Every software-engineer persona
already has `performance` as a secondary agent, so if nobody holds the brief
full-time this persona adds mainly `observability` and the curated list.

**Pairs well with:** `sre` (shares `observability` and `performance`, so it adds
little cost and covers the alerting side), `database_engineer`, and
`frontend_software_engineer` when the latency is in the browser.

**Agent Locations:**
- `prompticorn/agents/performance/`
- `prompticorn/agents/backend/`
- `prompticorn/agents/frontend/`
- `prompticorn/agents/observability/`

---

## 🗄️ Database Engineer

**Display Name:** Database Engineer  
**Persona Key:** `database_engineer`  
**Focus:** Designing storage that survives the second year

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find data modeling and schema resources
2. [DIAGRAMS_GUIDE.md](./DIAGRAMS_GUIDE.md) - ERD and diagram conventions

**Primary Agents:**
- `data` - Data pipelines, warehouses, and data quality systems
- `architect` - System design and technical decision making

**Secondary Agents:**
- `backend` - Backend systems and data persistence layers
- `migration` - Dependency upgrades and framework migrations

**Subagents inherited (13):**
- `data/` - governance, pipeline, quality, streaming, warehouse
- `architect/` - data-model, scaffold, task-breakdown
- `backend/` - api-design, caching, microservices, storage
- `migration/` - strategy
- **Cost:** `data` is the pipeline-and-warehouse agent, so `streaming`, `warehouse`
  and `governance` arrive even for a team whose entire estate is one OLTP Postgres.
  The warehouse-shaped skills in the curated list (`dimensional-modeling`,
  `slowly-changing-dimensions`) come from the same place, and `architect/scaffold`
  is project scaffolding rather than schema work.

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- data-model, database-selection, schema-migration
- data-pipeline, data-quality, data-quality-monitoring
- migration, caching-strategy

**Key Skills:**
- managed-database-selection, nosql-database-selection
- sql-optimization, data-partitioning
- dimensional-modeling, slowly-changing-dimensions
- data-model-discovery, mermaid-erd-creation
- object-storage-patterns, message-queue-selection
- distributed-caching-design
- data-versioning-reproducibility

**What it generates:** four agents plus 13 subagents, and the 43 skills and 26
workflows those agents map — the widest reachable skill surface of the nine after
`ml_engineer` and `ai_engineer`, because `data`, `architect` and `backend` are three
of the broadest agents in the registry.

**When to select it:** someone owns schemas, indexes, query plans and migrations as
their primary work, and the storage decisions outlive the services on top of them.

**When NOT to select it:** if the work is moving and transforming data rather than
designing where it lands, `data_engineer` is the fit (`code` + `data`, with
`devops`, `observability` and `performance`). If the modelling exists to feed
training, `data_scientist` owns that. The two personas share only the `data` agent,
so they are genuinely different selections rather than variations.

**Pairs well with:** `backend_software_engineer` or `fullstack_software_engineer`
(shares `backend` and `migration`), `data_engineer` (shares `data`), and
`platform_engineer` (shares `architect`).

**Agent Locations:**
- `prompticorn/agents/data/`
- `prompticorn/agents/architect/`
- `prompticorn/agents/backend/`
- `prompticorn/agents/migration/`

---

## 🎨 UX Designer

**Display Name:** UX Designer  
**Persona Key:** `ux_designer`  
**Focus:** Designing what users can actually use, then checking that they can

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find UX, accessibility, and design-system resources

**Primary Agents:**
- `frontend` - Accessible, performant user interfaces for web and mobile
- `product` - Product strategy, requirements, roadmap planning, and metrics

**Secondary Agents:** none

**Subagents inherited (7):**
- `frontend/` - accessibility, mobile, react-patterns, vue-patterns
- `product/` - metrics-analytics-lead, requirements-analyst, roadmap-planner
- **Cost:** selecting `frontend` pulls **both** `react-patterns` and `vue-patterns`.
  A React-only team gets the Vue prompt anyway, a Vue-only team gets the React one,
  and a web-only team also gets `mobile`. This is inherent to subagent inheritance —
  the framework prompts are not separately selectable — and is the clearest example
  in the library of a persona you should pick knowing what it costs.

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- ux-validation, user-research-guide
- responsive-design, component-architecture, accessibility
- a-b-testing, feature-prioritization

**Key Skills:**
- user-needs-discovery, user-testing-methods
- ux-writing-guidelines
- component-design-systems, responsive-design-patterns
- css-performance-optimization
- success-metrics-definition, competitor-analysis

**What it generates:** two agents plus 7 subagents, and the 22 skills and 15
workflows those agents map — the smallest footprint of the nine. The
`accessibility` workflow is curated into only two personas, this one and
`qa_tester`, so a team that wants accessibility treated as design work rather than a
test pass has to select one of them deliberately.

**When to select it:** research, interaction design and design-system work is held by
someone who is not primarily writing the components.

**When NOT to select it:** if the same person designs *and* builds the UI,
`frontend_software_engineer` is the better single choice — this persona selects no
`code`, `test` or `refactor` agent, so on its own it can specify an interface but has
no implementation agent beyond the universal five. Note too that its agent set is a
**superset** of `product_manager`'s single `product` agent: selecting both adds no
agent, only the four workflows in `product_manager`'s curated list that are not in this
one: `requirements-gathering`, `roadmap-planning`, `feature-launch-checklist` and
`analytics-setup`.

**Pairs well with:** `frontend_software_engineer` (shares `frontend`, so the pairing
costs only the three `product` subagents), `product_manager`, and
`performance_engineer` when the UI is the slow part.

**Agent Locations:**
- `prompticorn/agents/frontend/`
- `prompticorn/agents/product/`

---

## 🧠 ML Engineer

**Display Name:** ML Engineer  
**Persona Key:** `ml_engineer`  
**Focus:** Getting a trained model into production and keeping it healthy there

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find MLOps and model-serving resources

**Primary Agents:**
- `mlai` - ML pipelines, training, deployment, and inference systems
- `devops` - Deployment, infrastructure, CI/CD, and cloud operations

**Secondary Agents:**
- `data` - Data pipelines and feature data
- `observability` - Monitoring, logging, tracing, and alerting

**Subagents inherited (23):**
- `mlai/` - data-preparation, deployment, ml-ethics-reviewer, ml-evaluation-expert, mlops-engineer, model-training, model-training-specialist, monitoring
- `devops/` - aws, docker, gitops, kubernetes, terraform-deployment
- `data/` - governance, pipeline, quality, streaming, warehouse
- `observability/` - alerting, dashboards, logging, metrics, tracing
- **Cost:** 23 subagents, the largest of any of the nine. `mlai` contributes eight,
  and `model-training` and `model-training-specialist` among them are training
  prompts for a role whose whole premise is shipping a model someone else trained.
  The persona definition draws that line cleanly; subagent inheritance does not
  honour it.

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- production-ml-deployment, model-serving
- mlops-pipeline-setup, ml-monitoring-observability
- model-retraining-strategy, model-governance
- model-evaluation, experiment-tracking-setup

**Key Skills:**
- ml-deployment, mlops-pipeline-design
- model-monitoring, model-evaluation
- batch-vs-realtime-scoring
- feature-store-design, data-versioning-reproducibility
- deployment-rollback-strategies, kubernetes-resource-management

**What it generates:** four agents plus 23 subagents, and the 52 skills and 37
workflows those agents map — the largest reachable surface of the nine. The
distinctive part is the pairing of `mlai` with `devops`: `ml-deployment` and
`mlops-pipeline-design` next to `kubernetes-resource-management` and
`deployment-rollback-strategies`, which is exactly the seam this role works on.

**When to select it:** models are trained elsewhere (or by the same team wearing a
different hat) and someone is responsible for serving, retraining, monitoring and
rollback in production.

**When NOT to select it:** this persona's agent set
(`mlai`, `devops`, `data`, `observability`) is a **strict subset** of
`data_scientist`'s, which adds `code`, `test` and `performance`. A data scientist who
also deploys needs no second persona; conversely a platform team that only ships
models others train should select `ml_engineer` alone and skip
`data_scientist`'s modelling skills. If the model is a hosted LLM you did not train
and will not retrain, `ai_engineer` is the right persona and shares **no agent** with
this one.

**Pairs well with:** `platform_engineer` (shares `devops`; the cluster work is the
same work), `sre` (shares `devops` and `observability`), and `data_engineer` for the
upstream feature pipelines.

**Agent Locations:**
- `prompticorn/agents/mlai/`
- `prompticorn/agents/devops/`
- `prompticorn/agents/data/`
- `prompticorn/agents/observability/`

---

## ✨ AI Engineer

**Display Name:** AI Engineer  
**Persona Key:** `ai_engineer`  
**Focus:** Composing a model you did not train into a product that behaves

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find LLM, RAG, and evaluation resources

**Primary Agents:**
- `ai` - LLM applications, RAG systems, agents, and evaluation harnesses
- `backend` - Backend systems, APIs, and distributed architectures

**Secondary Agents:**
- `architect` - System design and technical decision making
- `test` - Comprehensive tests with a coverage-first approach

**Subagents inherited (8):**
- `ai/` - none
- `backend/` - api-design, caching, microservices, storage
- `architect/` - data-model, scaffold, task-breakdown
- `test/` - strategy
- **Cost and shape:** the `ai` agent ships **no subagents at all**, so every one of
  the eight comes from the three supporting agents, and none of them is LLM-specific.
  Its depth lives in the 12 skills and 5 workflows it maps, not in delegation — there
  is no retrieval or eval specialist to hand off to the way `mlai` has
  `ml-evaluation-expert`. Low blast radius, but also no deeper bench.

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- llm-feature-build, rag-pipeline-setup
- eval-harness-setup, prompt-iteration-cycle
- api-design

**Key Skills:**
- llm-application-architecture, prompt-engineering-practices
- rag-system-design, vector-store-selection
- llm-evaluation-and-testing
- agent-tool-design, llm-safety-and-guardrails
- llm-observability
- multiagent-orchestration

**Why `ai` and not `mlai`:** the two agents split on who trained the model, and the
persona follows the split deliberately (PRO-156). `mlai` is the classical training
lifecycle — algorithm selection, feature engineering, hyperparameter optimization,
drift detection, model governance — and it delegates to eight classical-ML subagents
including `model-training-specialist` and `ml-ethics-reviewer`; its own prompt says to
route there "when the work is training a model". `ai` starts from the opposite
premise: the model is a dependency you do not control, cannot inspect and cannot
version-pin by default, and may change underneath you without a release note. That
is why evaluation and observability are in this persona's primary surface rather than
treated as follow-up work — on a non-deterministic dependency they are how you find
out anything at all. Pointing this persona at `mlai` would have dragged training
subagents into an LLM build and collapsed the distinction that justifies a separate
persona.

**What it generates:** four agents plus 8 subagents, and the 48 skills and 24
workflows those agents map. Only three pieces of content are mapped exclusively to
the `ai` agent — the `prompt-engineering-practices` skill and the `llm-feature-build`
and `prompt-iteration-cycle` workflows. The rest is deliberately reachable from
neighbouring agents as well (`rag-system-design`, `vector-store-selection` and
`rag-pipeline-setup` from `data`; `llm-observability` from `observability`;
`llm-safety-and-guardrails` from `security`; `llm-evaluation-and-testing` and
`eval-harness-setup` from `test`; `llm-application-architecture` from `architect` and
`backend`). What this persona gives you is all of it in one selection, which no other
persona does.

**When to select it:** you are building a feature on a hosted or self-hosted language
model — RAG, an agent or tool-calling loop, an eval harness — and you did not train
the model.

**When NOT to select it:** if you are fine-tuning or training, that is
`data_scientist` (training) or `ml_engineer` (serving what was trained). This persona
shares **no agent at all** with `ml_engineer`, and only `test` with `data_scientist`,
so it genuinely is a different selection rather than a variant of either. If the LLM work is one feature inside an
otherwise ordinary service, a software-engineer persona plus this one is the honest
selection — `backend` and `test` are shared, so the pairing costs little.

**Pairs well with:** `backend_software_engineer` or `fullstack_software_engineer`
(shares `backend` and `test`), `qa_tester` for the eval harness (shares `test`), and
`platform_engineer` for the cost and rate-limit side of running a model in
production.

**Agent Locations:**
- `prompticorn/agents/ai/`
- `prompticorn/agents/backend/`
- `prompticorn/agents/architect/`
- `prompticorn/agents/test/`

---

## 📋 Engineering Manager

**Display Name:** Engineering Manager  
**Persona Key:** `engineering_manager`  
**Focus:** Sequencing the work and keeping the people unblocked

**Start here:**
1. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Find planning and prioritization resources
2. [PERSONAS.md](./PERSONAS.md) - Understand persona-based filtering

**Primary Agents:**
- `product` - Product strategy, requirements, roadmap planning, and metrics
- `architect` - System design and technical decision making

**Secondary Agents:**
- `refactor` - Code structure improvement without behaviour change
- `document` - Documentation, READMEs, and changelogs

**Subagents inherited (8):**
- `product/` - metrics-analytics-lead, requirements-analyst, roadmap-planner
- `architect/` - data-model, scaffold, task-breakdown
- `refactor/` - strategy
- `document/` - strategy-for-applications
- **Cost:** `refactor` is selected largely for one skill the role lives in
  (`technical-debt-management`) and `architect` brings `data-model` and `scaffold`,
  which are hands-on design prompts a manager may never open.

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- roadmap-planning, feature-prioritization, requirements-gathering
- task-breakdown, strategy, decision-log
- multi-agent-coordination

**Key Skills:**
- team-collaboration, stakeholder-communication
- requirements-specification, roadmap-prioritization
- success-metrics-definition
- problem-decomposition, technical-decision-making
- feature-planning, post-implementation-checklist
- technical-debt-management, continuous-improvement
- documentation-best-practices

**What it generates:** four agents plus 8 subagents, and the 36 skills and 24
workflows those agents map. One caveat worth knowing: of the seven workflows listed
above, `multi-agent-coordination` is mapped to no agent this persona selects — it is
reachable only because `orchestrator` is universal and therefore always enabled.

**Earlier shape (PRO-162):** this persona first selected `plan` (primary) and
`orchestrator` (secondary). Both are universal agents, enabled for every persona
regardless of choice, so it selected nothing of its own and differentiated on
`product` + `architect` alone — a near-duplicate of picking `product_manager` and
`architect` together. It was rebuilt on `product`, `architect`, `refactor` and
`document`, which is what makes `technical-debt-management` reachable here.

**When to select it:** one person sequences the work, holds the roadmap, and argues
for debt paydown, without owning a codebase area day to day.

**When NOT to select it:** its agent set is a **superset** of both
`product_manager`'s (`product`) and `technical_writer`'s (`document`), so selecting
those alongside it adds no agent — only their curated lists. If you write
requirements full-time, `product_manager` is the more focused choice; if you own the
system design, pick `architect`, which has `backend`, `frontend` and `data` that this
persona does not. And like `ux_designer`, this persona selects no implementation
agent.

**Pairs well with:** whichever software-engineer persona the team uses (they share
`refactor`), `architect` on a larger system, and `ux_designer` or `product_manager`
when discovery is a separate seat.

**Agent Locations:**
- `prompticorn/agents/product/`
- `prompticorn/agents/architect/`
- `prompticorn/agents/refactor/`
- `prompticorn/agents/document/`

---

## 🌍 Universal Agents (Available to All Personas)

These agents are **always available** regardless of selected personas:

- **ask** - General Q&A and research
- **debug** - Troubleshooting and error resolution
- **explain** - Code walkthroughs and onboarding
- **plan** - Strategic planning and work planning
- **orchestrator** - Multi-step workflow coordination

**Agent Locations:**
- `prompticorn/agents/ask/`
- `prompticorn/agents/debug/`
- `prompticorn/agents/explain/`
- `prompticorn/agents/plan/`
- `prompticorn/agents/orchestrator/`

---

## How to Use This Guide

1. **Find your persona** above (Architect, Software Engineer, etc.)
2. **Check which agents are available** to your role
3. **Search LIBRARY_INDEX.md** for specific workflows/skills you need
4. **Browse agent directories** at `prompticorn/agents/{agent-name}/` for detailed prompts

For complete persona configuration, see: `prompticorn/personas/personas.yaml`

For persona-based filtering design, see: `planning/current/adrs/ADR-001-persona-based-filtering.md`
