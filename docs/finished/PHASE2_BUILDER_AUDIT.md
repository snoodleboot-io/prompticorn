# Phase 2 Builder Audit: What Will Actually Need to Change?

## Critical Issue: Two Competing Systems

I've found a fundamental architectural problem that my design **assumed away**:

### System 1: Registry-Based (Cline, Cursor, Copilot)
- **Input source:** `promptosaurus/prompts/agents/` via `registry.py`
- **Registry maps:** `mode_key` → `list[filename]`
- **Example:** `registry.mode_files["code"]` = `["agents/code/subagents/code-feature.md", ...]`

### System 2: Kilo-Based (KiloIDE, KiloCLI)
- **Input source:** `promptosaurus/builders/kilo/kilo_modes.yaml` (SEPARATE from registry!)
- **YAML maps:** `slug` → `roleDefinition`, `whenToUse`, `groups`
- **Problem:** This is NOT connected to registry.mode_files

## Current Builder Implementations

### 1. CLINE Builder ✓ (Registry-based)
```python
class ClineBuilder(Builder):
    def build(self):
        # Reads registry.concat_order
        for label, filename in registry.concat_order:
            content = registry.prompt_body(filename)
        # Outputs: .clinerules (single concatenated file)
```
**Input:** Registry (agents/)  
**Output:** Single `.clinerules` file  
**Complexity:** Low - just concatenates

---

### 2. CURSOR Builder ✓ (Registry-based)
```python
class CursorBuilder(Builder):
    def build(self):
        # 1. Copy always_on rules as .mdc files
        for filename in registry.always_on:
            destination = .cursor/rules/{filename}
        # 2. Copy per-mode rules in subdirectories
        for mode_key, files in registry.mode_files.items():
            for filename in files:
                destination = .cursor/rules/{mode_key}/{filename}
        # 3. Create legacy .cursorrules fallback
        legacy_content = concatenate all registry.concat_order
```
**Input:** Registry (agents/)  
**Output:** Nested `.cursor/rules/` structure + legacy `.cursorrules`  
**Complexity:** Medium - creates multiple file types

---

### 3. COPILOT Builder ✓ (Registry-based)
```python
class CopilotBuilder(Builder):
    def build(self):
        # 1. Create .github/copilot-instructions.md
        for filename in registry.always_on:
            content += registry.prompt_body(filename)
        # 2. Create per-mode instruction files with applyTo
        for mode_key, files in registry.mode_files.items():
            destination = .github/instructions/{mode_key}.instructions.md
            frontmatter = {"applyTo": registry.copilot_apply[mode_key]}
            content = concat(files)
```
**Input:** Registry (agents/)  
**Output:** `.github/instructions/{mode}.instructions.md` with YAML frontmatter  
**Complexity:** Medium - creates per-mode files with applyTo targeting

---

### 4. KILO IDE Builder ✗ (Kilo-modes-based)
```python
class KiloIDEBuilder(KiloCodeBuilder):
    def build(self):
        # Reads kilo_modes.yaml (NOT registry!)
        kilo_modes = load_yaml("kilo_modes.yaml")
        for mode in kilo_modes.customModes:
            # Creates individual .kilo/agents/{slug}.md files
            # Each has: YAML frontmatter + roleDefinition + whenToUse
            destination = .kilo/agents/{slug}.md
```
**Input:** `kilo_modes.yaml` (SEPARATE from registry!)  
**Output:** Individual `.kilo/agents/{slug}.md` with YAML frontmatter  
**Complexity:** High - completely separate from registry system

---

### 5. KILO CLI Builder ✗ (Kilo-modes-based)
```python
class KiloCLIBuilder(KiloCodeBuilder):
    def build(self):
        # Reads registry (for custom modes) + special handling
        for mode in custom_modes:
            # Creates collapsed .opencode/rules/{MODE}.md
            # All subagents combined into one file per mode
        # Creates opencode.json manifest
        # Creates .kilocodemodes (backward compat)
```
**Input:** Registry + kilo_modes.yaml hybrid  
**Output:** Collapsed `.opencode/rules/{MODE}.md` + `opencode.json`  
**Complexity:** Very high - connects both systems awkwardly

---

### 6. NO "CLAUDE" Builder
❌ **There is no Claude builder in the codebase**. The user mentioned "kilo, cline, claude, cursor" but "Claude" either:
- Doesn't exist yet
- Was a typo
- Is being planned

---

## Phase 2 Impact Analysis

### What Needs to Change for Each Builder?

#### Registry-Based Builders (Cline, Cursor, Copilot)

