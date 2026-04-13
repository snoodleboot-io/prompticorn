# Test Coverage Improvement Workflow
name: "coverage-improvement-maintenance"

**Version:** 1.0  
**Cadence:** Weekly (Friday) + Quarterly Deep-Dive  
**Owner:** QA Team / Engineering  
**Status:** Active

---

## Quick Reference

### Weekly Coverage Check (20 min)

```bash
cd /home/john_aven/Documents/software/promptosaurus

# Generate coverage report
pytest --cov=promptosaurus --cov-report=html --cov-report=term -q

# View results
open htmlcov/index.html  # or browse to it

# Check per-module breakdown
cat .coverage

# Identify lowest coverage modules
pytest --cov=promptosaurus --cov-report=term-missing -q | grep -E "^promptosaurus.*[0-9]{1,2}%"
```

---

## Current Coverage Status

**Overall:** 64.3% (2,001 / 5,606 lines)
**Target:** 85%+ overall, 90% per-class minimum

**Lowest Coverage (Priority 1):**
- `promptosaurus/ui/_selector.py` - 32% (138 lines)
- `promptosaurus/ui/input/windows.py` - 25% (62 lines)
- `promptosaurus/ui/input/unix.py` - 20% (66 lines)
- `promptosaurus/ui/pipeline/orchestrator.py` - 24% (41 lines)
- `promptosaurus/registry.py` - 53% (117 lines)

---

## Weekly Coverage Report

**Template:**
```markdown
# Coverage Report - Week of YYYY-MM-DD

## Overall Metrics
- Overall coverage: X% (target: 85%+)
- Trend: [Up/Down/Stable]
- New coverage added: X%

## Top Improvements This Week
- Module A: +5% (was 60%, now 65%)
- Module B: +3% (was 42%, now 45%)

## Lowest Coverage (Action Needed)
- Module X: 20% (currently untested)
- Module Y: 35% (basic coverage only)

## New Tests Added
- X unit tests
- X integration tests
- X edge case tests

## Coverage Targets Met
- [ ] 90% for core modules (critical paths)
- [ ] 80% for most modules
- [ ] 85% overall minimum

## Blockers
[Any issues preventing coverage increase]
```

---

## Quarterly Deep-Dive (4 hours)

### Phase 1: Analyze Gaps (1 hour)

```bash
# Generate detailed HTML report
pytest --cov=promptosaurus --cov-report=html -q

# Open in browser and identify:
# 1. Untested functions
# 2. Untested error paths
# 3. Edge cases not covered
# 4. Integration gaps

# Export for analysis
pytest --cov=promptosaurus --cov-report=term-missing -q > coverage-analysis.txt
```

**What to look for:**
- Missing tests for error conditions
- Edge cases not covered
- Integration between modules
- Async/parallel code paths
- Database transaction handling

### Phase 2: Plan Tests (1.5 hours)

For each low-coverage module:
1. Identify untested functions
2. Categorize: happy path, error path, edge case
3. Estimate effort (XS/S/M)
4. Prioritize by risk (critical path first)

**Template:**
```
Module: [name]
Current coverage: X%
Target: 90%
Gap: X lines to cover

Functions needing tests:
- function_a(): Y lines (happy path) - XS
- function_b(): Z lines (error handling) - S
- function_c(): W lines (edge cases) - M

Total effort: X days
Priority: [P0/P1/P2]
```

### Phase 3: Implement Tests (1.5 hours + ongoing)

See TEST_CONVENTIONS.md for test structure.

```bash
# Create test file
touch tests/unit/[module]/test_[file].py

# Follow test class structure
class Test[ClassName]:
    def test_[method]_[scenario](self):
        # Arrange, Act, Assert
        pass
```

### Phase 4: Verify (30 min)

```bash
# Run tests with coverage
pytest tests/unit/[module]/test_[file].py --cov=promptosaurus.[module] --cov-report=term-missing

# Should see no uncovered lines
```

---

## Monthly Coverage Target Tracking

| Month | Target | Actual | Status | Focus Area |
|-------|--------|--------|--------|-----------|
| April | 60% | 64.3% | ✅ | Critical files baseline |
| May | 70% | - | 🔄 | UI components (32-62%) |
| June | 80% | - | 🔄 | Integration tests |
| July | 85% | - | 🔄 | Edge cases & error paths |
| Aug | 90% | - | 🔄 | Per-class compliance |

---

## Decision Tree

**Coverage increased this week?**
- YES: Celebrate! Continue same pace
- NO: Investigate blockers, increase effort

**Any module dropped in coverage?**
- YES: Identify why, revert if accidental
- NO: Good, coverage stable or growing

**Critical module below 50%?**
- YES: P0 priority, block releases
- NO: Normal maintenance

**Coverage below 80% overall?**
- YES: Make test expansion a priority
- NO: Maintain current pace

---

## Tools & Commands

### pytest-cov
```bash
# Full report (HTML)
pytest --cov=promptosaurus --cov-report=html

# Terminal with missing lines
pytest --cov=promptosaurus --cov-report=term-missing

# JSON for processing
pytest --cov=promptosaurus --cov-report=json
```

### Coverage.py (underlying tool)
```bash
# Erase previous coverage data
coverage erase

# Run and collect coverage
coverage run -m pytest

# Report
coverage report

# HTML report
coverage html
open htmlcov/index.html
```

### Mutation Testing (verify test quality)
```bash
pip install mutmut

# Run mutation tests
mutmut run --tests-dir tests

# See results
mutmut results
```

---

## Setting Coverage Thresholds

In `pyproject.toml`:
```toml
[tool.coverage.run]
source = ["promptosaurus"]
branch = true

[tool.coverage.report]
# Minimum coverage percentages
fail_under = 85  # Overall minimum
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]

[tool.coverage.html]
directory = "htmlcov"
```

---

## Coverage Improvement Action Plan

**Week 1: Critical Files (5 days)**
- `_selector.py` (32% → 90%)
- `windows.py` (25% → 90%)
- `unix.py` (20% → 90%)
- `orchestrator.py` (24% → 90%)

**Week 2: Important Modules (5 days)**
- `registry.py` (53% → 90%)
- Other medium-priority modules

**Week 3: Integration & Edge Cases (5 days)**
- Add integration tests
- Edge case coverage
- Error path coverage
- Final verification

**Result:** Overall coverage 64.3% → 85%+

