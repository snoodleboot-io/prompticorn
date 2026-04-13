# Promptosaurus Content Relationships Matrix

**Updated:** April 10, 2026

This document maps how agents, subagents, workflows, and skills relate to each other.

---

## Agent → Subagent Mapping

### Backend Agent
- **Subagents:**
  - api-design → Skill: api-versioning-strategy
  - microservices → Skill: microservices-communication-patterns
  - caching → Skill: distributed-caching-design
  - storage → Skill: nosql-database-selection

### Frontend Agent
- **Subagents:**
  - react-patterns → Skill: state-management-architecture
  - vue-patterns → Skill: state-management-architecture
  - mobile → Skill: responsive-design-patterns
  - accessibility → Skill: accessibility

### DevOps Agent
- **Subagents:**
  - docker → Skill: container-security-hardening
  - kubernetes → Skill: kubernetes-resource-management
  - aws → Skill: aws
  - terraform-deployment → Skill: iac-best-practices
  - gitops → Skill: gitops

### Data Agent
- **Subagents:**
  - pipeline → Workflow: data-pipeline, Skill: sql-optimization
  - warehouse → Skill: dimensional-modeling
  - quality → Workflow: data-quality, Skill: data-quality
  - governance → Skill: data-governance
  - streaming → Skill: streaming-patterns

### Observability Agent
- **Subagents:**
  - metrics → Skill: prometheus-patterns
  - logging → Workflow: logging-setup
  - tracing → Skill: distributed-tracing-instrumentation
  - alerting → Workflow: alert-configuration
  - dashboards → Skill: grafana-dashboard-design

### Incident Agent
- **Subagents:**
  - triage → Workflow: incident-response
  - postmortem → Workflow: postmortem
  - runbook → Subagent: runbook (reference)
  - oncall → Subagent: oncall (reference)

### Testing Agent
- **Subagents:**
  - unit-testing → Skill: test-data-strategies
  - integration-testing → Workflow: automated-testing
  - e2e-testing → Workflow: e2e-testing
  - load-testing → Skill: load-testing

### ML/AI Agent
- **Subagents:**
  - data-preparation → Skill: feature-engineering
  - model-training → Skill: model-evaluation
  - deployment → Skill: ml-deployment
  - monitoring → Skill: model-monitoring

### Performance Agent
- **Subagents:**
  - profiling → Workflow: performance-testing
  - bottleneck-analysis → Skill: bottleneck-analysis
  - optimization-strategies → Skill: optimization-strategies
  - benchmarking → Skill: benchmarking

---

## Workflow → Agent/Skill Mapping

### Backend Workflows
| Workflow | Agent | Skills | Related Subagents |
|----------|-------|--------|-------------------|
| api-design-workflow | Backend | api-versioning | api-design |
| microservices-architecture-workflow | Backend | microservices-communication | microservices |
| caching-strategy-workflow | Backend | distributed-caching | caching |
| database-selection-workflow | Backend | nosql-selection | storage |

### Frontend Workflows
| Workflow | Agent | Skills | Related Subagents |
|----------|-------|--------|-------------------|
| component-architecture-workflow | Frontend | component-design-systems | react-patterns, vue-patterns |
| state-management-workflow | Frontend | state-management-architecture | react-patterns, vue-patterns |
| frontend-performance-workflow | Frontend | css-optimization | accessibility |
| responsive-design-workflow | Frontend | responsive-design-patterns | mobile, accessibility |

### DevOps Workflows
| Workflow | Agent | Skills | Related Subagents |
|----------|-------|--------|-------------------|
| cicd-pipeline-workflow | DevOps | deployment-strategies | gitops |
| container-orchestration-workflow | DevOps | kubernetes-management | docker, kubernetes |
| infrastructure-as-code-workflow | DevOps | iac-best-practices | terraform-deployment |
| disaster-recovery-workflow | DevOps | deployment-rollback | aws |

### Testing Workflows
| Workflow | Agent | Skills | Related Subagents |
|----------|-------|--------|-------------------|
| testing-strategy-workflow | Testing | test-data-strategies | unit-testing |
| automated-testing-workflow | Testing | flaky-test-remediation | integration-testing, e2e-testing |
| performance-testing-workflow | Testing | load-testing | load-testing |
| security-testing-workflow | Testing | mutation-testing | unit-testing |

