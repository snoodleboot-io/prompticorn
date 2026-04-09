# Phase 2: Comprehensive Prompt Refactoring Design
## Minimal/Verbose + Prompt/Skill/Workflow Decomposition + Subagent Architecture

---

## Part 1: Prompt Component Architecture (NEW)

### Core Concept: Decompose Each Mode Into Components

Every agent/mode consists of THREE components:

```
AGENT = PROMPT + SKILLS + WORKFLOW

PROMPT:
  - Role definition: "You are a..."
  - Principles: Core values and constraints
  
SKILLS:
  - What the agent CAN DO (specific capabilities)
  - Constraints on those capabilities
  - Examples: "identify security vulnerabilities", "write idiomatic code"
  
WORKFLOW:
  - Step-by-step process the agent SHOULD FOLLOW
  - Decision points and checkpoints
  - Ordering of operations
  - Example: "1. Read code, 2. Check each line, 3. Identify issues, 4. Generate report"
```

### Why This Matters

**Current state:**
```
review mode:
  roleDefinition: "You are a principal engineer and code reviewer..."
    [covers correctness, security, performance, accessibility in one paragraph]
  whenToUse: "Use this mode when reviewing code..."
```

**Problems:**
- Code review, performance review, and accessibility review are bundled
- No clear skills or workflow defined
- Hard to make minimal versions - what do you remove?
- Can't reuse components across modes

**Proposed state:**
```
review agent (main):
  prompt: "You review code systematically"
  
  subagent: review-code
    prompt: "Review for correctness and logic"
    skills:
      - Identify logic errors
      - Check error handling
      - Verify business logic correctness
    workflow:
      1. Understand the code's intent
      2. Trace execution paths
      3. Identify issues by category
      4. Generate verdict
  
  subagent: review-performance
    prompt: "Review for performance issues"
    skills:
      - Identify O(n²) algorithms
      - Find unnecessary allocations
      - Spot blocking operations
    workflow:
      1. Profile mentally
      2. Identify bottlenecks
      3. Suggest optimizations
  
  subagent: review-accessibility
    prompt: "Review for accessibility"
    skills:
      - Check WCAG compliance
      - Identify usability issues
      - Verify screen reader compatibility
    workflow:
      1. Check standards compliance
      2. Test with assistive tech
      3. Generate report
```

---

## Part 2: Current Modes Analysis & Agent/Subagent Differentiation

### 15 Kilo Modes → Reimagined as Agent/Subagent Structure

#### ✅ TIER 1: PRIMARY AGENTS (Main modes users select)

**1. ARCHITECT Agent**
- Role: System design, architecture, technical decisions
- Current issues: Too broad, covers too much
- Proposed subagents:
  - **architect-scaffold** (project structure setup) ✓ EXISTING
  - **architect-task-breakdown** (decompose work) ✓ EXISTING
  - **architect-data-model** (design data structures) ✓ EXISTING
  - **architect-decision** (document architectural decisions) ⚠ MISSING
  - **architect-technology-selection** (choose technologies/frameworks) ⚠ MISSING
  - **architect-tradeoff-analysis** (evaluate design tradeoffs) ⚠ MISSING

**2. CODE Agent**
- Role: Feature implementation, code changes
- Current issues: Too broad, doesn't distinguish between different coding tasks
- Proposed subagents:
  - **code-feature** (implement features) ✓ EXISTING
  - **code-boilerplate** (generate structure) ✓ EXISTING
  - **code-house-style** (enforce style) ✓ EXISTING
  - **code-refactor** (improve structure) ⚠ DUPLICATE? (refactor is separate agent)
  - **code-migration** (handle upgrades) ✓ EXISTING
  - **code-dependency-upgrade** (upgrade deps) ✓ EXISTING
  - **code-security-fix** (secure vulnerable code) ⚠ MISSING
  - **code-performance-optimization** (optimize for speed) ⚠ MISSING

