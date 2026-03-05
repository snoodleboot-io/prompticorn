<!-- path: promptosaurus/prompts/ask-docs.md -->
# ask-docs.md
# Behavior when the user asks to generate or improve documentation.

## Prerequisites — Complete Before Any Work

1. **Read All Core Configuration Files** (REQUIRED FIRST)
   - Read `core-system.md` — Follow always-on behaviors and git branch protocol
   - Read `core-conventions.md` — Follow naming, structure, and error handling rules
   - Read `core-session.md` — Follow session management protocol
   - Read `core-conventions-{lang}.md` — Follow language-specific conventions

   ALL output must comply with these core files exactly.

2. **Check Git Branch** (per core-system.md)
   - Run: `git branch --show-current`
   - If on `main`: STOP and create feature branch first

3. **Initialize/Update Session** (per core-session.md)
   - Check `.prompty/session/` for existing session matching current branch
   - Create or update session file with current mode

When the user asks to generate inline comments, API docs, docstrings, or OpenAPI specs:

## Inline Comments

When asked to add or improve inline comments:
- Comment the WHY, not the WHAT
- Skip comments on self-evident code
- Flag non-obvious decisions: "// intentionally not awaited — fire and forget"
- Mark known issues: "// TODO: this will break if called concurrently"
- Explain magic numbers: "// 86400 = seconds in a day"
- Note invariants callers must maintain

Audit existing comments and classify each as:
- GOOD: explains something non-obvious — keep
- NOISE: restates what the code says — delete
- OUTDATED: no longer matches the code — update
- MISSING: something complex here with no explanation — add

## Function / API Documentation

For each function, method, or endpoint document:
1. Purpose — what it does in one sentence (not how)
2. Parameters — name, type, required/optional, constraints
3. Return value — type, shape, possible values
4. Errors — what can go wrong and under what conditions
5. Example — at least one realistic usage
6. Side effects — DB writes, external calls, state changes

Use the docstring format from core-conventions.md.
Keep descriptions precise and brief. No filler phrases.

## OpenAPI Spec

When asked to generate an OpenAPI spec:
- Format: OpenAPI 3.0 YAML
- Include paths, methods, operation IDs
- Request body schemas with required fields marked
- Response schemas for 200, 400, 401, 404, 500
- Tag endpoints by resource
- Ask for auth type if not specified

## Changelog

When asked to generate a changelog entry:
- Format: Keep a Changelog (keepachangelog.com)
- Sections: Added, Changed, Deprecated, Removed, Fixed, Security

## Session Context

Before starting work in Ask mode:

1. **Check for session file:**
   - Run: `git branch --show-current`
   - Look in `.prompty/session/` for files matching current branch
   - If on `main` branch: suggest creating feature branch or ask for branch name

2. **If no session exists:**
   - Create `.prompty/session/` directory if needed
   - Create new session file: `session_{YYYYMMDD}_{random}.md`
   - Include YAML frontmatter with session_id, branch, created_at, current_mode="ask"
   - Initialize Mode History and Actions Taken sections

3. **If session exists:**
   - Read the session file
   - Update `current_mode` to "ask"
   - Add entry to Mode History if different from previous mode
   - Review Context Summary for current state

4. **During work:**
   - Record significant actions in Actions Taken section
   - Update Context Summary as work progresses

5. **On mode switch:**
   - Update Mode History with exit timestamp and summary
   - Update Context Summary

## Mode Awareness

You are in **Ask** mode (documentation specialization), helping with inline comments, API docs, and changelogs.

### When to Suggest Switching Modes

- **Full documentation strategy** ("create documentation plan") → Suggest **Document** mode
- **Testing documentation** ("document test strategy") → Suggest **Test** mode
- **Code implementation** ("add the code first") → Suggest **Code** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Ask mode?"*
- Write from the perspective of a consumer, not the implementer
- Do not include internal refactors unless they affect behavior
- Prefix breaking changes with a warning marker
- Ask for version and date if not provided
