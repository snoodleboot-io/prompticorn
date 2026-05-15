# Technical Debt Cleanup Workflow
name: "tech-debt-cleanup-maintenance"

**Version:** 1.0  
**Cadence:** Monthly (Second Thursday)  
**Owner:** Engineering Team  
**Status:** Active

---

## Quick Reference

### Monthly Tech Debt Review (2 hours)

```bash
cd /home/john_aven/Documents/software/prompticorn

# 1. Find all TODO comments
grep -r "TODO:" --include="*.py" prompticorn/ > debt-todos.txt

# 2. Find all FIXME comments  
grep -r "FIXME:" --include="*.py" prompticorn/ > debt-fixmes.txt

# 3. Find type: ignore patterns
grep -r "type: ignore" --include="*.py" prompticorn/ > debt-type-ignore.txt

# 4. Find old comments or hacks
grep -r "HACK\|XXX\|KLUDGE" --include="*.py" prompticorn/ > debt-hacks.txt

# Review all generated files and categorize
```

---

## What Counts as Technical Debt

**High Priority (Fix Soon):**
- Commented-out code blocks (remove them!)
- `# type: ignore` without explanation
- Hardcoded values (should be config)
- Swallowed exceptions (silent failures)
- TODOs blocking release
- Known memory leaks or performance issues

**Medium Priority (Schedule Cleanup):**
- Complex functions (> 50 lines)
- High cyclomatic complexity (> 10)
- Duplicate code (DRY violations)
- Outdated comments
- Missing docstrings on public functions

**Low Priority (Nice to Have):**
- Style improvements
- Naming clarity
- Refactoring for readability
- Test organization
- Documentation polish

---

## Tech Debt Tracking

### Inventory Template

```markdown
# Tech Debt Inventory - April 2026

## High Priority (This Quarter)
- [ ] **Remove commented code in auth.py** (5 lines, 1 hour)
  - File: prompticorn/auth.py:45-50
  - Description: Old OAuth code, fully replaced
  - Effort: 15 min
  - Impact: Cleaner code
  - Owner: @engineer1

- [ ] **Fix type: ignore in registry.py** (2 instances, 2 hours)
  - File: prompticorn/registry.py:67
  - Description: Dynamic attribute access, needs redesign
  - Effort: 1.5 hours
  - Impact: Better type safety
  - Owner: @engineer2

## Medium Priority (This Year)
- Refactor large functions in orchestrator.py (> 50 lines)
- Add missing docstrings (12 public functions)
- Consolidate duplicate utils (3 locations)

## Low Priority (Ongoing)
- Style improvements
- Test organization
- Performance micro-optimizations
```

---

## Monthly Review Process (2 hours)

### Step 1: Search for Debt (30 min)

```bash
# Find all debt markers
grep -r "TODO:\|FIXME:\|HACK\|XXX\|type: ignore" --include="*.py" prompticorn/

# Find commented code (suspicious patterns)
grep -r "^[[:space:]]*#.*=" --include="*.py" prompticorn/ | grep -v "^#"

# Find long functions (code smell)
# (Check manually in IDE or use radon)
radon mi prompticorn/ -j  # Maintainability index

# Find high complexity (code smell)
radon cc prompticorn/ -j  # Cyclomatic complexity
```

### Step 2: Categorize (30 min)

For each item found:

```
CATEGORY: [High/Medium/Low]
LOCATION: [file:line]
TYPE: [Commented code / TODO / Type ignore / Complexity / Duplication / Other]
EFFORT: [15 min / 1 hour / 2 hours / 1 day / Unknown]
IMPACT: [Code quality / Type safety / Performance / Maintainability]
BLOCKER: [Yes/No] - Does this block a release?
OWNER: [Name or team]
```

### Step 3: Prioritize (30 min)

Sort by:
1. Blocking issues (must fix for release)
2. High impact + low effort
3. High priority + medium effort
4. Medium priority + low effort
5. Everything else

### Step 4: Create Tasks (30 min)

```bash
# Create GitHub issues or similar
gh issue create --title "Clean up commented code in auth.py" \
  --body "Remove 5 lines of old OAuth code (lines 45-50).
  
  Type: Code cleanup
  Effort: 15 minutes
  Priority: Medium
  
  See: docs/TECHNICAL_DEBT.md#auth-cleanup"
```

---

## Common Debt Patterns

### Pattern 1: Commented Code
```python
# ❌ Debt
def process_data(data):
    # old_result = old_algorithm(data)
    # new_result = new_algorithm(data)
    return new_algorithm(data)

# ✅ Clean
def process_data(data):
    return new_algorithm(data)
```

**Cleanup:** Delete. If you need history, it's in git.

### Pattern 2: Type Ignore Without Reason
```python
# ❌ Debt
x = some_function()  # type: ignore

# ✅ Good
x: SomeType = some_function()  # type: ignore - Dynamic attribute access needed
```

**Cleanup:** Add explanation or fix type issue.

### Pattern 3: Hardcoded Configuration
```python
# ❌ Debt
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30
API_URL = "https://api.example.com"

# ✅ Clean
from pydantic_settings import BaseSettings

class Config(BaseSettings):
    max_retries: int = 3
    timeout_seconds: int = 30
    api_url: str  # From env var
```

**Cleanup:** Move to pydantic-settings config.

### Pattern 4: Silent Error Handling
```python
# ❌ Debt
try:
    result = risky_operation()
except Exception:
    pass  # Silently fail
return None

# ✅ Clean
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise or handle explicitly
return result
```

**Cleanup:** Remove silent failures, add logging, re-raise or handle explicitly.

### Pattern 5: Code Duplication
```python
# ❌ Debt (appears 3 times)
if data["status"] == "active":
    user = get_user(data["id"])
    update_cache(user)
    log_event("user_loaded", user.id)

# ✅ Clean (extract function)
def load_active_user(data: dict) -> User:
    user = get_user(data["id"])
    update_cache(user)
    log_event("user_loaded", user.id)
    return user
```

**Cleanup:** Extract helper function, reuse everywhere.

---

## Decision Tree

**Is this blocking a release?**
- YES: Fix immediately (P0)
- NO: Schedule appropriately

**High impact + Low effort?**
- YES: Do it now
- NO: Schedule for next sprint

**Comments or commented code?**
- YES: Delete immediately (git has history)
- NO: Keep if non-obvious

**Type: ignore without explanation?**
- YES: Add explanation or fix
- NO: Good as-is

**Duplicate code?**
- YES: Extract and reuse
- NO: Continue

---

## Tech Debt Reduction Goals

**Q2 2026:**
- [ ] Remove all commented code
- [ ] Explain or fix all `type: ignore` patterns
- [ ] Move all hardcoded config to settings
- [ ] Reduce max function length to 30 lines
- [ ] Reduce average complexity to < 5

**Q3 2026:**
- [ ] Achieve 90% type coverage
- [ ] Document all complex algorithms
- [ ] 100% docstring coverage on public APIs
- [ ] All functions < 20 lines average

---

## Monthly Report Template

```markdown
# Tech Debt Cleanup Report - April 2026

## Summary
- Total items found: X
- Cleaned up: X
- Remaining: X
- Trend: [Improving / Stable / Worsening]

## Cleanups This Month
- [Item 1] (15 min) ✅
- [Item 2] (1 hour) ✅

## Remaining High Priority
- [Item 3] (2 hours)
- [Item 4] (4 hours)

## Metrics
- Total debt time estimate: X hours
- Code quality index: X/100
- Type coverage: X%

## Next Month Focus
- [Focus area 1]
- [Focus area 2]
```

