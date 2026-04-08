# Prompt System Architecture: Current vs Proposed

## Current Architecture (Monolithic)

```
.kilocodemodes
│
└── customModes (13 modes)
    ├── architect: { roleDefinition, whenToUse, groups }
    ├── code: { roleDefinition, whenToUse, groups }
    ├── test: { roleDefinition, whenToUse, groups }
    ├── review: { roleDefinition, whenToUse, groups }
    ├── debug: { roleDefinition, whenToUse, groups }
    └── ... (8 more modes)

.kilocode/rules/ (Core - Always Loaded)
├── system.md (256 lines) ← Session mgmt, branch rules, startup
├── conventions.md ← General conventions
├── conventions-python.md
└── conventions-typescript.md

.kilocode/rules-{MODE}/ (Mode-Specific Behaviors)
├── rules-code/
│   ├── feature.md ← How to implement features
│   ├── boilerplate.md ← How to scaffold code
│   └── house-style.md ← Code style enforcement
├── rules-architect/
│   ├── task-breakdown.md ← How to decompose epics
│   ├── data-model.md ← How to design schemas
│   └── scaffold.md ← How to setup projects
├── rules-test/
│   ├── strategy.md ← How to write tests
│   └── (other test strategies)
├── rules-review/
│   ├── code.md ← How to review code
│   ├── performance.md ← Performance review
│   └── accessibility.md ← A11y review
└── ... (other modes)

PROBLEM: Each rule file is embedded in a MODE context.
- Can't reuse "test-writing" across Code + Test + Migration modes
- No explicit skill/capability model
- Rules are scattered across 15+ directories
- Core conventions duplicated in mode descriptions
```

---

## Proposed Architecture (Modular + Orchestrated)

```
.kilocode/

├── rules/ (Core - Always Loaded)
│   ├── system.md (40 lines, condensed)
│   ├── conventions.md
│   ├── conventions-python.md
│   └── conventions-typescript.md
│
├── skills/ (NEW - Reusable Components)
│   ├── feature-implementation/
│   │   └── implementation.md ← Can be used by Code, Orchestrator, Migration
│   ├── boilerplate-generation/
│   │   └── scaffolding.md
│   ├── code-review/
│   │   ├── correctness.md
│   │   ├── performance.md
│   │   └── accessibility.md
│   ├── test-writing/
│   │   ├── unit-tests.md
│   │   ├── integration-tests.md
│   │   └── edge-cases.md
│   ├── epic-decomposition/
│   │   └── breakdown.md ← Can be used by Architect, Orchestrator, Planning
│   ├── data-modeling/
│   │   ├── schema-design.md
│   │   └── migrations.md
│   └── ... (15+ skills)
│
├── workflows/ (NEW - Skill Orchestration)
│   ├── feature-implementation-workflow.yaml
│   │   └── steps: [architect→code→test→review→orchestrate]
│   ├── hotfix-deployment.yaml
│   │   └── steps: [debug→code→test→orchestrate]
│   └── epic-delivery.yaml
│   │   └── steps: [architect→code→test→review→orchestrate→monitor]
│
├── modes/ (Lightweight - Role + Skill Composition)
│   ├── architect.yaml
│   │   ├── role: "Design systems and decompose work"
│   │   └── skills: [epic-decomposition, data-modeling, decision-logging]
│   ├── code.yaml
│   │   ├── role: "Implement features"
│   │   └── skills: [feature-implementation, boilerplate-generation, house-style]
│   ├── test.yaml
│   │   ├── role: "Write comprehensive tests"
│   │   └── skills: [test-writing, edge-case-generation, mutation-testing]
│   └── ... (10+ more modes)
│
└── .kilocodemodes (Kilo IDE Config - Auto-Generated from modes/)
    └── Derived from modes/ directory structure
        └── Each mode references its skills

BENEFITS:
✓ Skills are reusable across modes
✓ Modes are lightweight (just role + skill list)
✓ Easy to add new skills without touching modes
✓ Workflows compose skills into sequences
✓ Clear separation of concerns
✓ Skills can be versioned, tested independently
```

