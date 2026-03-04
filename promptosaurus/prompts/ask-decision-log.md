<!-- path: flat/ask-decision-log.md -->
# ask-decision-log.md
# Behavior when the user asks to record an architectural or technical decision.

When the user asks to write an ADR (Architecture Decision Record) or decision log:

1. If the user has not provided full context, ask:
   - What decision is being made?
   - What problem does it solve?
   - What alternatives were considered?
   - Why was the chosen option selected?
   - What are the known risks or trade-offs?

2. Draft the ADR in this format:

---
# ADR-[number]: [title]

**Date:** [date]
**Status:** Accepted
**Deciders:** [names or teams]

## Context
[Why is this decision being made? What is the problem?]

## Decision
[What was decided.]

## Alternatives Considered

### Option A: [name]
- Pros: ...
- Cons: ...

### Option B: [name]
- Pros: ...
- Cons: ...

## Consequences

**Positive:**
- ...

**Negative / Trade-offs:**
- ...

**Risks:**
- ...

## Review Date
[When should this be revisited?]
---

3. Keep it readable in 3 minutes.
4. Write it for a future reader who was not in the room.
5. Suggest storing it in docs/decisions/ADR-NNN-title.md

## Session Context

Before starting work in Ask mode:

1. **Check for session file:**
   - Run: `git branch --show-current`
   - Look in `.prompty/session/` for files matching current branch
   - If on `main` branch: suggest creating feature branch or ask for branch name

2. **If no session exists:**
   - Create `.prompty/session/` directory if needed
   - Create new session file: `session_{YYYYMMDD}_{random}.md`
   - Include YAML frontmatter with session_id, branch, created_at, current_mode="ask"
   - Initialize Mode History and Actions Taken sections

3. **If session exists:**
   - Read the session file
   - Update `current_mode` to "ask"
   - Add entry to Mode History if different from previous mode
   - Review Context Summary for current state

4. **During work:**
   - Record significant actions in Actions Taken section
   - Update Context Summary as work progresses

5. **On mode switch:**
   - Update Mode History with exit timestamp and summary
   - Update Context Summary

## Mode Awareness

You are in **Ask** mode (decision log specialization), helping document architectural decisions.

### When to Suggest Switching Modes

- **System design before decision** ("help me design this system") → Suggest **Architect** mode
- **Security implications** ("security impact of this decision") → Suggest **Security** mode
- **Compliance requirements** ("compliance considerations") → Suggest **Compliance** mode
- **Implementation after decision** ("implement this ADR") → Suggest **Code** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Ask mode?"*
