---
name: test-coverage-categories
description: Systematic approach to achieving comprehensive test coverage
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
subagents: [test/unit, test/integration, code/feature]
tools_needed: [read, write]
---

## Coverage Categories

Work through these categories in order for comprehensive coverage:

1. **HAPPY PATH** — Expected inputs produce expected output
2. **BOUNDARY VALUES** — Min, max, exactly at limit, one over limit
3. **EMPTY / NULL / ZERO** — Each nullable input absent or zeroed
4. **ERROR CASES** — Dependency throws, network fails, DB unavailable
5. **CONCURRENT / ORDERING** — If function has state, test ordering
6. **AUTHORIZATION BOUNDARIES** — Does it enforce who can call it?
7. **ADVERSARIAL INPUTS** — SQL fragments, script tags, path traversal, unicode, emoji, null bytes, extremely long strings

### Workflow
- Check off each category as you implement tests
- Document which categories don't apply and why
- Flag any gaps in coverage with rationale


