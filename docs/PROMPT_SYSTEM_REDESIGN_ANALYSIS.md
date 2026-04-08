# Prompt System Redesign Analysis

## Executive Summary

Your prompt system is well-architected but built on a monolithic model where each mode bundles everything together (core rules + role definition + subagent behaviors). This analysis explores:

1. **Verbose vs Minimal**: How to support both with a configuration-based approach
2. **Skills/Workflows**: How to extract reusable components and orchestration patterns
3. **Architect Mode Visibility**: Why it's defined but not visible in Kilo IDE

---

## 1. VERBOSE vs MINIMAL PROMPTS

### Current State: Monolithic Role Definitions

Each mode in `.kilocodemodes` has a verbose `roleDefinition` (150-400 words):

**Current (Verbose) - Architect Mode:**
```yaml
roleDefinition: You are a principal architect specializing in system design, data
  modeling, and technical decision making. You design scalable, maintainable systems
  with clear boundaries and appropriate abstractions. You consider tradeoffs between
  simplicity, performance, scalability, and maintainability. You create clear documentation
  of architectural decisions including the reasoning, alternatives considered, and
  consequences.
```

### Proposed: Dual-Level System

Create two variants: **VERBOSE** (current) and **MINIMAL** (ultra-concise):

#### Minimal Role Definition (1-2 sentences):
```yaml
architect:
  minimal: |
    You are a principal architect. Design scalable systems with clear abstractions.
    Document architectural decisions with reasoning and alternatives.
```

#### Minimal Behavior Files (3-4 bullet points instead of 40-line docs):

**Current:** `.kilocode/rules-code/feature.md` (31 lines)
```markdown
# Subagent - Code Feature
1. Read relevant files, identify changes, propose approach
2. Implement following conventions and patterns
3. List follow-up work and tests needed
Output: plan → confirmation → implementation → follow-up
```

**Minimal version (8 lines):**
```markdown
# Code: Implement Feature
- Read files → propose approach
- Implement + match patterns
- List follow-up work
```

### Implementation Strategy

**Option A: Configuration-Based Mode Selection**
```yaml
# .kilocodemodes configuration
promptLevel: "verbose" | "minimal"  # Toggle at startup

# Each mode has both:
customModes:
  - slug: architect
    roleDefinition:
      verbose: |
        You are a principal architect... (150+ words)
      minimal: |
        You are a principal architect... (1-2 sentences)
    whenToUse:
      verbose: |
        Use this mode for... (detailed explanation)
      minimal: |
        System design & architecture
```

**Option B: Separate Mode Files**
```
.kilocode/
├── rules-verbose/       # Current detailed prompts
│   ├── rules/
│   ├── rules-architect/
│   └── ...
├── rules-minimal/       # New condensed versions
│   ├── rules/
│   ├── rules-architect/
│   └── ...
└── .kilocodemodes.verbose
└── .kilocodemodes.minimal
```

### Sample Minimal Prompts (Impact Without Verbosity)

#### Architect (Minimal)
```markdown
# Architect Mode - Minimal

You design scalable systems with clear abstractions. Document decisions with 
reasoning, alternatives, and consequences.

When asked to design something:
- Ask clarifying questions about constraints and patterns
- Propose an approach with tradeoffs
- Document in ADR format

When asked to break down work:
- Create tasks: title, description, acceptance criteria, dependencies, size
- Flag architectural decision points
- Suggest execution sequence
```

#### Code (Minimal)
```markdown
# Code Mode - Minimal

You implement features following conventions and patterns.

When implementing:
- Read existing code for patterns
- Propose approach before coding
- Implement following conventions
- List follow-up work
```

#### Test (Minimal)
```markdown
# Test Mode - Minimal

You write tests that verify behavior, not implementation.

When writing tests:
- Cover: happy path, edge cases, error paths
- Name tests descriptively
- Mock only at true boundaries
- Target 80%+ coverage
```

