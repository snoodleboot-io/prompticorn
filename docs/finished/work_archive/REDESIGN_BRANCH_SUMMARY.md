# Prompt System Redesign - Branch Summary

**Branch:** `feat/prompt-system-redesign`

## What We Discovered

### Root Cause of Architect Not Showing

**Kilo platform changed its architecture:**
- **Old:** Custom modes in `.kilocodemodes` file (legacy)
- **New:** Individual `.md` files in `.kilo/agents/` directory (current)
- **Promptosaurus:** Still using legacy `.kilocodemodes` format
- **Result:** Architect and other custom modes hidden in new Kilo IDE

**Evidence:**
- Last time architect worked: using old Kilo with `.kilocodemodes` support
- New Kilo IDE: requires `.kilo/agents/*.md` format
- Builder: never updated to generate new format
- This is a platform regression, not a code bug

## Design Documents Created

### 1. `ARCHITECT_MODE_COMPLETE_ANALYSIS.md`
Executive summary of:
- Root cause (platform change)
- What needs to change
- Timeline and benefits
- How it fixes architect visibility

### 2. `DESIGN_KILO_REFACTOR_AND_MINIMAL_VERBOSE.md`
Comprehensive design for two initiatives:

#### Initiative 1: Refactor to New Kilo Architecture
- Migrate from `.kilocodemodes` (single YAML file) to `.kilo/agents/*.md` (individual files)
- Each agent file has YAML frontmatter + markdown body
- Map file permissions from `groups` to `permission` object
- Keep `.kilocode/rules/` for CLI core conventions

**Property mapping:**
```
.kilocodemodes slug             → agent filename
roleDefinition                  → markdown body (the prompt)
groups (file restrictions)      → permission object
description                     → frontmatter description
```

#### Initiative 2: Minimal/Verbose Setup Choice
- User picks during `prompt init`: "verbose" or "minimal"
- Choice stored in `.promptosaurus.yaml` under `prompts.verbosity`
- Same file structure (`.kilo/agents/`), different prompt content
- Minimal: ~500-1k tokens per agent (10x reduction)
- Verbose: ~5-10k tokens per agent (current)

**Setup flow:**
```
prompt init
→ Repository type?
→ Language?
→ [NEW] Prompt verbosity? [verbose/minimal]
→ ... other questions ...
→ Generate .kilo/agents/ with chosen verbosity
```

### 3. Original Research Documents

Also on branch:
- `PROMPT_SYSTEM_REDESIGN_ANALYSIS.md` - Initial three-direction analysis
- `PROMPT_SYSTEM_QUICK_REFERENCE.md` - Decision matrix and roadmap
- `PROMPT_SYSTEM_ARCHITECTURE.md` - Technical architecture deep dive

(These are still valid and provide good context, though now understood as needing refactor to new Kilo format)

## Implementation Plan

### Phase 1: Refactor Builder (Week 1)
**Files:** `promptosaurus/builders/kilo/kilo_ide.py`, config.py

Changes:
- Remove `.kilocodemodes` generation
- Generate `.kilo/agents/{agent-name}.md` files
- YAML frontmatter with: description, mode, permission, color
- Markdown body: the prompt content
- Keep `.kilocode/rules/` for CLI

### Phase 2: Minimal/Verbose Choice (Week 1-2)
**Files:** `config_handler.py`, `questions/`, `kilo_ide.py`

Changes:
- Add `prompts.verbosity` to config schema
- Add verbosity question to CLI init flow
- Create prompt content templates (minimal + verbose variants)
- Builder selects content based on config choice

### Phase 3: CLI + Migration (Week 2)
**Files:** `cli.py`, `questions/`

Changes:
- New `PromptVerbosityQuestion` class
- Auto-migration script for existing `.kilocodemodes`
- Documentation updates

## Benefits

✅ **Architect shows up** - Uses modern Kilo format
✅ **User control** - Pick verbose or minimal at setup
✅ **Token efficiency** - Minimal mode 10x smaller
✅ **Same structure** - `.kilo/agents/` whether verbose or minimal
✅ **Future-proof** - Supports new Kilo architecture
✅ **Extensible** - Per-agent model/color/temp support later

## What This Fixes

| Issue | Before | After |
|-------|--------|-------|
| Architect visibility | Hidden in new Kilo | Visible as `.kilo/agents/architect.md` |
| Custom agents | All hidden | All visible |
| Prompt control | No choice | Choose at setup |
| Token usage | Heavy (5-10k) | Flexible (500k-10k) |
| Platform support | Legacy (deprecated) | Modern (current) |

## Quick Start

To implement:

1. Review `DESIGN_KILO_REFACTOR_AND_MINIMAL_VERBOSE.md`
2. Phase 1: Refactor `KiloIDEBuilder` to generate `.kilo/agents/*.md`
3. Phase 2: Add verbosity question and content selection
4. Phase 3: Auto-migration for users with `.kilocodemodes`

---

## Summary

**This is not a bug fix — it's an architecture update.**

Kilo changed how it handles custom agents. Promptosaurus needs to be updated to use the new format. Once done, architect (and all other agents) will show up automatically in new Kilo IDE, and users can choose their preferred prompt verbosity at setup time.

Design is complete and ready for development.
