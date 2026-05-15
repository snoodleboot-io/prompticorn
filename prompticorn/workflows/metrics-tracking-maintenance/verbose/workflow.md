# Metrics & Monitoring Workflow
name: "metrics-tracking-maintenance"

**Version:** 1.0  
**Cadence:** Weekly (Monday) + Monthly Trend Analysis  
**Owner:** Engineering Team / Product Manager  
**Status:** Active

---

## Quick Reference

### Weekly Metrics Collection (30 min)

```bash
cd /home/john_aven/Documents/software/prompticorn

# Collect all metrics
echo "=== Metrics for Week of $(date +%Y-%m-%d) ===" >> metrics-log.csv

# 1. Test coverage
pytest --cov=prompticorn --cov-report=json -q
cat .coverage.json | jq '.totals.percent_covered' >> metrics-log.csv

# 2. Test count and pass rate
pytest --collect-only -q | wc -l >> metrics-log.csv
pytest -q 2>&1 | grep "passed" >> metrics-log.csv

# 3. Code metrics
wc -l prompticorn/**/*.py >> metrics-log.csv
radon cc prompticorn/ -a -j >> metrics-log.csv

# 4. Dependency count
pip list | grep -v "^-" | wc -l >> metrics-log.csv
```

---

## Key Metrics to Track

### Code Metrics

| Metric | Target | Why | Check Command |
|--------|--------|-----|---|
| **Coverage** | 85%+ | Ensures quality | `pytest --cov` |
| **Test Count** | Growing | More tests = fewer bugs | `pytest --collect-only` |
| **Lines of Code** | < 10K | Keep it lean | `wc -l prompticorn/**/*.py` |
| **Avg Complexity** | < 5 | Maintainability | `radon cc prompticorn/ -a` |
| **Cyclomatic Max** | < 15 | No overly complex functions | `radon cc prompticorn/ -a` |

### Quality Metrics

| Metric | Target | Why | Check Command |
|--------|--------|-----|---|
| **Type Coverage** | 100% | Type safety | `pyright .` |
| **Lint Issues** | 0 | Clean code | `ruff check .` |
| **Test Pass Rate** | 98%+ | Reliability | `pytest -q` |
| **Dependency Versions** | Current | Security | `pip list --outdated` |

### Operational Metrics

| Metric | Target | Why | Check Command |
|--------|--------|-----|---|
| **Build Time** | < 5 min | Fast feedback | `time pytest --cov` |
| **Release Frequency** | Monthly | Regular updates | Git tags |
| **Issue Response** | < 24h | User support | GitHub issues |
| **PR Review Time** | < 48h | Fast iteration | GitHub PRs |

---

## Weekly Metrics Report

**Template (save as `metrics-YYYY-MM-DD.md`):**

```markdown
# Weekly Metrics Report - Week of YYYY-MM-DD

**Collected:** [Date]  
**Period:** [Start Date] - [End Date]

## Code Quality

### Coverage
- Current: X%
- Target: 85%
- Trend: [↑/→/↓] [+1% / Stable / -2%]
- Last week: Y%

### Tests
- Total: X tests
- Passing: X (Y%)
- Failing: X
- Skipped: X
- Trend: [↑/→/↓] [+10 / Stable / -5]

### Complexity
- Average: X (target: < 5)
- Max: Y (target: < 15)
- Trend: [Improving / Stable / Worsening]

### Type Safety
- Coverage: 100%
- Status: ✅ Full type safety
- type: ignore count: X

## Code Volume

### Lines of Code
- prompticorn: X LOC
- Tests: Y LOC
- Docs: Z LOC
- Trend: [+100 / Stable / -50]

### File Count
- Source files: X
- Test files: Y
- Trend: [+2 / Stable / -1]

## Dependencies

### Outdated Packages
- Count: X (target: 0)
- Include: [package names]
- Action: [None / Schedule update / Update immediately]

### Security Issues
- Vulnerabilities: X (target: 0)
- Critical: X
- High: X
- Medium: X

## Performance

### Build/Test Time
- Full test suite: X sec (target: < 30s)
- Unit tests only: X sec (target: < 10s)
- Trend: [Faster / Stable / Slower]

### CI/CD
- Build success rate: X% (target: 100%)
- Average build time: X min
- Trend: [Improving / Stable / Declining]

## Team Metrics

### Contributions
- PRs merged this week: X
- Issues closed: X
- Code reviews: X
- Documentation added: X pages

### Responsiveness
- Avg PR review time: X hours (target: < 24h)
- Avg issue response time: X hours (target: < 6h)
- Trend: [Improving / Stable / Declining]

## Status

✅ **All metrics in target range**  
⚠️ **[X] metrics need attention**  
🔴 **[X] metrics critical**

## Alerts

[Any metrics that need immediate action]

## Notes

[Unusual trends, blockers, or observations]

## Next Week Focus

- [Focus area 1]
- [Focus area 2]
```

