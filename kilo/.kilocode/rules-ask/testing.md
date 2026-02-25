# ask-testing.md
# Behavior when the user asks to generate tests.

When the user asks to generate unit tests, integration tests, or edge case inputs:

## Unit Tests

Generate tests using the framework and mock library from core-conventions.md.
Style: Arrange-Act-Assert (AAA).

Cover:
1. Happy path — expected inputs produce expected outputs
2. Edge cases — empty inputs, zero, null/undefined, boundary values
3. Error cases — invalid inputs, dependency failures, network errors
4. State interactions — side effects, DB writes, external calls (use mocks)

Rules:
- Descriptive test names: it("returns null when user is not found")
- Mock only what crosses a boundary (DB, network, filesystem, time)
- Assert on specific behavior, not implementation details
- After generating, list any cases that could not be covered due to missing context
- Flag code that is difficult to test and suggest a refactor to improve testability

## Integration Tests

For service boundary or end-to-end tests:
- Use a real test database, not mocks, for DB-touching tests
- Mock only external third-party services
- Set up and tear down test data in beforeEach / afterEach
- Assert on both the response AND the resulting database state
- Cover auth/permission boundaries

## Edge Cases & Adversarial Inputs

When asked to generate edge case inputs:
Generate inputs across these categories:
1. Boundary values — min, max, exactly at limit, one over limit
2. Empty / null / zero / false
3. Type coercion — "1" instead of 1, "true" instead of true
4. Oversized inputs — very long strings, large numbers, deeply nested objects
5. Special characters — unicode, emoji, RTL, null bytes, newlines
6. Injection attempts — SQL fragments, script tags, path traversal
7. Missing required fields — each absent one at a time
8. Logical contradictions — end date before start date, negative quantities

Output as a structured list with expected behavior per input, not as test code.
