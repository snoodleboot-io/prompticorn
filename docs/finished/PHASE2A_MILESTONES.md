# Phase 2A: Implementation Milestones

**Timeline:** Apr 9 - May 20, 2026 (6 weeks)  
**Status:** Planning  
**Last Updated:** 2026-04-09

---

## Milestone Structure

Each milestone maps to a Story or group of stories and includes:
- **Definition of Done**: What must be completed before moving to next milestone
- **Deliverables**: Files, code, documentation to be produced
- **Success Criteria**: Measurable outcomes
- **Risk Assessment**: Potential blockers and mitigation

---

## Milestone 1: Foundation (Week 1: Apr 9-15)

**Story:** Story 1 - Infrastructure & Foundation  
**Owners:** Core Infrastructure Team (1-2 engineers)  
**Status:** Not Started

### Tasks Included
- Task 1.1: Pydantic IR Models
- Task 1.2: Parser Infrastructure  
- Task 1.3: Registry & Discovery System
- Task 1.4: Builder Base Classes & Interfaces
- Task 1.5: Component Selector & Composer
- Task 1.6: Unit Tests

### Deliverables

**Code:**
- `src/ir/models/agent.py` - Agent IR model
- `src/ir/models/skill.py` - Skill IR model
- `src/ir/models/workflow.py` - Workflow IR model
- `src/ir/models/tool.py` - Tool IR model
- `src/ir/models/rules.py` - Rules IR model
- `src/ir/models/project.py` - Project IR model
- `src/ir/parsers/yaml_parser.py` - YAML parsing
- `src/ir/parsers/markdown_parser.py` - Markdown parsing
- `src/ir/loaders/component_loader.py` - Component loading
- `src/registry/discovery.py` - Auto-discovery
- `src/registry/registry.py` - Registry management
- `src/builders/base.py` - Abstract base builder
- `src/builders/interfaces.py` - Mixin interfaces
- `src/builders/factory.py` - Builder factory
- `src/builders/component_selector.py` - Component selection
- `src/builders/component_composer.py` - Component composition

**Tests:**
- `tests/unit/ir/test_models.py` - Model tests (100% coverage)
- `tests/unit/ir/test_parsers.py` - Parser tests (85%+ coverage)
- `tests/integration/test_loaders.py` - Loader integration tests
- `tests/integration/test_discovery.py` - Discovery integration tests
- `tests/unit/builders/test_base.py` - Base builder tests (85%+ coverage)
- `tests/unit/builders/test_selector.py` - Selector tests (90%+ coverage)
- `tests/unit/builders/test_composer.py` - Composer tests (90%+ coverage)

**Documentation:**
- `docs/PHASE2A_IR_SPECIFICATION.md` - IR model documentation
- Architecture diagrams in ADR documents

### Definition of Done

- [ ] All IR models implemented with full type hints
- [ ] All parsers implemented with error handling
- [ ] Registry auto-discovery working (no manual registration)
- [ ] Builder base classes and factory pattern working
- [ ] Component selector handles minimal/verbose variants
- [ ] All unit tests passing (100% coverage on models, 85%+ on infrastructure)
- [ ] All integration tests passing with real file I/O
- [ ] No type errors (pyright strict mode passes)
- [ ] Code review approved by tech lead
- [ ] Documentation complete for all components

### Success Criteria

✅ **Must Have:**
- IR models accurately represent tool-agnostic agents/skills/workflows
- Auto-discovery loads agents from filesystem correctly
- Builder factory returns correct builder for each tool
- Component selector chooses correct variant (minimal/verbose)
- All infrastructure tests pass with 85%+ coverage
- No external dependencies beyond Pydantic and stdlib

✅ **Nice to Have:**
- Caching implemented in registry (faster subsequent loads)
- Detailed error messages for common mistakes
- Performance optimizations documented

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Pydantic version issues | Low | Medium | Pin version, test compatibility early |
| YAML/Markdown parsing edge cases | Medium | Medium | Add extensive test cases, fuzzing |
| Registry discovery performance | Low | Medium | Add caching, benchmark early |
| Builder abstraction too restrictive | Medium | High | Design review with team, iterate if needed |

### Previous Milestone
None (this is the foundation)

### Next Milestone
Milestone 2: Kilo Builder

---

## Milestone 2: Kilo Builder (Week 2: Apr 16-22)

**Story:** Story 2 - Kilo Builder Implementation  
**Owner:** Kilo Specialization Team (1 engineer)  
**Status:** Not Started  
**Depends On:** Milestone 1 ✓

### Tasks Included
- Task 2.1: Implement KiloBuilder Class
- Task 2.2: Implement Subagent Support
- Task 2.3: Integration Tests

### Deliverables

**Code:**
- `src/builders/kilo_builder.py` - KiloBuilder implementation
- Subagent generation logic (nested or separate files)

