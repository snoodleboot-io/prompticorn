# Session Context Management

## Overview

Session files provide persistent context across mode switches, enabling continuity throughout the development workflow. Each session is tied to a git branch and tracks mode history, actions taken, and current state.

## Session File Location

- **Directory:** `.prompty/session/`
- **Naming:** `session_{YYYYMMDD}_{random}.md` (e.g., `session_20260302_a7x9k2.md`)
- **Format:** Markdown with YAML frontmatter
- **Git:** Session files are gitignored and NOT committed

## Session File Format

```markdown
---
session_id: "session_20260302_a7x9k2"
branch: "feat/my-feature"
created_at: "2026-03-02T10:30:00Z"
current_mode: "code"
version: "1.0"
---

## Session Overview

**Branch:** feat/my-feature  
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

## Session Management Procedure

### On Mode Startup (REQUIRED)

1. **Determine current git branch:**
   - Run: `git branch --show-current`
   - If on `main` branch:
     - If sufficient context exists: suggest creating a feature branch
     - If insufficient context: ask user for branch name
   - If on feature branch: use that branch name

2. **Check for existing session:**
   - List files in `.prompty/session/`
   - Read each file's YAML frontmatter
   - Look for `branch:` field matching current branch
   - Find most recent session if multiple exist

3. **If no session exists:**
   - Create `.prompty/session/` directory if needed
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

## Best Practices

1. **Always check for existing session first** - Don't create duplicates
2. **Update session after significant work** - Keep context current
3. **Be concise in summaries** - Capture essence without verbosity
4. **Use UTC timestamps** - Consistent timezone handling (ISO8601 format)
5. **Link related files** - Reference created/modified files in actions
6. **Track decisions** - Record when user approves/rejects something

## Integration with Modes

All modes MUST:
1. Check for session on startup
2. Create session if none exists
3. Update session on mode switch
4. Record significant actions
5. Maintain Context Summary

This ensures continuity when switching between modes (e.g., Architect → Code → Test → Review).