### Security Workflows
| Workflow | Agent | Skills | Related Subagents |
|----------|-------|--------|-------------------|
| authentication-authorization-workflow | Security | api-security | - |
| data-encryption-workflow | Security | key-management | - |
| vulnerability-assessment-workflow | Security | threat-modeling | - |
| compliance-audit-workflow | Security | compliance-automation | - |

### Workflows
| Workflow | Agent | Skills | Related Subagents |
|----------|-------|--------|-------------------|
| data-pipeline-workflow | Data | sql-optimization | pipeline |
| data-quality-workflow | Data | data-quality | quality |
| schema-migration-workflow | Data | dimensional-modeling | warehouse |
| observability-workflow | Observability | prometheus-patterns | metrics |
| slo-sli-workflow | Observability | slo-sli-definition | alerting, dashboards |
| capacity-planning-workflow | Observability | monitoring-strategy | metrics |
| incident-response-workflow | Incident | incident-timeline | triage |
| postmortem-workflow | Incident | root-cause-five-whys | postmortem |

---

## Skill Dependency Graph

### Backend Skills
```
api-versioning-strategy
  ↓ (requires understanding of)
microservices-communication-patterns
  ↓ (combined with)
distributed-caching-design
  ↓ (informs)
nosql-database-selection
```

### Frontend Skills
```
component-design-systems
  ↓ (enables)
state-management-architecture
  ↓ (optimized by)
css-performance-optimization
  ↓ (applies to)
responsive-design-patterns
```

### DevOps Skills
```
container-security-hardening
  ↓ (orchestrated by)
kubernetes-resource-management
  ↓ (defined in)
iac-best-practices
  ↓ (deployed via)
deployment-rollback-strategies
  ↓ (detected by)
infrastructure-drift-detection
```

### Testing Skills
```
test-data-strategies
  ↓ (used in)
flaky-test-remediation
  ↓ (verified by)
mutation-testing
  ↓ (validated through)
load-testing
```

### ML/AI Skills
```
feature-engineering
  ↓ (leads to)
model-evaluation
  ↓ (enables)
ml-deployment
  ↓ (monitored by)
model-monitoring
```

### Security Skills
```
threat-modeling
  ↓ (informs)
api-security
  ↓ (requires)
key-management
  ↓ (enforced by)
compliance-automation
  ↓ (responds to)
incident-automation
```

---

## Cross-Domain Relationships

### Backend ↔ DevOps
- **api-design-workflow** → **cicd-pipeline-workflow**
- **microservices-architecture-workflow** → **container-orchestration-workflow**
- API security → Container security

### Backend ↔ Testing
- **api-design-workflow** → **testing-strategy-workflow**
- **microservices-communication** → **performance-testing-workflow**

### Frontend ↔ Testing
- **component-architecture-workflow** → **automated-testing-workflow**
- **responsive-design-workflow** → **e2e-testing-workflow**

### Data ↔ Observability
- **data-pipeline-workflow** → **observability-workflow**
- Data quality → Monitoring alerts

### Testing ↔ Observability
- **performance-testing-workflow** → **slo-sli-workflow**
- Load testing validates SLOs

### All Domains → Incident
- **incident-response-workflow** (universal incident handling)
- **postmortem-workflow** (cross-domain learning)

### All Domains → Security
- **security-testing-workflow** (test integration point)
- **data-encryption-workflow** (data protection)
- **api-security** (endpoint protection)

---

## Use Case Journeys

### Building a Production Backend Service
1. **Backend** agent → api-design-workflow
2. **Backend** subagent: api-design
3. Skills: api-versioning-strategy
4. → **Testing** agent → testing-strategy-workflow
5. → **DevOps** agent → cicd-pipeline-workflow
6. → **Observability** agent → observability-workflow
7. → **Security** workflows for hardening

### Scaling a Microservices System
1. **Backend** agent → microservices-architecture-workflow
2. **DevOps** agent → container-orchestration-workflow
3. **DevOps** subagent: kubernetes
4. Skills: kubernetes-resource-management
5. → **Performance** agent for optimization
6. → **Observability** agent → capacity-planning-workflow

