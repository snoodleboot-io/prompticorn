---
type: subagent
agent: orchestrator
name: maintenance
variant: verbose
version: 1.0.0
description: Comprehensive maintenance workflow coordination for production-ready systems
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

# Maintenance Orchestration (Verbose)

## Purpose

The Maintenance Orchestration subagent coordinates 8 critical operational workflows that ensure your codebase remains production-ready, secure, performant, and maintainable over the long term. These workflows form the backbone of continuous operational excellence.

## The 8 Maintenance Workflows

### 1. Code Quality Maintenance Workflow

**When to Use:**
- Per-PR code review to enforce standards
- Weekly quality summary to track trends
- Before releases to ensure baseline quality

**What It Does:**
- Runs automated checks (ruff format, ruff check, pyright)
- Verifies all tests passing and coverage not decreased
- Ensures no hardcoded secrets or constants
- Checks code follows naming conventions and patterns
- Validates docstrings on public functions
- Reviews error handling patterns

**Frequency:** 
- Automated: Every commit via pre-commit hooks
- Manual: Every PR review by code reviewer
- Summary: Weekly code quality report

**Integration:**
- CI/CD: Runs as part of build pipeline
- Pre-commit: Automated formatting and linting
- PR Review: Manual checklist for complex logic

---

### 2. Coverage Improvement Workflow

**When to Use:**
- Weekly analysis of coverage gaps
- After implementing new features
- Quarterly deep-dive to plan improvements

**What It Does:**
- Identifies untested code paths
- Categorizes by: happy path, error handling, edge cases
- Prioritizes by: risk level, effort to test, strategic importance
- Tracks progress toward coverage goals
- Reports coverage trends

**Targets:**
- Overall: 85%+ (allows for edge cases)
- Per-class: 90%+ minimum
- Critical paths: 95%+ (user-facing, security, data)

**3-Week Action Plan:**
- Week 1: Critical files (UI, security)
- Week 2: Important modules (core logic)
- Week 3: Integration and edge cases

**Tracking Metrics:**
- Line coverage %
- Branch coverage %
- Coverage trend (increasing/stable/declining)
- Gap areas requiring work

---

### 3. Dependency Update Workflow

**When to Use:**
- Weekly check for outdated packages
- Monthly full upgrade cycle
- Immediately for critical security patches

**What It Does:**
- Scans for outdated dependencies
- Reviews breaking changes in major versions
- Runs full test suite after updates
- Security audit for known vulnerabilities
- Documents changes in commit message

**Process:**

**Weekly Check (15 minutes):**
```bash
uv pip list --outdated  # See what's out of date
pip-audit --desc        # Check for vulnerabilities
```

**Monthly Update (2 hours):**
1. Check outdated packages (5 min)
2. Update dependencies (10 min)
3. Run test suite (20 min)
4. Security audit (5 min)
5. Commit and verify in CI (10 min)

**Decision Tree:**
- Critical vulnerability found? → Update immediately
- Breaking change in major version? → Create PR for review
- Minor/patch update? → Apply and test

**Rollback Procedure:**
If update breaks code:
```bash
git checkout HEAD~1 uv.lock pyproject.toml
uv sync
pytest  # Verify tests pass again
git commit -m "chore(deps): Revert [package] due to breaking changes"
```

---

### 4. Metrics & Monitoring Workflow

**When to Use:**
- Weekly collection of health metrics
- Monthly trend analysis
- Quarterly strategic review

**What It Does:**
- Collects: test count, pass rate, coverage %, complexity, build time
- Tracks: trends over time, alerts on regressions
- Reports: weekly snapshots, monthly trends, quarterly forecasts
- Identifies: optimization opportunities, performance issues

**Key Metrics:**
- **Coverage:** Target 85%+, trend should be stable/increasing
- **Test Pass Rate:** Target 98%+, flag any failures immediately
- **Code Complexity:** Avg cyclomatic < 5, max < 15
- **Build Time:** Should be < 30 seconds for full suite
- **Dependency Age:** Most recent versions, no critical CVEs

