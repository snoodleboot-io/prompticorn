# Refactoring Plan: Move kilo_modes to Builder

## Current Architecture

### Problem
- `kilo_modes` is currently defined in `promptosaurus/registry.py` (lines 287-393)
- It's shared between CLI and IDE builders, but each has different filtering needs
- The user wants to move this to the builder classes and load from YAML files

### Current Data Flow
```
registry.kilo_modes (dict)
    ↓
KiloCodeBuilder._write_manifest()
    ↓
Writes .kilocodemodes file
```

### Current Usage
- **CLI Builder**: Uses `registry.modes.keys()` filtered by `KILO_BUILTIN_MODES` → `custom_modes`
- **IDE Builder**: Same, uses `custom_modes` for file generation
- **Both**: Use `registry.kilo_modes` in `_write_manifest()` to generate manifest

## Proposed Changes

### 1. Create YAML file: `promptosaurus/builders/kilo_builtin_modes.yaml`

This file will contain the mode definitions currently in `registry.kilo_modes`:

```yaml
# Builtin mode definitions for Kilo IDE/CLI
modes:
  architect:
    name: "🏗️ Architect"
    description: "System design, architecture planning..."
    roleDefinition: "You are a principal architect..."
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
  # ... rest of modes
```

### 2. Modify `KiloCodeBuilder` in `kilo.py`

- Add class variable `KILO_BUILTIN_MODES` (already exists, rename from `KILO_BUILTIN_MODES` to be consistent)
- Add class variable `_kilo_modes: dict` (loaded from YAML)
- Add classmethod or staticmethod to load from YAML file
- Add `@property` for `kilo_modes` that returns loaded modes

### 3. Handle CLI vs IDE filtering

**CLI Builder** (`kilo_cli.py`):
- Should generate files for only custom modes (exclude built-in Kilo modes: architect, code, ask, debug, orchestrator)
- This is already working via `custom_modes` property

**IDE Builder** (`kilo_ide.py`):
- Should include ALL modes in `.kilocodemodes` manifest (including built-in)
- Currently generates files for custom modes (same as CLI)
- But the manifest should include all modes

### 4. Update `registry.py`

- Remove `kilo_modes` dict (lines 287-393)
- Keep the rest of the registry functionality

## Implementation Steps

1. **Create YAML file** with mode definitions
2. **Modify `KiloCodeBuilder`** to load modes from YAML
3. **Update `KiloCLIBuilder`** - may need adjustments
4. **Update `KiloIDEBuilder`** - may need adjustments for manifest
5. **Update `registry.py`** to remove `kilo_modes`
6. **Test both CLI and IDE builds**

## Notes

- `KILO_BUILTIN_MODES` in kilo.py is separate from `kilo_modes` - it's used to filter which modes get generated as files
- `kilo_modes` contains full mode definitions including roleDefinition, groups, etc.
- The YAML file should be in the `builders/` directory alongside the builder classes
