# Execution Plans - Current

This directory contains execution plans and task breakdowns for active work.

## Purpose

Execution plans provide:
- **Task Breakdown**: Detailed steps to complete a phase or feature
- **Timeline**: Expected duration and milestones
- **Dependencies**: What must complete before other tasks start
- **Status Tracking**: Progress on individual tasks

## File Naming Convention

```
PHASE{N}_{DESCRIPTION}.plan.md
{FEATURE_NAME}_execution.plan.md
```

Examples:
- `PHASE3_ROADMAP.plan.md`
- `PHASE2_EXECUTION_STATUS.plan.md`
- `auth_system_execution.plan.md`

## Contents

Typical execution plan includes:
- **Objective**: What we're building
- **Task Breakdown**: Numbered, prioritized tasks
- **Timeline**: Expected completion dates
- **Dependencies**: Task relationships
- **Status**: Current progress
- **Blockers**: Issues preventing progress

## Lifecycle

1. **Creation**: Plan created at start of phase/feature
2. **Active**: Updated as work progresses
3. **Completion**: Moved to `../../complete/execution-plans/` when phase finishes

## Status Indicators

Use checkboxes to track progress:
```markdown
- [ ] Task 1 - Not started
- [x] Task 2 - Complete
- [~] Task 3 - In progress (custom)
```

## Related Documentation

- `../../complete/execution-plans/` - Finished execution plans
- `../features/` - Feature specifications
- `../adrs/` - Architecture decisions
