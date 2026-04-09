# Story 3: Cline Builder Implementation

**Status:** Ready to Start (after Story 1)  
**Week:** 3 (Apr 23-29)  
**Owner:** Cline Specialization Team  
**Effort:** 15-20 hours (1 engineer)  
**Dependencies:** Story 1 ✓

---

## Overview

Implement ClineBuilder to generate `.clinerules` (single concatenated markdown file). Demonstrates skill activation mechanism unique to Cline.

## Description

Create ClineBuilder that translates IR models into Cline format, implementing Cline's `use_skill` tool invocation pattern.

## Tasks

| # | Task | Effort | Owner | Status |
|---|------|--------|-------|--------|
| 3.1 | Implement ClineBuilder Class | M (6-8h) | TBD | ☐ |
| 3.2 | Implement Skill Activation | S (3-4h) | TBD | ☐ |
| 3.3 | Integration Tests for Cline Builder | M (6-7h) | TBD | ☐ |

## Deliverables

### Code
- `src/builders/cline_builder.py` - ClineBuilder implementation
- Skill activation mechanism (`use_skill` format)

### Tests
- `tests/unit/builders/test_cline_builder.py` - Unit tests (90%+ coverage)
- `tests/integration/test_cline_builder.py` - E2E tests with real file I/O

### Example Output
- `.clinerules` - Example generated Cline rules file

## Acceptance Criteria

### Functional
- [ ] ClineBuilder extends AbstractBuilder correctly
- [ ] Generates single concatenated markdown file
- [ ] Skills section includes "use_skill" invocation instructions
- [ ] Skill activation instructions clear and actionable
- [ ] Subagent delegation properly documented
- [ ] Output is valid Cline rules format

### Quality
- [ ] Unit test coverage: 90%+
- [ ] All tests pass locally and in CI
- [ ] Code review approved

## Definition of Done

- [ ] All 3 tasks (3.1-3.3) complete
- [ ] ClineBuilder generates valid output
- [ ] All tests passing (local + CI)
- [ ] Coverage >= 85%
- [ ] Code review approved
- [ ] Output verified readable by Cline

## Dependencies

- Story 1: Infrastructure & Foundation ✓

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Cline skill activation format misunderstanding | Medium | Medium | Review Cline docs, test with actual Cline |
| Concatenation order issues | Low | Low | Test all section orders, validate output |

## Success Criteria

✅ **Must Have:**
- ClineBuilder generates single concatenated markdown file
- Skill section includes use_skill instructions
- Subagent delegation properly documented
- Integration tests verify real file I/O
- Coverage >= 85%

✅ **Nice to Have:**
- Skill invocation syntax validated
- Build single agent < 1 second

## Next Steps

After Story 3 Complete:
- Story 4-5 (Cloud Builders) - Week 4
- Story 6 (Testing & Validation) - Week 5

---

**Related Documents:**
- Feature: `docs/features/FEATURE_001_...md`
- Task Details: `../tasks/task_3_*.md`
- Milestones: `../../PHASE2A_MILESTONES.md`
- Roadmap: `../ROADMAP.md`
