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

**Display Name:** Software Engineer  
**Focus:** Writing, maintaining, and testing application code

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
- `test` - Testing and QA
- `review` - Code review

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
- `mlai` - ML infrastructure
- `data` - Data infrastructure

**Key Workflows:**
Search LIBRARY_INDEX.md for:
- cicd-pipeline, secret-management, infrastructure-as-code
- disaster-recovery, container-orchestration
- observability, incident-response, postmortem
- capacity-planning, deployment-automation

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
- feature-prioritization-workflow

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
- `mlai` - ML data infrastructure
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
- feature-engineering-guide, feature-store-design
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
