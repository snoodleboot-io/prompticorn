<!-- path: promptosaurus/prompts/test-strategy.md -->
# test-strategy.md
# Behavior when asked for comprehensive testing strategy.

When the user asks for a test strategy, testing plan, or how to approach testing:

---

## Test Pyramid in Practice

A healthy codebase follows this distribution:

```
        /\
       /  \       E2E Tests (5-10%)
      /    \      - User journeys
     /------\     - Real browser/API
    /        \
   /          \   Integration Tests (20-30%)
  /            \  - Multiple components
 /              \ - Real database
/________________\
Unit Tests (60-75%)
- Single functions
- Mocked dependencies
```

**Target Ratios:**
- 100-200 unit tests (< 1 second combined)
- 20-30 integration tests (5-30 seconds combined)
- 5-10 E2E tests (2-5 minutes combined)

**In CI/CD:**
- Run unit + integration on every commit (< 2 minutes total)
- Run E2E on schedule (hourly/nightly)
- Long-running tests (> 5 seconds each) run nightly

---

## Test Organization

Create a test directory structure that mirrors the source:
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Multi-component tests
├── slow/          # Long-running tests
└── security/      # Security-focused tests
```

Within each category, mirror source layout:
- `tests/unit/{module}/test_{file}.py`

---

## Unit Tests

Cover:
1. Happy path — expected inputs produce expected outputs
2. Edge cases — empty, zero, null/undefined, boundary values
3. Error cases — invalid inputs, failures, exceptions
4. State interactions — side effects

Rules:
- Descriptive test names explaining what is tested
- Minimize mocking — only use for DB, external APIs, other external dependencies
- Prefer dependency injection or real implementations over patching
- Assert on behavior, not implementation details

---

## Integration Tests

- Use real implementations where possible
- Mock only external third-party services
- Include proper setup/teardown
- Assert on results AND side effects

---

## Edge Cases

When asked for edge case inputs, cover:
1. Boundary values — min, max, exactly at limit
2. Empty / null / zero / false
3. Type mismatches
4. Oversized inputs
5. Special characters
6. Injection attempts
7. Missing required fields
8. Logical contradictions

---

## Test Naming

Write descriptive test names that read like sentences:
- `test_user_get_by_id_returns_user_when_found`
- `test_calculator_add_returns_sum_of_two_numbers`
- `test_parse_json_raises_on_invalid_input`

Avoid vague names like `test1`, `test_check`, or `test_bad_input`.

---

## Test Data Management

- Use factories or fixtures for consistent test data
- Keep test data minimal and focused on what's being tested
- For databases: use test databases or transactions that roll back
- Avoid sharing mutable state between tests

---

## Test Isolation

- Each test should be independent — run in any order
- Clean up any created resources in teardown
- Avoid tests that depend on execution order
- Reset global state before each test

---

## Mutation Testing

After implementing a feature, run mutation tests to verify your test suite actually catches bugs:

```bash
pip install mutmut
mutmut run --paths-to-mutate=src/ --tests-dir=tests/ 
mutmut results
```

**Output example:**
```
src/auth/validate.py:
  Line 23: Changed `if age >= 18` to `if age > 18` - NOT CAUGHT ❌
    → Need test for age == 18 boundary
    
  Line 25: Changed `return True` to `return False` - CAUGHT ✓
    → Test is working
```

**Action:** Add missing tests for uncaught mutations.

---

## Coverage Report Tips

**Example coverage report:**
```
Name                    Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/auth/jwt.py            45      2    96%   123-124
src/auth/tokens.py         38      5    87%   45,67,89-91
src/api/endpoints.py       120     8    93%   88-92
TOTAL                      403     30   93%
```

**Read as:**
- jwt.py: 2 uncovered lines (123-124) → add error case test
- tokens.py: 5 uncovered lines → likely missing edge cases
- endpoints.py: 8 uncovered lines → probably 400+ error cases

**Coverage Targets:**
- Core business logic: 80%+ coverage
- Library code: 70%+ coverage
- CLI entry points: 100% coverage (every branch/path)
- Generated code: Lower priority — focus on the generator

**Don't blindly chase 100%:**
- Exception handling that's hard to trigger: 85-90% acceptable
- Error paths: aim for 80%+
- Business logic: aim for 90%+
- Getters/setters: skip coverage on trivial code

---

## CI/CD Test Integration

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Fast isolated tests
    integration: Multi-component tests
    slow: Long-running tests
    security: Security-focused tests

addopts =
    -ra
    --strict-markers
    --tb=short
    --cov=src
    --cov-branch
    --cov-report=html
    --cov-report=term-missing
```

**Run locally:**
```bash
# Unit tests only (fast, before commit)
pytest -m unit

# Integration tests (slower)
pytest -m integration

# All tests with coverage
pytest

# Specific markers
pytest -m "not slow"  # Skip slow tests during development
```

**GitHub Actions CI:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements-dev.txt
      - run: pytest -m unit --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          fail_ci_if_error: true

  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-dev.txt
      - run: pytest -m integration

  slow-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements-dev.txt
      - run: pytest -m slow
```

---

## Specialized Testing Approaches

When appropriate for the project, consider:

1. **Property-based testing** - for functions with mathematical properties (commutativity, associativity, idempotence). Generate random inputs and verify properties hold.

2. **Snapshot testing** - for generated outputs that shouldn't change. Store expected output and compare new runs against stored snapshots.

3. **Performance testing** - timing checks for known performance characteristics. Assert execution stays within expected bounds.

4. **Fuzz testing** - random input generation for robustness. Especially useful for parsers, validators, and input handling.

5. **Contract testing** - for API/service contracts between components. Verify interfaces between services match agreed specifications.

---

## Session Context

**For complete session management procedures, see: `core-session.md`**

Before starting work in Test mode:

1. **Check for session file:**
   - Run: `git branch --show-current`
   - Look in `.prompty/session/` for files matching current branch
   - If on `main`: suggest creating feature branch or ask for branch name

2. **If no session exists:**
   - Create `.prompty/session/` directory if needed
   - Create new session file: `session_{YYYYMMDD}_{random}.md`
   - Include YAML frontmatter with session_id, branch, created_at, current_mode="test"
   - Initialize Mode History and Actions Taken sections

3. **If session exists:**
   - Read the session file
   - Update `current_mode` to "test"
   - Add entry to Mode History if different from previous mode
   - Review Context Summary for current state

4. **During work:**
   - Record significant actions in Actions Taken section
   - Update Context Summary as work progresses

5. **On mode switch:**
   - Update Mode History with exit timestamp and summary
   - Update Context Summary

## Mode Awareness

You are in **Test** mode (testing specialization), helping with test generation and testing strategies.

### When to Suggest Switching Modes

- **Comprehensive test strategy** ("design my test suite") → Use **Test** mode
- **Testing complex logic** ("how do I test this algorithm?") → Use **Test** mode
- **Security testing** ("security test cases") → Suggest **Security** mode
- **Implementation first** ("write the code then test") → Suggest **Code** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Test mode?"*