**Tests:**
- `tests/unit/builders/test_kilo_builder.py` - Unit tests (90%+ coverage)
- `tests/integration/test_kilo_subagents.py` - Subagent tests
- `tests/integration/test_kilo_builder.py` - E2E tests with real file I/O

**Example Output:**
- `.kilo/agents/code.md` - Example generated Kilo agent file
- `.kilo/agents/code/subagents/code-test.md` - Example subagent

### Definition of Done

- [ ] KiloBuilder class implements AbstractBuilder interface
- [ ] Generates valid Kilo agent files with YAML frontmatter + markdown sections
- [ ] Handles subagent generation with parent references
- [ ] All unit tests passing (90%+ coverage)
- [ ] All integration tests passing with real filesystem I/O
- [ ] Generated Kilo files verified as readable by Kilo IDE
- [ ] Code review approved
- [ ] Documentation complete

### Success Criteria

✅ **Must Have:**
- KiloBuilder generates YAML frontmatter correctly
- All markdown sections properly formatted
- Subagents organized hierarchically
- Integration tests verify real file I/O works
- Coverage >= 85%

✅ **Nice to Have:**
- Subagent discovery integration with registry
- Performance optimized (build single agent < 1 second)
- Pretty-printed output with proper markdown formatting

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Kilo format misunderstanding | Low | Medium | Review with Kilo expert, verify against real Kilo files |
| YAML frontmatter syntax errors | Low | Low | Add YAML validation, test against actual Kilo |
| Subagent nesting complexity | Medium | Medium | Design review, test thoroughly |

### Previous Milestone
Milestone 1: Foundation ✓

### Next Milestone
Milestone 3: Cline Builder

---

## Milestone 3: Cline Builder (Week 3: Apr 23-29)

**Story:** Story 3 - Cline Builder Implementation  
**Owner:** Cline Specialization Team (1 engineer)  
**Status:** Not Started  
**Depends On:** Milestone 1 ✓

### Tasks Included
- Task 3.1: Implement ClineBuilder Class
- Task 3.2: Implement Skill Activation
- Task 3.3: Integration Tests

### Deliverables

**Code:**
- `src/builders/cline_builder.py` - ClineBuilder implementation
- Skill activation mechanism (use_skill format)

**Tests:**
- `tests/unit/builders/test_cline_builder.py` - Unit tests (90%+ coverage)
- `tests/integration/test_cline_builder.py` - E2E tests with real file I/O

**Example Output:**
- `.clinerules` - Example generated Cline rules file

### Definition of Done

- [ ] ClineBuilder class implements AbstractBuilder interface
- [ ] Generates single `.clinerules` file with all sections concatenated
- [ ] Skill activation uses "use_skill" invocation pattern
- [ ] All unit tests passing (90%+ coverage)
- [ ] All integration tests passing with real file I/O
- [ ] Generated `.clinerules` verified as readable by Cline
- [ ] Code review approved
- [ ] Documentation complete

### Success Criteria

✅ **Must Have:**
- ClineBuilder generates single concatenated markdown file
- Skill section includes use_skill instructions
- Subagent delegation properly documented
- Integration tests verify real file I/O
- Coverage >= 85%

✅ **Nice to Have:**
- Skill invocation syntax validated
- Performance optimized (build single agent < 1 second)

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Cline skill activation format misunderstanding | Medium | Medium | Review Cline docs, test with actual Cline |
| Concatenation order issues | Low | Low | Test all section orders, validate output |

### Previous Milestone
Milestone 1: Foundation ✓

### Next Milestone
Milestone 4: Claude & Copilot Builders

---

## Milestone 4: Claude & Copilot Builders (Week 4: Apr 30-May 6)

**Story:** Story 4 - Claude & Copilot Builders  
**Story:** Story 5 - Cursor Builder (partial)  
**Owners:** Cloud Specialization Team (2 engineers)  
**Status:** Not Started  
**Depends On:** Milestone 1 ✓

### Tasks Included
- Task 4.1: Implement ClaudeBuilder Class
- Task 4.2: Implement Claude Subagent Delegation
- Task 4.3: Implement CopilotBuilder Class
- Task 4.4: Integration Tests
- Task 4.5: Implement CLI Tool
- Task 5.1: Implement CursorBuilder Class (partial)

### Deliverables

**Code:**
- `src/builders/claude_builder.py` - ClaudeBuilder implementation
- `src/builders/copilot_builder.py` - CopilotBuilder implementation
- `src/builders/cursor_builder.py` - CursorBuilder implementation (partial)
- `src/cli/build_command.py` - CLI tool for building

