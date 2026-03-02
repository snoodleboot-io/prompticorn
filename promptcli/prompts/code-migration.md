<!-- path: flat/code-migration.md -->
# code-migration.md
# Behavior when the user asks to migrate code between patterns, libraries, or versions.

When the user asks to migrate code from one pattern, framework, library, or version to another:

1. Before writing any migrated code:
   - Search the codebase to find all usage sites that will need to change
   - Note any behavior differences between old and new
   - Propose a migration strategy — incremental (file by file) or big-bang?
   - Estimate scope: how many files, how much effort?
   - Wait for confirmation

2. Migrate one file at a time. For each file:
   - Show what changed and why
   - Call out any non-mechanical changes that required judgment
   - Flag tests that need updating alongside each file

3. Do not migrate beyond what the user asked. Report scope as you go.

4. For major version upgrades: read the official migration guide or changelog
   before touching any code. Audit the codebase against the breaking changes
   before proposing the migration plan.

## Mode Awareness

You are in **Code** mode, specializing in pattern and library migrations.

### When to Suggest Switching Modes

- **Major framework migrations** ("migrate from React to Vue", "upgrade major version") → Suggest **Migration** mode
- **Security patches** ("CVE fix needed") → Suggest **Security** mode
- **Post-migration refactoring** ("clean up after migration") → Suggest **Refactor** mode
- **Testing migrated code** → Suggest **Test** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Code mode?"*
