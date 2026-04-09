# Architecture Decision Record: Phase 2 - Unified Prompt Architecture

**ADR ID:** ADR-002  
**Date:** 2026-04-08  
**Status:** Proposed  
**Deciders:** Promptosaurus Team  
**Supersedes:** ADR-001 (Phase 1 Kilo Refactor)  

---

## Context

The project currently has **two competing prompt management systems**:

1. **Registry-based** (Cline, Cursor, Copilot): Read from `prompts/agents/` via registry
2. **Kilo-based** (KiloIDE, KiloCLI): Read from separate `kilo_modes.yaml` file

This split creates:
- Maintenance burden (changes in two places)
- Unclear source of truth (which is canonical?)
- Difficulty adding new tools (no clear pattern)
- Impedance mismatch when trying to add Claude support

Additionally, all current prompts are monolithic (bundling multiple concerns into single roleDefinition), making it hard to:
- Create minimal variants with 90% token reduction
- Specialize behaviors (e.g., separate code review from performance review)
- Add targeted subagents

We are moving from alpha to beta and need a clean, extensible, maintainable foundation.

---

## Decision

### 1. **Unified Registry as Single Source of Truth**

**Decision:** All builders (KiloIDE, KiloCLI, Cline, Cursor, Copilot, Claude) read from unified registry. Deprecate `kilo_modes.yaml`.

**Alternatives Considered:**

**Alternative A: Keep kilo_modes.yaml separate**
- ✗ Maintain two independent prompt sources
- ✗ Duplicate effort when creating components
- ✗ Risk of divergence between systems
- ✗ Harder to add new tools (they need to choose which system to use)
- ✗ Maintenance burden grows with each new builder

**Alternative B: Create adapter (kilo_modes.yaml → registry)**
- ± Keep kilo_modes.yaml for backward compatibility
- ± Map to registry at runtime
- ± Adds complexity/indirection
- ± Still two "truth sources" conceptually
- ± Unclear which one owns the data

**Alternative C: Migrate kilo_modes.yaml content into registry** ✅ **CHOSEN**
- ✓ Single source of truth
- ✓ Registry infrastructure already exists
- ✓ No runtime mapping complexity
- ✓ Easy to add new builders (all use registry)
- ✓ Clear ownership (registry is canonical)
- ✓ Better for long-term maintainability
- ✗ Requires refactoring KiloIDE/KiloCLI
- ✗ Higher initial effort

**Rationale:** Beta release requires clean architecture. The small additional effort now prevents large maintenance burden later. Registry-first approach scales better.

---

### 2. **Component-Based Decomposition (Prompt/Skills/Workflow)**

**Decision:** Decompose each agent into three independent components that can be composed:
- **Prompt**: Role definition + principles
- **Skills**: Specific capabilities with constraints  
- **Workflow**: Step-by-step process/methodology

**File structure:**
```
agents/{agent}/{variant}/
  ├─ prompt.md       # What you are (role + principles)
  ├─ skills.md       # What you can do (capabilities list)
  └─ workflow.md     # How you work (step-by-step process)
```

**Alternatives Considered:**

**Alternative A: Keep monolithic roleDefinition**
- ✗ Can't create meaningful minimal variants
- ✗ Hard to identify what to cut for 90% reduction
- ✗ Bundles unrelated concerns
- ✗ Difficult to specialize

**Alternative B: YAML with structured sections**
```yaml
role: "..."
skills:
  - name: ...
    description: ...
workflow:
  - step: ...
```
- ± More machine-readable
- ± Harder for humans to edit
- ± Parsing complexity
- ✗ YAML can become verbose itself

**Alternative C: Markdown with section headers** ✅ **CHOSEN**
```markdown
# Prompt
You are...

# Skills
- Skill 1
- Skill 2

# Workflow
1. Step 1
2. Step 2
```
- ✓ Human-friendly format (easy to edit)
- ✓ Composable (sections load independently)
- ✓ Easy to parse (simple header detection)
- ✓ Already familiar format in codebase
- ✓ Clear visual separation
- ✓ Suitable for minimal/verbose variants

**Rationale:** Markdown is already standard in codebase. Component decomposition enables meaningful minimal variants (remove skill details, workflow checkpoints). Supports all builder formats.

---

### 3. **Minimal and Verbose as Separate Files**

**Decision:** Create separate `minimal/` and `verbose/` directories containing full component sets.

**File structure:**
```
agents/{agent}/
  ├─ minimal/
  │  ├─ prompt.md
  │  ├─ skills.md
  │  └─ workflow.md
  └─ verbose/
     ├─ prompt.md
     ├─ skills.md
     └─ workflow.md
```

**Alternatives Considered:**

**Alternative A: Dual-variant markdown (single file, both versions)**
```markdown
# Prompt

**Minimal:**
...

**Verbose:**
...
```
- ✗ One file becomes large and complex
- ✗ Easy to make mistakes (copy/paste errors)
- ✗ Harder to parse (need special logic)
- ✗ Versioning confusing (which is canonical?)