**3. REVIEW Agent**
- Role: Code quality assurance
- Current issues: Bundles code, performance, AND accessibility - these are distinct concerns
- Proposed subagents:
  - **review-code** (correctness, logic, error handling) ✓ EXISTING
  - **review-performance** (speed, efficiency, memory) ✓ EXISTING
  - **review-accessibility** (WCAG, usability, assistive tech) ✓ EXISTING
  - **review-maintainability** (readability, structure, testing) ⚠ MISSING

**4. TEST Agent**
- Role: Test writing and coverage
- Current issues: No subagents, treats all testing as monolithic
- Proposed subagents:
  - **test-strategy** (testing approach) ✓ EXISTING (in registry)
  - **test-unit** (unit test writing) ⚠ MISSING
  - **test-integration** (integration test writing) ⚠ MISSING
  - **test-edge-cases** (boundary condition testing) ⚠ MISSING
  - **test-mutation-scoring** (verify test quality) ⚠ MISSING

**5. DOCUMENT Agent**
- Role: Documentation generation
- Current issues: No subagents, one-size-fits-all approach
- Proposed subagents:
  - **document-api** (API documentation) ⚠ MISSING
  - **document-guide** (user/developer guides) ⚠ MISSING
  - **document-changelog** (release notes) ⚠ MISSING
  - **document-architecture** (architecture docs) ⚠ MISSING
  - **document-inline** (code comments) ⚠ MISSING

**6. REFACTOR Agent**
- Role: Code quality and structure improvement
- Current issues: Might overlap with code agent's refactor skill
- Proposed subagents:
  - **refactor-strategy** (plan refactoring) ✓ EXISTING
  - **refactor-duplication** (eliminate copy-paste) ⚠ MISSING
  - **refactor-complexity** (reduce cyclomatic complexity) ⚠ MISSING

**7. DEBUG Agent**
- Role: Problem diagnosis and fixing
- Current issues: No clear subagents
- Proposed subagents:
  - **debug-root-cause** (find underlying issue) ✓ EXISTING
  - **debug-log-analysis** (analyze logs/traces) ✓ EXISTING
  - **debug-rubber-duck** (think through problem) ✓ EXISTING
  - **debug-performance** (profile and optimize) ⚠ MISSING

**8. MIGRATION Agent**
- Role: Framework/dependency upgrades
- Current issues: No clear structure
- Proposed subagents:
  - **migration-strategy** (plan migration) ✓ EXISTING
  - **migration-breaking-changes** (identify what breaks) ⚠ MISSING
  - **migration-incremental** (perform step-by-step) ⚠ MISSING

**9. SECURITY Agent**
- Role: Security review and hardening
- Current issues: No subagents, treats all security uniformly
- Proposed subagents:
  - **security-review** (security audit) ✓ EXISTING
  - **security-threat-modeling** (identify attack vectors) ⚠ MISSING
  - **security-vulnerability-fix** (patch vulnerabilities) ⚠ MISSING
  - **security-secrets-management** (handle credentials) ⚠ MISSING

**10. COMPLIANCE Agent**
- Role: Regulatory compliance and auditing
- Current issues: No subagents
- Proposed subagents:
  - **compliance-review** (audit for compliance) ✓ EXISTING
  - **compliance-soc2** (SOC 2 requirements) ⚠ MISSING
  - **compliance-gdpr** (GDPR requirements) ⚠ MISSING
  - **compliance-hipaa** (HIPAA requirements) ⚠ MISSING

**11. EXPLAIN Agent**
- Role: Code walkthroughs, onboarding
- Current issues: Too broad, doesn't distinguish between explaining architecture vs implementation
- Proposed subagents:
  - **explain-architecture** (explain system design) ⚠ MISSING
  - **explain-code** (walkthrough implementation) ⚠ MISSING
  - **explain-patterns** (explain design patterns) ⚠ MISSING
  - **explain-onboarding** (new developer onboarding) ⚠ MISSING

