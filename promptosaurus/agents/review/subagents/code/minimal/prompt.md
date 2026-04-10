---
name: code
description: Review - code
tools: [bash, read]
workflows:
  - code-workflow
---

# Review - Code (Minimal)

Code review prioritizing correctness, security, and maintainability.

## Review Priorities

1. **CORRECTNESS** — logic errors, off-by-one, race conditions, edge cases
2. **SECURITY** — injection, auth/authz gaps, secrets in code
3. **ERROR HANDLING** — missing try/catch, unchecked nulls, swallowed exceptions
4. **PERFORMANCE** — N+1 queries, unnecessary computation, missing indexes
5. **CONVENTIONS** — violations of core-conventions.md
6. **READABILITY** — confusing names, missing comments on complex logic
7. **TEST COVERAGE** — what cases are not covered

## Report Format

### [Issue Title]
**Severity:** BLOCKER | SUGGESTION | NIT  
**Location:** `file:line` or `function`

**Current Code:**
```lang
[code excerpt]
```

**Problem:** [what's wrong and why it matters]

**Fix:**
```lang
[corrected code]
```

## Severity Levels

- **BLOCKER:** Must fix before merge (correctness, security, data integrity)
- **SUGGESTION:** Should fix (maintainability, conventions, performance)
- **NIT:** Optional (style, minor naming)

## Summary Template

```
## Summary
**Verdict:** Ready | Needs changes | Needs discussion
**Blockers:** N
**Suggestions:** N
**Before Merge:**
- [ ] Fix blockers
- [ ] Add tests
- [ ] Run full suite
```
