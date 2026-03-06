# Plan: KiloBuilder CLI/IDE Target Support - Revised

## Problem

The promptosaurus CLI needs to support two different output formats:
1. **CLI format** - Uses `opencode.json`, `.opencode/rules/`, `AGENTS.md`
2. **IDE format** (VSCode/JetBrains) - Uses `.kilo/rules-*`, `.kilocodemodes`

## Design

Instead of a single `KiloBuilder` with a target parameter, use separate builder classes - this is more SOLID (Single Responsibility Principle).

### New Class Structure

```
promptosaurus/builders/
├── __init__.py
├── builder.py           # Base Builder class
├── cline.py             # Existing
├── copilot.py           # Existing
├── cursor.py            # Existing
├── kilo.py              # KILOCodeBuilder (base for Kilo formats)
├── kilo_cli.py          # NEW: KiloCLIBuilder
└── kilo_ide.py          # NEW: KiloIDEBuilder
```

### Classes

1. **`KiloCodeBuilder`** (new base class in `kilo.py`)
   - Common functionality shared between CLI and IDE builders
   - Language file mapping
   - Core file handling

2. **`KiloCLIBuilder`** (new in `kilo_cli.py`)
   - Generates collapsed `.opencode/rules/{MODE}.md` files
   - Generates `opencode.json`
   - Generates `AGENTS.md`
   - Generates `.kilocodemodes` (for IDE support)

3. **`KiloIDEBuilder`** (new in `kilo_ide.py`)
   - Generates `.kilo/rules-{mode}/` directories with individual files
   - Generates `.kilocodemodes` (all 15 modes)
   - NO `opencode.json`, NO `AGENTS.md`, NO `.opencode/rules/`

### CLI Integration

In `promptosaurus/cli.py`, add `--target` option to `init` command:
```python
@click.option("--target", type=click.Choice(["cli", "ide"]), default="cli")
def init_prompts(target: str):
    builder_class = KiloCLIBuilder if target == "cli" else KiloIDEBuilder
    # ... rest of implementation
```

## Output Formats

### CLI Target (`KiloCLIBuilder`)
```
{output}/
├── AGENTS.md
├── opencode.json
├── .kilocodemodes
├── .opencode/
│   └── rules/
│       ├── _base.md
│       ├── architect.md
│       ├── ask.md
│       ├── code.md
│       ... (all 15 modes)
└── .kiloignore
```

### IDE Target (`KiloIDEBuilder`)
```
{output}/
├── .kilocodemodes
├── .kilo/
│   ├── rules-core/
│   │   ├── core-system.md
│   │   ├── core-conventions.md
│   │   └── core-session.md
│   ├── rules-architect/
│   │   ├── scaffold.md
│   │   ├── task-breakdown.md
│   │   └── data-model.md
│   ├── rules-ask/
│   │   ├── docs.md
│   │   ├── testing.md
│   │   └── decision-log.md
│   ... (all 15 modes)
└── .kiloignore
```

## Implementation Steps

1. **Create `promptosaurus/builders/kilo.py`** - Refactor to be base class `KiloCodeBuilder`
2. **Create `promptosaurus/builders/kilo_cli.py`** - New `KiloCLIBuilder` class
3. **Create `promptosaurus/builders/kilo_ide.py`** - New `KiloIDEBuilder` class
4. **Update `promptosaurus/builders/__init__.py`** - Export new builders
5. **Update `promptosaurus/cli.py`** - Add `--target` option, import new builders
6. **Update tests** - Add tests for both new builders

## Benefits

- **Single Responsibility**: Each builder does one thing well
- **Open/Closed**: Easy to add new targets without modifying existing code
- **Testability**: Each builder can be tested independently
- **Clarity**: Clear separation between CLI and IDE output formats
