---
name: incremental-implementation
description: Implement code one file at a time following conventions
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
subagents: [code/feature, code/bug-fix, code/refactor]
tools_needed: [edit, write, read]
---

## Instructions

When implementing:

1. **Follow Core Conventions exactly** - match language/framework standards
2. **Match existing patterns** in the same code layer
3. **Add inline comments** for non-obvious logic
4. **Add TODO comments** for judgment calls requiring user review
5. **Implement one file at a time** - don't jump between files

This maintains code quality and consistency.

