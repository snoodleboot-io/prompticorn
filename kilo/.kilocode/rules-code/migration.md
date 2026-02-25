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
