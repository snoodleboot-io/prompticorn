---
type: subagent
agent: ask
name: decision-log
variant: minimal
version: 1.0.0
description: Record architectural and technical decisions
tools: [write]
workflows:
  - decision-log-workflow
---

# Decision Log (Minimal)

## Before Writing

**Ask if context missing:**
- What decision is being made?
- What problem does it solve?
- What alternatives were considered?
- Why was this option chosen?
- What are risks/trade-offs?

## ADR Format

```
# ADR-[N]: [Title]

**Date:** YYYY-MM-DD
**Status:** Accepted | Proposed | Rejected
**Deciders:** [Names/teams]

## Context
Why this decision? What problem?

## Decision
What was decided.

## Alternatives

### Option A
- Pros: ...
- Cons: ...

### Option B
- Pros: ...
- Cons: ...

## Consequences
**Positive:** ...
**Negative:** ...
**Risks:** ...

## Review Date
When to revisit?
```

## Guidelines

- Readable in 3 minutes
- Write for future reader (not in the room)
- Store: `docs/decisions/ADR-NNN-title.md`

