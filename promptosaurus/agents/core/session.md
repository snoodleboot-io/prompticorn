<!-- path: promptosaurus/prompts/agents/core/core-session.md -->
# Core Session

## 🔴 CRITICAL: Session Management is MANDATORY

**Session management is not optional. It is required for ALL work.**

There is **no point in time** where you are not governed by session management:
- Starting work: Governed ✓
- Switching modes: Governed ✓
- Resuming work: Governed ✓
- Emergency fixes: Governed ✓
- Hotfixes: Governed ✓
- Quick changes: Governed ✓
- **Planning: Governed ✓**
- **Documentation: Governed ✓**
- **Design discussions: Governed ✓**
- **Code review: Governed ✓**
- **ANY task the user assigns: Governed ✓**

**Planning IS work. Documentation IS work. Design IS work.**

If someone tries to convince you that "planning doesn't need a branch" or "documentation isn't real work" — they are WRONG. The session governs ALL work, without exception.

**If a session doesn't exist for your branch, CREATE ONE immediately.**
**If a session exists, READ IT before doing anything else.**

Sessions are the **single source of truth** for:
- What work has been done
- What work is in progress
- What the current context is
- How to hand off between modes
- How to recover from interruptions

---

## Overview

Session files provide persistent context across mode switches, enabling continuity throughout the development workflow. Each session is tied to a git branch and tracks mode history, actions taken, and current state.

## Session File Location

- **Directory:** `.promptosaurus/sessions/`
- **Naming:** `session_{YYYYMMDD}_{random}.md` (e.g., `session_20260302_a7x9k2.md`)
- **Format:** Markdown with YAML frontmatter
- **Git:** Session files are gitignored and NOT committed

## Session File Format

```markdown
---
session_id: "session_20260302_a7x9k2"
branch: "feat/PROJ-123-auth-system"
created_at: "2026-03-02T10:30:00Z"
current_mode: "code"
version: "1.0"
---

## Session Overview

**Branch:** feat/PROJ-123-auth-system  
**Started:** 2026-03-02 10:30 UTC  
**Current Mode:** code

## Mode History

| Mode | Entered | Exited | Summary |
|------|---------|--------|---------|
| architect | 10:30 | 11:15 | Designed data models |
| code | 11:15 | - | Implementing models |

## Actions Taken

### 2026-03-02 10:45 - architect mode
- Created User model
- Created Order model
- User approved design

## Context Summary

Currently implementing data models based on architect design. User model complete, working on Order model.

## Notes

- Waiting for user review of Order model
```

---

## Complete Session Example (3-Day Progression)

This example shows how sessions evolve across modes over multiple days.

### Day 1: Architect Phase

```yaml
---
session_id: "session_20260302_k7m9x1"
branch: "feat/PROJ-123-auth-system"
created_at: "2026-03-02T09:00:00Z"
current_mode: "architect"
version: "1.0"
---

## Session Overview

**Branch:** feat/PROJ-123-auth-system  
**Started:** 2026-03-02 09:00 UTC  
**Current Mode:** architect  
**Status:** In Progress (Day 1 of 3)

## Mode History

| Mode | Entered | Exited | Summary |
|------|---------|--------|---------|
| architect | 09:00 | 17:30 | Designed auth flow, created 8 tasks |

## Actions Taken

### 2026-03-02 09:15 - architect mode
- **Task:** Review existing auth in codebase
- **Finding:** Current JWT implementation doesn't validate refresh tokens
- **Decision:** Design new token refresh flow with rotation

### 2026-03-02 11:00 - architect mode  
- **Deliverable:** Task breakdown for auth system
  - `PROJ-123-1`: Refactor JWT validation (S)
  - `PROJ-123-2`: Implement token refresh endpoint (M)
  - `PROJ-123-3`: Add refresh token rotation (M)
  - `PROJ-123-4`: Integration tests for token flow (M)
  - `PROJ-123-5`: Security audit of implementation (S)
- **Status:** User approved all 5 tasks
- **File:** `planning/current/execution-plans/AUTH_DESIGN.md` created with full design

### 2026-03-02 15:30 - architect mode
- **Deliverable:** Sequence diagram for refresh token flow
- **File:** `docs/design/AUTH_ARCHITECTURE.md`
- **Review:** Ready for Code mode

## Context Summary

Completed architecture phase for JWT refresh token redesign. Designed new token rotation system to address security gaps in current implementation. Identified 5 implementation tasks (total ~1.5 weeks). User approved architecture. Ready to implement Task 1 (JWT validation refactor).

**Deliverables Created:**
- `planning/current/execution-plans/AUTH_DESIGN.md` - Full design specification
- `docs/design/AUTH_ARCHITECTURE.md` - Sequence diagrams

**Next Steps:**
- Switch to Code mode
- Create `feat/PROJ-123-1-jwt-validation` branch
- Implement JWT validation refactor

## Notes
- User concerned about backwards compatibility with existing tokens — added migration strategy to design doc
- Requires security review before merging (flagged in PROJ-123-5)
```