**12. ASK Agent**
- Role: Answer questions, provide context
- Current issues: Very broad
- Proposed subagents:
  - **ask-docs** (documentation generation) ✓ EXISTING
  - **ask-testing** (testing guidance) ✓ EXISTING
  - **ask-decision-log** (record decisions) ✓ EXISTING
  - **ask-explanation** (explain concepts) ⚠ MISSING

**13. PLANNING Agent**
- Role: Requirements and planning
- Current issues: Limited subagents
- Proposed subagents:
  - **planning-prd** (product requirements) ⚠ MISSING (implied)
  - **planning-ard** (architecture decisions) ⚠ MISSING (implied)
  - **planning-estimation** (size/effort estimation) ⚠ MISSING
  - **planning-stakeholder** (communicate with stakeholders) ⚠ MISSING

**14. ENFORCEMENT Agent**
- Role: Code standards audit
- Current issues: Very specialized, single purpose
- Proposed subagents:
  - **enforcement-standards** (check against conventions) ⚠ EXISTING but monolithic
  - **enforcement-patterns** (check design patterns) ⚠ MISSING
  - **enforcement-security** (check security rules) ⚠ MISSING

**15. ORCHESTRATOR Agent**
- Role: Multi-step workflow coordination
- Current issues: Meta-agent, no clear subagents
- Proposed subagents:
  - **orchestrator-meta** (process management) ✓ EXISTING
  - **orchestrator-devops** (deployment/infrastructure) ✓ EXISTING
  - **orchestrator-pr-description** (generate PR descriptions) ✓ EXISTING
  - **orchestrator-feature-coordination** (feature delivery from design to deploy) ⚠ MISSING

---

## Part 3: Minimal vs Verbose Variants

### Strategy: Decompose Minimal/Verbose at Component Level

Instead of creating two full versions of each agent, create variants for each COMPONENT:

**Minimal variant (stripped to essentials):**
```yaml
prompt:
  role: "You are a [concise 1-2 sentence definition]"
  
skills:
  - "[Core skill 1]"
  - "[Core skill 2]"
  
workflow:
  - "[Step 1]"
  - "[Step 2]"
```

**Verbose variant (full detail):**
```yaml
prompt:
  role: "[Detailed role definition with expertise areas]"
  principles:
    - "[Principle 1 with explanation]"
    - "[Principle 2 with explanation]"
  
skills:
  - name: "[Skill name]"
    description: "[How to perform this skill]"
    constraints: "[When NOT to use this skill]"
  
workflow:
  - name: "[Step name]"
    description: "[What this step accomplishes]"
    checkpoints: "[How to verify completion]"
    fallbacks: "[What to do if this fails]"
```

### Token Impact Estimate

**Minimal (all modes):** ~500-800 tokens total
**Verbose (all modes):** ~4000-5000 tokens total
**Reduction:** 85-90%

---

## Part 4: Directory Structure (New)

