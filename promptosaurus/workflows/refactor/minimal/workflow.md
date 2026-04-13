---
name: "refactor"
version: 1.0
languages: [all]
subagents: [code/refactor, test/unit, review/code]
---

# Refactor Workflow (Minimal)

## Step 1: Define Scope

- Identify the code smell: long method, duplicate code, god object, magic numbers
- State the goal: improve readability, reduce duplication, or simplify logic
- Define what is NOT changing (external behavior, API contracts)
- Limit scope to smallest change that achieves goal

## Step 2: Write Tests First

- Add tests for current behavior if missing
- Ensure all existing tests pass before refactoring
- Target: 80%+ coverage on code being refactored
- Tests act as safety net during changes

## Step 3: Make Smallest Change

- Refactor in tiny increments (one method extraction at a time)
- Run tests after each micro-change
- Commit after each successful test run
- Use IDE refactoring tools (Extract Method, Rename, Inline)

## Step 4: Verify Tests Still Pass

- Run full test suite after each change
- If tests fail, revert immediately and try smaller step
- Check that no new warnings or errors appear
- Verify performance hasn't degraded (if critical path)

## Step 5: Document and Review

- Add comments explaining non-obvious decisions
- Update related documentation if behavior surface changed
- Self-review changes before requesting team review
- Note any follow-up refactoring opportunities in TODO comments
