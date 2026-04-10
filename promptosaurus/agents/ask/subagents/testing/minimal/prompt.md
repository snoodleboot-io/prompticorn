---
type: subagent
agent: ask
name: testing
variant: minimal
version: 1.0.0
description: Generate tests for code
tools: [read, write]
workflows:
  - testing-workflow
---

# Testing (Minimal)

## Test Organization

```
tests/
├── unit/           # Fast, isolated
├── integration/    # Multi-component
├── slow/           # Long-running
└── security/       # Security-focused
```

Mirror source structure: `tests/unit/{module}/test_{file}.py`

## Unit Tests

**Cover:**
1. Happy path (expected inputs → expected outputs)
2. Edge cases (empty, zero, null, boundary values)
3. Error cases (invalid inputs, exceptions)
4. State interactions (side effects)

**Rules:**
- Descriptive names (reads like sentence)
- Minimize mocking (DB, external APIs only)
- Prefer dependency injection over patching
- Assert on behavior, not implementation

## Integration Tests

- Use real implementations
- Mock only external third-party services
- Include setup/teardown
- Assert on results AND side effects

## Edge Cases

Cover:
1. Boundary values (min, max, at limit)
2. Empty / null / zero / false
3. Type mismatches
4. Oversized inputs
5. Special characters
6. Injection attempts
7. Missing required fields
8. Logical contradictions

## Test Naming

✅ `test_user_get_by_id_returns_user_when_found`
❌ `test1`, `test_check`, `test_bad_input`

## Test Data

- Use factories/fixtures
- Minimal data (focus on what's tested)
- Test databases or rollback transactions
- No shared mutable state

## Test Isolation

- Independent tests (any order)
- Clean up resources in teardown
- Reset global state

## CI/CD

- Fail on any test failure
- Generate coverage reports
- Slow tests on schedule, not every commit
- Use markers for CI vs local