**Current:** Read from `prompts/agents/` → files loaded directly  
**After Phase 2:** Read from `prompts/agents/{mode}/minimal|verbose/{component}.md`

**Changes needed:**
1. Update registry to discover component structure
2. ComponentSelector to choose minimal or verbose
3. ComponentComposer to merge prompt/skill/workflow
4. Each builder needs to support verbosity config parameter

**Example transformation:**

```python
# BEFORE (Cursor)
for mode_key, files in registry.mode_files.items():
    for filename in files:
        body = registry.prompt_body(filename)  # Reads full content
        destination = .cursor/rules/{mode_key}/{filename}
        write(destination, body)

# AFTER (Cursor with components)
for mode_key, files in registry.mode_files.items():
    for filename in files:
        prompt = ComponentSelector.select_prompt(filename, verbosity)
        skills = ComponentSelector.select_skills(filename, verbosity)
        workflow = ComponentSelector.select_workflow(filename, verbosity)
        
        body = ComponentComposer.compose(prompt, skills, workflow)
        destination = .cursor/rules/{mode_key}/{filename}
        write(destination, body)
```

**Refactoring effort:** Medium (all three follow same pattern)

---

#### Kilo Builders (KiloIDE, KiloCLI)

**Current:** Read from `kilo_modes.yaml` (separate YAML file with 15 modes)  
**After Phase 2:** Need to decide:

**Option A: Keep kilo_modes.yaml as source (WORSE)**
- Maintain two separate prompt sources forever
- Duplicate effort creating components
- Risk of divergence

**Option B: Migrate to registry (BETTER)**
- Move kilo_modes into registry structure
- Delete kilo_modes.yaml
- Both systems use registry as source of truth
- But requires major refactoring

**Option C: Create adapter (COMPROMISE)**
- Keep kilo_modes.yaml for backward compat
- Map it to registry structure programmatically
- Builders read from registry

**Recommendation:** Option B (migrate to registry)

**Why:**
- Single source of truth
- Registry already has all the infrastructure
- Both Kilo and other builders benefit
- Cleaner long-term architecture

**Refactoring required:**

1. **For KiloIDE:**
   - Currently: reads kilo_modes.yaml → creates `.kilo/agents/{slug}.md`
   - Future: read from registry + components → create same output
   - Must compose roleDefinition from prompt/skills/workflow
   - Must map groups→permissions

2. **For KiloCLI:**
   - Currently: reads registry (for custom modes) + kilo_modes.yaml (for 15 modes)
   - Future: read all from registry only
   - Creates `.opencode/rules/{MODE}.md` (collapsed format)
   - Must handle built-in modes (architect, code, etc.) differently

**Refactoring effort:** Very high (requires rethinking Kilo architecture)

---

## Implementation Impact Summary

### If Phase 2 Applies to ALL Builders:

**Registry-based builders affected:**
- ✓ Cline (Medium effort)
- ✓ Cursor (Medium effort)
- ✓ Copilot (Medium effort)

**Kilo builders affected:**
- ✗ KiloIDE (High effort - needs major refactoring)
- ✗ KiloCLI (Very high effort - two systems to reconcile)

**If we choose Option B (migrate to registry):**
- Must deprecate/delete `kilo_modes.yaml`
- Must move 15 Kilo modes into registry structure
- Must update KiloIDE, KiloCLI to read from registry
- ~400-500 lines of registry changes
- ~600-800 lines of builder changes

---

## Questions For You

Before proceeding with Phase 2, I need clarity:

1. **Should Phase 2 include Kilo builders?**
   - If YES: We need to solve the kilo_modes.yaml problem first
   - If NO: We can proceed with registry-based only (Cline, Cursor, Copilot)

2. **If YES to Kilo: Which option?**
   - Option A: Keep separate (⚠️ maintenance burden)
   - Option B: Migrate to registry (🔧 architectural cleanup)
   - Option C: Create adapter (🤝 compromise)

3. **What about "Claude" builder you mentioned?**
   - Typo for Copilot?
   - Planned future tool?
   - Something else?

4. **Scope: Registry-only (3 builders) or all-inclusive (5 builders)?**
   - Registry-only: ~6 weeks (component creation + integration)
   - All-inclusive: ~10-12 weeks (includes Kilo refactoring)

---

## Next Steps

I need your decision on:
- [ ] Should Phase 2 refactor all builders or just registry-based?
- [ ] If all: Which solution for kilo_modes.yaml (A, B, or C)?
- [ ] Clarify "Claude" builder reference

Once you clarify, I can create a realistic, builder-specific Phase 2 plan.