---

## Layer Definitions

### Layer 1: Core Rules (Unchanging Foundation)
**Files:** `.kilocode/rules/*.md`
**Loaded:** Always, for every mode
**Frequency:** Updated ~monthly (convention changes)
**Content:**
- Git branching rules
- Session management
- Naming conventions
- Error handling patterns
- Type system rules
- Import organization

**Lifecycle:** No. When you update rules, it affects ALL modes. Breaking change if you change core behavior.

---

### Layer 2: Skills (Reusable Procedures)
**Files:** `.kilocode/skills/{skill-name}/*.md`
**Loaded:** Only when mode asks for it
**Frequency:** Updated ~weekly (refining guidance)
**Content:**
- Step-by-step procedures for accomplishing a task
- Success criteria and acceptance rules
- Anti-patterns to avoid
- Examples and edge cases

**Examples:**
- `skills/feature-implementation/`: How to build a new feature
- `skills/test-writing/unit-tests.md`: How to write unit tests
- `skills/code-review/`: How to review code for correctness
- `skills/epic-decomposition/`: How to break down large work

**Reuse:** A skill is used by multiple modes:
```
Skills: test-writing
Used by modes: test, code, migration, orchestrator
Reason: Everyone needs to know how to write tests
```

---

### Layer 3: Modes (Role + Orchestration)
**Files:** `.kilocode/modes/{mode-slug}.yaml`
**Loaded:** When user selects mode
**Frequency:** Updated ~monthly (role/responsibility changes)
**Content:**
- Role definition (1-2 sentences)
- Which skills this role uses
- Which IDE features available (read/edit/browse/command)

**Example:** Architect Mode
```yaml
architect:
  slug: architect
  name: "🏗️ Architect"
  role: "Design scalable systems and decompose work"
  skills:
    - epic-decomposition    # When asked to break down work
    - data-modeling         # When asked to design schema
    - decision-logging      # When asked to document decisions
    - risk-assessment       # When asked to identify risks
  capabilities:
    - read: true
    - edit: [docs/*.md, .promptosaurus/sessions/*.md]
    - command: true
    - browse: true
```

---

### Layer 4: Workflows (Multi-Mode Sequences)
**Files:** `.kilocode/workflows/{workflow-name}.yaml`
**Loaded:** When user invokes a workflow (future feature)
**Frequency:** Updated ~monthly (process changes)
**Content:**
- Sequence of modes to engage
- Inputs to each mode
- Success criteria for each step
- Rollback/error handling

**Example:** Feature-to-Production Workflow
```yaml
feature-to-production:
  name: "Build & Ship a Feature"
  steps:
    - mode: architect
      task: "Break down feature into tasks"
      input: "Feature description"
      output: "Task breakdown with dependencies"
      
    - mode: code
      task: "Implement each task"
      input: "Task breakdown"
      output: "Code + tests"
      
    - mode: test
      task: "Verify test coverage"
      input: "Code changes"
      output: "Test report"
      
    - mode: review
      task: "Review for quality"
      input: "Code + tests"
      output: "Review feedback"
      
    - mode: orchestrator
      task: "Coordinate merge + deploy"
      input: "Reviewed code"
      output: "Deployed feature"
```

---

## Transition Path: Current → Proposed

### Phase 1: Create Minimal Variants (Week 1)
```
.kilocode/rules-minimal/        ← New: condensed versions
├── system.md                   ← 40 lines instead of 256
├── conventions.md
└── rules-code/feature.md       ← 10 lines instead of 31

Both verbose and minimal coexist.
IDE can toggle: promptLevel: verbose|minimal
```

### Phase 2: Extract Skills (Weeks 2-3)
```
.kilocode/skills/               ← New: extracted from rules-*
├── feature-implementation/
│   ├── implementation.md       ← Moved from rules-code/feature.md
│   └── patterns.md
├── test-writing/
│   ├── unit-tests.md           ← Moved from rules-test/strategy.md
│   └── edge-cases.md
└── ... (10+ more skills)

Existing .kilocode/rules-*/ directories remain for compatibility.
Skills are parallel structure.
```

