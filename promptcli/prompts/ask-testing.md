<!-- path: promptcli/prompts/ask-testing.md -->
# ask-testing.md
# Behavior when the user asks to generate tests.

When the user asks to generate unit tests, integration tests, or edge case inputs:

---

## General Testing Principles (Language/Tooling Agnostic)

### Test Organization

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

### Unit Tests

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

### Integration Tests

- Use real implementations where possible
- Mock only external third-party services
- Include proper setup/teardown
- Assert on results AND side effects

### Edge Cases

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

## Python-Specific Testing

When working with Python projects:

### Framework
- Use `unittest.TestCase` for test classes
- Use `pytest` as the test runner

### Organization
- Add markers in `conftest.py`:
  - `@pytest.mark.unit`
  - `@pytest.mark.integration`
  - `@pytest.mark.slow`
  - `@pytest.mark.security`
- Auto-apply markers based on test directory

### Running Tests
```bash
# Full suite with coverage
pytest --cov={src} --cov-report=html --cov-report=term

# By marker
pytest -m unit
pytest -m integration
```
