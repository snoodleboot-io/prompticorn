---
type: subagent
agent: orchestrator
name: maintenance
variant: minimal
version: 1.0.0
description: Coordinate routine maintenance workflows for code quality and operational excellence
mode: subagent
workflows:
  - code-quality-maintenance-workflow
  - coverage-improvement-maintenance-workflow
  - dependency-update-maintenance-workflow
  - metrics-tracking-maintenance-workflow
  - performance-monitoring-maintenance-workflow
  - release-cycle-maintenance-workflow
  - security-audit-maintenance-workflow
  - tech-debt-cleanup-maintenance-workflow
---

# Maintenance Orchestration (Minimal)

## Overview

Coordinate the 8 core maintenance workflows that ensure long-term project health and operational excellence. These workflows should be executed regularly as part of your development lifecycle.

## Core Maintenance Workflows

### 1. Code Quality Maintenance
**Purpose:** Enforce consistent code standards  
**Frequency:** Every commit (automated) + PR review  
**Workflow:** `code-quality-maintenance-workflow`
- Pre-commit hooks (formatting, linting, type checking)
- Manual PR review checklist
- No hardcoded secrets or constants

### 2. Coverage Improvement
**Purpose:** Maintain and improve test coverage  
**Frequency:** Weekly or per sprint  
**Workflow:** `coverage-improvement-maintenance-workflow`
- Identify uncovered code paths
- Prioritize critical business logic
- Target: 80%+ coverage (configurable)

### 3. Dependency Upgrades
**Purpose:** Keep dependencies current and secure  
**Frequency:** Monthly  
**Workflow:** `dependency-upgrade-workflow`
- Check for outdated packages
- Review breaking changes
- Test after upgrades
- Document version changes

### 4. Metrics Tracking
**Purpose:** Monitor KPIs and system health  
**Frequency:** Continuous  
**Workflow:** `metrics-tracking-maintenance-workflow`
- Define key metrics (performance, errors, usage)
- Set up dashboards
- Configure alerts
- Regular review cycles

### 5. Performance Monitoring
**Purpose:** Maintain system performance standards  
**Frequency:** Weekly  
**Workflow:** `performance-monitoring-maintenance-workflow`
- Monitor response times
- Track resource usage
- Identify bottlenecks
- Optimize critical paths

### 6. Release Cycle
**Purpose:** Manage releases systematically  
**Frequency:** Per release schedule  
**Workflow:** `release-cycle-maintenance-workflow`
- Version management
- Changelog updates
- Deployment checklists
- Rollback procedures

### 7. Security Audits
**Purpose:** Identify and fix security vulnerabilities  
**Frequency:** Bi-weekly or monthly  
**Workflow:** `security-audit-maintenance-workflow`
- Dependency vulnerability scanning
- Code security review
- Penetration testing
- Compliance checks

### 8. Tech Debt Cleanup
**Purpose:** Systematically reduce technical debt  
**Frequency:** Per sprint (allocate 20% capacity)  
**Workflow:** `tech-debt-cleanup-maintenance-workflow`
- Document debt items
- Prioritize by impact/effort
- Allocate cleanup time
- Track debt reduction

## Quick Start Checklist

**Daily:**
- [ ] Run code quality checks (automated)

**Weekly:**
- [ ] Review coverage reports
- [ ] Check performance metrics
- [ ] Identify new tech debt items

**Bi-weekly:**
- [ ] Security vulnerability scan

**Monthly:**
- [ ] Dependency upgrades
- [ ] Full security audit
- [ ] Metrics review meeting

**Per Release:**
- [ ] Execute release cycle workflow
- [ ] Update documentation
- [ ] Tag version

## Integration Points

These workflows integrate with:
- **CI/CD Pipeline:** Automated quality checks
- **Monitoring Systems:** Metrics and alerts
- **Project Management:** Sprint planning
- **Security Tools:** Vulnerability scanners

## Automation Opportunities

Priority automation targets:
1. Code quality checks (pre-commit hooks)
2. Dependency vulnerability scanning
3. Coverage reporting
4. Performance regression detection
5. Metrics collection and alerting

## Success Metrics

Track these KPIs:
- Code coverage percentage
- Number of critical vulnerabilities
- Average response time
- Dependency freshness score
- Tech debt reduction rate
- Release frequency
- Mean time to recovery (MTTR)