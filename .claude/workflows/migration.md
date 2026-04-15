## Migration Workflow

### Step 1: Define Migration Scope

Before touching any code, clearly define what's being migrated:
- **What**: Framework version, database schema, language version, architecture pattern, or third-party dependency
- **Why**: Performance improvement, security fix, feature enablement, deprecation deadline, or tech debt reduction
- **Affected areas**: List all modules, services, and features impacted
- **Risk level**: Low (isolated change), Medium (cross-cutting), or High (critical path)

Clarify ambiguities:
- Does this break backward compatibility?
- Are there known breaking changes in the target version?
- What's the timeline and deadline?
- Is there a rollback requirement if deployment fails?

Document your findings before proceeding.

### Step 2: Create Comprehensive Test Plan

Design tests to verify nothing breaks during migration:
- **Functionality verification**: What core features must continue working unchanged?
- **Integration points**: Which service boundaries or API contracts must remain stable?
- **Performance**: Will migration affect response time or throughput?
- **Data integrity**: For database migrations, how do you verify data consistency?
- **Edge cases**: What corner cases could migration affect (concurrent access, race conditions)?

Write or identify existing tests covering these areas. If they don't exist, create them BEFORE migration starts—this becomes your safety net.

### Step 3: Create Detailed Migration Checklist

Build a step-by-step procedure you'll follow:

```
Migration Checklist: [name]

Before Migration:
- [ ] All tests passing on current version
- [ ] Code committed and pushed
- [ ] Backup/snapshot created if applicable
- [ ] Rollback plan documented
- [ ] Team notified of planned changes

During Migration:
- [ ] Update dependencies/version to target
- [ ] Fix all compiler/linter errors
- [ ] Update imports/APIs that changed
- [ ] Update configuration files
- [ ] Run unit tests after each logical change
- [ ] Commit regularly with clear messages

After Migration:
- [ ] Full test suite passing
- [ ] Integration tests passing
- [ ] Performance benchmarks (if applicable)
- [ ] Code review approval
- [ ] Documentation updated
- [ ] Team walkthrough of changes
```

Post the checklist where you can reference it—you'll check off items as you proceed.

### Step 4: Execute Migration in Logical Stages

Migrate one logical unit at a time, not everything at once:

1. **Identify logical units**: Separate modules, features, or integration points that can be updated independently
2. **Start with least critical**: Begin with utilities or internal-only code, end with public APIs or critical paths
3. **One stage per commit**: Each logical unit = one or more related commits
4. **Test after each stage**: Run tests immediately after updating each unit
5. **Resolve issues immediately**: Don't accumulate failures—fix blockers before moving to next stage

Example for framework upgrade (old → new):
- Stage 1: Update build config and dependencies only (no code changes yet)
- Stage 2: Update imports and basic API calls in utility layer
- Stage 3: Update service layer
- Stage 4: Update API/route layer
- Stage 5: Update tests to new patterns
- Stage 6: Remove old imports and deprecated APIs

### Step 5: Verify No Regressions

After migration is complete:

1. **Run full test suite**: All unit tests must pass with good coverage
2. **Run integration tests**: Multi-component tests must pass
3. **Manual testing**: Walk through critical user flows manually in a test environment
4. **Performance baseline**: If migration could affect performance, measure and compare
5. **Lint/type checking**: Ensure no new style violations or type errors introduced

If tests fail, don't push forward—identify the root cause and fix it. Tests are your safety net.

### Step 6: Document and Communicate

Record what changed and why:

- **Migration guide**: Step-by-step for any manual changes others need to make
- **Breaking changes**: List anything that will require code changes from users/downstream services
- **API changes**: Document deprecated APIs, new patterns, renames
- **Configuration changes**: What config values changed or are no longer supported
- **Performance notes**: Did migration improve or regress performance?

Share with team in writing (not just verbal) so there's a record.

### Step 7: Monitor and Support Rollback

If something goes wrong after deployment:

1. **Have rollback command ready**: Git revert, version downgrade, config change—know exactly what to run
2. **Monitor for issues**: Watch logs and metrics immediately after deploying
3. **Be ready to execute rollback**: If critical issues appear, execute rollback procedure immediately
4. **Document what failed**: Record the failure mode so you can prevent it next time

Keep communication going with your team about health of the migration.