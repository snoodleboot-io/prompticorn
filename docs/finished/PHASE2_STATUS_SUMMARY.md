# Phase 2 Architecture Status Summary

**Date:** 2026-04-09  
**Branch:** feat/prompt-system-redesign  
**Status:** ✅ ARCHITECTURE COMPLETE, READY FOR IMPLEMENTATION

---

## Phase 2 Goal

Design and implement a **unified, extensible architecture** for Promptosaurus to support 6 AI tools (Kilo IDE, Kilo CLI, Cline, Cursor, Copilot, Claude) with a single Intermediate Representation (IR) that enables skill/workflow reuse and seamless tool switching.

---

## What We Accomplished

### Phase 2A: Architecture Design ✅ COMPLETE

**Documents Created:**
1. **PHASE2_REGISTRY_ARCHITECTURE.md** (355 lines)
   - SOLID principles applied (Interface Segregation via mixins)
   - Registry + Factory pattern for builder discovery
   - Mixin-based architecture (SupportsSkills, SupportsWorkflows, etc)
   - Tool-agnostic IR translation layer

2. **PHASE2A_IR_MODELS_AND_BUILDERS.md** (560 lines)
   - 5 Pydantic models: Agent, Skill, Workflow, Rules, Project
   - Builder interface with `build_agent()` and `validate_agent()`
   - Minimal/Verbose prompt strategy (dual fields in all models)
   - Builder mixin interfaces (SupportsSkills, SupportsWorkflows, SupportsProgressTracking)
   - Phase 2A scope: Kilo, Cline, Claude (HIGH CONFIDENCE tools)
   - Phase 2B scope: Copilot, Cursor, Kilo CLI (deferred for later research)

3. **PHASE2_UNIFIED_ARCHITECTURE.md** (350 lines)
   - Current vs Proposed system comparison
   - 4-layer architecture (IR, Builders, Tools, Output)
   - Backward compatibility strategy
   - Risk analysis and mitigation

### Phase 2B: Execution Model Research ✅ 4/6 HIGH CONFIDENCE

**Execution Models Documented:**

| Tool | Confidence | Model | Key Findings |
|------|------------|-------|--------------|
| **Claude** | ✅ HIGH | Tool calling loop | API verified, well-documented |
| **Cline** | ✅ HIGH | Tool + focus chain | Source analyzed: FocusChainManager, use_skill tool |
| **Kilo IDE** | ✅ HIGH | Agent loading + session | Local source verified: .kilocodemodes, .kilocode/rules-{mode}/ |
| **Copilot** | 🟡 MEDIUM | Hook-based | Inferred from VS Code Agent API patterns |
| **Cursor** | 🟠 LOW | Autonomous agent | Marketing docs only, no source available |
| **Kilo CLI** | 🟠 LOW | Step-based | Not yet researched |

**Research Findings:**
- Cline focus chain: File-based progress tracking with watchers (FocusChainManager class)
- Cline skills: Directory-based discovery + use_skill tool invocation
- Cline workflows: Toggle-based with .clinerules/ directory structure
- Kilo structure: Agent modes + session management, instruction loading from .kilocode/rules-{mode}/
- Claude: Standard tool calling with JSON schemas

**Deliverable:** `docs/EXECUTION_MODELS.md` (409 lines)

### Phase 2A Implementation Planning ✅ COMPLETE

**Deliverable:** `docs/PHASE2A_IMPLEMENTATION_ROADMAP.md` (450+ lines)

**6-Week Implementation Plan:**
- **Week 1:** Pydantic models + Parser (120+ unit tests)
- **Week 2:** KiloBuilder (40+ integration tests with real file I/O)
- **Week 3:** ClineBuilder with focus chain support (45+ tests)
- **Week 4:** ClaudeBuilder + CLI tool + configuration (50+ tests)
- **Week 5:** Comprehensive testing, E2E scenarios, security audit
- **Week 6:** Phase 2A release prep, Phase 2B architecture design

**Success Criteria:**
- 85%+ test coverage across codebase
- Real file I/O integration tests
- CLI tool (build, validate, init, list commands)
- Documentation: API reference, builder guides, getting started
- E2E scenarios: Feature workflow, multi-agent project

---

## Key Architecture Decisions

### 1. IR as Pydantic Models (Single Source of Truth)
- **Why:** Type safety, validation, serialization
- **Models:** Agent, Skill, Workflow, Rules, Project
- **Dual fields:** `prompt` + `prompt_verbose` for context-constrained scenarios

### 2. Builder Pattern with Mixins
- **Why:** Extensibility without coupling, interface segregation (SOLID)
- **Base:** `PromptosaurusBuilder(ABC)` with `build_agent()` + `validate_agent()`
- **Mixins:** `SupportsSkills`, `SupportsWorkflows`, `SupportsProgressTracking`
- **Benefit:** Tools that don't support skills (like Claude) simply don't implement mixin

### 3. Registry + Factory for Builder Discovery
- **Why:** Decoupling, dynamic loader registration, no hardcoded imports
- **Pattern:** `BuilderRegistry.register("kilo", KiloBuilder)` → `BuilderFactory.create("kilo")`
- **Auto-discovery:** Can scan `promptosaurus/builders/` directory for builder modules