**Tests:**
- `tests/unit/builders/test_claude_builder.py` - Unit tests (90%+ coverage)
- `tests/unit/builders/test_copilot_builder.py` - Unit tests (90%+ coverage)
- `tests/unit/builders/test_cursor_builder.py` - Unit tests (90%+ coverage)
- `tests/unit/cli/test_build_command.py` - CLI tests
- `tests/integration/test_claude_builder.py` - E2E tests
- `tests/integration/test_copilot_builder.py` - E2E tests
- `tests/integration/test_cli_build.py` - CLI integration tests

**Example Output:**
- Claude Messages API payload (JSON)
- `.github/instructions/code.instructions.md` - Example Copilot file
- `.cursorrules` - Example Cursor file (partial)

### Definition of Done

- [ ] ClaudeBuilder generates valid JSON payload compatible with Messages API
- [ ] CopilotBuilder generates `.github/instructions/{mode}.md` files with YAML frontmatter
- [ ] CursorBuilder generates `.cursorrules` (at least 80% complete)
- [ ] Subagent delegation working for Claude and Copilot
- [ ] CLI tool working: `prompt-build --tool kilo` (and other tools)
- [ ] All unit tests passing (90%+ coverage)
- [ ] All integration tests passing with real file I/O
- [ ] JSON/YAML syntax validated
- [ ] Code review approved
- [ ] Documentation complete

### Success Criteria

✅ **Must Have:**
- Claude builder outputs valid JSON for Messages API
- Copilot builder generates files with correct YAML frontmatter
- Cursor builder complete or >80% complete
- CLI tool works for all builders
- All integration tests pass
- Coverage >= 85%

✅ **Nice to Have:**
- CLI tool supports `--all` flag (build all tools simultaneously)
- Performance optimized (build all 5 tools for one agent < 5 seconds)
- Helpful error messages if JSON/YAML invalid

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Claude API compatibility | Medium | High | Test with actual Messages API, review schema |
| Copilot format misunderstanding | Medium | Medium | Review Copilot docs thoroughly, test |
| CLI arg parsing issues | Low | Low | Comprehensive CLI tests |
| JSON schema generation bugs | Medium | Medium | Validate schema against claude-python SDK |

### Previous Milestone
Milestone 1: Foundation ✓

### Next Milestone
Milestone 5: Final Integration & Testing

---

## Milestone 5: Final Integration & Testing (Week 5: May 7-13)

**Story:** Story 6 - Testing & Validation  
**Story:** Story 5 - Cursor Builder (complete)  
**Owners:** QA & Testing Team (2 engineers)  
**Status:** Not Started  
**Depends On:** Milestones 2, 3, 4 ✓

### Tasks Included
- Task 5.2: Integration Tests for Cursor (complete)
- Task 6.1: E2E Scenario Tests
- Task 6.2: Mutation Testing
- Task 6.3: Real File I/O Validation
- Task 6.4: Coverage Analysis & Gaps
- Task 6.5: Performance & Load Testing

### Deliverables

**Tests:**
- `tests/integration/test_cursor_builder.py` - Complete Cursor tests
- `tests/e2e/test_scenarios.py` - E2E scenario tests (5 scenarios)
- `tests/integration/test_file_io.py` - File I/O validation tests
- `tests/performance/test_benchmarks.py` - Performance benchmarks
- Mutation test report (mutmut.ini, mutation report)
- Coverage reports (HTML + summary)

**Documentation:**
- `docs/PHASE2A_TEST_REPORT.md` - Complete test results
- Performance benchmarks documented
- Coverage analysis documented

### Definition of Done

- [ ] All 5 E2E scenarios passing
- [ ] Mutation score >= 80% on infrastructure and builders
- [ ] Overall code coverage >= 85%
- [ ] Real file I/O tests pass (all builders writing to filesystem)
- [ ] Performance targets met (build all 5 tools < 5 seconds per agent)
- [ ] No memory leaks detected
- [ ] All tests pass locally
- [ ] All tests pass in CI
- [ ] Code review approved

### Success Criteria

✅ **Must Have:**
- E2E: Load code agent → build all 5 tools → validate all outputs ✓
- E2E: Load architect agent → build all tools → validate outputs ✓
- E2E: Agent with subagents → all tools generate subagents ✓
- Mutation score >= 80% on all code
- Coverage >= 85% overall
- All builders produce valid output files
- File I/O works correctly (no errors)
- Performance < 5 seconds per agent

✅ **Nice to Have:**
- Performance < 1 second per agent (optimized)
- Memory usage tracked and documented
- Detailed performance breakdown by builder

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Low mutation score on edge cases | Medium | Medium | Add more edge case tests, review test quality |
| Coverage gaps in error handling | Low | Low | Add tests for error paths |
| Performance degradation | Low | Medium | Profile and optimize bottlenecks |
| File I/O permission issues | Low | Low | Test with various permissions |

### Previous Milestone
Milestones 2, 3, 4 ✓

### Next Milestone
Milestone 6: Documentation & Release