### Incident Response & Learning
1. **Incident** agent → incident-response-workflow
2. **Incident** subagent: triage
3. Skills: incident-timeline-creation
4. → incident-response-workflow completion
5. → postmortem-workflow
6. Skills: root-cause-five-whys
7. → Share learnings with relevant domain agents

### Data Platform Development
1. **Data** agent → data-pipeline-workflow
2. **Data** subagent: pipeline
3. Skills: sql-optimization, idempotency-patterns
4. → **Data** subagent: quality
5. → **Data** subagent: warehouse
6. → **Observability** agent for data monitoring

### Frontend Application Development
1. **Frontend** agent → component-architecture-workflow
2. **Frontend** subagent: react-patterns or vue-patterns
3. Skills: component-design-systems
4. → state-management-workflow
5. → frontend-performance-workflow
6. → responsive-design-workflow
7. → **Testing** agent → automated-testing-workflow

---

## Integration Points

### By Agent Pair

| Agent Pair | Integration | Artifact |
|-----------|-------------|----------|
| Backend ↔ Frontend | API contract | api-design-workflow |
| Backend ↔ DevOps | Deployment | cicd-pipeline-workflow |
| Backend ↔ Testing | Test coverage | testing-strategy-workflow |
| DevOps ↔ Observability | Monitoring setup | observability-workflow |
| Data ↔ Testing | Data validation | data-quality-workflow |
| Testing ↔ Observability | SLO validation | slo-sli-workflow |
| Any ↔ Incident | Incident response | incident-response-workflow |
| Any ↔ Security | Security hardening | security workflows |

### By Workflow Group

| Group | Entry Point | Dependency | Exit Point |
|-------|-------------|----------|-----------|
| Architecture | API/Component workflows | Design skills | Implementation |
| Implementation | Backend/Frontend workflows | Development skills | Deployment |
| Deployment | DevOps workflows | Infrastructure skills | Operations |
| Operations | Observability workflows | Monitoring skills | Incident response |
| Crisis | Incident workflows | Response skills | Postmortem |
| Learning | Postmortem workflow | Analysis skills | Architecture updates |

---

## Content Reusability Matrix

### High Reuse (Used in 3+ contexts)
- api-versioning-strategy (backend, testing, security)
- state-management-architecture (frontend, testing, ml)
- incident-timeline-creation (all domains)
- distributed-tracing-instrumentation (backend, devops, observability)

### Medium Reuse (Used in 2 contexts)
- container-security-hardening (devops, security)
- feature-engineering (ml, data)
- load-testing (testing, performance)
- threat-modeling (security, all domains)

### Specialized (Domain-specific)
- responsive-design-patterns (frontend only)
- model-monitoring (ml/ai only)
- dimensional-modeling (data only)
- 5-whys root cause (incident only)

---

## Recommended Reading Order by Role

### Backend Developer
1. Backend agent
2. api-design-workflow
3. microservices-communication-patterns skill
4. caching-strategy-workflow
5. database-selection-workflow

### Frontend Developer
1. Frontend agent
2. component-architecture-workflow
3. state-management-workflow
4. css-performance-optimization skill
5. responsive-design-workflow

### DevOps Engineer
1. DevOps agent
2. cicd-pipeline-workflow
3. container-orchestration-workflow
4. infrastructure-as-code-workflow
5. deployment-rollback-strategies skill

### SRE
1. Observability agent
2. slo-sli-workflow
3. capacity-planning-workflow
4. Incident agent
5. threat-modeling skill

### Data Engineer
1. Data agent
2. data-pipeline-workflow
3. data-quality-workflow
4. dimensional-modeling skill
5. sql-optimization skill

### QA/Test Engineer
1. Testing agent
2. testing-strategy-workflow
3. automated-testing-workflow
4. performance-testing-workflow
5. flaky-test-remediation skill

---

## Version Control

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | April 10, 2026 | Initial relationships matrix for Development 1 + Development 2 |

---

**Use this matrix to navigate between related content and understand how different parts of the library work together.**
