# Maintenance Workflows

Operational procedures for maintaining Promptosaurus library quality, stability, and security.

**Purpose:** These workflows ensure the library remains production-ready through systematic monitoring, testing, and improvement practices.

---

## 8 Core Maintenance Workflows

### 1. **Dependency Update Workflow**
**Cadence:** Weekly check, Monthly update  
**Owner:** Engineering Team  
**File:** `1-dependency-update-workflow.md`

Procedures for keeping dependencies current and secure.
- Weekly outdated package check
- Monthly full dependency update
- Security vulnerability handling
- Rollback procedures

**Key Activities:**
- `uv pip list --outdated` (weekly)
- `uv sync --upgrade` (monthly)
- `pip-audit` (security check)

---

### 2. **Security Audit Workflow**
**Cadence:** Monthly (First Wednesday)  
**Owner:** Security Team / Engineering  
**File:** `2-security-audit-workflow.md`

Comprehensive security review of code and dependencies.
- Dependency vulnerability scanning
- Code security analysis (bandit)
- Type safety verification (pyright)
- Secrets detection and prevention

**Key Tools:**
- `pip-audit` - Dependency vulnerabilities
- `bandit` - Code security scanning
- `pyright` - Type safety check
- `detect-secrets` - Secrets scanning

---

### 3. **Performance Monitoring Workflow**
**Cadence:** Weekly (Thursday)  
**Owner:** Engineering Team  
**File:** `3-performance-monitoring-workflow.md`

Track and optimize performance metrics.
- Test suite performance tracking
- Code complexity monitoring
- Maintainability index tracking
- Build/deploy time monitoring

**Key Metrics:**
- Test suite duration (target: < 25 sec)
- Cyclomatic complexity (target: avg < 5)
- Maintainability index (target: > 80)
- Code size metrics

---

### 4. **Code Quality Review Workflow**
**Cadence:** Per PR + Weekly Summary  
**Owner:** Code Reviewers / Engineering  
**File:** `4-code-quality-workflow.md`

PR review standards and code quality gates.
- Pre-commit checks (ruff, pyright, pytest)
- PR review checklist
- Standards compliance verification
- Test coverage validation

**Key Tools:**
- `ruff` - Formatting & linting
- `pyright` - Type checking
- `pytest` - Test execution
- Coverage reporting

---

### 5. **Test Coverage Improvement Workflow**
**Cadence:** Weekly (Friday) + Quarterly Deep-Dive  
**Owner:** QA Team / Engineering  
**File:** `5-coverage-improvement-workflow.md`

Systematic approach to improving test coverage.
- Current: 64.3% (2,001 / 5,606 lines)
- Target: 85%+ overall, 90% per-class

**Focus Areas (Priority Order):**
1. UI components (32-62% coverage)
2. Critical paths (orchestrator, registry, selector)
3. Integration tests
4. Edge case coverage

**3-Week Expansion Plan:**
- Week 1: Critical files → 90%
- Week 2: Important modules → 90%
- Week 3: Integration & edge cases

---

### 6. **Release Cycle Workflow**
**Cadence:** Monthly (Last Friday)  
**Owner:** Release Manager / Engineering Lead  
**File:** `6-release-cycle-workflow.md`

Standardized release procedures.
- Pre-release verification
- Version bumping (semantic versioning)
- Changelog generation
- GitHub release creation
- Post-release validation

**Release Steps:**
1. Create release branch
2. Update version & changelog
3. Tag release
4. Create PR for review
5. Merge to main
6. Create GitHub release

---

### 7. **Technical Debt Cleanup Workflow**
**Cadence:** Monthly (Second Thursday)  
**Owner:** Engineering Team  
**File:** `7-tech-debt-cleanup-workflow.md`

Systematic identification and elimination of technical debt.

**Debt Categories:**
- High Priority: Commented code, type: ignore, hardcoded config
- Medium Priority: Complex functions, duplicated code
- Low Priority: Style improvements, documentation polish

**Monthly Process:**
1. Search for debt markers (TODO, FIXME, type: ignore, etc.)
2. Categorize by priority and effort
3. Estimate effort and impact
4. Create tasks and schedule

---

### 8. **Metrics & Monitoring Workflow**
**Cadence:** Weekly (Monday) + Monthly Analysis  
**Owner:** Engineering Team / Product Manager  
**File:** `8-metrics-tracking-workflow.md`

Comprehensive metrics collection and trend analysis.

**Key Metrics Tracked:**
- Code coverage (target: 85%+)
- Test count and pass rate (target: 98%+)
- Lines of code (target: < 10K)
- Average complexity (target: avg < 5)
- Dependency count and security
- Build/test time trends

**Reporting:**
- Weekly collection and snapshot
- Monthly trend analysis
- Quarterly strategic review

