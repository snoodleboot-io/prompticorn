# Product Requirements Document: Phase 2 - Unified Prompt Architecture

**Status:** In Development  
**Phase:** Phase 2  
**Owner:** Promptosaurus Team  
**Updated:** 2026-04-08

---

## Executive Summary

Phase 2 refactors the prompt system from a flat, monolithic structure to a **component-based architecture** supporting multiple AI tools (Kilo IDE, Kilo CLI, Cline, Cursor, Copilot, Claude) with **minimal and verbose variants**. This moves the project from alpha to beta by creating an extensible, maintainable, unified foundation.

**Key outcomes:**
- Decompose 15 agent modes into reusable prompt/skill/workflow components
- Add 34 specialized subagents for targeted capabilities
- Support minimal (90% token reduction) and verbose variants
- Unified input source (no separate kilo_modes.yaml)
- Support for 6 AI tools from single codebase

---

## Problem Statement

### Current State (Alpha)

1. **Two Competing Systems**
   - Registry-based (Cline, Cursor, Copilot): `prompts/agents/`
   - Kilo-based (KiloIDE, KiloCLI): `kilo_modes.yaml` (separate)
   - No unified source of truth

2. **Monolithic Agents**
   - Each agent role bundles multiple concerns in one roleDefinition
   - Example: "Review" agent mixes code, performance, accessibility
   - Hard to specialize or create minimal variants
   - No clear skill or workflow definition

3. **No Minimal Variant Support**
   - All prompts are full-featured
   - ~4000 tokens per user project
   - No cost/speed optimization path

4. **Limited Extensibility**
   - Adding new tool (Claude) requires separate builder
   - No clear pattern for subagents
   - Maintenance burden as tools multiply

5. **Missing Capabilities**
   - Some specialized workflows underspecified (e.g., security threat modeling)
   - Documentation generation lacks subagents
   - Testing strategies monolithic

### Impact

- High token costs for users
- Difficult to support new tools
- Complex maintenance as codebase grows
- Beta release blocked on these issues

---

## Requirements

### Functional Requirements

#### FR1: Component-Based Prompt Architecture
**Requirement:** Decompose each agent into three components:
- **Prompt**: Role definition + principles (what you are)
- **Skills**: Specific capabilities with constraints (what you can do)
- **Workflow**: Step-by-step process (how you work)

**Acceptance Criteria:**
- [ ] All 15 primary agents decomposed into prompt/skills/workflow
- [ ] Each component loadable independently
- [ ] Components composable to form complete agent instruction
- [ ] Format: Markdown with clear section headers

**Rationale:** Enables meaningful minimal variants (can remove details from skills/workflow) and reusable components across agents.

---

#### FR2: Subagent Architecture
**Requirement:** Create specialized subagents under each primary agent with defined relationships.

**Acceptance Criteria:**
- [ ] Directory structure: `agents/{agent}/subagents/{subagent}/`
- [ ] Minimum 34 new subagents created (per analysis)
- [ ] Each subagent has clear, distinct purpose
- [ ] Subagents inherit from parent agent principles
- [ ] Registry discovers subagent structure automatically

**Subagents Summary:**
- Architect: +3 (decision, technology-selection, tradeoff-analysis)
- Code: +2 (security-fix, performance-optimization)
- Review: +1 (maintainability)
- Test: +4 (unit, integration, edge-cases, mutation-scoring)
- Document: +5 (api, guide, changelog, architecture, inline)
- Debug: +1 (performance)
- Migration: +2 (breaking-changes, incremental)
- Security: +3 (threat-modeling, vulnerability-fix, secrets)
- Compliance: +3 (soc2, gdpr, hipaa)
- Explain: +4 (architecture, code, patterns, onboarding)
- Ask: +1 (explanation)
- Planning: +2 (estimation, stakeholder)
- Enforcement: +2 (patterns, security)
- Orchestrator: +1 (feature-coordination)

**Total new subagents: 34**

---

#### FR3: Minimal and Verbose Variants
**Requirement:** Create minimal (90% token reduction) and verbose variants for all components.

