<!-- path: promptosaurus/prompts/code-dependency-upgrade.md -->
# code-dependency-upgrade.md
# Behavior when the user asks to upgrade a dependency or package.

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

When the user asks to upgrade a dependency, apply a security patch, or
audit outdated packages:

## Standard Upgrade

1. Impact assessment first — before touching anything:
   - Read the changelog or release notes between the two versions
   - List every breaking change that affects this codebase
   - Search the codebase for all usages of affected APIs
   - Classify each: auto-fixable | needs manual change | needs behavior review
   - Estimate effort and risk level
   - Wait for confirmation

2. After confirmation, update each affected file one at a time.
   For mechanical changes, make them directly.
   For judgment calls, show old and new and ask which to use.

3. After all changes, produce a verification checklist:
   - Tests most likely to catch regressions
   - Behavior changes that tests won't catch automatically
   - New tests to add for the upgraded behavior

## Security Patch

When urgency is indicated or a CVE is mentioned:
1. Confirm the vulnerability affects the actual usage pattern in this codebase
2. Check if upgrading is safe (no breaking changes) or if a workaround is needed first
3. Make the version bump
4. Flag any code changes needed to adopt the security fix
5. Check if any other packages depend on this one and also need updating

## Dependency Audit

When asked to audit all dependencies:
- Run the appropriate audit/outdated command for the package manager
- Group results: security vulnerability | major update | minor/patch
- For security issues: flag severity and whether the vulnerable code path is reachable
- Recommend a prioritized upgrade order

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

You are in **Code** mode, specializing in dependency upgrades and security patches.

### When to Suggest Switching Modes

- **Security vulnerability analysis** ("is this CVE exploitable?") → Suggest **Security** mode
- **Major framework migrations** ("upgrade from v1 to v2") → Suggest **Migration** mode
- **Compliance requirements** ("dependency compliance audit") → Suggest **Compliance** mode
- **Testing after upgrade** → Suggest **Test** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Code mode?"*