#### Review (Minimal)
```markdown
# Review Mode - Minimal

You review code for correctness, security, maintainability—in that priority order.

When reviewing:
- Report severity (BLOCKER / SUGGESTION / NIT)
- Show exact location and concrete fix
- End with verdict: Ready / Needs changes / Needs discussion
```

### Minimal Impact Comparison

| Aspect | Verbose | Minimal | Trade-off |
|--------|---------|---------|-----------|
| Roledef length | 150-400 words | 1-2 sentences | Less context, clear intent |
| Behavior doc | 40+ lines | 5-10 lines | Removes examples, keeps essence |
| Learning curve | Thorough | Fast | Deep guidance vs quick start |
| Token usage | ~5-10k per mode | ~0.5-1k per mode | 10x smaller but loses nuance |
| Fit for | Detailed work | Quick context | Different use cases |

---

## 2. SKILLS/WORKFLOWS REDESIGN

### Current Problem: Everything is a Mode

The system treats "things to do" as "modes to enter":
- Code feature → **Code mode** (with feature.md subagent)
- Break down epic → **Architect mode** (with task-breakdown.md subagent)
- Write test → **Test mode** (with strategy.md subagent)
- Deploy something → **Orchestrator mode** (with devops.md subagent)

But these aren't really modes—they're **skills** (reusable procedures) and **workflows** (sequences of skills).

### Proposed Architecture

#### Layer 1: Core Rules (No Change)
```
.kilocode/rules/
├── system.md              # ← Always loaded
├── session.md
├── conventions.md
├── conventions-python.md
├── conventions-typescript.md
```

#### Layer 2: Skills (NEW - Extracted from Mode Rules)
```
.kilocode/skills/
├── feature-implementation/    # Was: rules-code/feature.md
│   └── implementation.md
├── test-writing/              # Was: rules-test/strategy.md
│   ├── unit-tests.md
│   ├── integration-tests.md
│   └── edge-cases.md
├── code-review/               # Was: rules-review/code.md
│   ├── correctness-check.md
│   ├── performance-check.md
│   └── security-check.md
├── task-breakdown/            # Was: rules-architect/task-breakdown.md
│   └── epic-decomposition.md
├── data-modeling/             # Was: rules-architect/data-model.md
│   └── schema-design.md
└── documentation/             # Was: rules-document/strategy.md
    ├── api-docs.md
    ├── README.md
    └── inline-comments.md
```

#### Layer 3: Modes (Orchestration + Role)
```
.kilocodemodes                   # ← Role definitions + skill orchestration
├── architect:                   # What architect DOES
│   └── uses: [data-modeling, task-breakdown, decision-log]
├── code:                        # What developer DOES
│   └── uses: [feature-implementation, house-style, boilerplate]
├── test:                        # What test engineer DOES
│   └── uses: [test-writing, coverage-analysis]
├── review:                      # What reviewer DOES
│   └── uses: [code-review, performance-review, accessibility-check]
└── ...
```

### Real-World Example: Feature Implementation Workflow

**Old approach (monolithic):**
1. Enter Code mode
2. Read rules-code/feature.md
3. Read rules-code/house-style.md
4. Read rules-code/boilerplate.md
5. Implement
6. Switch to Test mode
7. Read rules-test/strategy.md
8. Write tests
9. Switch to Review mode

**New approach (modular):**
1. Load skill: feature-implementation
2. Load skill: test-writing
3. Load skill: code-review
4. Orchestrate: implement → test → review
5. Mode selection (code/architect/debug) determines **how** but skills define **what**

### Breaking Out Architect Mode into Skills

**Current:** Everything in one mode file
```
.kilocode/rules-architect/
├── task-breakdown.md    (Epic decomposition)
├── data-model.md        (Schema design)
└── scaffold.md          (Project setup)
```

