---
name: "dependency-upgrade"
description: Comprehensive process for safe dependency upgrades with breaking change detection and rollback procedures
languages: [python, typescript, go, rust, java]
subagents: [migration, test, security]
steps:
  - Assess current state and dependency impact analysis
  - Check available versions and analyze breaking changes
  - Plan upgrade strategy based on semver and risk assessment
  - Update dependency declarations with appropriate constraints
  - Run dependency install and verify lock file changes
  - Execute comprehensive test suite with coverage validation
  - Fix compatibility issues with systematic approach
  - Verify functionality with manual testing if needed
  - Commit upgrade with detailed documentation
  - Document any follow-up work or known issues
---

## Steps

### Step 1: Assess current state and dependency impact analysis

Before upgrading, understand where the dependency is used and its criticality.

**Gather Information:**

1. **Find all usages:**
   ```bash
   # Python
   grep -r "from <package>" --include="*.py" | head -20
   grep -r "import <package>" --include="*.py" | head -20
   
   # TypeScript
   grep -r "from '<package>'" --include="*.ts" --include="*.tsx" | head -20
   grep -r "require('<package>')" --include="*.ts" | head -20
   
   # Go
   grep -r "<package>" --include="*.go" | head -20
   ```

2. **Assess criticality:**
   - Is this in the hot path (performance critical)?
   - Does this handle security-sensitive operations?
   - Is this a core dependency or peripheral?
   - How many files import this?

3. **Review current version:**
   ```bash
   # Python
   uv pip show <package-name>
   
   # TypeScript
   npm list <package-name>
   
   # Go
   go list -m <package-name>
   ```

4. **Create branch for upgrade:**
   ```bash
   git checkout -b chore/upgrade-<package-name>-x-y-z
   ```

### Step 2: Check available versions and analyze breaking changes

Determine what versions are available and what changed between current and target version.

**Research Available Versions:**

```bash
# Python
uv pip index versions <package-name>

# TypeScript
npm view <package-name> versions --json

# Go
go list -m -versions <package-name>

# Rust
cargo search <package-name> --limit 1
```

**Analyze Release Notes:**

For each version between current and target:
1. Read the CHANGELOG or release notes
2. Identify sections: Breaking Changes, Deprecations, New Features, Fixes
3. Search for your package's usages in the release notes

**Breaking Change Detection:**

Look for:
- **API removals:** Functions, classes, or modules deleted
- **Signature changes:** Parameters added/removed/reordered
- **Default behavior changes:** Previously implicit behavior now explicit
- **Renamed items:** Old API names changed
- **Type changes:** Return types or parameter types changed
- **Deprecated features being removed:** Features marked as deprecated are now gone

### Step 3: Plan upgrade strategy based on semver and risk assessment

Decide how to approach the upgrade based on breaking change severity.

**Semver Strategy:**

**Patch (1.2.3 → 1.2.4) - No breaking changes**
- Safe to upgrade automatically
- Update version constraint
- Run tests, commit and deploy

**Minor (1.2.3 → 1.3.0) - New features, no breaking changes**
- Safe to upgrade
- Update constraint to `^1.3.0`
- Run tests, may need code updates for new features

**Major (1.2.3 → 2.0.0) - Breaking changes expected**
- Need careful analysis before upgrading
- Create detailed change plan
- Estimate effort to fix compatibility issues

**Risk Assessment:**

| Factor | Low Risk | Medium Risk | High Risk |
|--------|----------|-------------|-----------|
| Files affected | 1-2 | 3-5 | 6+ |
| Location | Peripheral | Business logic | Hot path/security |
| Breaking changes | 0 | 1-3 | 4+ |
| Test coverage | >90% | 80-90% | <80% |

**Decision Tree:**

- Low risk patch/minor? → Upgrade immediately
- Medium risk minor? → Upgrade with careful testing
- Medium/High risk major? → Plan specific changes carefully
- Complex major with tight timeline? → Consider waiting for next release cycle

### Step 4: Update dependency declarations with appropriate constraints

Update your manifest file(s) with the new version and appropriate constraints.

**Python Version Constraints:**