---

## Monthly Trend Analysis (1.5 hours)

### Step 1: Collect Weekly Reports (15 min)
Gather all 4-5 weekly reports for the month

### Step 2: Analyze Trends (45 min)

```bash
# Create trend analysis
python3 << 'EOF'
import json
from pathlib import Path

metrics_files = list(Path('.').glob('metrics-*.md'))
trend_data = {
    'coverage': [],
    'tests': [],
    'complexity': [],
    'build_time': [],
}

for file in sorted(metrics_files):
    # Parse metrics file and extract values
    # Append to trend_data
    pass

# Print trends
for metric, values in trend_data.items():
    print(f"{metric}: {values[-1]} (trend: {['↑' if values[-1] > values[-2] else '→' if values[-1] == values[-2] else '↓']}")
EOF
```

### Step 3: Create Monthly Summary (30 min)

```markdown
# Monthly Metrics Summary - April 2026

## Overall Assessment
[1-2 sentences on how month went]

## Metrics Trend

### Coverage
- Week 1: 62%
- Week 2: 63%
- Week 3: 64%
- Week 4: 64.3%
- Trend: ↑ Improving
- Target: 85% (need +20.7%)

### Tests
- Week 1: 1,310 tests
- Week 2: 1,312 tests
- Week 3: 1,315 tests
- Week 4: 1,316 tests
- Trend: ↑ Growing

### Complexity
- Week 1: 4.2 avg
- Week 2: 4.2 avg
- Week 3: 4.1 avg
- Week 4: 4.1 avg
- Trend: → Stable

## Best Performers
- [Team/Area with best metrics]
- [Area with most improvement]

## Areas Needing Attention
- [Coverage still below target]
- [Complexity in [module]]
- [Build time trending up]

## Recommendations

### Immediate (This Week)
- [Action 1]
- [Action 2]

### This Month
- [Action 1]
- [Action 2]

### This Quarter
- [Strategic improvement]

## Confidence Level
- Code quality: ✅ High
- Test coverage: ⚠️ Medium (improving)
- Performance: ✅ High
- Release readiness: ✅ High
```

---

## Dashboard (Optional - Manual Tracking)

**Create a simple tracking sheet (CSV or Google Sheet):**

```
Date,Coverage%,Tests,TestPass%,AvgComplexity,BuildTime(sec),Issues,PRs,Notes
2026-04-01,62.0,1310,98.2,4.2,18,"coverage low",5,"baseline"
2026-04-08,63.5,1312,98.3,4.2,18,"stable",6,"dependency update"
2026-04-15,64.0,1315,98.3,4.1,19,"trending up",7,"ui tests added"
2026-04-22,64.3,1316,98.3,4.1,20,"on track",8,"ready for phase3"
```

**Update weekly, review monthly for trends**

---

## Decision Tree

**Metrics improving?**
- YES: Celebrate! Maintain pace
- NO: Investigate what changed

**Coverage below target?**
- YES: Make test expansion priority
- NO: Maintain, continue

**Build time increasing?**
- YES: Investigate (slow tests, dependencies?)
- NO: Good, stable

**Security vulnerabilities?**
- YES: P0 priority
- NO: Continue normal workflow

**Test pass rate < 95%?**
- YES: Debug failures, fix issues
- NO: Acceptable

---

## Tracking Tools

### Manual Tracking
- CSV file (metrics-log.csv)
- Google Sheets (shared dashboard)
- Markdown reports (in git)

### Automated Tools (Optional)
- GitHub Actions: Collect metrics on schedule
- Coverage.py: Integrated coverage tracking
- pytest plugins: Built-in performance metrics

### Integration Points
- Commit: Include metrics in commit message for major changes
- PR: Add metrics comparison in PR description
- Release: Include metrics in release notes