**Monthly Report Template:**
```
Coverage: X% (was Y%, trend: ↑/→/↓)
Tests: N total (M passing, X failing/skipped)
Complexity: X avg (was Y, trend: ↑/→/↓)
Build Time: X sec (was Y sec, trend: ↑/→/↓)
Alerts: [Any metrics below target]
Actions: [What needs attention this month]
```

---

### 5. Performance Monitoring Workflow

**When to Use:**
- Weekly Thursday check for regressions
- Monthly trend analysis
- After major changes that might impact performance

**What It Does:**
- Measures test suite execution time
- Analyzes code complexity (cyclomatic, maintainability)
- Detects performance regressions
- Identifies bottlenecks
- Recommends optimizations

**Targets:**
- Test suite: < 25 seconds
- Avg complexity: < 5
- Maintainability index: > 80
- No functions > 50 lines (unless justified)

**Weekly Check:**
```bash
time pytest --cov -q          # Test duration
radon cc promptosaurus/ -a    # Complexity analysis
radon mi promptosaurus/       # Maintainability index
```

**Response Actions:**
- If slower than last week: Find slow tests, consider parallelization
- If complexity rising: Schedule refactoring
- If maintainability declining: Improve naming, reduce function length

---

### 6. Release Cycle Workflow

**When to Use:**
- Monthly scheduled release (last Friday)
- Emergency hotfixes (when needed)
- After completing major feature work

**What It Does:**
- Verifies all tests passing
- Updates version number (semantic versioning)
- Generates changelog
- Creates git tag and GitHub release
- Documents breaking changes if any
- Verifies CI/CD passes

**Steps:**

**Pre-Release (Week Before):**
- Review commits since last release
- Identify breaking changes
- Plan version bump (MAJOR.MINOR.PATCH)
- Draft changelog

**Release Day (Last Friday, 3 hours):**
1. Create release branch (5 min)
2. Update version in __init__.py (5 min)
3. Update CHANGELOG.md (15 min)
4. Create git tag (5 min)
5. Create PR for review (5 min)
6. Review and merge (30 min)
7. Create GitHub release (10 min)
8. Verify CI/CD passes (5 min)

**Versioning:**
- MAJOR: Breaking changes, major refactors
- MINOR: New features, backward compatible
- PATCH: Bug fixes only

**Post-Release:**
- Verify release published
- Update documentation if needed
- Notify team/users

---

### 7. Security Audit Workflow

**When to Use:**
- Monthly comprehensive security review (first Wednesday)
- Weekly quick dependency check
- Immediately for critical vulnerabilities

**What It Does:**
- Scans dependencies for CVEs
- Analyzes code for security issues
- Checks for hardcoded secrets
- Verifies safe patterns
- Assesses compliance posture

**Tools:**
- `pip-audit`: Dependency vulnerabilities
- `bandit`: Code security issues
- `pyright`: Type safety (catches some unsafe patterns)
- `detect-secrets`: Secrets in code

**Monthly Audit (2 hours):**
1. Dependency scan (10 min)
2. Code security analysis (15 min)
3. Type safety check (10 min)
4. Secrets scan (5 min)
5. Generate report (10 min)
6. Assess findings (30 min)
7. Create remediation tasks (20 min)

**Risk Levels:**
- P0 (Critical): Update immediately, deploy ASAP
- P1 (High): Update in next release cycle
- P2 (Medium): Include in monthly updates
- P3 (Low): Document and monitor

**Response Actions:**
- Hardcoded secret found? → Remove, rotate secret, commit immediately
- Critical CVE? → Update dependency, test, deploy
- Code security issue? → Fix per severity, add tests

---

### 8. Tech Debt Cleanup Workflow

