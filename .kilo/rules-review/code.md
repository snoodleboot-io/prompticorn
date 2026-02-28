<!-- path: flat/review-code.md -->
# review-code.md
# Behavior when the user asks for a code review.

When the user asks to review code, a diff, or a pull request:

Review in this priority order:

1. CORRECTNESS — logic errors, off-by-one errors, race conditions, unhandled edge cases
2. SECURITY — injection risks, auth/authz gaps, secrets in code, unsafe deserialization
3. ERROR HANDLING — missing try/catch, unchecked nulls, swallowed exceptions
4. PERFORMANCE — N+1 queries, unnecessary computation in hot paths, missing indexes
5. CONVENTIONS — violations of core-conventions.md
6. READABILITY — confusing names, missing comments on complex logic, dead code
7. TEST COVERAGE — what cases are not covered by the accompanying tests

For each issue found, report:
- Severity: BLOCKER / SUGGESTION / NIT
- Location: filename and line reference or function name
- What is wrong
- Suggested fix (with code if non-trivial)

Severity definitions:
- BLOCKER: must fix before merge — correctness, security, or data integrity issue
- SUGGESTION: should fix — degrades maintainability or violates conventions
- NIT: optional — style preference, no functional impact

End with a summary verdict: Ready to merge / Needs changes / Needs discussion.

If the user has not provided context about what the code does, ask before reviewing.
