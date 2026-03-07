# ARD: Builder Architecture Refactoring

## Context

The `kilo_modes` dictionary containing mode definitions is currently in `promptosaurus/registry.py` (lines 287-393). This was originally designed for the IDE builder but is now needed by both CLI and IDE builders with different filtering requirements:

- **CLI Builder**: Should generate files only for custom modes (exclude built-in: architect, code, ask, debug, orchestrator)
- **IDE Builder**: Should include all modes in the `.kilocodemodes` manifest

The registry module should only contain registry-specific data (modes, mode_files, concat_order), not builder-specific definitions.

## Decision

Move `kilo_modes` from `registry.py` into the builder classes, loading from a static YAML file in the `builders/` directory.

### Implementation Approach

1. **Create YAML file** `promptosaurus/builders/kilo_builtin_modes.yaml` containing all mode definitions in this format:

```yaml
# Builtin mode definitions for Kilo IDE/CLI
modes:
  architect:
    name: "🏗️ Architect"
    description: "System design, architecture planning, and technical decision making"
    roleDefinition: "You are a principal architect specializing..."
    whenToUse: "Use this mode for system design..."
    groups:
      - read
      - browser
      - edit:
          fileRegex: "docs/.*\\.md$"
          description: "Documentation files"
      - edit:
          fileRegex: "\\.promptosaurus/sessions/.*\\.md$"
          description: "Session management files"
  test:
    name: "🧪 Test"
    description: "Write comprehensive tests with coverage-first approach"
    roleDefinition: "You are a principal test engineer..."
    whenToUse: "Use this mode when writing new tests..."
    groups:
      - read
      - edit
      - command
  # ... remaining modes follow same pattern
```

2. **Add class variable** to `KiloCodeBuilder` that loads from YAML at class definition time
3. **Provide access** via `kilo_modes` property on the builder classes
4. **Remove** `kilo_modes` from `registry.py`

## Alternatives Considered

### Alternative 1: Keep kilo_modes in registry.py
- **Pros**: No code changes needed, simple
- **Cons**: Tight coupling between registry and builders, same filtering for both builders
- **Decision**: Rejected - doesn't solve the problem of different filtering needs

### Alternative 2: Move to each builder class separately
- **Pros**: Complete separation
- **Cons**: Duplication of mode definitions between CLI and IDE builders
- **Decision**: Rejected - DRY violation

### Alternative 3: Move to YAML, load in base builder class (CHOSEN)
- **Pros**: Single source of truth, decoupled from registry, can be extended
- **Cons**: Need to handle YAML loading
- **Decision**: Accepted - best balance of concerns

## Consequences

### Positive
- Decoupled registry from builder-specific data
- Single YAML file for mode definitions (DRY)
- Easy to add/modify modes without code changes
- Clear separation of concerns
- CLI and IDE can have different filtering logic

### Negative / Tradeoffs
- Need to handle YAML loading and parsing
- Need to ensure YAML stays in sync with Python types
- Additional file to maintain

### Neutral
- The `LANGUAGE_FILE_MAP` could also be moved to YAML (future consideration)

## Risks and Mitigation

- **Risk**: YAML file not found at runtime
  - **Mitigation**: Use `Path(__file__).parent` for relative path, fail fast with clear error

- **Risk**: YAML structure doesn't match expected format
  - **Mitigation**: Validate structure when loading, provide clear error messages

- **Risk**: Backwards compatibility break
  - **Mitigation**: Test both CLI and IDE builds after changes

## Related Documents

- PRD: [`docs/prd/builder-architecture-refactoring.md`](docs/prd/builder-architecture-refactoring.md)
- Plan: [`plans/builder-refactoring-plan.md`](plans/builder-refactoring-plan.md)
