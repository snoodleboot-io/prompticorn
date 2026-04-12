# Performance Monitoring Workflow

**Version:** 1.0  
**Cadence:** Weekly (Thursday) + On-demand  
**Owner:** Engineering Team  
**Status:** Active

---

## Quick Reference

### Weekly Performance Check (30 min)

```bash
cd /home/john_aven/Documents/software/promptosaurus

# 1. Test suite performance
time pytest --cov -q

# 2. Code complexity
radon cc promptosaurus/ -a > complexity-report.txt

# 3. Line count and maintainability
radon mi promptosaurus/ > maintainability-report.txt

# 4. Dependency size
pip show -v promptosaurus | grep -i size
```

---

## Metrics to Monitor

### Test Suite Performance
**Target:** < 25 seconds for full suite

```bash
time pytest --cov -q
```

**What to do if slow:**
- If > 30 sec: Investigate slow tests
- Use `pytest --durations=10` to see slowest tests
- Consider parallelizing with `pytest -n auto`
- Move slow integration tests to separate CI job

### Code Complexity
**Target:** Average cyclomatic complexity < 5

```bash
radon cc promptosaurus/ -a
```

**Interpretation:**
- A-B (1-5): Simple, clear
- C (6-10): Moderate, watch this
- D (11-20): High complexity, consider refactoring
- E (21+): Very high, refactor required

**Action:**
- If avg complexity > 5: Schedule refactoring
- Focus on functions with complexity D or E
- Extract helper functions

### Maintainability Index
**Target:** > 80 (Excellent)

```bash
radon mi promptosaurus/
```

**Scale:**
- 100-20: Excellent
- 20-10: Good
- 10-0: Poor

**Action:**
- If < 20: Not urgent but monitor
- If < 10: Schedule improvement work
- Focus on files with lowest scores

### Code Size Metrics
**Monitor these quarterly:**
- Total lines of code
- Number of functions/classes
- Average function length (target: < 30 lines)

```bash
wc -l promptosaurus/**/*.py
cloc promptosaurus/
```

---

## Weekly Performance Report

**Template:**
```markdown
# Weekly Performance Report
**Week of:** YYYY-MM-DD

## Test Suite
- Duration: X seconds
- Pass rate: X%
- Coverage: X%
- Status: ✅ / ⚠️

## Code Quality
- Avg complexity: X
- Maintainability: X
- New issues: X
- Status: ✅ / ⚠️

## Build/Deploy
- CI duration: X min
- Deploy duration: X min
- Failures: X
- Status: ✅ / ⚠️

## Alerts
[Any performance regressions]

## Actions This Week
- [Action 1]
- [Action 2]
```

---

## Decision Tree

**Test suite slower than last week?**
- YES: Run with --durations=10, identify slow tests
- NO: Continue to next metric

**Code complexity increasing?**
- YES: Review recent commits, refactor high-complexity functions
- NO: Acceptable

**CI/CD slower than last week?**
- YES: Check resource usage, enable caching if not present
- NO: Acceptable

**Coverage trending down?**
- YES: Block new PRs without tests, increase focus
- NO: Maintain current pace

---

## Optimization Opportunities

### If Test Suite > 30 seconds
1. Identify slowest tests: `pytest --durations=10`
2. Check if they use real I/O or mocks
3. Parallelize: `pip install pytest-xdist` then `pytest -n auto`
4. Use fixtures for setup/teardown
5. Consider splitting into unit/integration/slow

### If Complexity Rising
1. Extract helper functions
2. Break down large conditionals
3. Use early returns to reduce nesting
4. Consider breaking class into smaller classes
5. Document complex algorithms

### If Maintainability Declining
1. Improve variable/function naming
2. Remove commented-out code
3. Reduce function length (target < 30 lines)
4. Extract duplicated code
5. Add docstrings to unclear functions

---

## Historical Trends (Monthly Review)

Track over time:
- Test duration trend
- Complexity trend
- Coverage trend
- Lines of code growth
- Dependency count

**Maintenance log entry:**
```
PERFORMANCE - WEEK OF YYYY-MM-DD
- Test suite: X sec (was Y, trend: up/down/stable)
- Avg complexity: X.X (was Y.Y, trend: up/down/stable)  
- Coverage: X% (was Y%, trend: up/down/stable)
- Actions: [list any changes made]
```

---

## Tools Setup

### radon (complexity analysis)
```bash
pip install radon

# Cyclomatic complexity
radon cc promptosaurus/ -a

# Maintainability Index
radon mi promptosaurus/

# Raw metrics
radon raw promptosaurus/
```

### pytest plugins (for performance)
```bash
pip install pytest-durations  # Built-in, use --durations=N
pip install pytest-xdist      # Parallel execution: -n auto
pip install pytest-benchmark  # For performance tests
```

---

## Red Flags

- Test suite duration increasing week-over-week
- Complexity growing in critical modules
- Coverage trending down consistently
- More failures in CI than locally
- Memory usage growing significantly
- Build time increasing consistently

**Response:** Schedule team discussion about root cause, create improvement task

