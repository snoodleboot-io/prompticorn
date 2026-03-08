<!-- path: promptosaurus/prompts/agents/ask/subagents/ask-testing.md -->
# Subagent - Ask Testing

Behavior when the user asks to generate tests.

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

### Test Naming

Write descriptive test names that read like sentences:
- `test_user_get_by_id_returns_user_when_found`
- `test_calculator_add_returns_sum_of_two_numbers`
- `test_parse_json_raises_on_invalid_input`

Avoid vague names like `test1`, `test_check`, or `test_bad_input`.

### Test Data Management

- Use factories or fixtures for consistent test data
- Keep test data minimal and focused on what's being tested
- For databases: use test databases or transactions that roll back
- Avoid sharing mutable state between tests

### Test Isolation

- Each test should be independent — run in any order
- Clean up any created resources in teardown
- Avoid tests that depend on execution order
- Reset global state before each test

### Async Testing

When testing async code:
- Ensure async functions are properly awaited
- Test both success and error paths
- Use async test utilities provided by the framework

### CI/CD Integration

Run tests in pipelines:
- Fail CI if any test fails
- Generate coverage reports
- Run slow tests on schedule, not every commit
- Use test markers to filter what runs in CI vs local

### Mutation Testing

To verify test quality:
- Introduce small bugs (mutations) into code
- Run tests — they should catch the mutation
- Low mutation score means tests aren't catching bugs
- Use tools like `mutmut` (Python) or `Stryker`

### Specialized Testing Approaches

When appropriate for the project, consider:
- Property-based testing (e.g., Hypothesis, fast-check)
- Contract testing for API boundaries
- Load testing for performance-critical paths
- Fuzzing for input validation
