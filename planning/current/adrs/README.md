# Architecture Decision Records (ADRs) - Current

This directory contains Architecture Decision Records for active work.

## Purpose

ADRs document significant architectural and technical decisions made during development.
They capture:
- **Context**: Why the decision was needed
- **Options**: What alternatives were considered
- **Decision**: What was chosen
- **Consequences**: Trade-offs and implications

## When to Create an ADR

Create an ADR when:
- Making a significant technical decision (database choice, framework selection)
- Choosing between competing architectural approaches
- Adopting new patterns or practices
- Making trade-offs that future developers need to understand

## File Naming Convention

```
{YYYYMMDD}_{decision_topic}.adr.md
```

Examples:
- `20260401_database_selection.adr.md`
- `20260415_async_execution_model.adr.md`
- `20260420_authentication_strategy.adr.md`

## Template

See `../.kilo/rules/decision-log-template.md` for the ADR template.

## Lifecycle

1. **Creation**: ADR created during planning/design phase
2. **Active**: Referenced during implementation
3. **Completion**: Moved to `../../complete/adrs/` when work finishes
4. **Reference**: Historical record of why decisions were made

## Related Documentation

- `../../complete/adrs/` - Completed ADRs
- `../../backlog/adrs/` - Exploratory ADRs for future work