---

## Milestone 6: Documentation & Release (Week 6: May 14-20)

**Story:** Story 7 - Documentation & Release  
**Owners:** Documentation & Release Team (2 engineers)  
**Status:** Not Started  
**Depends On:** Milestone 5 ✓

### Tasks Included
- Task 7.1: Implementation Guide
- Task 7.2: Builder Documentation
- Task 7.3: Migration Guide
- Task 7.4: API Documentation
- Task 7.5: Release & Communication

### Deliverables

**Documentation:**
- `docs/PHASE2A_IMPLEMENTATION_GUIDE.md` - How the system works (4-5 pages)
- `docs/builders/KILO_BUILDER.md` - KiloBuilder documentation with examples
- `docs/builders/CLAUDE_BUILDER.md` - ClaudeBuilder documentation
- `docs/builders/CLINE_BUILDER.md` - ClineBuilder documentation
- `docs/builders/COPILOT_BUILDER.md` - CopilotBuilder documentation
- `docs/builders/CURSOR_BUILDER.md` - CursorBuilder documentation
- `docs/PHASE2A_MIGRATION_GUIDE.md` - Migration from Phase 1
- `docs/api/` - Generated API documentation (pdoc)
- `CHANGELOG.md` - Updated with Phase 2A changes
- `docs/PHASE2A_RELEASE_NOTES.md` - Release announcement

**Release:**
- Version bumped (e.g., 0.2.0 if previous was 0.1.x)
- Release branch created
- Release tag created
- Release published

### Definition of Done

- [ ] Implementation Guide complete and reviewed
- [ ] All 5 builder docs complete with examples
- [ ] Migration guide complete with step-by-step instructions
- [ ] API documentation generated and verified
- [ ] CHANGELOG updated with all changes
- [ ] Release notes written and reviewed
- [ ] All documentation spell-checked and proofread
- [ ] Documentation links verified
- [ ] Version bumped
- [ ] Release tag created
- [ ] Release published
- [ ] Stakeholders notified

### Success Criteria

✅ **Must Have:**
- Implementation Guide explains IR, builders, and extensibility
- All 5 builder docs include examples and configuration options
- Migration guide helps users upgrade from Phase 1
- API docs are comprehensive and navigable
- CHANGELOG lists all changes with categories
- Release notes suitable for public announcement
- All documentation is clear and accessible to engineers

✅ **Nice to Have:**
- Video walkthrough of implementation (optional)
- Tutorial for creating new builders (optional)
- FAQ addressing common questions
- Troubleshooting guide

### Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Documentation out of sync with code | Low | Medium | Review docs against final code, iterate |
| Incomplete builder docs | Low | Medium | Checklist for each builder doc, review |
| Release notes missing important info | Low | Low | Review against all PRs merged |

### Previous Milestone
Milestone 5: Final Integration & Testing ✓

### Next Milestone
Phase 2B Planning (future)

---

## Milestone Summary Table

| Milestone | Week | Status | Stories | Tasks | Est Hours | Dependencies |
|-----------|------|--------|---------|-------|-----------|--------------|
| 1: Foundation | 1 | Ready | Story 1 | 1.1-1.6 | 28-35 | None |
| 2: Kilo | 2 | Ready | Story 2 | 2.1-2.3 | 15-20 | M1 |
| 3: Cline | 3 | Ready | Story 3 | 3.1-3.3 | 15-20 | M1 |
| 4: Claude/Copilot | 4 | Ready | Story 4-5 | 4.1-4.5, 5.1 | 35-45 | M1 |
| 5: Testing | 5 | Ready | Story 6 + S5 | 6.1-6.5, 5.2 | 33-41 | M2, M3, M4 |
| 6: Release | 6 | Ready | Story 7 | 7.1-7.5 | 18-26 | M5 |
| **TOTAL** | **6** | **Ready** | **7** | **32** | **144-187** | - |

---

## Key Assumptions

1. **Team Capacity**: 1-2 full-time engineers per story (can work in parallel except where dependencies exist)
2. **No Major Blocking Issues**: Research is complete, no unexpected technical blockers
3. **Tool Compatibility**: Kilo, Claude, Cline, Cursor, Copilot APIs are available and unchanged
4. **Testing Infrastructure**: pytest, mutmut, and coverage tools available
5. **Code Review Process**: Average 1-2 business days per PR
6. **No Major Refactoring**: No major refactoring of existing codebase during this phase

## Success Definition

**Phase 2A is complete when:**

✅ All 6 milestones delivered  
✅ All 32 tasks completed with acceptance criteria met  
✅ 85%+ code coverage achieved  
✅ All E2E scenarios passing  
✅ Mutation score >= 80%  
✅ All builders generating valid tool-specific output  
✅ Documentation complete and reviewed  
✅ Release published and communicated  

---
