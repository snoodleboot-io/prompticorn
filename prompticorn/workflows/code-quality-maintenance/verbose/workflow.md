# Code Quality Review Workflow
name: "code-quality-maintenance"

**Version:** 1.0  
**Cadence:** Per PR + Weekly Summary  
**Owner:** Engineering Team / Code Reviewers  
**Status:** Active

---

## Quick Reference

### Pre-Commit Checks (Automated)

```bash
# All of these run automatically on git commit
# (hooks configured in .git/hooks/pre-commit)

# 1. Formatting
ruff format .

# 2. Linting
ruff check . --fix

# 3. Type checking
pyright .

# 4. Test execution
pytest -q
```

### Manual PR Review Checklist

- [ ] Code follows naming conventions (snake_case, PascalCase)
- [ ] No hardcoded secrets or constants (use config)
- [ ] Tests added or updated
- [ ] Coverage hasn't dropped
- [ ] Docstrings on public functions
- [ ] No console.log or print statements (except logging)
- [ ] Error handling is explicit
- [ ] Code follows existing patterns
- [ ] No type: ignore without explanation
- [ ] Documentation updated

---

## Code Standards (Per-PR)

### Naming Conventions
- **Files:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions/methods:** `snake_case`
- **Constants:** Use pydantic-settings, not UPPER_CASE
- **Database tables:** `snake_case`

### Type Safety
- All public functions must have type hints
- No `Any` without explicit narrowing
- Use `T | None` not `Optional[T]`
- Verify with `pyright .` (strict mode)

### Testing Requirements
- Unit tests: 80%+ coverage
- Integration tests: Cover API contracts
- New code: Must have tests
- Coverage: Don't decrease from PR

### Error Handling
- Never catch Exception (too broad)
- Always include context in errors
- Log failures, don't swallow
- Document expected exceptions

### Documentation
- Public functions: Docstring required
- Complex logic: Inline comments explaining WHY
- Anti-patterns: Document why you're not doing it
- Non-obvious choices: Flag with TODO comment

---

## Automated Checks

### Ruff (Linting + Formatting)
```bash
# Format code
ruff format .

# Check for issues
ruff check . --fix

# Specific rule
ruff check . --select E501  # Line too long
```

**Fail if:**
- F401: Unused imports
- E501: Line > 100 chars (after format, use # noqa if necessary)
- W291: Trailing whitespace
- E302: Missing blank lines between functions

### Pyright (Type Checking)
```bash
# Run type checker in strict mode
pyright .

# Check specific file
pyright prompticorn/module.py

# Show diagnostics
pyright . --outputjson | jq .
```

**Fail if:**
- Any type errors (red)
- `unknown` without narrowing
- Missing type annotations on public functions

### Tests
```bash
# Run test suite with coverage
pytest --cov -q

# Fail if:
# - Any test failures
# - Coverage drops from baseline
```

---

## Weekly Code Quality Report

**Template:**
```markdown
# Code Quality Summary - Week of YYYY-MM-DD

## Pull Requests Reviewed
- Total: X
- Approved: X
- Requested changes: X
- Issues found: X

## Common Issues This Week
- [Issue type]: X occurrences
- [Issue type]: X occurrences

## Code Standards Compliance
- Type coverage: X%
- Test coverage: X%
- Ruff issues: X (fixed)
- Linting failures: X (fixed)

## Improvements Made
- [Improvement]
- [Improvement]

## Standards Not Met (Follow-up)
- [PR or file needing attention]
- [PR or file needing attention]

## Next Week Focus
- [Focus area]
```

---

## PR Review Workflow

### 1. Automated Checks (5 min)
- [ ] All CI checks green
- [ ] No new ruff violations
- [ ] Type checking passes
- [ ] Tests passing
- [ ] Coverage not decreased

### 2. Code Review (10-15 min)
- [ ] Follows naming conventions
- [ ] Type-safe (no Any without reason)
- [ ] Includes tests
- [ ] Has docstrings where needed
- [ ] Error handling explicit
- [ ] Matches existing patterns
- [ ] No hardcoded config/secrets

### 3. Testing Review (5 min)
- [ ] Unit tests included
- [ ] Edge cases covered
- [ ] Integration tests if needed
- [ ] Coverage >= 80%
- [ ] Test names are descriptive

### 4. Documentation (3 min)
- [ ] Docstrings on public functions
- [ ] Complex logic explained
- [ ] Dangerous patterns documented
- [ ] README updated if needed

### 5. Approval Decision
- **Approve:** All checks green, code is clear
- **Request Changes:** Specific issues listed
- **Comment:** Questions that need clarification

---

## Common Issues & Fixes

### Type Error: No Return Type Annotation
```python
# ❌ Bad
def validate_user(data):
    return User.from_dict(data)

# ✅ Good
def validate_user(data: dict) -> User:
    return User.from_dict(data)
```

### Test Coverage Below 80%
- Add tests for uncovered lines
- Use pytest --cov to identify gaps
- Test error paths, not just happy path

### Hardcoded Configuration
```python
# ❌ Bad
API_KEY = "secret-key-here"

# ✅ Good
from pydantic_settings import BaseSettings
class Config(BaseSettings):
    api_key: str  # From env var
```

### Unused Import
```python
# ❌ Bad
import os  # Imported but never used

# ✅ Good
# Remove unused imports, ruff check will catch
```

---

## When to Request Changes vs Approve

### Request Changes (Author needs to revise)
- Missing required tests
- Type errors or missing annotations
- Coverage decreased
- Code doesn't follow conventions
- Unsafe error handling
- Hardcoded secrets/config

### Approve (Author may merge)
- All automated checks pass
- Code clear and follows standards
- Tests comprehensive
- Documentation complete
- No unresolved conversations

### Comment (Discussion, no block)
- "Consider X for readability"
- "Alternative approach: Y"
- "Related: see PR #123"

