---
name: test-mocking-rules
description: Guidelines for when and how to use mocks in tests
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
subagents: [test/unit, test/integration]
tools_needed: []
---

## Mocking Rules

### When to Mock
- Mock only at process boundaries:
  - Database connections
  - Network calls (HTTP, external APIs)
  - Filesystem operations
  - Time/date functions
  - Random number generation

### What NOT to Mock
- **Never mock the thing under test**
- **Never mock internal helpers** — test them through the public interface
- **Never mock your own database** in integration tests

### Consistency
- Use the mock library from core-conventions.md consistently
- Follow the same mocking patterns across the codebase
