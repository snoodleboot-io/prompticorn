# Prompt System Architecture Analysis

## Current State (What I've Found)

### Two Parallel Systems

The codebase has **two completely different** prompt management systems that need to be understood:

#### System 1: Registry-Based (Agents/Subagents)
- **Location:** `promptosaurus/prompts/agents/`
- **Used by:** Cline, Copilot, Cursor, Copilot CLI
- **Structure:**
  ```
  agents/
  ├─ core/                      (always loaded)
  │  ├─ core-system.md
  │  ├─ core-conventions.md
  │  ├─ core-session.md
  │  └─ core-conventions-*.md   (per language)
  │
  ├─ architect/
  │  └─ subagents/
  │     ├─ architect-scaffold.md
  │     ├─ architect-task-breakdown.md
  │     └─ architect-data-model.md
  │
  ├─ code/
  │  └─ subagents/
  │     ├─ code-feature.md
  │     ├─ code-boilerplate.md
  │     ├─ code-house-style.md
  │     ├─ code-refactor.md
  │     ├─ code-migration.md
  │     └─ code-dependency-upgrade.md
  │
  ├─ review/
  │  └─ subagents/
  │     ├─ review-code.md
  │     ├─ review-performance.md
  │     └─ review-accessibility.md
  │
  └─ [other agents]
  ```
  
- **Managed by:** `promptosaurus/registry.py`
  - `registry.mode_files` maps mode → list of subagent files
  - `registry.concat_order` defines concatenation order
  - Each tool reads appropriate files based on its format

#### System 2: Kilo Modes (YAML-Based)
- **Location:** `promptosaurus/builders/kilo/kilo_modes.yaml` (15 custom modes with roleDefinition/whenToUse)
- **Used by:** KiloIDE, KiloCLI
- **Current Outputs:**
  - KiloIDE: `.kilo/agents/{slug}.md` (individual agent files with YAML frontmatter)
  - KiloCLI: `.opencode/rules/{MODE}.md` + `opencode.json` manifest
  - Both: `.kilocodemodes` (compatibility manifest, copied to user project)

### Key Discovery: Subagents Already Exist

Looking at the registry, there's already a subagent concept:
- **Architect mode** has subagents: scaffold, task-breakdown, data-model
- **Code mode** has subagents: feature, boilerplate, house-style, refactor, migration, dependency-upgrade
- **Review mode** has subagents: code review, performance review, accessibility review
- **Debug mode** has subagents: root-cause, log-analysis, rubber-duck

BUT these are only in the registry-based system (agents/), not in kilo_modes.yaml.

### What's Missing / Questions

1. **Are Kilo systems using outdated structure?**
   - kilo_modes.yaml has all 15 modes flattened with full roleDefinition
   - Registry has subagents (specialized behaviors within modes)
   - Which is source of truth? Should Kilo use registry instead?

2. **Prompt/Skill/Workflow Structure?**
   - User mentioned "prompts have prompt/skill/workflows" 
   - Where is this defined? I don't see this structure anywhere
   - Is this a proposed new organization?

3. **Minimal vs Verbose - Where Does It Go?**
   - Registry-based files? (create minimal/ and verbose/ subdirs?)
   - Kilo_modes.yaml? (duplicate entries?)
   - Both systems?

4. **Missing Subagents**
   - What specialized subagents might each mode need?
   - Example: Should architect have "architecture-review", "technology-selection" subagents?
   - Should code have more specific subagents?

5. **Cline, Cursor, Copilot - Current State**
   - Do they properly handle subagents from registry?
   - Or are they flattening all subagents into concatenated output?

---

## Questions for Clarification

Before I redesign Phase 2, I need to understand:

1. **What does "prompts have prompt/skill/workflows" mean?**
   - Is this a new structure we're introducing?
   - Or does it already exist and I'm not seeing it?

2. **Are we deprecating kilo_modes.yaml?**
   - Should Kilo builders move to registry-based like other tools?
   - Or keep both systems?

3. **For minimal/verbose:**
   - Do we need both variants for ALL 15 modes, or just specific ones?
   - Should each subagent have minimal/verbose variants?
   - Example: `architect-scaffold-minimal.md` and `architect-scaffold-verbose.md`?

4. **Missing subagents:**
   - Should every mode have specialized subagents like architect/code/review?
   - What specific subagents should be added for testing, documentation, compliance, etc?

5. **Kilo specifics:**
   - Should Kilo modes also have subagents?
   - Should KiloIDE generate `.kilo/agents/{slug}/subagent-name.md` structure?

---

## Current System Behaviors

### Cline
```
ClineBuilder.build()
  ├─ Reads from registry.concat_order
  └─ Generates single .clinerules file with all content concatenated
```

### KiloIDE  
```
KiloIDEBuilder.build()
  ├─ Reads from kilo_modes.yaml (15 modes)
  └─ Generates .kilo/agents/{slug}.md (one per mode)
     └─ Each has YAML frontmatter + roleDefinition + whenToUse
```

### KiloCLI
```
KiloCLIBuilder.build()
  ├─ Reads from kilo_modes.yaml (15 modes)
  ├─ Generates .opencode/rules/{MODE}.md (collapsed format)
  └─ Generates opencode.json manifest
```

### Cursor, Copilot
- Use registry-based system (subagents)
- Generate various output formats

---

## What Needs to Happen

Looking at Phase 1 completion, we:
- ✓ Refactored KiloIDEBuilder to generate new format
- ✓ Added YAML frontmatter support
- ✓ Validated permission mapping

For Phase 2 (Minimal/Verbose), we need to:
1. Clarify the true architecture (registry vs kilo_modes)
2. Decide on prompt structure (prompt/skill/workflows if real)
3. Understand subagent strategy across all modes
4. Define what "minimal" and "verbose" actually means in context
5. Ensure consistency across all builders (Cline, Kilo, Cursor, Copilot)

