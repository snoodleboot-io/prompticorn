---
name: testing
version: 1.0
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
subagents: [test/unit, test/integration, code/feature]
---

# Testing Workflow (Minimal)

## Step 1: Happy Path Tests

- Test primary use case with valid inputs
- Assert on expected outputs AND side effects
- Use descriptive test names: `test_user_login_succeeds_with_valid_credentials`
- Keep tests independent - no shared mutable state

## Step 2: Boundary Values

- Test min/max values, exactly at limits
- Empty collections, zero values, single element
- First and last items in sequences
- Timestamps at edge of valid ranges

## Step 3: Empty/Null Cases

- Test with null/undefined/None for nullable parameters
- Empty strings, empty arrays, empty objects
- Missing optional fields in request bodies
- Verify appropriate defaults or error handling

## Step 4: Error Cases

- Invalid inputs trigger appropriate exceptions
- Malformed data returns clear error messages
- External service failures are handled gracefully
- Assert on error type AND error message content

## Step 5: Coverage Verification

- Run coverage tool: `pytest --cov` or `vitest --coverage`
- Target: 80%+ line coverage, 70%+ branch coverage
- Identify untested paths in coverage report
- Add tests for critical uncovered branches

## Step 6: Test Isolation

- Each test cleans up resources (DB transactions, temp files)
- Tests pass in any order
- Mock external dependencies (APIs, databases, filesystem)
- Use fixtures/factories for consistent test data