**When to Use:**
- Monthly review (second Thursday)
- Sprint planning (allocate 20% capacity)
- Quarterly strategic cleanup

**What It Does:**
- Identifies tech debt items (TODOs, FIXMEs, hacks)
- Categorizes by priority and effort
- Prioritizes for cleanup
- Tracks debt reduction
- Reports on progress

**Debt Categories:**

**High Priority (Fix Soon):**
- Commented-out code blocks
- Missing type hints (type: ignore without explanation)
- Hardcoded values (should be config)
- Silent error handling
- TODOs blocking releases

**Medium Priority (Schedule Cleanup):**
- Functions > 50 lines
- High cyclomatic complexity
- Duplicate code (DRY violations)
- Missing docstrings
- Outdated comments

**Low Priority (Nice to Have):**
- Style improvements
- Naming clarity
- Test organization
- Documentation polish

**Monthly Process:**
1. Search for debt markers (grep TODO, FIXME, type: ignore)
2. Categorize each item
3. Estimate effort (15 min, 1 hour, 2 hours, 1 day, unknown)
4. Assess impact (code quality, maintainability, performance)
5. Prioritize by: impact + effort
6. Create GitHub issues for each
7. Schedule in sprint backlog

**Tracking Metrics:**
- Total debt items identified
- Debt items resolved this month
- Time spent on cleanup
- Average age of oldest debt items
- Debt reduction trend

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────┐
│     Maintenance Orchestration (Workflow Coordinator) │
└─────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┬──────────────────┬──────────────────┐
        │               │               │                  │                  │
   Code Quality    Coverage        Dependency      Performance          Security
   Management      Improvement      Updates         Monitoring            Audits
        │               │               │                  │                  │
        └───────────────┼───────────────┴──────────────────┴──────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   Release Cycle   Metrics Tracking  Tech Debt Cleanup
```

## Success Metrics

Track these KPIs monthly:
- **Code Quality:** Test pass rate (target 98%+)
- **Coverage:** Overall % and trend (target 85%+, increasing)
- **Dependencies:** Freshness score, CVEs found/resolved
- **Performance:** Test duration trend, complexity index
- **Security:** Critical/high vulns found, time to remediation
- **Tech Debt:** Items resolved per month, total debt trend
- **Releases:** On-time release frequency, hotfix count

## Automation Opportunities

Priority automation targets (by ROI):
1. **Code quality checks** via pre-commit hooks
2. **Dependency scanning** in CI/CD pipeline
3. **Coverage reporting** automatic on PR/main
4. **Performance regression detection** on merge
5. **Metrics collection** scheduled daily
6. **Security scanning** scheduled weekly
7. **Tech debt alerts** on new TODOs/FIXMEs

## When to Escalate

Escalate immediately if:
- Critical security vulnerability discovered
- Test pass rate drops below 90%
- Any code with hardcoded secrets
- Performance degradation > 20%
- Release blocked by failing tests
- Dependency conflict blocking work

## Recommended Schedule

**Daily:**
- Pre-commit checks (automated, < 30 sec)

**Weekly:**
- Monday: Metrics collection
- Thursday: Performance monitoring
- Friday: Coverage analysis

**Monthly:**
- First Wednesday: Security audit
- First Monday: Dependency updates
- Second Thursday: Tech debt review
- Last Friday: Release cycle

**Quarterly:**
- Coverage deep-dive
- Performance optimization planning
- Security posture review
- Tech debt strategic cleanup

## Getting Started

1. **Start Small:** Begin with Code Quality (automated)
2. **Add Security:** Security audits (monthly)
3. **Track Metrics:** Weekly health check
4. **Expand Gradually:** Add other workflows as capacity allows
5. **Automate:** Move manual workflows to CI/CD pipeline

Remember: Maintenance workflows are **not overhead** - they are **investments in sustainability**. Every hour spent on maintenance saves 10x the effort in firefighting later.
