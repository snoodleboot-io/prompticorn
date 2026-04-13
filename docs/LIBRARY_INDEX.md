# Promptosaurus Library Index

**Version:** 0.1.0  
**Last Updated:** April 13, 2026  
**Status:** Current

Complete searchable catalog of all Promptosaurus agents, workflows, and skills.

---

## Quick Navigation

- [Agents](#agents) - 25 primary agents
- [Personas](#personas) - 9 role-based personas
- [Universal Agents](#universal-agents) - Always available
- [By Domain](#by-domain) - Organized by technical domain

---

## Agents

### All Primary Agents (25 total)

Located in `promptosaurus/agents/[agent-name]/`

| Agent | Purpose | Persona Affinity |
|-------|---------|------------------|
| **architect** | System design and architecture planning | Architect |
| **ask** | General Q&A and research | Universal |
| **backend** | Backend systems, APIs, microservices | Software Engineer, Architect |
| **code** | Code implementation | Software Engineer, Data Engineer, Data Scientist |
| **compliance** | Compliance audits (SOC2, GDPR, HIPAA, etc.) | Security Engineer |
| **data** | Data pipelines, warehouses, quality systems | Data Engineer, Architect |
| **debug** | Troubleshooting and error resolution | Universal |
| **devops** | CI/CD, infrastructure, deployment automation | DevOps Engineer |
| **document** | Documentation generation and improvement | Technical Writer |
| **enforcement** | Code quality enforcement | Software Engineer, Security Engineer |
| **explain** | Code walkthroughs and onboarding | Universal |
| **frontend** | Frontend architecture and UI development | Software Engineer, Architect |
| **incident** | Incident response and management | DevOps Engineer |
| **migration** | Dependency upgrades and framework migrations | Software Engineer |
| **mlai** | ML/AI pipelines, model training, deployment | Data Scientist |
| **observability** | Monitoring, logging, tracing, alerting | DevOps Engineer |
| **orchestrator** | Multi-step workflow coordination | Universal |
| **performance** | Performance optimization and benchmarking | Software Engineer, Data Engineer |
| **plan** | Strategic planning and work planning | Universal |
| **product** | Product strategy, requirements, roadmaps | Product Manager |
| **qa-tester** | Quality assurance and testing strategies | QA/Tester |
| **refactor** | Code refactoring and restructuring | Software Engineer |
| **review** | Code review and quality assessment | Software Engineer, QA/Tester, Security Engineer |
| **security** | Security reviews, threat modeling | Security Engineer |
| **test** | Testing and QA | Software Engineer, QA/Tester, Data Scientist |

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

**9 role-based personas** for agent filtering:

| Persona | Focus | Primary Agents |
|---------|-------|----------------|
| **Software Engineer** | Writing, maintaining, testing code | code, test, refactor, migration |
| **Architect** | System design, architecture | architect, backend, frontend, data |
| **QA/Tester** | Quality assurance, testing | test, review, qa-tester |
| **DevOps Engineer** | Infrastructure, deployment, ops | devops, observability, incident |
| **Security Engineer** | Security, threat modeling, compliance | security, compliance |
| **Product Manager** | Requirements, roadmap planning | product |
| **Data Engineer** | Data pipelines, ETL, data quality | data, code |
| **Data Scientist** | ML/AI, model development | mlai, code |
| **Technical Writer** | Documentation, guides | document |

For detailed persona information, see: [PERSONAS.md](./PERSONAS.md)

For persona-based filtering, see: [PERSONA_GUIDES.md](./PERSONA_GUIDES.md)

---

## By Domain

### Backend & APIs
- **Agents:** backend, code, performance
- **Use Cases:** REST APIs, GraphQL, microservices, caching, database selection

### Frontend & UI
- **Agents:** frontend, code, performance
- **Use Cases:** React, Vue.js, mobile apps, accessibility, state management

### DevOps & Infrastructure
- **Agents:** devops, observability, incident
- **Use Cases:** CI/CD, Docker, Kubernetes, Terraform, monitoring, incident response

### Data Engineering
- **Agents:** data, code, performance
- **Use Cases:** ETL pipelines, data quality, data warehouses, streaming

### ML & AI
- **Agents:** mlai, data, code
- **Use Cases:** Model training, feature engineering, model deployment, monitoring

### Security & Compliance
- **Agents:** security, compliance, review
- **Use Cases:** Threat modeling, vulnerability assessment, code review, audits

### Testing & QA
- **Agents:** test, qa-tester, review, performance
- **Use Cases:** Unit testing, integration testing, load testing, quality assurance

### Documentation
- **Agents:** document, explain
- **Use Cases:** Technical writing, code walkthroughs, API documentation

---

## Component Counts

| Type | Count | Verified |
|------|-------|----------|
| **Primary Agents** | 25 | ✅ |
| **Subagents** | 82 | ✅ |
| **Workflows** | 100 | ✅ |
| **Skills** | 108 | ✅ |
| **Personas** | 9 | ✅ |

---

## How to Use This Index

### Search by Agent Name
Find the agent in the [Agents](#agents) table above and check its location: `promptosaurus/agents/[agent-name]/`

### Search by Persona
1. Find your role in [Personas](#personas)
2. Check which agents are available
3. Browse those agent directories

### Search by Domain
1. Find your domain in [By Domain](#by-domain)
2. Check recommended agents
3. Explore agent subdirectories for workflows and skills

### Find Workflows and Skills
- Subagents located in: `promptosaurus/agents/[agent-name]/subagents/[subagent-name]/`
- Each subagent has `minimal/` and `verbose/` variants

---

## File Locations

### Agent Prompts
- Location: `promptosaurus/agents/[agent-name]/prompt.md`
- Example: `promptosaurus/agents/backend/prompt.md`

### Subagents
- Location: `promptosaurus/agents/[agent-name]/subagents/[subagent-name]/[minimal|verbose]/prompt.md`
- Example: `promptosaurus/agents/backend/subagents/api-design/minimal/prompt.md`

### Persona Configuration
- Location: `promptosaurus/personas/personas.yaml`
- Defines which agents/workflows/skills are available per persona

---

## Related Documentation

- **PERSONAS.md** - Persona-based filtering system
- **PERSONA_GUIDES.md** - Quick reference by role
- **RELATIONSHIPS_MATRIX.md** - How components relate to each other
- **ARCHITECTURE.md** - System architecture overview

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1.0 | 2026-04-13 | Initial release baseline with accurate counts |

