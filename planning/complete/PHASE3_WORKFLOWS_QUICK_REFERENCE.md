# Phase 3 Workflows Quick Reference

**45 generic workflows** organized in 4 tracks covering ML/AI, Security, Product, and Workflow Patterns.

Each workflow has **2 variants**:
- **Minimal:** 20-40 lines - key concepts and steps
- **Verbose:** 100-150+ lines - detailed guidance, examples, best practices

---

## Track 1: ML/AI Workflows (12)

| Workflow | Purpose | Use When |
|----------|---------|----------|
| model-evaluation-workflow | Evaluate model performance | Testing different models or approaches |
| model-serving-workflow | Deploy models for inference | Moving from training to production |
| mlops-pipeline-setup | Build production ML pipelines | Setting up continuous retraining |
| feature-engineering-guide | Design features for ML | Improving model performance |
| data-quality-monitoring | Monitor data quality | Detecting data issues early |
| model-governance-workflow | Govern model lifecycle | Managing model versions and approvals |
| hyperparameter-tuning | Optimize hyperparameters | Improving model accuracy |
| model-retraining-strategy | Plan model updates | Handling model drift |
| experiment-tracking-setup | Track experiments | Managing multiple model runs |
| model-interpretability-guide | Explain model decisions | Understanding model behavior |
| production-ml-deployment | Deploy models safely | Going to production |
| ml-monitoring-observability | Monitor production models | Detecting issues in production |

---

## Track 2: Security Workflows (10)

| Workflow | Purpose | Use When |
|----------|---------|----------|
| threat-modeling-workflow | Identify threats | Designing new systems |
| vulnerability-scanning-workflow | Find vulnerabilities | Regular security audits |
| security-testing-workflow | Test for vulnerabilities | Before deployment |
| compliance-audit-workflow | Verify compliance | Meeting regulatory requirements |
| incident-response-security | Handle security incidents | When breaches occur |
| security-hardening-checklist | Secure systems | Building security baselines |
| penetration-testing-guide | Test security defenses | Finding weaknesses |
| security-code-review | Review code for security | Before merging |
| dependency-scanning-workflow | Check dependencies | Managing supply chain risk |
| secret-management-workflow | Secure secrets | Protecting credentials |

---

## Track 3: Product Workflows (8)

| Workflow | Purpose | Use When |
|----------|---------|----------|
| requirements-gathering-workflow | Collect requirements | Starting new features |
| roadmap-planning-workflow | Plan feature roadmap | Setting quarterly goals |
| feature-prioritization-workflow | Prioritize features | Deciding what to build |
| user-research-guide | Research user needs | Understanding customers |
| ux-validation-workflow | Validate UX designs | Before building |
| analytics-setup-workflow | Set up analytics | Tracking usage |
| a-b-testing-workflow | Run A/B tests | Validating changes |
| feature-launch-checklist | Launch features | Going to production |

---

## Track 4: Workflow Patterns (15)

Meta-workflows for orchestrating other workflows:

| Workflow | Purpose | Use When |
|----------|---------|----------|
| workflow-orchestration-patterns | Coordinate multi-step processes | Managing complex workflows |
| multi-agent-coordination-workflow | Coordinate multiple agents | Distributed work |
| async-workflow-execution | Execute asynchronously | Non-blocking operations |
| workflow-versioning-management | Manage workflow versions | Evolution and compatibility |
| workflow-error-handling-patterns | Handle errors in workflows | Fault tolerance |
| workflow-monitoring-workflow | Monitor workflow health | Detecting issues |
| workflow-testing-patterns | Test workflows | Quality assurance |
| workflow-documentation-patterns | Document workflows | Maintainability |
| workflow-migration-patterns | Migrate workflows | System upgrades |
| workflow-performance-optimization | Optimize workflow performance | Speed and efficiency |
| workflow-dependency-management | Manage dependencies | Preventing deadlocks |
| workflow-rollback-strategies | Rollback on failure | Safe deployments |
| workflow-scaling-patterns | Scale to higher load | Growth |
| workflow-security-in-workflows | Secure workflow execution | Protecting data |
| workflow-compliance-patterns | Ensure compliance in workflows | Meeting requirements |

---

## How to Use

### Find a Workflow

1. Identify your domain: ML/AI, Security, Product, or Workflow Patterns
2. Look at the table above
3. Choose the workflow that matches your need

### Access a Workflow

```
promptosaurus/workflows/[workflow-name]/
├── minimal/
│   └── workflow.md      ← Quick overview
└── verbose/
    └── workflow.md      ← Detailed guide
```

### Read a Workflow

**Start with minimal** to understand the concept.  
**Read verbose** for detailed steps and examples.

### Cross-References

- **Related Workflows:** Listed within each workflow
- **Linked Skills:** Each workflow references relevant skills
- **Agents:** Workflows linked to appropriate Phase 3 agents

---

## Registration

All 45 workflows are registered in `language_skill_mapping.yaml`:

- **Python:** Track 1 ML/AI workflows + all track 4 patterns
- **Security:** All Track 2 security workflows
- **Product:** All Track 3 product workflows

This enables:
- Workflow discovery by language/role
- Integration with CLI tools
- Mapping to appropriate specialist agents

---

## Quality Metrics

- ✓ 45/45 workflows exist
- ✓ 90/90 files (minimal + verbose)
- ✓ All YAML frontmatter valid
- ✓ All registered in mapping file
- ✓ 23/23 integration tests PASSED

---

**Last Updated:** April 2026  
**Phase:** 3.0.0  
**Status:** Production-Ready
