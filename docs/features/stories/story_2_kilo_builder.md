# Story 2: Kilo Builder Implementation

**Status:** Ready to Start (after Story 1)  
**Week:** 2 (Apr 16-22)  
**Owner:** Kilo Specialization Team  
**Effort:** 15-20 hours (1 engineer)  
**Dependencies:** Story 1 ✓

---

## Overview

Implement the first concrete builder - KiloBuilder - to generate `.kilo/agents/{name}.md` files with YAML frontmatter and markdown sections. This establishes the pattern all other builders will follow.

## Description

Create KiloBuilder that translates tool-agnostic IR models into Kilo IDE format, demonstrating the builder pattern for subsequent builders.

## Tasks

| # | Task | Effort | Owner | Status |
|---|------|--------|-------|--------|
| 2.1 | Implement KiloBuilder Class | M (6-8h) | TBD | ☐ |
| 2.2 | Implement Subagent Support | S (4-5h) | TBD | ☐ |
| 2.3 | Integration Tests for Kilo Builder | M (6-7h) | TBD | ☐ |

## Deliverables

### Code
- `src/builders/kilo_builder.py` - KiloBuilder implementation
- Subagent generation logic (nested markdown files)

### Tests
- `tests/unit/builders/test_kilo_builder.py` - Unit tests (90%+ coverage)
- `tests/integration/test_kilo_subagents.py` - Subagent tests
- `tests/integration/test_kilo_builder.py` - E2E tests with real file I/O

### Example Output
- `.kilo/agents/code.md` - Example generated Kilo agent file
- `.kilo/agents/code/subagents/code-test.md` - Example subagent

## Acceptance Criteria

### Functional
- [ ] KiloBuilder extends AbstractBuilder correctly
- [ ] Generates YAML frontmatter with name, description, model, state_management
- [ ] Generates # System Prompt section with agent.system_prompt
- [ ] Generates # Tools, # Skills, # Workflows, # Subagents sections
- [ ] Proper markdown formatting (headers, lists, code blocks)
- [ ] Subagent files generated with parent references
- [ ] Subagent files follow same format as parent agent
- [ ] Output is valid Kilo agent file format

### Quality
- [ ] Unit test coverage: 90%+
- [ ] All tests pass locally and in CI
- [ ] Code review approved

## Definition of Done

- [ ] All 3 tasks (2.1-2.3) complete
- [ ] KiloBuilder generates valid output
- [ ] All tests passing (local + CI)
- [ ] Coverage >= 85%
- [ ] Code review approved
- [ ] Output verified readable by Kilo IDE

## Dependencies

- Story 1: Infrastructure & Foundation ✓

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Kilo format misunderstanding | Low | Medium | Review with Kilo expert, verify against actual files |
| YAML frontmatter syntax errors | Low | Low | Add YAML validation, test against actual Kilo |
| Subagent nesting complexity | Medium | Medium | Design review, test thoroughly |

## Success Criteria

✅ **Must Have:**
- KiloBuilder generates YAML frontmatter correctly
- All markdown sections properly formatted
- Subagents organized hierarchically
- Integration tests verify real file I/O
- Coverage >= 85%

✅ **Nice to Have:**
- Subagent discovery integration with registry
- Build single agent < 1 second
- Pretty-printed output with proper markdown

## Next Steps

After Story 2 Complete:
- Story 3 (Cline Builder) - Week 3
- Story 4-5 (Cloud Builders) - Week 4 (can overlap with Story 3)

---

**Related Documents:**
- Feature: `docs/features/FEATURE_001_...md`
- Task Details: `../tasks/task_2_*.md`
- Milestones: `../../PHASE2A_MILESTONES.md`
- Roadmap: `../ROADMAP.md`
