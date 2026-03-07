# PRD: Builder Architecture Refactoring

## Problem Statement

The `kilo_modes` dictionary containing mode definitions (roleDefinition, groups, etc.) is currently located in `promptosaurus/registry.py`. This creates several issues:

1. **Shared state problem**: `kilo_modes` is used by both `KiloCLIBuilder` and `KiloIDEBuilder`, but the filtering requirements differ between them
2. **Coupling**: The registry module shouldn't need to know about builder-specific mode definitions
3. **Maintainability**: Mode definitions are hardcoded in Python rather than being data-driven
4. **Extensibility**: Adding new modes requires modifying Python code rather than a data file

## Goals

1. Move `kilo_modes` from `registry.py` to the builder classes
2. Load mode definitions from a static YAML file in the `builders/` directory
3. Implement proper CLI vs IDE filtering - CLI uses filtered subset, IDE uses all modes
4. Remove `kilo_modes` from registry.py to decouple concerns

## Non-Goals

- Changing the actual mode behavior or functionality
- Adding new modes (just moving existing definitions)
- Modifying how modes are used in the runtime

## User Stories

- As a developer, I want mode definitions in a YAML file so that I can easily add or modify modes without changing Python code
- As a builder maintainer, I want different filtering logic for CLI vs IDE outputs so that each gets the appropriate modes
- As a system architect, I want to decouple the registry from builder-specific data so that changes don't ripple through unrelated modules

## Acceptance Criteria

- [ ] YAML file created at `promptosaurus/builders/kilo_builtin_modes.yaml` containing all mode definitions
- [ ] `KiloCodeBuilder` loads mode definitions from YAML file
- [ ] `kilo_modes` removed from `registry.py`
- [ ] CLI builder generates mode files only for custom modes (excludes built-in)
- [ ] IDE builder includes all modes in `.kilocodemodes` manifest
- [ ] Both builders continue to work correctly after refactoring
- [ ] No breaking changes to existing functionality

## Success Metrics

- Registry module no longer contains builder-specific mode definitions
- Mode definitions are loaded from YAML at class initialization time
- Both CLI and IDE builds produce correct output

## Timeline

- Target Date: TBD
- Milestones:
  1. Create YAML file with mode definitions: [date]
  2. Modify KiloCodeBuilder to load from YAML: [date]
  3. Update registry.py to remove kilo_modes: [date]
  4. Test CLI and IDE builds: [date]
