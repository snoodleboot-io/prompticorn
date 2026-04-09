# Design: Kilo Architecture Refactor + Minimal/Verbose Setup Choice

## Overview

Two interconnected initiatives:

1. **Refactor to new Kilo architecture** - Migrate from `.kilocodemodes` (legacy) to `.kilo/agents/*.md` (current)
2. **Add minimal/verbose choice at setup** - User chooses verbosity level during `prompt init`, affects prompt content

## Initiative 1: Kilo Architecture Refactor

### Current State (Legacy)
- Single `.kilocodemodes` YAML file
- Contains all modes as `customModes` array
- File restrictions via `groups` nested arrays
- No per-agent model pinning or other properties

### New State (Current Kilo)
- Individual `.md` files in `.kilo/agents/` directory
- Each file: agent name from filename, YAML frontmatter + markdown body
- Per-agent permissions, models, colors, temperature, steps
- Built-in agent override support
- Auto-migration from legacy format

### Migration Path

#### Old Format (`.kilocodemodes`)
```yaml
customModes:
  - slug: architect
    name: 🏗️ Architect
    description: System design...
    roleDefinition: You are a principal architect...
    whenToUse: Use this mode for...
    groups:
      - read
      - browser
      - - edit
        - fileRegex: "..."
```

#### New Format (`.kilo/agents/architect.md`)
```markdown
---
description: System design, architecture planning, and technical decision making
mode: primary
permission:
  read:
    "*": "allow"
  edit:
    "docs/**/*.md": "allow"
    ".promptosaurus/sessions/**/*.md": "allow"
    "*": "deny"
  bash: "deny"
color: "#FF9500"
---

You are a principal architect specializing in system design...
(markdown body becomes the prompt)
```

### Builder Changes Required

**Current:** `KiloIDEBuilder` creates:
- `.kilocode/rules/` (core files)
- `.kilocode/rules-{mode}/` (per-mode files)
- `.kilocodemodes` (manifest)

**New:** Update to create:
- `.kilo/agents/{agent-name}.md` (individual agent files with frontmatter + prompt)
- Keep `.kilocode/rules/` for core conventions (read by CLI)
- No more `.kilocodemodes` needed (Kilo auto-discovers `.kilo/agents/*.md`)

### Architect Property Mapping

| Old (YAML) | New (.md frontmatter) | Notes |
|------------|----------------------|-------|
| `slug` | filename (minus `.md`) | e.g., `architect.md` |
| `name` | (implied, used for display) | Remove emoji? Or keep in prompt? |
| `description` | `description` field | Required |
| `roleDefinition` | markdown body | Main prompt content |
| `whenToUse` | part of `description` or prompt | Combine into description |
| `groups` | `permission` object | Map file restrictions |
| (new) | `mode` | Set to "primary" for user-selectable |
| (new) | `color` | Can add for UI theming |

---

## Initiative 2: Minimal vs Verbose Setup Choice

### Goal
User chooses at `prompt init` time whether they want minimal or verbose prompts. Same file structure, different content.

### Setup Flow

```
prompt init

Are you setting up a new project? [y/n]
> y

Repository type? [single-language/multi-language-monorepo]
> single-language

Language? [python/typescript/...]
> python

Prompt verbosity? [verbose/minimal]
> verbose

... other questions ...

Building configuration...
✓ Created .promptosaurus.yaml
✓ Created .kilo/agents/ with verbose prompts
```

### Config Storage

Add to `.promptosaurus.yaml`:
```yaml
version: '1.0'
prompts:
  verbosity: "verbose"  # or "minimal"
  
repository:
  type: single-language
  
spec:
  language: python
  ...
```

### Builder Implementation

**In `KiloIDEBuilder.build()`:**

```python
def build(self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False) -> list[str]:
    # Get verbosity choice from config
    prompts_config = config.get("prompts", {}) if config else {}
    verbosity = prompts_config.get("verbosity", "verbose")
    
    # Generate agent files with appropriate verbosity
    for agent_name, agent_def in self.kilo_modes.items():
        agent_prompt = self._get_agent_prompt(agent_name, verbosity)
        self._create_agent_file(output, agent_name, agent_def, agent_prompt, dry_run)
```

### Prompt Generation

Create prompt templates with verbosity variants:

**Template structure:**
```
.kilo/prompts/
├── architect.md
│   ├── {verbose}
│   └── {minimal}
├── code.md
│   ├── {verbose}
│   └── {minimal}
└── ...
```

**Or:** Have both inline in builder:

```python
def _get_agent_prompt(self, agent_name: str, verbosity: str) -> str:
    """Get prompt content based on verbosity level."""
    prompts = {
        "architect": {
            "verbose": """You are a principal architect specializing in system design...
[comprehensive roledef with philosophy, approach, patterns]
""",
            "minimal": """You are a principal architect. Design scalable systems with clear abstractions.
[essential guidance only]
"""
        },
        "code": {
            "verbose": """You are a principal software engineer...[detailed guidance]""",
            "minimal": """You implement features following conventions...[essential only]"""
        }
    }
    return prompts.get(agent_name, {}).get(verbosity, "")
```

