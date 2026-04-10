---
languages: ["markdown"]
subagents: ["ask", "architect"]
---

# Decision Log (ADR) Workflow (Minimal)

## 1. Gather Context
If not provided, ask for:
- What decision is being made?
- What problem does it solve?
- What alternatives were considered?
- Why was the chosen option selected?
- What are the risks or trade-offs?

## 2. Create ADR File
Store in `docs/decisions/` or `docs/adr/`:
```bash
# Naming: ADR-{number}-{title}.md
# Example: ADR-001-use-postgresql-over-mongodb.md
```

## 3. Write ADR Using Standard Format
```markdown
# ADR-{number}: {Title}

**Date:** YYYY-MM-DD
**Status:** Accepted | Proposed | Rejected | Superseded
**Deciders:** {Names or roles}

## Context
{Why is this decision needed? What problem exists?}

## Decision
{What was decided.}

## Alternatives Considered

### Option A: {Name}
**Pros:** ...
**Cons:** ...

### Option B: {Name}
**Pros:** ...
**Cons:** ...

## Consequences

**Positive:**
- ...

**Negative:**
- ...

**Risks:**
- ...

## Review Date
{When should this be revisited?}
```

## 4. Keep It Concise
- Readable in 3 minutes or less
- Focus on WHY, not HOW
- Write for someone who wasn't in the room
- Use bullet points over paragraphs

## 5. Link Related ADRs
Reference related decisions:
- Dependencies (what decisions led to this?)
- Superseded by (what decision replaced this?)
- Related (what other decisions are affected?)

## 6. Review and Store
- Get approval from relevant stakeholders
- Commit ADR to version control
- Update decision log index (if maintained)
- Set calendar reminder for review date