**Acceptance Criteria:**
- [ ] Minimal variant for each component created
- [ ] Verbose variant for each component created
- [ ] Token count reduction verified: 85-90% for minimal
- [ ] User can select verbosity during `promptosaurus init`
- [ ] Config stores selected verbosity: `spec.prompts.verbosity`

**Minimal Variant Rules:**
- Prompt: 1-2 sentences (core role only, no elaboration)
- Skills: 3-4 bullet points (core capabilities, no constraints)
- Workflow: 3-4 main steps (essentials, no checkpoints)

**Verbose Variant Rules:**
- Prompt: Full detailed role definition
- Skills: Each skill detailed with constraints and examples
- Workflow: Detailed steps with checkpoints and fallbacks

**Token Impact:**
- Minimal (all agents): ~500-800 tokens
- Verbose (all agents): ~4000-5000 tokens
- Reduction: 85-90%

---

#### FR4: Unified Builder Architecture
**Requirement:** All builders (KiloIDE, KiloCLI, Cline, Cursor, Copilot, Claude) read from unified registry.

**Acceptance Criteria:**
- [ ] Deprecate kilo_modes.yaml
- [ ] Migrate 15 Kilo modes into registry structure
- [ ] All builders use registry.mode_files as input
- [ ] kilo_modes.yaml deleted (or moved to finished/)
- [ ] ComponentSelector handles verbosity for all builders
- [ ] Each builder composes agent output from components

**Builders to Support:**
- KiloIDE: `.kilo/agents/{slug}.md` (individual files with YAML frontmatter)
- KiloCLI: `.opencode/rules/{MODE}.md` (collapsed format) + `opencode.json`
- Cline: `.clinerules` (single concatenated file)
- Cursor: `.cursor/rules/` (nested structure) + `.cursorrules` (legacy)
- Copilot: `.github/instructions/{mode}.instructions.md` (per-mode with applyTo)
- Claude: *(to be defined - new tool)*

---

#### FR5: Claude Builder Support
**Requirement:** Create new builder for Claude AI assistant.

**Acceptance Criteria:**
- [ ] Claude builder implementation complete
- [ ] Output format follows Claude configuration standards
- [ ] Supports minimal/verbose variants
- [ ] Uses unified registry as input
- [ ] Documented in AGENTS.md

**Note:** Claude format to be determined during design phase.

---

### Non-Functional Requirements

#### NFR1: Maintainability
- Single source of truth for all prompt content
- Clear separation of concerns (prompt/skills/workflow)
- DRY principle: components reusable across modes

#### NFR2: Performance
- Component loading cached efficiently
- Registry discovery optimized
- No degradation in build time

#### NFR3: Extensibility
- Easy to add new subagents
- Easy to add new builders
- New tools can use unified architecture

#### NFR4: Backward Compatibility
- `.kilocodemodes` output maintained for transition period
- Existing projects continue to work
- Graceful deprecation of old format

---

## Scope

### In Scope

✅ Component-based architecture design and implementation  
✅ Decompose 15 primary agents into prompt/skills/workflow  
✅ Create 34 new specialized subagents  
✅ Create minimal and verbose variants for all components  
✅ Migrate from kilo_modes.yaml to unified registry  
✅ Update all 5 existing builders (Kilo IDE, Kilo CLI, Cline, Cursor, Copilot)  
✅ Create new Claude builder  
✅ Support verbosity selection in CLI  
✅ Update registry to auto-discover component structure  

### Out of Scope

❌ Refactoring non-prompt builder infrastructure (template handlers, etc.)  
❌ Changing user-facing CLI interface (beyond adding verbosity question)  
❌ Modifying core conventions or base rules  
❌ Performance optimization beyond component loading  
❌ New AI tools beyond Claude (future phase)  

---

## Success Criteria

### Acceptance Criteria (MVP)

1. **Architecture**
   - [ ] Component structure implemented and validated
   - [ ] Registry discovers agents/subagents automatically
   - [ ] ComponentSelector selects minimal/verbose correctly
   - [ ] All builders read from unified registry

2. **Content**
   - [ ] 15 primary agents decomposed (45 files: 3 components × 2 variants)
   - [ ] 34 subagents created (102 files: 3 components × 2 variants)
   - [ ] Total: ~270+ new prompt files
   - [ ] All components tested for syntax and parsing

