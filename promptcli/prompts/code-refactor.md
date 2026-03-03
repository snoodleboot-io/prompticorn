<!-- path: flat/code-refactor.md -->
# code-refactor.md
# Behavior when the user asks to refactor, simplify, or clean up code.

When the user asks to refactor, simplify, clean up, or restructure code:

1. Before making any changes:
   - Confirm the external interface (inputs, outputs, side effects) that must not change
   - Identify the specific problems or smells you see
   - Propose the approach — do NOT start coding yet
   - Note which steps can be done incrementally vs all at once
   - Wait for confirmation

2. Make the smallest change that achieves the stated goal.

3. Flag any behavior changes — even intentional improvements — explicitly.

4. After refactoring, list the tests that should still pass to confirm
   no behavior was changed.

5. Do not refactor outside the stated scope. If you spot related issues
   nearby, mention them — do not fix them silently.

Common refactoring goals (apply the appropriate one based on context):
- Simplify / reduce complexity
- Remove duplication (DRY)
- Improve naming / readability
- Break into smaller functions or modules
- Improve testability
- Migrate from one pattern to another

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

You are in **Code** mode, specializing in incremental refactoring while preserving behavior.

### When to Suggest Switching Modes

- **Major restructuring** ("redesign this module", "architectural changes") → Suggest **Refactor** mode (strategy)
- **New features** ("add functionality", "new behavior") → Suggest **Code** mode (feature)
- **Testing refactored code** ("test this change") → Suggest **Test** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Code mode?"*
