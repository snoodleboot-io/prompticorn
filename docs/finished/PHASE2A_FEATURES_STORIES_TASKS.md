# Phase 2A: Features → Stories → Tasks Breakdown

**Timeline:** Week 1-6 (6 weeks, starting Apr 9 2026)  
**Status:** Planning Complete  
**Last Updated:** 2026-04-09

---

## Feature: Phase 2A - Unified Prompt Architecture Implementation

**Description:** Implement unified, tool-agnostic IR and builders for 5 AI tools (Kilo, Claude, Cline, Cursor, Copilot). Single source of truth for agent configurations with tool-specific output.

**Success Criteria:**
- ✓ All 5 builders generate correct output for their respective tools
- ✓ IR models are tool-agnostic and complete
- ✓ 85%+ test coverage on all code
- ✓ Real file I/O tests pass
- ✓ E2E scenario tests pass (create IR → build all tools → validate output)
- ✓ Documentation complete
- ✓ No manual registration needed (auto-discovery via filesystem)

**Owner:** Engineering Team  
**Stakeholders:** All tool users (Kilo, Claude, Cline, Cursor, Copilot)

---

## Story 1: Infrastructure & Foundation (Week 1)

**Description:** Create core IR models, parser infrastructure, registry, and builder base classes. This is the foundation all other builders depend on.

**Size:** Large (1 week, 5 engineers or 1 engineer full-time)  
**Dependencies:** None (first story)  
**Owner:** Core Infrastructure Team

### Task 1.1: Create Pydantic IR Models

**Description:** Implement tool-agnostic data models for agents, skills, workflows, rules, and projects.

**Acceptance Criteria:**
- [ ] Agent model with name, description, system_prompt, tools, skills, workflows, subagents
- [ ] Skill model with name, description, instructions, tools_needed
- [ ] Workflow model with name, description, steps (list of strings)
- [ ] Tool model with name, description, parameters (JSON schema)
- [ ] Rules model with constraints and guidelines (flexible structure)
- [ ] Project model with registry settings, verbosity preference, builder configs
- [ ] All models have full type hints
- [ ] All models have docstrings explaining purpose and usage
- [ ] Validation logic for required fields and constraints
- [ ] Unit tests: 100% coverage on all models
- [ ] Pass pyright strict mode

**File(s):** `src/ir/models/agent.py`, `src/ir/models/skill.py`, `src/ir/models/workflow.py`, `src/ir/models/tool.py`, `src/ir/models/rules.py`, `src/ir/models/project.py`, `tests/unit/ir/test_models.py`

**Effort:** XS (3-4 hours)  
**Owner:** 1 engineer

---

### Task 1.2: Create Parser Infrastructure

**Description:** Implement YAML and Markdown parsers to load IR models from files.