```toml
# pyproject.toml
package = "^1.2.3"    # Allow patches and minor versions
package = "^1.2.0"    # Allow all 1.x versions
package = "2.0.0"     # Exact version (for major upgrades)
```

**TypeScript Version Constraints:**

```json
{
  "dependencies": {
    "package": "^1.2.3",
    "another": "~1.2.3",
    "third": "1.2.3"
  }
}
```

- `^1.2.3` - Allow changes that don't modify left-most non-zero digit
- `~1.2.3` - Allow patch updates only
- `1.2.3` - Exact version (safest for breaking changes)

**Go and Rust:**

Go uses exact versions in `go.mod`. Rust uses semver in `Cargo.toml`.

### Step 5: Run dependency install and verify lock file changes

Install the new dependency and verify lock file changes are reasonable.

**Install Step:**

```bash
# Python
uv sync

# TypeScript
npm install

# Go
go get -u ./...

# Rust
cargo update --package <package-name>
```

**Verify Lock File Changes:**

```bash
git diff package-lock.json
# or
git diff uv.lock
# or
git diff go.sum
```

**What to check:**
1. **Target dependency updated?** Version changed to what you specified
2. **Transitional dependencies reasonable?** Indirect dependencies didn't explode
3. **Duplicate dependencies avoided?** No two versions of same package
4. **Security issues?** Watch for security warnings

### Step 6: Execute comprehensive test suite with coverage validation

Run all tests to catch compatibility issues. Measure coverage to ensure tests are effective.

**Run Full Test Suite:**

```bash
# Python
pytest --cov=promptosaurus --cov-report=html

# TypeScript
npm test -- --coverage

# Go
go test ./... -cover
```

**Validate Coverage Targets:**

Coverage should meet or exceed:
- Line coverage: >80%
- Branch coverage: >70%
- Function coverage: >85%

**Test Categories to Verify:**

1. **Unit tests** - Fast, isolated tests of individual functions
2. **Integration tests** - Multi-component tests at service boundaries
3. **API contract tests** - If exposed as library, test public API
4. **Performance tests** - If dependency affects performance

**Handling Test Failures:**

If tests fail:
1. Note which tests failed and why
2. Check if failure is due to actual code problem or environment issue
3. Don't skip/ignore failing tests - understand root cause first
4. Move to Step 7 (Fix compatibility issues)

### Step 7: Fix compatibility issues with systematic approach

Address any breaking changes methodically.

**Identify Affected Code:**

```bash
# Find all calls to old signature
grep -r "library.old_function(" --include="*.py" src/
```

**Fix Patterns:**

**Pattern 1: Function Renamed**
```python
# OLD
from old_package import old_function

# NEW
from new_package import new_function
```

**Pattern 2: Parameter Added**
```python
# OLD
library.request(url)

# NEW
library.request(url, timeout=30)  # timeout now required
```

**Pattern 3: Return Type Changed**
```python
# OLD
users = library.get_users()  # returned list

# NEW
users = list(library.get_users())  # now returns iterator
```

**Pattern 4: Behavior Changed**
```python
# OLD
library.sort(data)  # sorted in-place

# NEW
sorted_data = library.sort(data)  # returns new list
```

**Fixing Strategy:**

1. **Run one failing test:**
   ```bash
   pytest tests/unit/auth/test_jwt_validator.py::test_specific_case -v
   ```

2. **Read error message carefully** - identify what changed
3. **Find all occurrences** of the old pattern
4. **Apply fix consistently** across all files
5. **Re-run test** to verify fix works
6. **Move to next failing test**

### Step 8: Verify functionality with manual testing if needed

Beyond automated tests, verify critical functionality works end-to-end.

**Determine if manual testing is needed:**
- ✓ Upgrade touches core authentication flow
- ✓ Dependency handles payments or security-sensitive data
- ✓ Changes involve database migrations
- ✓ Performance-critical dependency with significant version jump

**Manual Testing Checklist:**

For authentication library upgrade:
- [ ] Can create new user account
- [ ] Can log in with existing credentials
- [ ] Session tokens are valid
- [ ] Logout properly invalidates sessions
- [ ] Expired tokens are rejected
- [ ] CORS/CSRF protections still work

