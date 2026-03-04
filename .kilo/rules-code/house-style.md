
# code-house-style.md
# Behavior when the user asks to check or enforce house style.

When the user asks to check code against house style, audit style, or
when you are about to write new code in an unfamiliar part of the codebase:

1. Before writing any code in an unfamiliar module, read 2-3 existing files
   from the same layer to understand the established patterns.

2. When auditing code for style, check against core-conventions.md and
   against patterns observed in the rest of the codebase. Report:
   - Every deviation from core-conventions.md
   - Any patterns that don't match how similar code is written elsewhere
   - Severity: MUST FIX (will confuse maintainers) or NIT (minor preference)

3. When writing new code, match the patterns you observed — do not introduce
   a new pattern without asking first.

4. If asked to summarize house style for a new contributor, read 3-4
   representative source files and produce a brief style guide covering:
   - File and folder naming
   - Error handling pattern
   - Async style
    - Module structure (imports, exports)
    - Testing patterns

## Session Context

Before starting work in Code mode:

1. **Check for session file:**
   - Run: `git branch --show-current`
   - Look in `.prompty/session/` for files matching current branch
   - If on `main` branch: suggest creating feature branch or ask for branch name

2. **If no session exists:**
   - Create `.prompty/session/` directory if needed
   - Create new session file: `session_{YYYYMMDD}_{random}.md`
   - Include YAML frontmatter with session_id, branch, created_at, current_mode="code"
   - Initialize Mode History and Actions Taken sections

3. **If session exists:**
   - Read the session file
   - Update `current_mode` to "code"
   - Add entry to Mode History if different from previous mode
   - Review Context Summary for current state

4. **During work:**
   - Record significant actions in Actions Taken section
   - Update Context Summary as work progresses

5. **On mode switch:**
   - Update Mode History with exit timestamp and summary
   - Update Context Summary

## Mode Awareness

You are in **Code** mode, specializing in house style auditing and pattern matching.

### When to Suggest Switching Modes

- **Refactoring** ("refactor this to match house style") → Suggest **Refactor** mode
- **New feature implementation** ("implement this feature") → Suggest **Code** mode (feature)
- **Security review** ("check for security issues") → Suggest **Security** mode
- **Code review** ("review this PR", "code quality check") → Suggest **Review** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Code mode?"*