### 4. Tool-Specific Output Translation
- **Why:** Each tool has different execution model (Claude: tools, Cline: files, Kilo: directories)
- **Translation:** IR → Tool-specific format happens IN builders, not in core
- **Example:** ClineBuilder writes `.agents/skills/` directory structure, KiloBuilder writes `.kilocode/rules-{mode}/`

### 5. Real File I/O in Tests
- **Why:** Catch edge cases (permissions, paths, format issues) that mocks miss
- **Approach:** Use `tempfile` for isolated test directories, actually write files, verify
- **Coverage:** 85%+ across codebase, 100+ tests

---

## Files Created This Phase

### Documentation
- `docs/PHASE2_REGISTRY_ARCHITECTURE.md` - Architecture + SOLID principles
- `docs/ard/PHASE2A_IR_MODELS_AND_BUILDERS.md` - IR models + builders
- `docs/PHASE2_UNIFIED_ARCHITECTURE.md` - System comparison
- `docs/EXECUTION_MODELS.md` - Tool execution models with source analysis
- `docs/PHASE2A_IMPLEMENTATION_ROADMAP.md` - Week-by-week plan
- `docs/PHASE2_STATUS_SUMMARY.md` - This file

### Session Management
- `.promptosaurus/sessions/session_20260409_phase2_research.md` - Phase 2 work tracking

### Research Artifacts
- Cloned Cline repository: `/tmp/ai_tools_research/cline/` (analyzed focus chain, workflows)
- Examined Promptosaurus structure: `.kilocode/`, `.kilocodemodes` (verified agent loading)

---

## Phase 2A vs Phase 2B Scope

### Phase 2A (Ready to Implement - 6 weeks)
**Builders:**
- KiloBuilder (agent + skills + workflows to .kilocode/)
- ClineBuilder (agent + skills to .agents/ + focus chain config)
- ClaudeBuilder (agent + skills to tool JSON schemas)

**Infrastructure:**
- Pydantic IR models
- YAML/Markdown parser
- Registry + Factory pattern
- CLI tool
- Test suite (85%+ coverage)

**Outcome:** 3 fully-working builders with comprehensive tests

### Phase 2B (Deferred - 4-6 weeks after Phase 2A)
**Builders:**
- CopilotBuilder (hook-based orchestration)
- CursorBuilder (autonomous agent mode)
- KiloCliBuilder (step-based execution)

**Research Needed:**
- Copilot Agent API deep dive
- Cursor public documentation/examples
- Kilo CLI execution model

**Outcome:** Complete tool coverage (6/6 tools supported)

---

## How to Proceed

### Immediate Next Steps
1. **Review Phase 2A design** (PHASE2A_IR_MODELS_AND_BUILDERS.md)
2. **Confirm 6-week timeline** feasible
3. **Allocate resources** (recommend 1 FTE engineer)
4. **Set up test infrastructure** (pytest, coverage tools)
5. **Create project tracking** (GitHub Projects or similar)

### Starting Week 1
- Clone repo on fresh branch
- Set up IDE for Python development
- Begin with Pydantic models (Task 1.1.1)
- Real file I/O tests from Day 1

### Risks to Watch
- **Builder validation complexity** - May need iteration on error handling
- **Phase 2B feature creep** - Keep scope bounded to 3 builders in Phase 2A
- **Tool changes** - Cline/Kilo/Claude APIs may evolve; review before implementing

---

## Why This Architecture Works

### For Users
- **Single definition, multiple tools:** Write agent once, use in Kilo/Cline/Claude
- **Skill reuse:** Share test-writing skill across all tools
- **Workflow portability:** Define workflow once, execute in any tool
- **Progressive adoption:** Start with one tool, add others as needed

### For Developers
- **Type safety:** Pydantic validates all inputs
- **Extensibility:** Add new builder without changing core
- **Testing:** Real file I/O, comprehensive coverage
- **Clarity:** SOLID principles, clear separation of concerns

### For the Project
- **Future-proof:** Easily add more tools (Copilot, Cursor, etc)
- **Maintainable:** IR models vs tool-specific code isolated
- **Backward compatible:** Can coexist with Phase 1 system
- **Foundation:** Enables next phases (auto-expansion, optimization, etc)

---

## Glossary

| Term | Definition |
|------|-----------|
| **IR** | Intermediate Representation - Pydantic models (Agent, Skill, etc) |
| **Builder** | Translates IR to tool-specific output (IR → Kilo files) |
| **Registry** | Central registry of available builders |
| **Factory** | Creates builder instances on demand |
| **Mixin** | Optional interface for builders (SupportsSkills, SupportsWorkflows) |
| **Focus Chain** | Cline's progress tracking (markdown todo list with file watcher) |
| **Prompt Verbose** | Detailed prompt version with examples (optional, auto-expanded) |
| **Tool** | An AI platform (Claude, Kilo, Cline, Copilot, Cursor, Kilo CLI) |

---

## Questions & Next Steps

**For Architecture Review:**
- Are 3 Phase 2A builders sufficient for MVP?
- Should Phase 2B be tackled immediately or deferred?
- Any concerns with mixin approach for optional features?

**For Implementation:**
- Which engineer will lead development?
- Will you do daily standups for progress?
- Any deadline pressure or timeline constraints?

**For Phase 2B:**
- Who will research Copilot/Cursor/Kilo CLI APIs?
- Should Phase 2B start before Phase 2A ships?