```
promptosaurus/
├── prompts/
│   ├── agents/
│   │   ├── core/                          (always loaded)
│   │   │   ├── core-system.md
│   │   │   ├── core-conventions.md
│   │   │   └── ...
│   │   │
│   │   ├── architect/
│   │   │   ├── minimal/
│   │   │   │   ├── prompt.md              (role + principles)
│   │   │   │   ├── skills.md              (list of capabilities)
│   │   │   │   └── workflow.md            (step-by-step process)
│   │   │   │
│   │   │   ├── verbose/
│   │   │   │   ├── prompt.md
│   │   │   │   ├── skills.md
│   │   │   │   └── workflow.md
│   │   │   │
│   │   │   └── subagents/
│   │   │       ├── architect-scaffold/
│   │   │       │   ├── minimal/
│   │   │       │   │   ├── prompt.md
│   │   │       │   │   ├── skills.md
│   │   │       │   │   └── workflow.md
│   │   │       │   └── verbose/
│   │   │       │       ├── prompt.md
│   │   │       │       ├── skills.md
│   │   │       │       └── workflow.md
│   │   │       │
│   │   │       ├── architect-task-breakdown/
│   │   │       │   └── ... (minimal/verbose)
│   │   │       │
│   │   │       ├── architect-data-model/
│   │   │       │   └── ... (minimal/verbose)
│   │   │       │
│   │   │       ├── architect-decision/        ⚠ NEW
│   │   │       │   └── ... (minimal/verbose)
│   │   │       │
│   │   │       ├── architect-technology-selection/  ⚠ NEW
│   │   │       │   └── ... (minimal/verbose)
│   │   │       │
│   │   │       └── architect-tradeoff-analysis/  ⚠ NEW
│   │   │           └── ... (minimal/verbose)
│   │   │
│   │   ├── code/
│   │   │   ├── minimal/ ... verbose/
│   │   │   └── subagents/ (with new ones)
│   │   │       ├── code-feature/
│   │   │       ├── code-boilerplate/
│   │   │       ├── code-house-style/
│   │   │       ├── code-migration/
│   │   │       ├── code-dependency-upgrade/
│   │   │       ├── code-security-fix/       ⚠ NEW
│   │   │       └── code-performance-optimization/  ⚠ NEW
│   │   │
│   │   ├── review/
│   │   │   ├── minimal/ ... verbose/
│   │   │   └── subagents/
│   │   │       ├── review-code/
│   │   │       ├── review-performance/
│   │   │       ├── review-accessibility/
│   │   │       └── review-maintainability/  ⚠ NEW
│   │   │
│   │   ├── test/
│   │   │   ├── minimal/ ... verbose/
│   │   │   └── subagents/
│   │   │       ├── test-strategy/
│   │   │       ├── test-unit/               ⚠ NEW
│   │   │       ├── test-integration/        ⚠ NEW
│   │   │       ├── test-edge-cases/         ⚠ NEW
│   │   │       └── test-mutation-scoring/   ⚠ NEW
│   │   │
│   │   ├── document/
│   │   │   ├── minimal/ ... verbose/
│   │   │   └── subagents/
│   │   │       ├── document-api/            ⚠ NEW
│   │   │       ├── document-guide/          ⚠ NEW
│   │   │       ├── document-changelog/      ⚠ NEW
│   │   │       ├── document-architecture/   ⚠ NEW
│   │   │       └── document-inline/         ⚠ NEW
│   │   │
│   │   ├── refactor/
│   │   ├── debug/
│   │   ├── migration/
│   │   ├── security/
│   │   ├── compliance/
│   │   ├── explain/
│   │   ├── ask/
│   │   ├── planning/
│   │   ├── enforcement/
│   │   └── orchestrator/
│   │       (all following same minimal/verbose + subagent structure)
```

---

## Part 5: Implementation Impact

### Files to Create

**New prompt components:**
- 15 main agents × (minimal + verbose) × 3 files (prompt/skills/workflow) = 90 files
- ~30 new subagents × (minimal + verbose) × 3 files = 180 files
- **Total: ~270 new prompt files**

**Code changes:**
- Update KiloIDEBuilder to compose agent files from components
- Update KiloCLIBuilder to compose agent files from components
- Update registry to support new structure
- Create ComponentSelector (like PromptSelector but for components)
- Update all builders to support minimal/verbose selection

### Files to Modify

- `promptosaurus/registry.py` - add component-level discovery
- `promptosaurus/builders/builder.py` - pass verbosity to subclasses
- `promptosaurus/builders/kilo/kilo_ide.py` - compose from components
- `promptosaurus/builders/kilo/kilo_cli.py` - compose from components
- `promptosaurus/builders/cline.py` - support minimal/verbose
- Other builders - support minimal/verbose
- `promptosaurus/cli.py` - add verbosity question

