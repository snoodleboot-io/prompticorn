---
name: dependency-upgrade
description: Safely upgrade project dependencies with minimal risk
languages: [python, typescript, go, rust]
subagents: [migration, test]
steps:
  - Check available versions and breaking changes
  - Update dependency manifest/lock file
  - Run install to fetch new versions
  - Execute full test suite
  - Fix any compatibility issues
  - Create commit documenting the upgrade
---

## Steps

### Step 1: Check available versions and breaking changes

Review what versions are available for your dependency.

**For Python (uv):**
```bash
uv pip list --outdated
uv pip compile --upgrade-package <package-name>
```

**For TypeScript (npm/pnpm):**
```bash
npm outdated
npm view <package-name> versions
```

**For Go:**
```bash
go list -u -m all
```

Check the dependency's changelog/release notes for breaking changes before upgrading.

### Step 2: Update dependency manifest/lock file

Modify your dependency declaration to the new version.

**Python:** Update `pyproject.toml` version constraint
**TypeScript:** Update `package.json` version constraint
**Go:** Update `go.mod` version

Use conservative version constraints:
- Patch updates: `^1.2.3` (allows 1.2.x)
- Minor updates: `^1.2.0` (allows 1.x.x)
- Major updates: Explicit version (requires review)

### Step 3: Run install to fetch new versions

Install dependencies with the updated constraints.

```bash
# Python
uv sync

# TypeScript
npm install
# or
pnpm install

# Go
go get -u ./...
```

### Step 4: Execute full test suite

Run all tests to catch compatibility issues early.

```bash
# Python
pytest --cov

# TypeScript
npm test -- --coverage

# Go
go test ./...
```

All tests must pass before proceeding.

### Step 5: Fix any compatibility issues

If tests fail, identify which APIs changed in the new version.

**Typical issues:**
- Renamed functions or classes
- Changed function signatures (parameter reordering, new required params)
- Removed deprecated features
- Changed return types
- New validation rules

Consult the dependency's migration guide and apply necessary code changes.

### Step 6: Create commit documenting the upgrade

Write a clear commit message following Conventional Commits.

```
chore(deps): upgrade <dependency-name> from X.Y.Z to A.B.C

- Updated <dependency-name> to A.B.C
- Fixed compatibility issue in <file.ext>
- All tests passing with updated version
```

Include link to release notes if breaking changes required code updates.