**Acceptance Criteria:**
- [ ] YAMLParser class that loads YAML frontmatter from markdown files
- [ ] MarkdownParser class that extracts sections from markdown (## Section)
- [ ] ComponentLoader class that loads prompt/skills/workflow files
- [ ] SkillParser that extracts skill metadata and instructions
- [ ] WorkflowParser that parses workflow steps from markdown
- [ ] Error handling with descriptive messages
- [ ] Support for optional components (some agents may not have workflows)
- [ ] Unit tests: 85%+ coverage
- [ ] Integration tests: Load sample agent file and verify structure

**File(s):** `src/ir/parsers/yaml_parser.py`, `src/ir/parsers/markdown_parser.py`, `src/ir/loaders/component_loader.py`, `src/ir/loaders/skill_loader.py`, `src/ir/loaders/workflow_loader.py`, `tests/unit/ir/test_parsers.py`, `tests/integration/test_loaders.py`

**Effort:** S (4-6 hours)  
**Owner:** 1 engineer

---

### Task 1.3: Create Registry & Discovery System

**Description:** Implement auto-discovery registry that scans filesystem for agents and builds IR models.

**Acceptance Criteria:**
- [ ] RegistryDiscovery class that scans `agents/` directory
- [ ] Discovers agents with minimal/verbose variants
- [ ] Discovers subagents under `agents/{agent}/subagents/`
- [ ] Auto-loads prompt.md, skills.md, workflow.md for each variant
- [ ] Validates all required files exist
- [ ] Returns dict of Agent IR models (key=agent_name)
- [ ] Handles missing optional files gracefully
- [ ] Registry caching (load once per session)
- [ ] Unit tests: 85%+ coverage
- [ ] Integration tests: Load entire agents/ directory and verify structure

**File(s):** `src/registry/discovery.py`, `src/registry/registry.py`, `src/registry/errors.py`, `tests/integration/test_discovery.py`

**Effort:** S (5-7 hours)  
**Owner:** 1 engineer

---

### Task 1.4: Create Builder Base Classes & Interfaces

**Description:** Implement abstract builder base class and mixin interfaces for tool-specific builders.

**Acceptance Criteria:**
- [ ] AbstractBuilder base class with build(agent, options) → str|dict method
- [ ] validate() method that checks IR model is valid before building
- [ ] Mixin interfaces: SupportsSkills, SupportsWorkflows, SupportsRules, SupportsSubagents
- [ ] Builder registry that tracks all available builders
- [ ] BuilderFactory that returns correct builder for tool name
- [ ] Error handling: clear messages for missing builders or invalid IR
- [ ] Builder interface documentation
- [ ] Unit tests: 85%+ coverage
- [ ] Tests for factory pattern and builder selection

**File(s):** `src/builders/base.py`, `src/builders/interfaces.py`, `src/builders/registry.py`, `src/builders/factory.py`, `tests/unit/builders/test_base.py`, `tests/unit/builders/test_factory.py`

**Effort:** S (4-5 hours)  
**Owner:** 1 engineer

---

### Task 1.5: Create Component Selector & Composer

**Description:** Implement logic to select minimal/verbose variants and compose them for builders.

**Acceptance Criteria:**
- [ ] ComponentSelector class that chooses minimal or verbose based on config
- [ ] Selects correct variant directory (minimal/ or verbose/)
- [ ] Loads all three components: prompt, skills, workflow
- [ ] Falls back to verbose if minimal missing (with warning)
- [ ] ComponentComposer class that assembles components into output format
- [ ] Composer handles component ordering (prompt first, then tools, skills, workflows)
- [ ] Handles missing optional components
- [ ] Unit tests: 90%+ coverage
- [ ] Tests for all variant combinations

**File(s):** `src/builders/component_selector.py`, `src/builders/component_composer.py`, `tests/unit/builders/test_selector.py`, `tests/unit/builders/test_composer.py`

**Effort:** XS (3-4 hours)  
**Owner:** 1 engineer

---

### Task 1.6: Unit Tests for Infrastructure (Task 1.1-1.5)

**Description:** Comprehensive unit test suite for all infrastructure components. Aim for 85%+ coverage.

**Acceptance Criteria:**
- [ ] All models tested (happy path + edge cases)
- [ ] All parsers tested with valid/invalid inputs
- [ ] Registry discovery tested with full directory structure
- [ ] Builder base classes tested for correct abstraction
- [ ] Component selector tested for all variant combinations
- [ ] Error cases tested (missing files, invalid YAML, etc.)
- [ ] Total coverage: 85%+ on infrastructure
- [ ] All tests pass locally
- [ ] No type errors in tests (pyright strict)

**File(s):** `tests/unit/ir/`, `tests/unit/builders/`, `tests/unit/registry/`

**Effort:** M (8-10 hours)  
**Owner:** 1 engineer

---

## Story 2: Kilo Builder Implementation (Week 2)

**Description:** Implement KiloBuilder to generate `.kilo/agents/{name}.md` with YAML frontmatter + markdown sections.

**Size:** Medium (1 week)  
**Dependencies:** Story 1 (Infrastructure complete)  
**Owner:** Kilo Specialization Team

### Task 2.1: Implement KiloBuilder Class

**Description:** Create KiloBuilder that translates IR to Kilo format.

**Acceptance Criteria:**
- [ ] KiloBuilder extends AbstractBuilder
- [ ] build(agent: Agent, options) → str
- [ ] Generates YAML frontmatter: name, description, model, state_management
- [ ] Generates # System Prompt section with agent.system_prompt
- [ ] Generates # Tools section with markdown list of tools
- [ ] Generates # Skills section with skill descriptions and locations
- [ ] Generates # Workflows section with step descriptions
- [ ] Generates # Subagents section with subagent references
- [ ] Proper markdown formatting (headers, lists, code blocks)
- [ ] validate() checks IR has required fields
- [ ] Output is valid Kilo agent file format
- [ ] Unit tests: 90%+ coverage

**File(s):** `src/builders/kilo_builder.py`, `tests/unit/builders/test_kilo_builder.py`

**Effort:** M (6-8 hours)  
**Owner:** 1 engineer

---

### Task 2.2: Implement Subagent Support for Kilo

**Description:** Handle subagent generation for Kilo (nested markdown files or separate agents).

**Acceptance Criteria:**
- [ ] KiloBuilder detects subagents in IR
- [ ] Generates subagent files with parent reference
- [ ] Subagent files follow same format as parent agent
- [ ] Subagent files include parent context/constraints
- [ ] Proper nesting in output directory structure
- [ ] Subagent discovered as part of agent hierarchy
- [ ] Unit tests: 85%+ coverage
- [ ] Integration test: Generate agent + subagents, verify all files created

**File(s):** `src/builders/kilo_builder.py` (extended), `tests/integration/test_kilo_subagents.py`

**Effort:** S (4-5 hours)  
**Owner:** 1 engineer

---

### Task 2.3: Integration Tests for Kilo Builder

**Description:** End-to-end tests for Kilo builder with real file I/O.

**Acceptance Criteria:**
- [ ] Test: Load IR model from agents/ directory
- [ ] Test: Build Kilo output from IR
- [ ] Test: Write Kilo files to temp directory
- [ ] Test: Verify output files are readable by Kilo IDE
- [ ] Test: Verify YAML frontmatter is valid
- [ ] Test: Verify markdown sections are properly formatted
- [ ] Test: Rebuild with different variants (minimal/verbose)
- [ ] Test: Handle missing optional components gracefully
- [ ] All tests pass with real filesystem I/O
- [ ] Coverage: 85%+

**File(s):** `tests/integration/test_kilo_builder.py`

**Effort:** M (6-7 hours)  
**Owner:** 1 engineer

---

## Story 3: Cline Builder Implementation (Week 3)

**Description:** Implement ClineBuilder to generate `.clinerules` (concatenated markdown).

**Size:** Medium (1 week)  
**Dependencies:** Story 1 (Infrastructure complete)  
**Owner:** Cline Specialization Team

### Task 3.1: Implement ClineBuilder Class

**Description:** Create ClineBuilder that translates IR to Cline format.

**Acceptance Criteria:**
- [ ] ClineBuilder extends AbstractBuilder
- [ ] build(agent: Agent, options) → str
- [ ] Generates # {Agent Name} Rules header
- [ ] Generates system_prompt as prose (no markdown)
- [ ] Generates ## Tools section with tool descriptions
- [ ] Generates ## Skills section with skill descriptions
- [ ] Skills include "use_skill" invocation instructions
- [ ] Generates ## Workflows section with workflow steps
- [ ] Generates ## Subagents section with delegation instructions
- [ ] All sections concatenated in single file
- [ ] Proper markdown formatting
- [ ] validate() checks IR completeness
- [ ] Output is valid Cline rules format
- [ ] Unit tests: 90%+ coverage

**File(s):** `src/builders/cline_builder.py`, `tests/unit/builders/test_cline_builder.py`

**Effort:** M (6-8 hours)  
**Owner:** 1 engineer

---

### Task 3.2: Implement Skill Activation for Cline

**Description:** Handle Cline's skill activation mechanism (use_skill tool).

**Acceptance Criteria:**
- [ ] Skills section includes activation instructions
- [ ] Format: "use_skill {skill_name}" invocation pattern
- [ ] Instructions explain when to use each skill
- [ ] Links to skill documentation locations
- [ ] Subagent delegation uses skill activation
- [ ] Handles skill dependencies (tools required)
- [ ] Unit tests: 85%+ coverage

**File(s):** `src/builders/cline_builder.py` (extended)

**Effort:** S (3-4 hours)  
**Owner:** 1 engineer

---

### Task 3.3: Integration Tests for Cline Builder

**Description:** End-to-end tests for Cline builder with real file I/O.

**Acceptance Criteria:**
- [ ] Test: Load IR model, build Cline output
- [ ] Test: Write `.clinerules` to temp directory
- [ ] Test: Verify file is readable by Cline
- [ ] Test: Verify markdown syntax is valid
- [ ] Test: Verify skill invocation syntax is correct
- [ ] Test: Rebuild with different agents and variants
- [ ] All tests pass with real filesystem I/O
- [ ] Coverage: 85%+

**File(s):** `tests/integration/test_cline_builder.py`

**Effort:** M (6-7 hours)  
**Owner:** 1 engineer

---

## Story 4: Claude & Copilot Builders Implementation (Week 4)

**Description:** Implement ClaudeBuilder and CopilotBuilder.

**Size:** Large (1 week)  
**Dependencies:** Story 1 (Infrastructure complete)  
**Owner:** Cloud Specialization Team

### Task 4.1: Implement ClaudeBuilder Class

**Description:** Create ClaudeBuilder that generates Messages API payload.

**Acceptance Criteria:**
- [ ] ClaudeBuilder extends AbstractBuilder
- [ ] build(agent: Agent, options) → dict
- [ ] Generates "system" field with system_prompt
- [ ] Generates "tools" array with JSON schema definitions
- [ ] Tools include name, description, input_schema
- [ ] Generates "instructions" section with skills and workflows
- [ ] Skills descriptions include activation instructions
- [ ] Workflows include step descriptions
- [ ] Output is valid JSON
- [ ] Output is compatible with Claude API (Messages)
- [ ] validate() checks completeness
- [ ] Unit tests: 90%+ coverage
- [ ] JSON validation tests

**File(s):** `src/builders/claude_builder.py`, `tests/unit/builders/test_claude_builder.py`

**Effort:** M (7-9 hours)  
**Owner:** 1 engineer

---

### Task 4.2: Implement Subagent Delegation for Claude

**Description:** Handle Claude subagent invocation (separate Claude API calls).

**Acceptance Criteria:**
- [ ] Subagents mapped to separate Claude instances
- [ ] Each subagent gets system_prompt + tools + skills
- [ ] Subagent configuration included in output
- [ ] Delegation instructions clear in parent prompt
- [ ] Unit tests: 85%+ coverage

**File(s):** `src/builders/claude_builder.py` (extended)

**Effort:** S (4-5 hours)  
**Owner:** 1 engineer

---

### Task 4.3: Implement CopilotBuilder Class

**Description:** Create CopilotBuilder that generates `.github/instructions/{mode}.md` files.

**Acceptance Criteria:**
- [ ] CopilotBuilder extends AbstractBuilder
- [ ] build(agent: Agent, options) → dict (multiple files)
- [ ] Generates main agent file: `.github/instructions/{agent}.instructions.md`
- [ ] YAML frontmatter: applyTo with model and parentAgents
- [ ] Generates # System Prompt section
- [ ] Generates ## Skills section with locations and activation
- [ ] Generates ## Workflows section
- [ ] Generates ## Subagents section
- [ ] Generates ## Tools & Permissions section
- [ ] Creates separate files for each subagent with parent reference
- [ ] Output is valid Copilot instruction format
- [ ] validate() checks completeness
- [ ] Unit tests: 90%+ coverage

**File(s):** `src/builders/copilot_builder.py`, `tests/unit/builders/test_copilot_builder.py`

**Effort:** M (7-9 hours)  
**Owner:** 1 engineer

---

### Task 4.4: Integration Tests for Claude & Copilot

**Description:** End-to-end tests for Claude and Copilot builders.

**Acceptance Criteria:**
- [ ] Test: Load IR, build Claude payload
- [ ] Test: Verify Claude payload is valid JSON
- [ ] Test: Verify schema of tools matches Claude API
- [ ] Test: Build Copilot instructions
- [ ] Test: Write Copilot files to temp directory
- [ ] Test: Verify Copilot YAML frontmatter is valid
- [ ] Test: Verify Copilot files are readable
- [ ] Test: Build with subagents, verify delegation
- [ ] All tests pass with real file I/O
- [ ] Coverage: 85%+

**File(s):** `tests/integration/test_claude_builder.py`, `tests/integration/test_copilot_builder.py`

**Effort:** M (8-10 hours)  
**Owner:** 1 engineer

---

### Task 4.5: Implement CLI Tool for Building

**Description:** Create CLI that loads IR and generates all builder outputs.

**Acceptance Criteria:**
- [ ] CLI command: `prompt-build --tool kilo` (or claude, cline, copilot, cursor)
- [ ] CLI command: `prompt-build --all` (builds all tools)
- [ ] CLI accepts `--variant minimal` or `--variant verbose`
- [ ] CLI accepts `--agent {name}` (or builds all)
- [ ] CLI validates output before writing
- [ ] CLI reports success/failure for each builder
- [ ] Help text clearly explains options
- [ ] Error messages are descriptive
- [ ] Unit tests for CLI argument parsing
- [ ] Integration tests for full build workflow

**File(s):** `src/cli/build_command.py`, `tests/unit/cli/test_build_command.py`, `tests/integration/test_cli_build.py`

**Effort:** S (5-6 hours)  
**Owner:** 1 engineer

---

## Story 5: Cursor Builder Implementation (Week 4 + into Week 5)

**Description:** Implement CursorBuilder to generate `.cursorrules`.

**Size:** Small-Medium (3-4 days)  
**Dependencies:** Story 1 (Infrastructure complete)  
**Owner:** Cursor Specialization Team

### Task 5.1: Implement CursorBuilder Class

**Description:** Create CursorBuilder that translates IR to Cursor format.

**Acceptance Criteria:**
- [ ] CursorBuilder extends AbstractBuilder
- [ ] build(agent: Agent, options) → str
- [ ] Generates # {Agent Name} Rules header
- [ ] Generates system_prompt as prose
- [ ] Generates ## Skills section with skill processes
- [ ] Generates ## Workflows section with step descriptions
- [ ] Generates ## Tools Available section
- [ ] Single concatenated file format
- [ ] Proper markdown formatting
- [ ] validate() checks IR completeness
- [ ] Output is valid Cursor rules format
- [ ] Unit tests: 90%+ coverage

**File(s):** `src/builders/cursor_builder.py`, `tests/unit/builders/test_cursor_builder.py`

**Effort:** S (4-5 hours)  
**Owner:** 1 engineer

---

### Task 5.2: Integration Tests for Cursor Builder

**Description:** End-to-end tests for Cursor builder.

**Acceptance Criteria:**
- [ ] Test: Load IR, build Cursor output
- [ ] Test: Write `.cursorrules` to temp directory
- [ ] Test: Verify file format and syntax
- [ ] Test: Rebuild with different agents and variants
- [ ] All tests pass with real file I/O
- [ ] Coverage: 85%+

**File(s):** `tests/integration/test_cursor_builder.py`

**Effort:** S (3-4 hours)  
**Owner:** 1 engineer

---

## Story 6: Testing & Validation (Week 5)

**Description:** Comprehensive testing including E2E scenarios, mutation tests, and validation.

**Size:** Large (1 week)  
**Dependencies:** Stories 1-5 (all builders complete)  
**Owner:** QA & Testing Team

### Task 6.1: E2E Scenario Tests

**Description:** Test complete workflows from IR load through all builder outputs.

**Acceptance Criteria:**
- [ ] Scenario 1: Load code agent → build all 5 tools → validate all outputs
- [ ] Scenario 2: Load architect agent → build all 5 tools → validate outputs
- [ ] Scenario 3: Load agent with subagents → build all tools → verify subagent generation
- [ ] Scenario 4: Build minimal variant → verify token reduction
- [ ] Scenario 5: Build verbose variant → verify completeness
- [ ] All scenarios pass
- [ ] Real filesystem I/O used (no mocks)
- [ ] Timing benchmarks recorded (< 5s for all 5 tools)

**File(s):** `tests/e2e/test_scenarios.py`

**Effort:** M (8-10 hours)  
**Owner:** 1-2 engineers

---

### Task 6.2: Mutation Testing

**Description:** Run mutation tests to verify test quality (mutation score ≥ 80%).

**Acceptance Criteria:**
- [ ] mutmut installed and configured
- [ ] Run mutation tests on all infrastructure code
- [ ] Run mutation tests on all builders
- [ ] Mutation score ≥ 80% on infrastructure
- [ ] Mutation score ≥ 80% on builders
- [ ] Identify and fix weak tests (low mutation detection)
- [ ] Report generated and reviewed

**File(s):** `mutmut.ini`, `tests/mutations/`

**Effort:** M (8-10 hours)  
**Owner:** 1 engineer

---

### Task 6.3: Real File I/O Validation

**Description:** Test all builders with actual filesystem operations.

**Acceptance Criteria:**
- [ ] Test: Build all tools to temp directories
- [ ] Test: Verify all output files created successfully
- [ ] Test: Verify files are readable by target tool (manual validation)
- [ ] Test: Verify YAML/JSON syntax is valid (parsers)
- [ ] Test: Verify markdown syntax is correct
- [ ] Test: Test file permissions and ownership
- [ ] Test: Test with various filesystem permissions
- [ ] No file I/O errors reported

**File(s):** `tests/integration/test_file_io.py`

**Effort:** S (5-6 hours)  
**Owner:** 1 engineer

---

### Task 6.4: Coverage Analysis & Gaps

**Description:** Analyze coverage metrics and fill gaps.

**Acceptance Criteria:**
- [ ] Generate coverage report: `pytest --cov`
- [ ] Overall coverage: 85%+
- [ ] Infrastructure coverage: 85%+
- [ ] Builder coverage: 85%+
- [ ] Parsers coverage: 85%+
- [ ] Identify uncovered code paths
- [ ] Add tests for gaps
- [ ] Final coverage report: 85%+

**File(s):** Coverage reports, additional tests as needed

**Effort:** M (8-10 hours)  
**Owner:** 1 engineer

---

### Task 6.5: Performance & Load Testing

**Description:** Verify performance meets targets.

**Acceptance Criteria:**
- [ ] Load 100 agents from registry: < 2 seconds
- [ ] Build single agent (all 5 tools): < 5 seconds
- [ ] Build all agents (all 5 tools): < 60 seconds
- [ ] Memory usage < 500MB for full registry
- [ ] No memory leaks (verified with memory profiler)
- [ ] Performance benchmarks documented

**File(s):** `tests/performance/test_benchmarks.py`

**Effort:** S (4-5 hours)  
**Owner:** 1 engineer

---

## Story 7: Documentation & Release (Week 6)

**Description:** Complete documentation and prepare for release.

**Size:** Medium (1 week)  
**Dependencies:** Stories 1-6 (all code complete)  
**Owner:** Documentation & Release Team

### Task 7.1: Implementation Guide

**Description:** Document how the Phase 2A system works for future developers.

**Acceptance Criteria:**
- [ ] Document: IR models and their purpose
- [ ] Document: How to add a new builder
- [ ] Document: How parsers work
- [ ] Document: Registry discovery mechanism
- [ ] Document: Component selector/composer logic
- [ ] Document: Builder factory pattern
- [ ] Document: File I/O patterns used
- [ ] Document: Testing patterns and conventions
- [ ] Guide includes code examples
- [ ] Guide is comprehensive (4-5 pages)

**File(s):** `docs/PHASE2A_IMPLEMENTATION_GUIDE.md`

**Effort:** M (6-8 hours)  
**Owner:** 1 engineer

---

### Task 7.2: Builder Documentation

**Description:** Document each builder's specific implementation.

**Acceptance Criteria:**
- [ ] Document: KiloBuilder format and output
- [ ] Document: ClaudeBuilder API compatibility
- [ ] Document: ClineBuilder skill activation
- [ ] Document: CopilotBuilder file structure
- [ ] Document: CursorBuilder format
- [ ] Each builder document includes examples
- [ ] Each builder document includes configuration options
- [ ] Troubleshooting section for each builder

**File(s):** `docs/builders/KILO_BUILDER.md`, `docs/builders/CLAUDE_BUILDER.md`, `docs/builders/CLINE_BUILDER.md`, `docs/builders/COPILOT_BUILDER.md`, `docs/builders/CURSOR_BUILDER.md`

**Effort:** M (8-10 hours)  
**Owner:** 1-2 engineers

---

### Task 7.3: Migration Guide

**Description:** Guide existing users from Phase 1 to Phase 2A.

**Acceptance Criteria:**
- [ ] Document: What's changing in Phase 2A
- [ ] Document: How to update existing agent configs
- [ ] Document: How to migrate from kilo_modes.yaml to registry
- [ ] Document: Breaking changes (if any)
- [ ] Document: Backward compatibility notes
- [ ] Document: How to test migration
- [ ] Migration script (if needed) documented
- [ ] FAQ section with common questions

**File(s):** `docs/PHASE2A_MIGRATION_GUIDE.md`

**Effort:** S (4-5 hours)  
**Owner:** 1 engineer

---

### Task 7.4: API Documentation

**Description:** Generate API documentation from docstrings.

**Acceptance Criteria:**
- [ ] All public classes have docstrings
- [ ] All public methods have docstrings
- [ ] Generate HTML API docs: `pdoc src/`
- [ ] API docs are readable and navigable
- [ ] API docs include examples
- [ ] API docs published to docs/api/

**File(s):** `docs/api/` (generated from docstrings)

**Effort:** S (3-4 hours)  
**Owner:** 1 engineer

---

### Task 7.5: Release & Communication

**Description:** Finalize release and communicate to stakeholders.

**Acceptance Criteria:**
- [ ] Version bump: Phase 2A release version
- [ ] CHANGELOG updated with all changes
- [ ] Release notes written
- [ ] All documentation reviewed
- [ ] Code review completed (all PRs)
- [ ] Release branch created
- [ ] Tag created for release
- [ ] Release announcement written
- [ ] Documentation published

**File(s):** `CHANGELOG.md`, `docs/PHASE2A_RELEASE_NOTES.md`, release tag

**Effort:** S (3-4 hours)  
**Owner:** Release Manager

---

## Summary by Story

| Story | Size | Week | Tasks | Est. Hours |
|-------|------|------|-------|-----------|
| 1: Infrastructure | Large | 1 | 6 | 28-35 |
| 2: Kilo Builder | Medium | 2 | 3 | 15-20 |
| 3: Cline Builder | Medium | 3 | 3 | 15-20 |
| 4: Claude & Copilot | Large | 4 | 5 | 32-40 |
| 5: Cursor Builder | Small | 4-5 | 2 | 7-9 |
| 6: Testing & Validation | Large | 5 | 5 | 33-41 |
| 7: Documentation | Medium | 6 | 5 | 18-26 |
| **TOTAL** | **XL** | **6** | **32** | **148-191** |

**Effort Estimate:** 148-191 hours (3-5 engineers for 6 weeks)

---

## Task Dependencies Map

```
Story 1: Infrastructure
├─→ Task 1.1: Pydantic Models
├─→ Task 1.2: Parsers
├─→ Task 1.3: Registry
├─→ Task 1.4: Base Classes
├─→ Task 1.5: Component Selector
└─→ Task 1.6: Unit Tests
    ↓ (dependencies)
    
Story 2: Kilo Builder (depends on Story 1)
├─→ Task 2.1: KiloBuilder
├─→ Task 2.2: Subagents
└─→ Task 2.3: Integration Tests
    ↓
    
Story 3: Cline Builder (depends on Story 1)
├─→ Task 3.1: ClineBuilder
├─→ Task 3.2: Skill Activation
└─→ Task 3.3: Integration Tests
    ↓
    
Story 4: Claude & Copilot (depends on Story 1)
├─→ Task 4.1: ClaudeBuilder
├─→ Task 4.2: Claude Subagents
├─→ Task 4.3: CopilotBuilder
├─→ Task 4.4: Integration Tests
└─→ Task 4.5: CLI Tool
    ↓
    
Story 5: Cursor Builder (depends on Story 1)
├─→ Task 5.1: CursorBuilder
└─→ Task 5.2: Integration Tests
    ↓
    
Story 6: Testing & Validation (depends on Stories 2-5)
├─→ Task 6.1: E2E Scenarios
├─→ Task 6.2: Mutation Testing
├─→ Task 6.3: File I/O Validation
├─→ Task 6.4: Coverage Analysis
└─→ Task 6.5: Performance Testing
    ↓
    
Story 7: Documentation (depends on Story 6)
├─→ Task 7.1: Implementation Guide
├─→ Task 7.2: Builder Documentation
├─→ Task 7.3: Migration Guide
├─→ Task 7.4: API Documentation
└─→ Task 7.5: Release
```

---
