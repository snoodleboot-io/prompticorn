# Phase 3 Skills Quick Reference

**50 specialized skills** organized in 4 tracks for deep technical knowledge.

Each skill has **2 variants**:
- **Minimal:** Concise overview (20-40 lines)
- **Verbose:** Comprehensive guide with examples (100-150+ lines)

---

## Track 1: ML/AI Skills (15)

Core techniques for machine learning development:

| Skill | Topic | Covers |
|-------|-------|--------|
| data-validation-pipelines | Data Quality | Building robust validation for ML data |
| feature-store-design | Feature Management | Designing centralized feature repositories |
| model-performance-debugging | Troubleshooting | Diagnosing and fixing poor model performance |
| hyperparameter-optimization | Tuning | Grid search, random search, Bayesian optimization |
| data-versioning-reproducibility | Reproducibility | Versioning data and ensuring reproducible experiments |
| ensemble-methods | Modeling | Combining multiple models effectively |
| cross-validation-strategies | Validation | Robust cross-validation approaches |
| imbalanced-classification | Data Issues | Handling class imbalance in classification |
| time-series-preprocessing | Data Processing | Preparing time series data for ML |
| dimensionality-reduction | Feature Selection | Reducing feature dimensions while preserving information |
| anomaly-detection-techniques | Pattern Detection | Identifying outliers and anomalies |
| feature-importance-analysis | Interpretation | Understanding which features matter |
| model-interpretability | Explanation | Making model decisions understandable |
| batch-vs-realtime-scoring | Architecture | Designing prediction serving systems |
| mlops-pipeline-design | Production | Building production ML pipelines |

---

## Track 2: Security Skills (12)

Core techniques for security and compliance:

| Skill | Topic | Covers |
|-------|-------|--------|
| threat-identification | Threat Analysis | Identifying threats in systems |
| vulnerability-assessment | Assessment | Finding and scoring vulnerabilities |
| secure-code-review | Code Review | Reviewing code for security issues |
| cryptography-fundamentals | Encryption | Understanding and applying cryptography |
| authentication-design | Identity | Designing secure authentication |
| authorization-patterns | Access Control | Implementing authorization systems |
| api-security-hardening | API Security | Securing REST/GraphQL APIs |
| security-testing-strategies | Testing | Security testing techniques |
| incident-response-planning | Incidents | Planning incident response procedures |
| compliance-assessment | Compliance | Assessing compliance with standards |
| secret-management | Secrets | Securely managing credentials |
| security-architecture-review | Architecture | Reviewing security architecture |

---

## Track 3: Product Skills (10)

Core techniques for product management:

| Skill | Topic | Covers |
|-------|-------|--------|
| user-needs-discovery | Research | Understanding user needs |
| requirements-specification | Requirements | Writing clear requirements |
| success-metrics-definition | Metrics | Defining success metrics and KPIs |
| roadmap-prioritization | Planning | Prioritizing and sequencing features |
| user-testing-methods | Validation | Testing with actual users |
| competitor-analysis | Strategy | Analyzing competitive landscape |
| ux-writing-guidelines | Copy | Writing effective UX copy |
| launch-readiness-checklist | Launch | Preparing for product launch |
| stakeholder-communication | Communication | Communicating with stakeholders |
| product-analytics-setup | Analytics | Setting up product analytics |

---

## Track 4: Cross-Domain Skills (13)

Applicable across ML/AI, Security, and Product:

| Skill | Topic | Covers |
|-------|-------|--------|
| technical-decision-making | Decisions | Making sound technical choices |
| architecture-documentation | Documentation | Documenting system architecture |
| code-review-practices | Process | Conducting effective code reviews |
| testing-strategies | Testing | Comprehensive testing approaches |
| documentation-best-practices | Docs | Writing effective documentation |
| team-collaboration | Teamwork | Working effectively in teams |
| problem-decomposition | Analysis | Breaking down complex problems |
| technical-communication | Communication | Explaining technical concepts clearly |
| performance-optimization | Performance | Optimizing system performance |
| debugging-methodology | Debugging | Systematic debugging approaches |
| quality-assurance | QA | Ensuring quality across deliverables |
| technical-debt-management | Maintenance | Managing and reducing technical debt |
| continuous-improvement | Culture | Building improvement mindset |

---

## How to Use Skills

### Find a Skill

1. Identify domain: ML/AI, Security, Product, or Cross-Domain
2. Find the skill in the table above
3. Access the skill directory

### Access a Skill

```
promptosaurus/skills/[skill-name]/
├── minimal/
│   └── SKILL.md         ← Quick reference
└── verbose/
    └── SKILL.md         ← Detailed guide
```

### Read a Skill

**Start with minimal** for quick overview.  
**Read verbose** for implementation details, examples, and best practices.

### Integration with Workflows

Skills are referenced by related workflows:
- Workflows link to relevant skills
- Skills provide deeper technical knowledge
- Use workflows for process, skills for techniques

---

## Skill Relationships

**Skills are often grouped:**

**ML/AI Stack:**
- data-validation → feature-store → model-training → model-deployment → mlops-pipeline

**Security Stack:**
- threat-identification → vulnerability-assessment → secure-code-review → api-security → incident-response

**Product Stack:**
- user-needs → requirements → metrics → roadmap → launch

**Cross-Domain:**
- Apply technical-decision-making → architecture-documentation → code-review → testing → quality-assurance

---

## Quality Metrics

- ✓ 50/50 skills exist
- ✓ 100/100 files (minimal + verbose)
- ✓ All YAML frontmatter valid
- ✓ All registered in mapping file
- ✓ Organized in 4 tracks

---

## Skill Depth Levels

| Level | Audience | Skill Type |
|-------|----------|-----------|
| Fundamental | Everyone | Cross-domain skills (documentation, testing, collaboration) |
| Intermediate | Domain specialists | Track-specific skills (15 ML/AI, 12 Security, 10 Product) |
| Advanced | Experts | Deep dives with tools and frameworks |

---

**Last Updated:** April 2026  
**Phase:** 3.0.0  
**Status:** Production-Ready
