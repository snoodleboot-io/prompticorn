# test-strategy.md
# Behavior when the user asks to write, run, or improve tests.

The goal of this mode is coverage and edge-case thinking — not just
making existing code pass. Think adversarially about what can break.

## Before Writing Any Tests

1. Read the source file(s) under test first — do not assume their shape.
2. Read core-conventions.md for the test framework and mock library.
3. Identify the public interface: what inputs go in, what outputs or
   side effects come out. Only test through that interface.
4. If the code is untestable as written, say so and suggest the minimal
   refactor needed before writing tests.

## Test Structure — Always AAA

Arrange: set up state and inputs
Act: call the thing under test
Assert: verify outputs and side effects

One logical assertion per test. One behavior per test name.

Test names must be descriptive sentences:
  it("returns null when the user ID does not exist")
  it("throws AuthError when the token is expired")

## Coverage Targets

Work through these categories in order:

1. HAPPY PATH — the expected inputs produce the expected output
2. BOUNDARY VALUES — min, max, exactly at limit, one over limit
3. EMPTY / NULL / ZERO — each nullable input absent or zeroed
4. ERROR CASES — dependency throws, network fails, DB is unavailable
5. CONCURRENT / ORDERING — if the function has state, test ordering
6. AUTHORIZATION BOUNDARIES — does it enforce who can call it?
7. ADVERSARIAL INPUTS — SQL fragments, script tags, path traversal,
   unicode, emoji, null bytes, extremely long strings

## Mocking Rules

- Mock only at process boundaries: DB, network, filesystem, time, randomness
- Never mock the thing under test
- Never mock internal helpers — test them through the public interface
- Use the mock library from core-conventions.md consistently

## Integration Tests

- Use a real test database — never mock it for integration tests
- Mock only external third-party services (payment APIs, email, etc.)
- Set up and tear down all test data in beforeEach / afterEach
- Assert on both the HTTP response AND the resulting database state
- Always test auth boundaries: unauthenticated, wrong role, correct role

## After Generating Tests

- List any cases that could not be covered and why
- Flag any code paths that are impossible to test without a refactor
- Note what the coverage percentage will approximately be
- Suggest which tests to run first to get the fastest signal on regressions
