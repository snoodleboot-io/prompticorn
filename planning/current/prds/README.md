# Product Requirements Documents - Current

This directory contains PRDs for projects currently in scope.

## Purpose

PRDs define project-level requirements:
- **Vision**: What are we building and why?
- **Goals**: What success looks like
- **Scope**: What's in and out of scope
- **User Needs**: Who are we building for?
- **Requirements**: High-level functional and non-functional requirements
- **Timeline**: Project phases and milestones

## File Naming Convention

```
{project_name}.prd.md
{PHASE}_{project_name}.prd.md
```

Examples:
- `agent_framework.prd.md`
- `PHASE3_workflow_system.prd.md`

## PRD vs Feature Spec

| PRD | Feature Spec |
|-----|--------------|
| Project-level | Feature-level |
| Multiple features | Single feature |
| Strategic | Tactical |
| Why and what | What and how |
| Phases and milestones | Tasks and acceptance criteria |

## Template Structure

```markdown
# PRD: [Project Name]

## Vision
[What we're building and why it matters]

## Goals
- Goal 1
- Goal 2

## Scope
### In Scope
- Item 1
- Item 2

### Out of Scope
- Item 1
- Item 2

## User Needs
[Who are we building for? What problems do they have?]

## Requirements
### Functional
- Requirement 1
- Requirement 2

### Non-Functional
- Performance
- Security
- Usability

## Timeline
- Phase 1: [Milestone]
- Phase 2: [Milestone]

## Success Metrics
- Metric 1
- Metric 2
```

## Lifecycle

1. **Creation**: PRD written at project start
2. **Refinement**: Updated as understanding deepens
3. **Implementation**: Referenced during development
4. **Completion**: Moved to `../../complete/prds/` when project ships

## Related Documentation

- `../features/` - Individual feature specs (derived from PRD)
- `../execution-plans/` - Implementation plans
- `../adrs/` - Architecture decisions