**New:** Architect mode = orchestration + skills
```
.kilocode/skills/
├── task-breakdown/
│   ├── epic-decomposition.md      ← Core skill
│   ├── sizing-guide.md
│   └── dependency-analysis.md
├── data-modeling/
│   ├── schema-design.md           ← Core skill
│   ├── entity-relationships.md
│   └── migration-strategy.md
└── project-scaffolding/
    ├── structure-design.md        ← Core skill
    └── boilerplate-generation.md

.kilocodemodes
architect:
  roleDefinition: You design systems and break down epics
  skills: [task-breakdown, data-modeling, project-scaffolding]
  subagents: {
    "break down epic": task-breakdown,
    "design schema": data-modeling,
    "scaffold project": project-scaffolding
  }
```

### Benefits of Skills/Workflows Architecture

| Benefit | How Achieved |
|---------|-------------|
| **Reuse** | A skill (e.g., test-writing) is used by multiple modes |
| **Composition** | Modes are assembled from skills; complex workflows orchestrate multiple skills |
| **Clarity** | Skill = "this is how you do X"; Mode = "this is the role that uses X, Y, Z" |
| **Testing** | Skills can be unit tested independently |
| **Evolution** | Add new skill without touching mode definitions |
| **Documentation** | Clear what each skill does; clear what role handles what |

---

## 3. ARCHITECT MODE NOT SHOWING IN KILO

### Current State

**Architect IS defined in `.kilocodemodes` (lines 2-18):**
```yaml
customModes:
  - slug: architect
    name: 🏗️ Architect
    description: System design, architecture planning...
    roleDefinition: You are a principal architect...
```

**But it doesn't appear in Kilo IDE. Why?**

### Root Cause Analysis

#### Hypothesis 1: Kilo IDE vs Kilo CLI Different Config
- Kilo IDE uses `.kilocode/` configuration
- Kilo CLI might use different config location
- `.kilocodemodes` might be for IDE only

**Evidence:** Instructions in system.md reference `.kilo/` but project uses `.kilocode/`

#### Hypothesis 2: Mode Registration Issue
- Modes in `.kilocodemodes` are "custom modes"
- Kilo IDE might only show "built-in" modes by default
- Custom modes might need explicit registration

**Check:** Look for where `.kilocodemodes` is loaded and how Kilo IDE discovers modes

#### Hypothesis 3: Configuration Not Being Loaded
- Kilo IDE might not be looking at `.kilocodemodes`
- Might need environment variable or config flag to enable custom modes
- Plugin system might be disabled

### Investigation Steps

1. **Check Kilo IDE Settings:**
   ```bash
   # Does Kilo look for .kilocodemodes?
   grep -r "kilocodemodes" ~/.config/kilo/ 2>/dev/null
   
   # Are custom modes enabled?
   grep -r "customModes" ~/.config/kilo/ 2>/dev/null
   ```

2. **Check Kilo IDE Plugin System:**
   - Kilo extensions might not be loading `.kilocode/rules`
   - Check if VS Code extension is installed and enabled
   - Check if there's a Kilo settings file that controls which modes appear

3. **Check Environment:**
   - Is `KILOCODE_PATH` set?
   - Is `.kilocode/` in the right location?
   - Are file permissions blocking access?

### Proposed Solutions

#### Solution 1: Explicit Mode Registration (If Supported)
```yaml
# .kilocode/mode-registry.yaml
modes:
  - id: architect
    slug: architect
    name: 🏗️ Architect
    enabled: true
    source: .kilocodemodes
```

#### Solution 2: Move to Built-in Mode Location
If Kilo has a standard location for modes:
```
~/.config/kilo/modes/architect.yaml
```

#### Solution 3: Verify Kilo IDE Configuration
Check if there's a setting that controls custom mode visibility:
```json
// ~/.config/kilo/settings.json
{
  "kilocode.customModes.enabled": true,
  "kilocode.searchPaths": [".kilocode"]
}
```

