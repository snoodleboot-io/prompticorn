# Story 4 & 5: Cloud Builders (Claude, Copilot, Cursor)

**Status:** Ready to Start (after Story 1)  
**Week:** 4 (Apr 30-May 6)  
**Owner:** Cloud Specialization Team  
**Effort:** 35-45 hours (2 engineers)  
**Dependencies:** Story 1 ✓

---

## Overview

Implement three builders in parallel: ClaudeBuilder (JSON for Messages API), CopilotBuilder (.github/instructions/), and CursorBuilder (.cursorrules). Also create CLI tool for building all tools from command line.

## Description

Create builders for cloud-native tools, demonstrating how IR translates to different formats (JSON, YAML+Markdown, plain Markdown).

## Tasks

| # | Task | Effort | Owner | Status |
|---|------|--------|-------|--------|
| 4.1 | Implement ClaudeBuilder Class | M (7-9h) | TBD | ☐ |
| 4.2 | Implement Claude Subagent Delegation | S (4-5h) | TBD | ☐ |
| 4.3 | Implement CopilotBuilder Class | M (7-9h) | TBD | ☐ |
| 4.4 | Integration Tests (Claude & Copilot) | M (8-10h) | TBD | ☐ |
| 4.5 | Implement CLI Tool | S (5-6h) | TBD | ☐ |
| 5.1 | Implement CursorBuilder (partial) | S (4-5h) | TBD | ☐ |

## Deliverables

### Code
- `src/builders/claude_builder.py` - ClaudeBuilder (JSON output for Messages API)
- `src/builders/copilot_builder.py` - CopilotBuilder (.github/instructions/)
- `src/builders/cursor_builder.py` - CursorBuilder (.cursorrules) - 80%+ complete
- `src/cli/build_command.py` - CLI tool for building

### Tests
- `tests/unit/builders/test_claude_builder.py` - Unit tests (90%+ coverage)
- `tests/unit/builders/test_copilot_builder.py` - Unit tests (90%+ coverage)
- `tests/unit/builders/test_cursor_builder.py` - Unit tests (90%+ coverage)
- `tests/unit/cli/test_build_command.py` - CLI tests
- `tests/integration/test_claude_builder.py` - E2E tests
- `tests/integration/test_copilot_builder.py` - E2E tests
- `tests/integration/test_cli_build.py` - CLI integration tests

### Example Output
- Claude Messages API payload (JSON)
- `.github/instructions/code.instructions.md` - Example Copilot file
- `.cursorrules` - Example Cursor file (partial)

## Acceptance Criteria

### Functional
- [ ] ClaudeBuilder generates valid JSON for Claude Messages API
- [ ] CopilotBuilder generates `.github/instructions/{mode}.md` with YAML frontmatter
- [ ] CursorBuilder generates `.cursorrules` (at least 80% complete)
- [ ] Subagent delegation working for Claude and Copilot
- [ ] CLI tool works: `prompt-build --tool kilo` (and other tools)
- [ ] CLI tool works: `prompt-build --all` (builds all tools)
- [ ] CLI supports `--variant minimal` and `--variant verbose`
- [ ] CLI supports `--agent {name}` or builds all agents

### Quality
- [ ] Unit test coverage: 90%+ on builders
- [ ] All tests pass locally and in CI
- [ ] Code review approved

## Definition of Done

- [ ] All 6 tasks (4.1-4.5, 5.1) complete
- [ ] ClaudeBuilder generating valid output
- [ ] CopilotBuilder generating valid output
- [ ] CursorBuilder at 80%+ complete
- [ ] CLI tool working
- [ ] All tests passing (local + CI)
- [ ] Coverage >= 85%
- [ ] Code review approved

## Dependencies

- Story 1: Infrastructure & Foundation ✓

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Claude API compatibility | Medium | High | Test with actual Messages API, review schema |
| Copilot format misunderstanding | Medium | Medium | Review Copilot docs thoroughly, test |
| CLI arg parsing issues | Low | Low | Comprehensive CLI tests |
| JSON schema generation bugs | Medium | Medium | Validate schema against claude-python SDK |
| Multiple builders in parallel | Medium | Medium | Daily standups, clear interfaces |

## Success Criteria

✅ **Must Have:**
- Claude builder outputs valid JSON for Messages API
- Copilot builder generates files with correct YAML frontmatter
- Cursor builder complete or >80% complete
- CLI tool works for all builders
- All integration tests pass
- Coverage >= 85%

✅ **Nice to Have:**
- CLI tool supports `--all` flag (build all tools simultaneously)
- Build all 5 tools for one agent < 5 seconds
- Helpful error messages if JSON/YAML invalid

## Next Steps

After Story 4-5 Complete:
- Story 5.2: Complete Cursor Builder - Week 5
- Story 6: Testing & Validation - Week 5
- Story 7: Documentation & Release - Week 6

---

**Related Documents:**
- Feature: `docs/features/FEATURE_001_...md`
- Task Details: `../tasks/task_4_*.md`, `../tasks/task_5_*.md`
- Milestones: `../../PHASE2A_MILESTONES.md`
- Roadmap: `../ROADMAP.md`