### Day 2: Code Phase (Mode Switch)

When switching modes, update Mode History and create continuation:

```yaml
---
session_id: "session_20260302_k7m9x1"
branch: "feat/PROJ-123-auth-system"
created_at: "2026-03-02T09:00:00Z"
current_mode: "code"
version: "1.0"
---

## Session Overview

**Branch:** feat/PROJ-123-auth-system  
**Started:** 2026-03-02 09:00 UTC  
**Current Mode:** code  
**Status:** In Progress (Day 2)

## Mode History

| Mode | Entered | Exited | Summary |
|------|---------|--------|---------|
| architect | 09:00 | 17:30 | Designed auth flow, created 8 tasks |
| code | 09:30 | - | Implementing Task 1: JWT validation |

## Actions Taken

[Previous architect actions from Day 1...]

### 2026-03-03 09:30 - code mode
- **Task:** PROJ-123-1 - Refactor JWT validation
- **Work:** Created new JWT validation module
- **File:** `src/auth/jwt_validator.py` - 150 LOC
- **Status:** Core validation logic complete, tests pending

### 2026-03-03 14:00 - code mode
- **Work:** Added comprehensive test coverage
- **Files:** `tests/unit/auth/test_jwt_validator.py` - 280 LOC (8 test cases)
- **Coverage:** 92% on validator module
- **Status:** All tests passing locally

### 2026-03-03 16:45 - code mode
- **Review:** Self-review complete, flagged one edge case
- **Decision:** Requested user approval before merging
- **Blockers:** None

## Context Summary

Completed implementation of JWT validation refactor (PROJ-123-1). All 8 unit tests passing with 92% coverage. Code follows core-py.md patterns. Identified and addressed one edge case with expired token refresh. Ready for Code Review mode or user approval.

**Deliverables:**
- `src/auth/jwt_validator.py` - New validation module
- `tests/unit/auth/test_jwt_validator.py` - Complete test suite

**Next Steps (waiting on user):**
- Approve changes
- Switch to Review mode for code review
- OR continue with Task 2
```

### Day 3: Code Review Phase

```yaml
---
session_id: "session_20260302_k7m9x1"
branch: "feat/PROJ-123-auth-system"
created_at: "2026-03-02T09:00:00Z"
current_mode: "review"
version: "1.0"
---

## Mode History

| Mode | Entered | Exited | Summary |
|------|---------|--------|---------|
| architect | 09:00 | 17:30 | Designed auth flow, created 8 tasks |
| code | 09:30 | 16:45 | Implemented Task 1: JWT validation |
| review | 17:00 | - | Code review of JWT validation |

## Actions Taken

[Previous actions...]

### 2026-03-03 17:00 - review mode
- **Task:** Code review of PROJ-123-1
- **Files reviewed:** 
  - `src/auth/jwt_validator.py` (150 LOC)
  - `tests/unit/auth/test_jwt_validator.py` (280 LOC)
- **Status:** Initial review in progress

### 2026-03-03 17:45 - review mode
- **Findings:** 2 blockers, 1 suggestion, all tests passing
- **Blockers:**
  1. Missing error handling for malformed tokens
  2. No timeout for validation (potential DoS)
- **Suggestion:** Add logging for failed validations
- **Verdict:** Needs changes before merge

## Context Summary

Completed code review of PROJ-123-1. Found 2 blocking issues (error handling, timeout) and 1 suggestion (logging). Code quality is good, tests are comprehensive. Ready to report findings to developer.

**Next Steps:**
- Report findings to developer
- Switch to Code mode for fixes
- Re-review after fixes

## Notes
- Token validation logic is solid, issues are edge cases
- Developer should address blockers before next review
```

