# Architecture Decision Records - Backlog

This directory contains exploratory ADRs for future work.

## Purpose

Capture architectural explorations and decision-making for features not yet in scope:
- **Exploration**: Investigate potential approaches
- **Options**: Document alternatives before commitment
- **Rough Decisions**: Tentative choices pending prioritization
- **Research**: Record findings for future reference

## Status

**EXPLORATORY**: These are not final decisions.

ADRs here are:
- Not yet approved for implementation
- Subject to change
- Useful for future planning
- May be abandoned if priorities shift

## File Naming Convention

Consider status prefixes:
```
DRAFT_{YYYYMMDD}_{decision_topic}.adr.md
PROPOSED_{YYYYMMDD}_{decision_topic}.adr.md
```

Examples:
- `DRAFT_20260501_nosql_migration.adr.md`
- `PROPOSED_20260515_graphql_adoption.adr.md`

## Lifecycle

1. **Creation**: Exploratory ADR for future feature
2. **Refinement**: Update as more information becomes available
3. **Promotion**: Move to `../../current/adrs/` when prioritized
4. **Abandonment**: Delete if no longer relevant

## Related Documentation

- `../../current/adrs/` - Approved, active ADRs
- `../features/` - Future feature specs
- `../../research/` - Supporting research
