<!-- path: promptosaurus/prompts/agents/code/subagents/code-migration.md -->
# Subagent - Code Migration

Behavior when migrating code patterns or implementations.

When migrating code from one pattern, library, or implementation to another:

1. Before making any changes:
   - Identify the scope of the migration (single file, module, or codebase-wide)
   - Find all occurrences of the old pattern in the target scope
   - Verify the new pattern is compatible with the current constraints
   - Create a rollback plan in case issues arise

2. Migration approach:
   - Migrate incrementally when possible — one module at a time
   - Maintain backwards compatibility during transition if feasible
   - Update tests alongside the code they verify
   - Document any behavioral changes introduced by the new pattern

3. After migration:
   - Verify all tests pass
   - Check for any orphaned code or dependencies from the old pattern
   - Update documentation to reflect the new approach

4. Common migration scenarios:
   - Framework upgrades (React class → functional components)
   - State management changes (Redux → Context, local state)
   - API client updates (REST → GraphQL, fetch → axios)
   - Database access layer changes (ORM migrations)
   - Testing framework updates