3. **Builders**
   - [ ] KiloIDE generates correct `.kilo/agents/` output
   - [ ] KiloCLI generates correct `.opencode/rules/` output
   - [ ] Cline generates correct `.clinerules` output
   - [ ] Cursor generates correct `.cursor/rules/` output
   - [ ] Copilot generates correct `.github/instructions/` output
   - [ ] Claude builder creates appropriate output format

4. **User Experience**
   - [ ] `promptosaurus init` asks for verbosity preference
   - [ ] Config correctly stores `spec.prompts.verbosity`
   - [ ] Generated config reflects user's choice
   - [ ] Token count reduction verified (85-90% for minimal)

5. **Quality**
   - [ ] All tests passing (unit + integration)
   - [ ] E2E test: init with minimal → verify output
   - [ ] E2E test: init with verbose → verify output
   - [ ] Documentation updated for Phase 2
   - [ ] Backward compatibility maintained

---

## Implementation Timeline

**Total Duration:** 10-12 weeks (including Kilo refactoring)

### Phase 2A: Planning & Design (Week 1)
- Finalize component file format (Markdown with headers)
- Define Claude builder output format
- Create detailed specification for each builder

### Phase 2B: Component Creation (Weeks 2-4)
- Decompose 15 primary agents
- Create 34 new subagents
- Write minimal and verbose variants (~270 files)
- Validate all component syntax

### Phase 2C: Registry & Builders (Weeks 5-7)
- Update registry to discover components
- Create ComponentSelector and ComponentComposer
- Migrate kilo_modes.yaml content to registry
- Update all 5 builders + create Claude builder

### Phase 2D: Integration (Weeks 8-9)
- Update CLI to support verbosity question
- Integrate component selection into build pipeline
- Update config schema

### Phase 2E: Testing & Validation (Weeks 10-11)
- Unit tests for all builders
- Integration tests (init → build workflows)
- E2E tests with real output
- Token count verification

### Phase 2F: Documentation & Release (Week 12)
- Update AGENTS.md for all tools
- Create migration guide from alpha
- User guide for verbosity options
- Release notes

---

## Dependencies

### External
- YAML parsing library (already included)
- Markdown parsing for component discovery (may need new dep)

### Internal
- Registry infrastructure (must be extended)
- Builder base class (must be modified)
- CLI module (must add verbosity question)
- Config handler (must support prompts.verbosity)

---

## Assumptions

1. Unified registry can accommodate all 15 Kilo modes without performance degradation
2. Minimal variants acceptable for all users (85% token reduction)
3. All builders can compose output from components
4. Claude builder output format can be determined during design phase
5. No breaking changes to user-facing CLI (only additions)

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Component format not suitable for all builders | Low | High | Early validation with each builder |
| Token reduction doesn't meet 85% target | Low | Medium | Iterative refinement of minimal variants |
| Registry performance degrades | Low | High | Profile and optimize early |
| Kilo migration introduces regressions | Medium | High | Comprehensive testing before deprecation |
| Claude builder format not finalizable | Medium | Medium | Start with simple format, iterate |
| 34 new subagents unmaintainable | Low | Medium | Clear ownership and documentation |

---

## Success Metrics

1. **Technical**
   - All tests passing (>95% success rate)
   - Build time unchanged (<5% variance)
   - Token count: minimal 85-90% reduction from verbose

2. **User**
   - Users can select verbosity during init
   - Generated config correctly reflects choice
   - All 6 tools produce correct output

3. **Maintainability**
   - Single registry source of truth
   - Clear component structure (prompt/skills/workflow)
   - New subagents can be added in <2 hours
   - New builders can be added in <1 week

4. **Quality**
   - Phase 2 work enables smooth Phase 3 (CLI integration)
   - Documentation complete and accurate
   - Zero known architectural debt introduced

---

## Sign-Off

**PRD Owner:** Promptosaurus Team  
**Approval Date:** 2026-04-08  
**Target Start:** 2026-04-15  
**Estimated Completion:** 2026-06-30