**Alternative B: Separate files** ✅ **CHOSEN**
```
prompt-minimal.md
prompt-verbose.md
```
- ✓ Each variant fully independent
- ✓ Easy to parse (just load the right one)
- ✓ Easy to edit (no confusion)
- ✓ Clear versioning (two separate files)
- ✓ Supports selective loading
- ± Doubles file count

**Alternative C: Runtime composition (strip minimal from verbose)**
- ✗ Complex logic to determine what to remove
- ✗ High chance of errors
- ✗ Minimal version might be invalid
- ✗ Not repeatable (different code path)

**Rationale:** Separate files ensure independent, valid variants. ComponentSelector chooses between them. No ambiguity about which is source of truth.

---

### 4. **Subagent Structure and Organization**

**Decision:** Subagents live under parent agent and inherit parent's principles.

**File structure:**
```
agents/architect/
  ├─ minimal/
  ├─ verbose/
  └─ subagents/
     ├─ architect-scaffold/
     ├─ architect-task-breakdown/
     ├─ architect-data-model/
     ├─ architect-decision/        ← NEW
     ├─ architect-technology-selection/  ← NEW
     └─ architect-tradeoff-analysis/     ← NEW
```

**Each subagent follows same structure:**
```
subagent-name/
  ├─ minimal/
  │  ├─ prompt.md
  │  ├─ skills.md
  │  └─ workflow.md
  └─ verbose/
     ├─ prompt.md
     ├─ skills.md
     └─ workflow.md
```

**Alternatives Considered:**

**Alternative A: Flat structure (all subagents at top level)**
```
agents/
  ├─ architect-scaffold/
  ├─ architect-task-breakdown/
  ├─ code-feature/
  ├─ code-boilerplate/
  ...
```
- ✗ No hierarchy/relationship to parent
- ✗ Confusing to navigate (50+ agents at same level)
- ✗ Hard to identify which subagents belong to which agent
- ✗ Difficult to manage permissions/discovery

**Alternative B: Nested under parent** ✅ **CHOSEN**
```
agents/{parent}/subagents/{subagent}/
```
- ✓ Clear parent-child relationship
- ✓ Organized by logical grouping
- ✓ Easier to navigate
- ✓ Subagents inherit parent context
- ✓ Registry can auto-discover hierarchy
- ✓ Supports future: architect/subagents/subsubagents/

**Rationale:** Nesting provides clear ownership and inheritance. Makes it obvious which agent a subagent belongs to. Scales well as new subagents are added.

---

### 5. **Registry Discovery vs Explicit Registration**

**Decision:** Registry auto-discovers component structure from filesystem instead of explicit manual registration.

**Approach:**
```python
# Registry discovers components by scanning:
agents/
  ├─ {agent}/
  │   ├─ minimal/
  │   │   ├─ prompt.md
  │   │   ├─ skills.md
  │   │   └─ workflow.md
  │   ├─ verbose/
  │   │   ├─ prompt.md
  │   │   ├─ skills.md
  │   │   └─ workflow.md
  │   └─ subagents/
  │       └─ {subagent}/
  │           ├─ minimal/
  │           └─ verbose/
  └─ ... (repeat for other agents)
```

**Alternatives Considered:**

**Alternative A: Explicit registration in registry.py**
```python
mode_files = {
    "architect": {
        "component": "prompt",
        "variants": ["minimal", "verbose"],
        "subagents": ["scaffold", "task-breakdown", ...]
    }
}
```
- ✗ Duplicates information (filesystem is source)
- ✗ Easy to forget registration when adding new file
- ✗ Manual sync burden
- ✗ Errors if registration doesn't match filesystem

**Alternative B: Auto-discovery** ✅ **CHOSEN**
```python
def discover_agents(agents_dir):
    """Scan filesystem and auto-discover structure."""
    agents = {}
    for agent_path in (agents_dir / "agents").glob("*/"):
        agent_name = agent_path.name
        agents[agent_name] = {
            "minimal": load_components(agent_path / "minimal"),
            "verbose": load_components(agent_path / "verbose"),
            "subagents": discover_subagents(agent_path / "subagents"),
        }
    return agents
```
- ✓ Single source of truth (filesystem)
- ✓ No manual registration needed
- ✓ Add file → automatically included
- ✓ Harder to get out of sync
- ✓ Self-documenting (structure is clear)
- ± Requires robust filesystem scanning
- ± Some validation overhead

**Rationale:** Reduces maintenance burden. Filesystem becomes single source of truth for structure. Adding new agent/subagent doesn't require code changes.

---

### 6. **All 6 Builders Support (Including New Claude Builder)**

**Decision:** Update all 5 existing builders to use components + create new Claude builder.

**Builders:**
- **KiloIDE**: `.kilo/agents/{slug}.md` (individual files with YAML frontmatter)
- **KiloCLI**: `.opencode/rules/{MODE}.md` (collapsed format) + `opencode.json`
- **Cline**: `.clinerules` (single concatenated file)
- **Cursor**: `.cursor/rules/` (nested) + `.cursorrules` (legacy)
- **Copilot**: `.github/instructions/{mode}.instructions.md` (per-mode with applyTo)
- **Claude**: *(TBD during implementation)*