---

## Part 6: Summary of Additions

### NEW SUBAGENTS (34 new specialized agents)

**Architect additions:**
- architect-decision (document design decisions)
- architect-technology-selection (technology choices)
- architect-tradeoff-analysis (evaluate design options)

**Code additions:**
- code-security-fix (fix security vulnerabilities)
- code-performance-optimization (optimize for speed)

**Review additions:**
- review-maintainability (structure, readability, testing)

**Test additions:**
- test-unit (unit test writing)
- test-integration (integration test writing)
- test-edge-cases (boundary condition testing)
- test-mutation-scoring (verify test quality)

**Document additions:**
- document-api (API documentation)
- document-guide (user/developer guides)
- document-changelog (release notes)
- document-architecture (architecture documentation)
- document-inline (code comments)

**Debug additions:**
- debug-performance (profile and optimize)

**Migration additions:**
- migration-breaking-changes (identify breaking changes)
- migration-incremental (perform step-by-step migration)

**Security additions:**
- security-threat-modeling (identify attack vectors)
- security-vulnerability-fix (patch vulnerabilities)
- security-secrets-management (credentials and secrets)

**Compliance additions:**
- compliance-soc2 (SOC 2 auditing)
- compliance-gdpr (GDPR compliance)
- compliance-hipaa (HIPAA compliance)

**Explain additions:**
- explain-architecture (explain system design)
- explain-code (code walkthroughs)
- explain-patterns (design patterns explanation)
- explain-onboarding (new developer onboarding)

**Ask additions:**
- ask-explanation (explain concepts)

**Planning additions:**
- planning-estimation (size and effort estimation)
- planning-stakeholder (stakeholder communication)

**Enforcement additions:**
- enforcement-patterns (design pattern enforcement)
- enforcement-security (security rule enforcement)

**Orchestrator additions:**
- orchestrator-feature-coordination (feature delivery)

**Total:** 34 new subagents (from 15 current to ~49 total)

---

## Part 7: Implementation Roadmap

### Phase 2A: Component Structure (Week 1)
- [ ] Design prompt/skill/workflow file format (YAML or Markdown with sections)
- [ ] Create structure for first agent (architect) with all minimal/verbose variants
- [ ] Implement ComponentSelector and ComponentComposer classes
- [ ] Update registry to discover components

### Phase 2B: Prompt Creation (Weeks 2-3)
- [ ] Break down all 15 main agents into prompt/skill/workflow
- [ ] Create minimal variants (90 files for main agents)
- [ ] Create verbose variants
- [ ] Create all 34 new subagents (minimal + verbose)
- [ ] **Total: 270+ new prompt files**

### Phase 2C: Builder Integration (Weeks 4-5)
- [ ] Update KiloIDEBuilder to compose from components
- [ ] Update KiloCLIBuilder to compose from components
- [ ] Update Cline, Cursor, Copilot builders
- [ ] Update registry to support new component structure
- [ ] Update CLI to ask about verbosity

### Phase 2D: Testing & Validation (Week 6)
- [ ] E2E tests: init → build with minimal
- [ ] E2E tests: init → build with verbose
- [ ] Token count verification
- [ ] Validate all generated files
- [ ] Documentation updates

---

## Key Questions Remaining

1. **YAML or Markdown for components?**
   - YAML: Structured, easier to parse
   - Markdown: Human-readable, easier to edit
   - Recommendation: Markdown with clear section headers (# Prompt, # Skills, # Workflow)

2. **Mandatory vs Optional Subagents?**
   - Should all subagents be included in generated configs?
   - Or let builders choose which ones to include?
   - Recommendation: Include all, let builders filter

3. **Backward Compatibility?**
   - Keep kilo_modes.yaml for compatibility?
   - Or make clean break?
   - Recommendation: Sunset kilo_modes.yaml, move to new structure

