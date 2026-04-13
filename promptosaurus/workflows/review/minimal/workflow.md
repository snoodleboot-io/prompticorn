---
name: "review"
description: Streamlined code review process
languages: [all]
subagents: [review/code, review/security, review/compliance]
steps:
  - Review code against patterns
  - Check test coverage
  - Verify error handling
  - Validate security
  - Approve or request changes
---

## Code Review Workflow

### Step 1: Review code against patterns
Check code follows core-conventions.md and matches existing patterns in the codebase.

### Step 2: Check test coverage
Verify test coverage targets are met and tests properly validate behavior.

### Step 3: Verify error handling
Ensure errors are properly caught, logged, and handled with appropriate context.

### Step 4: Validate security
Check for security vulnerabilities, secrets management, and access control.

### Step 5: Approve or request changes
Provide feedback: approve for merge or request specific changes before approval.