### Phase 3: Create Mode Definitions (Weeks 3-4)
```
.kilocode/modes/                ← New: lightweight mode configs
├── architect.yaml              ← references skills
├── code.yaml                   ← references skills
└── ... (10+ modes)

Old .kilocodemodes still works (for IDE compatibility).
.kilocode/modes/ is canonical source of truth.
```

### Phase 4: Add Workflow Definitions (Week 5)
```
.kilocode/workflows/            ← New: multi-mode sequences
├── feature-to-production.yaml
├── hotfix-deployment.yaml
└── epic-delivery.yaml

Optional enhancement—requires workflow executor to implement.
```

---

## Current File Count Analysis

**Current System:**
```
.kilocode/rules/                 5 files
.kilocode/rules-architect/       3 files
.kilocode/rules-ask/             4 files
.kilocode/rules-code/            3 files
.kilocode/rules-compliance/      1 file
.kilocode/rules-debug/           4 files
.kilocode/rules-document/        1 file
.kilocode/rules-enforcement/     1 file
.kilocode/rules-explain/         1 file
.kilocode/rules-migration/       4 files
.kilocode/rules-orchestrator/    3 files
.kilocode/rules-planning/        2 files
.kilocode/rules-refactor/        2 files
.kilocode/rules-review/          3 files
.kilocode/rules-security/        1 file
.kilocode/rules-test/            1 file

Total: ~44 files across 16 directories (deeply nested)
```

**Proposed System (After Phase 4):**
```
.kilocode/rules/                 5 files (core - unchanged)
.kilocode/skills/                15 directories, ~40 files (extracted from rules-*)
.kilocode/modes/                 13 files (new, lightweight)
.kilocode/workflows/             5 files (new, optional)
.kilocode/rules-minimal/         ~20 files (new, parallel to current)

Total: ~80 files, but much better organized:
- Easy to find: all skills in one place
- Easy to understand: mode = role + skill list
- Easy to extend: add skill without touching modes
- Easy to navigate: less deep nesting
```

---

## Why Skills/Workflows Matter

### Problem 1: Scattered Knowledge
Currently, "how to write tests" lives in:
- `.kilocode/rules-test/strategy.md` (Test mode perspective)
- Embedded in `.kilocode/rules-code/feature.md` (Code mode mentions it)
- Implied in `.kilocode/rules-ask/testing.md` (Ask mode testing subagent)

**With Skills:** Single source of truth in `.kilocode/skills/test-writing/`

### Problem 2: Incomplete Workflows
Users often need to chain modes:
1. Architect: Break down feature
2. Code: Implement feature
3. Test: Write tests
4. Review: Review code

Currently, this is manual. Users have to:
- Exit architect mode
- Enter code mode
- Exit code mode
- Enter test mode
- Exit test mode
- Enter review mode

**With Workflows:** Can invoke "feature-to-production" and orchestrate the sequence.

### Problem 3: Adding New Capabilities
Currently, to add "mutation testing" capability:
1. Create `.kilocode/rules-test/mutation-testing.md`
2. Update Test mode description
3. Update system docs
4. Update all related mode references

**With Skills:** Just add `.kilocode/skills/mutation-testing/` and reference it from Test mode.

---

## Implementation Decision: Backwards Compatibility

**Question:** Should we keep existing `.kilocode/rules-*/` directories?

**Option A: Parallel (Safest)**
- Keep `.kilocode/rules-*/` as-is
- Add `.kilocode/skills/` alongside
- IDE loads from both during transition
- Deprecate old directories over time
- Migration: 6+ months

**Option B: Cutover (Cleanest)**
- Move all `.kilocode/rules-*/` into `.kilocode/skills/`
- Update `.kilocodemodes` to reference skills
- Rename/consolidate directories
- Clean one-time migration
- Migration: 2-3 weeks

**Recommendation:** Start with Option A (parallel), then migrate to B after 1-2 months of validation.

