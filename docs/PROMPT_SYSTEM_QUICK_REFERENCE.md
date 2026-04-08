# Prompt System Redesign - Quick Reference

## Three Separate Initiatives

### Initiative 1: VERBOSE vs MINIMAL (Token/Context Reduction)

**Problem:** Current prompts are detailed (5-10k tokens per mode load). Users with context constraints need ultra-minimal versions.

**Solution:** Support both variants

| Current | Minimal Impact | Examples |
|---------|---|---|
| Architect roledef: 150 words | Architect roledef: 2 sentences | "Design systems with clear abstractions" |
| Feature.md: 31 lines | Feature.md: 10 lines | "Read files → propose → implement" |
| Task-breakdown.md: 40 lines | Task-breakdown.md: 12 lines | Size guide only, no methodology |
| System.md: 256 lines | System.md: 40 lines | Rules only, no explanations |

**Implementation:** Option B (Separate Files)
```
.kilocode/rules-minimal/          ← New directory
├── system.md                      ← Condensed
├── conventions.md
└── rules-code/feature.md          ← Condensed
```

**Impact:** 10x token reduction when using minimal variants, zero impact on verbose mode

---

### Initiative 2: SKILLS/WORKFLOWS (Architecture Refactor)

**Problem:** Current system is monolithic. Each "mode" is a bundle of:
- Role definition
- Core rules (duplicated)
- Subagent behaviors (task-breakdown, feature, testing strategies)
- This makes it hard to:
  - Reuse a skill across modes (e.g., "test writing" is Test-mode-only)
  - Compose complex workflows (need to manually chain modes)
  - Update a skill without touching mode files

**Solution:** Extract skills from modes

**Before (Current):**
```
Mode: Code
├── Role: "implement features following conventions"
├── Skills used: feature-implementation, house-style, boilerplate
└── But this is hardcoded in the role definition
```

**After (Proposed):**
```
Skill: feature-implementation
├── .kilocode/skills/feature-implementation/
├── Reusable by: Code, Orchestrator, Migration modes
└── Can be versioned, tested, documented independently

Mode: Code
├── Role: "implement features following conventions"
├── Uses skills: [feature-implementation, house-style, boilerplate]
└── Clear what skill is used and why
```

**What Extracts to Skills:**
- `rules-code/feature.md` → `skills/feature-implementation/`
- `rules-code/boilerplate.md` → `skills/boilerplate-generation/`
- `rules-test/strategy.md` → `skills/test-writing/`
- `rules-architect/task-breakdown.md` → `skills/epic-decomposition/`
- `rules-architect/data-model.md` → `skills/data-modeling/`
- `rules-review/code.md` → `skills/code-review/`

**Impact:**
- Enables skill reuse across modes
- Enables complex workflow composition
- Makes system more extensible (add skill without touching modes)
- Clear separation of concerns

---

### Initiative 3: ARCHITECT MODE VISIBILITY

**Current Situation:**
- Architect IS defined in `.kilocodemodes` (lines 2-18)
- Architect does NOT appear in Kilo IDE mode selector
- Architect works if manually invoked, but not discoverable

**Why It's Hidden:**
Three possible causes:
1. **Kilo IDE Version Issue** - Older version doesn't load custom modes from `.kilocodemodes`
2. **Config Path Issue** - `.kilocodemodes` not in right location for IDE to find
3. **Extension Disabled** - Kilo extension not loading `.kilocode/` rules

**How to Debug:**
```bash
# Check if .kilocodemodes is being read
grep -r "customModes" ~/.config/kilo/

# Check Kilo extension version
code --list-extensions | grep kilo

# Check if .kilocode path is accessible
ls -la .kilocode/rules-architect/
```

**Quick Fix:**
1. Open Kilo extension settings in VS Code
2. Look for "Kilo Code Modes" or "Custom Modes"
3. Enable if disabled
4. Reload VS Code
5. Check mode selector - architect should appear