---

## Quick Start

### Day 1: Set Up Workflows
```bash
# View available workflows
ls -la docs/workflows/maintenance/

# Read overview
cat docs/workflows/maintenance/README.md

# Read specific workflow
cat docs/workflows/maintenance/1-dependency-update-workflow.md
```

### Week 1: Start with Low-Effort Workflows
**Recommended order:**
1. Metrics tracking (weekly Monday) - 30 min
2. Performance monitoring (weekly Thursday) - 30 min
3. Code quality (per PR, continuous)
4. Dependency updates (monthly first Monday)

### Week 2: Add Security & Testing
5. Security audit (monthly first Wednesday)
6. Coverage improvement (ongoing)

### Ongoing
7. Release cycle (monthly last Friday)
8. Tech debt cleanup (monthly second Thursday)

---

## Workflow Interdependencies

```
Metrics & Monitoring
├── Informs: Performance, Coverage, Quality
├── Uses data from: All other workflows
└── Tracks: Trends across all areas

Performance Monitoring
├── Depends on: Code Quality (PR reviews)
├── Feeds to: Metrics, Tech Debt
└── Triggers: Optimization work

Code Quality Review
├── Per PR: All code goes through
├── Depends on: Tests passing, type checking
├── Feeds to: Coverage, Metrics
└── Blocks: Merge if tests fail

Test Coverage Improvement
├── Depends on: Code Quality (types safe)
├── Feeds to: Metrics, Release readiness
└── Targets: 85%+ overall, 90% per-class

Security Audit
├── Monthly: Deep vulnerability scan
├── Depends on: Dependency Updates
├── P0 if: Critical vuln found
└── Feeds to: Release decision

Dependency Update
├── Weekly check, Monthly update
├── Depends on: Security audit
├── Triggers: Coverage tests
└── Feeds to: Release notes

Release Cycle
├── Monthly: Last Friday
├── Depends on: All quality gates passing
├── Requires: Tests ✅, Coverage ✅, Security ✅
└── Produces: Version tag, Release notes

Tech Debt Cleanup
├── Monthly: Second Thursday
├── Depends on: Metrics analysis
├── Feeds to: Code Quality, Complexity metrics
└── Targets: Reduce complexity, remove TODOs
```

---

## Integration with CI/CD

All workflows can be automated in GitHub Actions:

```yaml
# Weekly metrics collection
- cron: '0 9 * * 1'  # Monday 9 AM
  jobs:
    - collect_metrics
    - run_tests
    - check_coverage

# Security audit
- cron: '0 9 * * 3'  # Wednesday 9 AM
  jobs:
    - security_audit
    - dependency_check

# Performance baseline
- cron: '0 14 * * 4'  # Thursday 2 PM
  jobs:
    - performance_check
    - complexity_analysis
```

---

## Status Dashboard

| Workflow | Frequency | Owner | Status | Next Run |
|----------|-----------|-------|--------|----------|
| Dependency Update | Weekly | Team | ✅ Active | This Monday |
| Security Audit | Monthly | Security | ✅ Active | First Wed |
| Performance Monitor | Weekly | Team | ✅ Active | This Thursday |
| Code Quality | Per PR | Reviewers | ✅ Active | Ongoing |
| Coverage Improvement | Weekly | QA | ✅ Active | This Friday |
| Release Cycle | Monthly | Manager | ✅ Active | Last Friday |
| Tech Debt Cleanup | Monthly | Team | ✅ Active | Second Thu |
| Metrics Tracking | Weekly | Product | ✅ Active | This Monday |

---

## Documentation Files

All workflows follow this structure:

- **Quick Reference** - Commands at a glance
- **Detailed Procedures** - Step-by-step instructions
- **Decision Trees** - When to take different actions
- **Templates** - Checklists and report formats
- **Tools & Configuration** - Setup and commands

---

## Success Criteria

✅ **All 8 workflows operational** (This status)
✅ **Metrics dashboard maintained** (Weekly updates)
✅ **No P0 security issues** (Audit-driven)
✅ **Coverage improving** (Target: 85%+ by end of Q2)
✅ **Releases on schedule** (Monthly cadence)
✅ **Tech debt managed** (Monthly cleanup)
✅ **Performance stable** (Trend tracking)
✅ **Code quality consistent** (PR gates)

---

## Contact & Support

**Questions about workflows?**
- See specific workflow file for detailed procedures
- Check decision trees for edge cases
- Refer to tools & configuration for setup help

**Need to update a workflow?**
- Modify the markdown file
- Update the integration steps if needed
- Commit change with explanation

**Not following a workflow?**
- Schedule with owner to discuss barriers
- Identify blockers and resolve them
- Update workflow if it's unrealistic

