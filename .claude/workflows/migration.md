## Steps

### Step 1: Before making any changes:

Define the migration precisely, and build the safety net before touching anything.

**Scope it:**
- **What:** framework version, database schema, language version, architecture
  pattern, or third-party dependency
- **Why:** performance, security fix, feature enablement, deprecation deadline, or
  tech-debt reduction — a migration with no stated why will stall halfway
- **Affected areas:** every module, service, and feature impacted
- **Risk level:** low (isolated), medium (cross-cutting), high (critical path)

**Resolve the ambiguities that change the plan:**
- Does this break backward compatibility?
- What breaking changes does the target version document?
- Is there a deadline, and is rollback required after deployment?

**Build the safety net.** Identify or write tests covering the behaviour that must
not change — core functionality, integration contracts, data integrity, and the
edge cases (concurrency, race conditions) a migration disturbs. Write them *before*
the migration starts. Tests added afterwards encode the new behaviour, including
whatever it broke.

**Record the checklist:**
```
Before:  tests green · code pushed · backup taken · rollback documented · team notified
During:  bump version · fix errors · update changed APIs · update config · test each change
After:   full suite · integration tests · benchmarks · review · docs · walkthrough
```

### Step 2: Migration approach:

Migrate one logical unit at a time. A single large commit that touches everything
cannot be reviewed, bisected, or partially reverted.

1. **Identify units** that can move independently
2. **Start with the least critical** — utilities and internal code first, public
   APIs and critical paths last
3. **One unit per commit,** with a message naming the unit
4. **Test immediately after each unit,** not at the end
5. **Fix failures before continuing.** Accumulated breakage compounds until the
   cause is unidentifiable

Typical staging for a framework upgrade:

```
1. build config + dependencies only, no code changes
2. imports and basic API calls in the utility layer
3. service layer
4. API / route layer
5. tests moved to new patterns
6. remove deprecated APIs and old imports
```

Keep the old path working until the last stage. That is what makes every
intermediate commit independently revertible.

### Step 3: After migration:

Verify, then communicate.

**Verify:**
1. Full unit suite green, coverage not reduced
2. Integration tests green
3. Manual walkthrough of critical user flows in a test environment
4. Performance compared against the pre-migration baseline, where it could be affected
5. Lint and type checks clean — no new violations introduced

A failing test after migration is information, not an obstacle. Find the root cause;
do not adjust the test to match the new behaviour unless the behaviour change was
the intent.

**Communicate, in writing:**
- Migration guide for any manual steps others must take
- Breaking changes requiring downstream work
- Deprecated APIs, renames, and new patterns
- Configuration values changed or no longer supported
- Performance impact, in either direction

**Then stay ready to roll back:**
- Know the exact rollback command before deploying, not during the incident
- Watch logs and metrics immediately after deploy
- Execute rollback promptly on critical issues — diagnose afterwards
- Record what failed, so the next migration avoids it

### Step 4: Common migration scenarios:

**Framework or library major version.** Read the upgrade guide end to end first.
Expect the breaking changes list to be incomplete. Upgrade one major at a time;
skipping versions compounds unrelated breakages into one unintelligible failure.

**Database schema.** Use expand → migrate → contract: add the new column, dual-write
and backfill, switch reads, and only then drop the old column — as a separate,
later deploy. Never combine the drop with the change that stopped using it, or
rollback becomes impossible.

**Language version.** Upgrade the toolchain and CI first so failures surface in the
pipeline rather than on one developer's machine. Deprecation warnings are the
migration checklist for the version after next — fix them now while they are warnings.

**Dependency replacement.** Introduce the new dependency behind the existing
interface, migrate call sites incrementally, and remove the old one last. If no such
interface exists, creating one is the first migration step.

**Monolith to services.** Extract one bounded context at a time, keeping the
monolith's interface intact until the extracted service is proven under real load.
Move the data last — it is the step that cannot be quietly reverted.