### File Output

Whether verbose or minimal, output structure is identical:

```
.kilo/
├── agents/
│   ├── architect.md          (contains chosen verbosity)
│   ├── code.md
│   ├── test.md
│   └── ...
└── agent/ (legacy alias)
    └── (same files)
```

User can change verbosity by:
1. Editing `.promptosaurus.yaml` `prompts.verbosity` value
2. Running `prompt init` again
3. Regenerating agents

---

## Implementation Plan

### Phase 1: Refactor to New Kilo (Week 1)

**Files to modify:**
- `promptosaurus/builders/kilo/kilo_ide.py` - Main builder refactor
- `promptosaurus/builders/kilo/kilo_cli.py` - CLI builder (legacy format, can deprecate)
- `promptosaurus/builders/kilo/config.py` - Config loading

**Changes:**
1. Remove `kilo_modes.yaml` dependency
2. Update `KiloIDEBuilder.build()` to generate `.kilo/agents/*.md` files
3. Create agent file with YAML frontmatter + markdown body
4. Map `groups` (file restrictions) to `permission` object
5. Keep `.kilocode/rules/` for core conventions (Kilo CLI reads these)

**Testing:**
- Unit tests for agent file generation
- Integration test: full build generates valid `.kilo/agents/` structure
- Verify Kilo can load and display the agents

### Phase 2: Add Minimal/Verbose Choice (Week 1-2)

**Files to modify:**
- `promptosaurus/config_handler.py` - Add `prompts.verbosity` to config
- `promptosaurus/questions/` - Add verbosity question to CLI flow
- `promptosaurus/builders/kilo/kilo_ide.py` - Select prompt based on verbosity

**Changes:**
1. Add verbosity question to `prompt init` flow
2. Store choice in `.promptosaurus.yaml`
3. Build prompt templates with minimal/verbose variants
4. Pass verbosity to builder, select appropriate content
5. Document how user can change verbosity later

**Testing:**
- Test minimal mode generates shorter prompts
- Test verbose mode generates detailed prompts
- Test same file structure output
- Test changing verbosity and regenerating

### Phase 3: Update CLI Questions (Week 2)

**Add to question flow:**

```python
# In prompts/questions/
class PromptVerbosityQuestion(Question):
    """Ask user about prompt verbosity preference."""
    
    def __init__(self):
        super().__init__(
            key="prompts.verbosity",
            question="Prompt verbosity?",
            choices=["verbose", "minimal"],
            default="verbose",
            help_text="Verbose: detailed prompts with examples. Minimal: concise guidance only."
        )
```

---

## Benefits of This Design

### For Users
- **Choice at setup:** Pick verbosity level once, don't repeat
- **Same structure:** Familiar file layout regardless of choice
- **Easy switching:** Change `.promptosaurus.yaml` and regenerate
- **Better Kilo support:** New architecture is officially supported

### For Codebase
- **Modern:** Uses current Kilo patterns
- **Simpler:** No `.kilocodemodes` complexity
- **Extensible:** Easy to add per-agent config later
- **Cleaner:** Individual files easier to maintain

### Token Efficiency
- **Minimal:** ~500-1k tokens per agent (10x smaller)
- **Verbose:** ~5-10k tokens per agent (current)
- **User controls:** Pick based on their context windows

---

## Migration Path for Existing Users

**Automatic migration:**
1. Detect old `.kilocodemodes` exists
2. Run migration script (convert to new format)
3. Move old file to `.kilocodemodes.legacy` backup
4. Generate new `.kilo/agents/*.md` files

**Script:**
```python
def migrate_from_legacy_kilocodemodes(kilo_modes_path: Path, output_dir: Path) -> int:
    """Migrate from .kilocodemodes to .kilo/agents/*.md format."""
    
    kilo_modes = yaml.safe_load(kilo_modes_path.read_text())
    
    for mode in kilo_modes.get("customModes", []):
        slug = mode["slug"]
        agent_file = output_dir / f"{slug}.md"
        
        # Build frontmatter
        frontmatter = {
            "description": mode.get("description"),
            "mode": "primary",
            "permission": _convert_groups_to_permissions(mode.get("groups", []))
        }
        
        # Build markdown body
        body = mode.get("roleDefinition", "")
        
        # Write file
        agent_file.write_text(f"---\n{yaml.dump(frontmatter)}---\n\n{body}")
    
    # Backup legacy file
    kilo_modes_path.rename(kilo_modes_path.with_suffix(".legacy"))
    
    return len(kilo_modes.get("customModes", []))
```

---

## Summary

**What we're doing:**
1. Modernizing to new Kilo architecture (`.kilo/agents/*.md`)
2. Adding user choice for minimal/verbose at setup time
3. Same file structure, different content based on choice

**Impact:**
- Users get modern Kilo support
- Architect mode and others show up
- Users control prompt verbosity
- Easier to maintain and extend

**Timeline:** 2 weeks to fully implement both initiatives