For database library upgrade:
- [ ] Can connect to database
- [ ] Can query data
- [ ] Transactions roll back on error
- [ ] Connection pooling works under load
- [ ] Concurrent queries don't deadlock

### Step 9: Commit upgrade with detailed documentation

Create a commit that documents the upgrade thoroughly for future developers.

**Commit Message Format:**

```
chore(deps): upgrade <package-name> from X.Y.Z to A.B.C

## Summary
<Brief description of why this upgrade was needed>

## Changes
- Updated <package-name> to A.B.C
- Fixed <N> compatibility issues related to API changes
- Updated <number> call sites with new function signatures

## Breaking Changes (from dependency perspective):
- Function `old_api()` removed, replaced with `new_api()`
- ClassA signature changed - now requires `new_param`

## Testing
- All 340 unit tests passing
- All 15 integration tests passing
- Coverage: 92% (target: 80%)
- Manual testing of auth flow: ✓ Passed

## Related Issues
Closes: #1234 (dependency security update)

## Notes
- Previous version had 3 known security vulnerabilities (fixed)
- New version requires Python 3.11+ (we already require 3.12+, compatible)
- No performance degradation observed
```

**Commit Best Practices:**

- Keep dependency updates in their own commit (don't mix with feature work)
- Include reference to breaking changes if major version bump
- Link to release notes in commit for future reference
- Document any manual changes required
- Note if this unblocks other work

### Step 10: Document any follow-up work or known issues

Record anything that needs attention after the upgrade.

**Create follow-up tasks for:**

- Performance monitoring needed for dependency with algorithm changes
- Documentation updates if API surface changed
- Upgrade of other packages that depend on this one
- Testing of edge cases not covered by unit tests
- Monitoring of production behavior after deployment

**Document Migration Issues:**

```markdown
# Migration Guide: <package-name> X.Y.Z → A.B.C

## Breaking Changes

### Removed: `library.old_function()`
**What:** This function was removed without replacement
**Impact:** Our code in `src/auth/handler.py` used this function
**Fix:** Replaced with new `library.new_function()` - see line 45

### Changed: `library.ClassA.__init__()`
**What:** Added required parameter `format: str`
**Impact:** All instantiations of ClassA must pass format parameter
**Fix:** Updated 3 instantiation sites to pass `format='json'`

## Migration Checklist

- [x] Upgraded package to A.B.C
- [x] Updated pyproject.toml
- [x] All unit tests passing
- [x] All integration tests passing
- [x] Fixed 2 compatibility issues
- [x] Manual testing completed
- [ ] Deploy to staging (ready for next release)
- [ ] Monitor performance in production

## Performance Impact

- Query performance: +2% improvement
- Memory usage: No change
- Startup time: No change

## Rollback Plan

If critical issues found in production:

```bash
git revert <commit-hash>
# OR
git checkout <old-commit> -- pyproject.toml uv.lock
uv sync
```

Then deploy immediately.
```

---

## Common Pitfalls & How to Avoid Them

### ❌ Pitfall 1: Skipping Test Run
**Solution:** Always run full test suite before committing

### ❌ Pitfall 2: Upgrading Multiple Major Dependencies at Once
**Solution:** Upgrade one at a time, commit separately

### ❌ Pitfall 3: Ignoring Release Notes
**Solution:** Always read CHANGELOG and breaking changes first

### ❌ Pitfall 4: Using Overly Permissive Version Constraints
**Solution:** Use caret `^` or tilde `~` to constrain major version bumps

### ❌ Pitfall 5: Not Testing Critical Paths Manually
**Solution:** Manually test critical flows (auth, payments, core features)

### ❌ Pitfall 6: Forgetting to Update Documentation
**Solution:** Update docs/comments whenever APIs change

### ❌ Pitfall 7: Assuming Same Version Works Across Monorepo
**Solution:** Use dependency locking, audit all services use consistent versions

---

## Automation Options

### Dependabot (GitHub)
Automatically creates pull requests for dependency updates.

### Renovate (Alternative)
More flexible alternative with group updates and auto-merge options.

### CI Integration
Add dependency security scanning:
```bash
uv pip check        # Python
npm audit           # TypeScript
cargo audit         # Rust
```