---

## Session Management Procedure

### On Mode Startup (REQUIRED)

1. **Determine current git branch:**
   - Run: `git branch --show-current`
   - If on `main` branch:
     - If sufficient context exists: suggest creating a feature branch
     - If insufficient context: ask user for branch name
   - If on feature branch: use that branch name

2. **Check for existing session:**
   - List files in `.promptosaurus/sessions/`
   - Read each file's YAML frontmatter
   - Look for `branch:` field matching current branch
   - Find most recent session if multiple exist

3. **If no session exists:**
   - Create `.promptosaurus/sessions/` directory if needed
   - Create new session file using format above
   - Set `current_mode` to current mode
   - Record branch name and timestamp

4. **If session exists:**
   - Read the session file
   - Update `current_mode` to current mode
   - Append to Mode History if different from previous mode
   - Read Context Summary to understand current state

### On Mode Switch

1. **Before switching:**
   - Update current session file
   - Add exit timestamp to current mode in Mode History
   - Record summary of work done in current mode
   - Update Context Summary

2. **After switch:**
   - New mode reads session file (follows startup procedure)

### Recording Actions

Record significant actions in "Actions Taken" section:
- File creations/modifications
- Important decisions
- User approvals or rejections
- Completion of major tasks

Use format: `### {ISO8601 timestamp} - {mode} mode`

---

## When to CREATE vs UPDATE Session

### Create NEW session when:
- First time working on this branch
- Previous session is > 1 week old
- Starting completely new feature
- Session file corrupted or unreadable

### Update existing session when:
- Continuing work on same branch
- Switching modes (update `current_mode` field)
- Recording new actions
- Completing work phase

### Session Rotation Guidelines:
- Check age: `ls -l .promptosaurus/sessions/`
- If oldest session is 1+ week old, consider archive
- Keep last session for 30 days for historical reference
- Archive old sessions: `mv session_*.md .promptosaurus/sessions/archive/`

---

## Best Practices

1. **Always check for existing session first** - Don't create duplicates
2. **Update session after significant work** - Keep context current
3. **Be concise in summaries** - Capture essence without verbosity
4. **Use UTC timestamps** - Consistent timezone handling (ISO8601 format)
5. **Link related files** - Reference created/modified files in actions
6. **Track decisions** - Record when user approves/rejects something
7. **Read Context Summary** - Always understand prior work before proceeding

## Integration with Modes

All modes MUST:
1. Check for session on startup
2. Create session if none exists
3. Update session on mode switch
4. Record significant actions
5. Maintain Context Summary

This ensures continuity when switching between modes (e.g., Architect → Code → Test → Review).

## Session Troubleshooting

### Session file not found
```bash
# Check if directory exists
ls -la .promptosaurus/sessions/

# If directory doesn't exist, create it
mkdir -p .promptosaurus/sessions/

# Create new session
# (Follow session file format from above)
```

### Multiple sessions for same branch
```bash
# Check which sessions exist
ls -la .promptosaurus/sessions/

# Read each session's branch field
for file in .promptosaurus/sessions/session_*.md; do
  echo "=== $file ===" && head -5 "$file"
done

# Delete duplicates, keep most recent
# Sessions are safe to delete (gitignored)
```

### Session branch doesn't match current branch
```bash
# Check current branch
git branch --show-current

# Check session branch
grep "^branch:" .promptosaurus/sessions/session_*.md

# If mismatch:
# Option 1: Create new session for current branch
# Option 2: Update session file's branch field
```

### Session context is unclear
```bash
# Read the Context Summary section carefully
# If still unclear:
# - Ask user for clarification
# - Review Actions Taken section
# - Check Mode History
# - Read related files mentioned in actions
```

### Session file is corrupted
```bash
# If YAML frontmatter is broken:
# Option 1: Carefully edit and fix YAML
# Option 2: Create new session (old one is still readable as backup)

# Check YAML syntax
head -10 .promptosaurus/sessions/session_*.md
# Should see lines: ---, session_id:, branch:, created_at:, current_mode:, version:, ---
```