#### Solution 4: Check VS Code Extension
If using Kilo as VS Code extension:
- Open extension settings
- Look for "Kilo Code Modes" settings
- Ensure "Show Custom Modes" is enabled
- Check that `.kilocode/` is recognized as project root

### How Architect Should Work in Kilo

Once visible, architect mode should:
1. Show in mode selector (along with Code, Test, Debug, etc.)
2. Load `.kilocode/rules-architect/` files
3. Execute architect-specific behaviors from subagent files
4. Integrate with session management

**Expected flow:**
```
User clicks mode selector → Selects "🏗️ Architect"
→ Kilo loads .kilocodemodes architect definition
→ Loads .kilocode/rules-architect/* files
→ Shows architect-specific command palette
→ Can ask to "break down epic", "design schema", "scaffold project"
```

---

## Recommendations: Priority Order

### Phase 1: Quick Wins (1 week)
1. **Fix Architect Mode Visibility**
   - Investigate why it's not showing in Kilo IDE
   - Verify `.kilocodemodes` is being loaded
   - Test architect mode manually if needed

2. **Create Minimal Prompt Variants** (Option B: Separate Files)
   - Duplicate `.kilocodemodes` → `.kilocodemodes.minimal`
   - Create `.kilocode/rules-minimal/` with condensed prompts
   - Add toggle in docs explaining how to switch

### Phase 2: Structural Refactor (2-3 weeks)
1. **Extract Skills**
   - Create `.kilocode/skills/` directory
   - Move existing rule files into skill structure
   - Build skill index/registry

2. **Refactor Mode Definitions**
   - Simplify modes to orchestration + role only
   - Remove duplicate content (move to skills)
   - Update `.kilocodemodes` to reference skills

3. **Build Workflow Orchestration**
   - Create workflow definitions
   - Example: `feature-to-production` workflow uses [architect, code, test, review, orchestrator]
   - Document how to execute workflows

### Phase 3: Documentation & Tooling (1 week)
1. **Update AGENTS.md** to reflect skill/workflow model
2. **Create skill catalog** showing what each skill does
3. **Create workflow recipes** for common patterns
4. **Add prompting guide** for switching between verbose/minimal

---

## Appendix: Example Minimal Prompt Files

### `.kilocode/rules-minimal/system.md`
```markdown
# System Rules (Minimal)

## Starting Work
1. **Branch:** Always on feature branch (never main)
2. **Session:** Create or read session in .promptosaurus/sessions/
3. **Context:** Read session Context Summary before proceeding

## Working
- Follow conventions in conventions.md
- Run tests before commit
- Update session after significant work

## Committing
- Conventional commits: feat|fix|refactor|test|docs|chore
- No secrets in commits
- Tests must pass
```

### `.kilocode/rules-minimal/conventions.md`
```markdown
# Conventions (Minimal)

## Files
- Python: snake_case
- Classes: One per file, PascalCase filename
- Tests: tests/{unit,integration}/test_{file}.py

## Code
- Type hints on all public functions
- Error handling: custom exceptions, don't swallow
- Imports: stdlib → third-party → local

## Testing
- Unit: fast, isolated, 80%+ coverage
- Integration: real services where possible
- Names: describe what they test

## Git
- Branches: feat|bugfix|hotfix / TICKET-ID - description
- Commits: Conventional Commits format
- PR: Summary section required
```

---

## Questions for Next Steps

1. **Verbose vs Minimal:** Do you want both available simultaneously (config toggle) or switchable per project?

2. **Skills Extraction:** Should we extract ALL rules into skills, or keep core conventions as "always-on" rules?

3. **Architect Mode:** Should we investigate the Kilo IDE integration issue now, or assume it's a version/config problem?

4. **Timeline:** Should Phase 1 (fixes) happen before Phase 2 (refactor), or in parallel?

5. **Backwards Compatibility:** Do existing workflows/automation rely on current `.kilocodemodes` structure?