**Alternatives Considered:**

**Alternative A: Builders work independently (some use components, some don't)**
- ✗ Inconsistent experience
- ✗ Some tools get minimal/verbose, others don't
- ✗ Harder to maintain (different code paths)
- ✗ Doesn't solve original problem (two systems)

**Alternative B: All builders use components** ✅ **CHOSEN**
```python
# ComponentSelector chooses minimal or verbose
prompt = ComponentSelector.select(agent, "prompt", verbosity)
skills = ComponentSelector.select(agent, "skills", verbosity)
workflow = ComponentSelector.select(agent, "workflow", verbosity)

# ComponentComposer builds output for specific builder format
content = ComponentComposer.compose(prompt, skills, workflow)

# Each builder composes its own output format
KiloCLIBuilder.build() → collapse components into .opencode/rules/{MODE}.md
ClineBuilder.build() → concatenate all components into .clinerules
CursorBuilder.build() → copy components to .cursor/rules/ structure
```
- ✓ Consistent experience across all tools
- ✓ All tools support minimal/verbose
- ✓ Single composition logic
- ✓ Easier to maintain
- ✗ All 5 builders need updates

**Rationale:** Consistent user experience. All tools support cost optimization (minimal variants). Single source of truth removes confusion.

---

### 7. **Configuration: Verbosity Storage**

**Decision:** Store verbosity preference in config at `spec.prompts.verbosity`.

**Config structure:**
```yaml
version: '1.0'
repository:
  type: single-language
spec:
  language: python
  runtime: '3.14'
  package_manager: uv
  prompts:                    # NEW SECTION
    verbosity: minimal        # or "verbose"
    style: standard           # future expansion
```

**Alternatives Considered:**

**Alternative A: CLI flag only (no config storage)**
- ✗ User has to specify every build
- ✗ No "sticky" preference
- ✗ High friction

**Alternative B: Environment variable**
- ✗ Not discoverable
- ✗ Hard to track what's configured
- ✗ Easy to forget

**Alternative C: Store in config** ✅ **CHOSEN**
- ✓ Discoverable in `.promptosaurus.yaml`
- ✓ Version controlled (can be in git)
- ✓ Sticky preference
- ✓ Consistent across rebuilds
- ✓ Compatible with future expansion

**Rationale:** Config is appropriate place for project-level preferences. User sets it once during init, then it persists.

---

## Consequences

### Positive

1. **Single source of truth** - Registry is canonical; no kilo_modes.yaml duplication
2. **Cleaner architecture** - All builders use same ComponentSelector/Composer
3. **Extensible for future tools** - New builders just need to compose components
4. **Cost optimization path** - All users can choose minimal variants (85-90% token reduction)
5. **Better maintainability** - Filesystem is self-documenting; no manual registration
6. **Consistent experience** - All 6 tools work the same way
7. **Supports specialized workflows** - Subagents enable targeted capabilities

### Negative

1. **Refactoring effort** - KiloIDE and KiloCLI need significant changes
2. **File count increase** - ~270 new prompt files (15 agents × 3 components × 2 variants × ... subagents)
3. **Complexity in ComponentSelector** - Must handle all builder output formats
4. **Registry scaling** - Must handle discovery of 50+ agents/subagents
5. **Migration burden** - Users upgrading from alpha to beta need guidance

### Neutral

1. **Directory depth increases** - agents/{agent}/subagents/{subagent}/{variant}/component.md
2. **Filesystem becomes interface** - Discovery logic depends on file naming conventions

---

## Implementation Notes

### Dependencies

- Registry must be extended to support component structure
- ComponentSelector class must be created
- ComponentComposer class must be created
- All 5 builders must be updated to use components
- New Claude builder must be created
- CLI must add verbosity question
- Config schema must include prompts.verbosity

### Testing Strategy

- Unit tests for ComponentSelector (all variants)
- Unit tests for ComponentComposer (all builders)
- Integration tests: init → build → verify output
- E2E tests: full workflow with all builders
- Regression tests: ensure backward compatibility

### Rollout

1. **Phase 2A**: Planning & design finalized
2. **Phase 2B**: Components created (~270 files)
3. **Phase 2C**: Registry & builders updated
4. **Phase 2D**: Integration & testing
5. **Phase 2E**: Documentation
6. **Phase 2F**: Beta release with deprecation notice for kilo_modes.yaml

---

## Related Decisions

- **ADR-001**: Phase 1 Kilo Refactor (generates `.kilo/agents/` format)
- **PRD-002**: Phase 2 Unified Prompt Architecture (functional requirements)
- **Phase 3**: CLI Integration (will use this architecture for verbosity config)

---

## Approval

**Proposed By:** Promptosaurus Team  
**Approved By:** *[pending]*  
**Date Approved:** *[pending]*  

**Review Comments:** 
- [To be filled in during review]