**If Still Hidden:**
- Architect might not be in "built-in" list (it's custom)
- Need to check Kilo IDE source to understand mode discovery mechanism
- May need explicit registration in settings

---

## Decision Matrix: Which to Tackle First?

| Initiative | Effort | Impact | Dependencies | Blockers |
|-----------|--------|--------|--------------|----------|
| **Minimal Prompts** | 3 days | High (token reduction) | None | None |
| **Skills/Workflows** | 2-3 weeks | Very High (architecture) | Minimal done? | Need design review |
| **Architect Visibility** | 1 day research | Medium (enables architect) | None | IDE version/config |

**Recommended Sequence:**
1. **Day 1:** Debug architect mode visibility (quick win or identify blocker)
2. **Day 2-4:** Create minimal prompt variants (immediate value, low risk)
3. **Week 2-4:** Skills/workflows refactor (bigger change, needs planning)

---

## Minimal Prompts: What to Keep vs Drop

### Keep (Essential Context):
- Session management rules (branching, commits)
- Convention enforcement (naming, error handling, typing)
- What each mode/skill DOES (purpose, not philosophy)
- Acceptance criteria (what success looks like)

### Drop (Nice-to-Have):
- Extended examples (assume reader knows context)
- Philosophy/reasoning (trust the reader understands)
- Repetitive explanations (condense to bullet points)
- "When to use" elaborations (title should be clear)

**Example - Current vs Minimal:**

**Current (Test Mode):**
```markdown
When asked to generate tests:
You write comprehensive, well-organized test suites covering happy paths, 
edge cases, and error conditions. You use descriptive test names that explain
what they test. You apply the Arrange-Act-Assert pattern consistently...
[500 more words]
```

**Minimal:**
```markdown
# Test Writing Skill

When asked for tests:
- Cover: happy path, edge cases, errors
- Name tests descriptively (what they test)
- Use Arrange-Act-Assert pattern
- Mock at boundaries only (DB, API, filesystem)
- Target 80%+ coverage
```

**Token Savings:** ~300 tokens → ~50 tokens (6x reduction)

---

## Skills Registry (Post-Refactor)

Once skills are extracted, they could be catalogued:

```
SKILLS AVAILABLE (15 total)

Core Skills (Always Available):
  - code-reading: Analyze existing code structure
  - convention-checking: Verify code against standards

Development Skills:
  - feature-implementation: Build new features
  - boilerplate-generation: Create scaffolding
  - refactoring: Improve structure without changing behavior

Testing Skills:
  - unit-test-writing: Fast isolated tests
  - integration-test-writing: Multi-component tests
  - edge-case-generation: Find boundary conditions
  - mutation-testing: Verify test quality

Review Skills:
  - code-review: Correctness + security + performance
  - performance-analysis: Profile and optimize
  - accessibility-review: WCAG compliance

Architecture Skills:
  - epic-decomposition: Break down large work
  - data-modeling: Design schemas
  - decision-logging: Document architectural decisions
  - risk-assessment: Identify technical risks

Operations Skills:
  - deployment-planning: Generate deploy checklists
  - ci-cd-generation: Create pipelines
  - observability-design: Plan monitoring
```

Each skill would have:
- Purpose (one sentence)
- When to use (description)
- Input/output (what it expects, what it produces)
- Dependencies (other skills it builds on)
- Examples (how it's used)

---

## Implementation Roadmap

### Phase 1: Quick Wins (Week 1)
- [ ] Debug architect visibility in Kilo IDE
- [ ] Create .kilocode/rules-minimal/ directory structure
- [ ] Write 5 minimal prompts (system, code, test, review, architect)
- [ ] Document how to switch between verbose/minimal
- [ ] Test minimal prompts with sample tasks

### Phase 2: Full Minimal Coverage (Week 2)
- [ ] Complete all mode definitions in minimal variant
- [ ] Complete all skill files in minimal variant
- [ ] Update documentation
- [ ] Create option in .kilocodemodes to select promptLevel

### Phase 3: Skills Extraction (Weeks 3-4)
- [ ] Create skills/ directory structure
- [ ] Move rules-*/*.md to skills/*/
- [ ] Build skills registry
- [ ] Update mode definitions to reference skills
- [ ] Document skill composition model

### Phase 4: Workflow Orchestration (Week 5)
- [ ] Define workflow format
- [ ] Create example workflows (feature-to-prod, bug-hotfix, refactoring)
- [ ] Build workflow executor
- [ ] Document workflow patterns

---

## Questions for You

1. **Priority:** Which initiative should start first? (Architect visibility / Minimal prompts / Skills)

2. **Minimal Approach:** Option A (config-based toggle) or Option B (separate files)?

3. **Skills Scope:** Extract ALL rules as skills, or keep system/conventions as core always-loaded rules?

4. **Backwards Compat:** Do you have automation/workflows depending on current file structure?

5. **Validation:** Should we test minimal prompts with real tasks before full rollout?

