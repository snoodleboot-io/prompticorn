# Planning Directory

This directory contains all AI-generated and user-added development planning materials.

## Purpose

The planning directory separates internal development artifacts from user-facing documentation.
This ensures clarity between:
- **What we're building** (planning)
- **What we've built** (docs)

## Structure

```
planning/
├── current/      # In-scope work (active backlog and current phase)
├── complete/     # Finished work and delivered phases
├── backlog/      # Future work (backlog, not in current scope)
└── research/     # Research and analysis used for planning
```

## Subdirectory Contents

Each phase directory (`current/`, `complete/`, `backlog/`) contains:

- **adrs/** - Architecture Decision Records (design decisions during planning)
- **execution-plans/** - Phase/sprint execution plans and task breakdowns
- **features/** - Feature specifications and requirements
- **prds/** - Product/project requirements documents

## Usage

### During Active Development
- Place planning documents in `current/`
- Update execution plans as work progresses
- Record decisions in `current/adrs/`

### When Work Completes
- Move planning artifacts from `current/` to `complete/`
- This preserves historical context without cluttering active workspace

### For Future Work
- Place speculative features in `backlog/`
- Move to `current/` when prioritized and scoped

## Note

**This directory is NOT user-facing.**

It contains internal development planning and decision-making artifacts.
For user documentation, see `../docs/`

## Related Documentation

- `../docs/` - User-facing documentation and guides
- `../_temp/` - Ephemeral working files (not committed)
