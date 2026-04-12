# Feature Specifications - Current

This directory contains specifications for features currently being implemented.

## Purpose

Feature specs define:
- **User Value**: What problem does this solve?
- **Functional Requirements**: What must the feature do?
- **Non-Functional Requirements**: Performance, security, usability constraints
- **Acceptance Criteria**: How do we know it's done?
- **Implementation Notes**: Technical considerations

## File Naming Convention

```
{feature_name}.feature.md
{TICKET_ID}_{feature_name}.feature.md
```

Examples:
- `interactive_selection.feature.md`
- `PROJ-123_oauth_authentication.feature.md`

## Template Structure

```markdown
# Feature: [Name]

## Problem Statement
[What user problem are we solving?]

## User Stories
- As a [role], I want [capability], so that [benefit]

## Requirements
### Functional
- [ ] Requirement 1
- [ ] Requirement 2

### Non-Functional
- Performance: [criteria]
- Security: [criteria]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Notes
[Implementation considerations]
```

## Lifecycle

1. **Creation**: Feature spec written during planning
2. **Implementation**: Referenced during development
3. **Completion**: Moved to `../../complete/features/` when shipped

## Related Documentation

- `../prds/` - Project requirements (higher level)
- `../execution-plans/` - Task breakdowns
- `../adrs/` - Architecture decisions
