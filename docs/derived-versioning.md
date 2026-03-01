# Derived Versioning for Trunk-Based Development

## Overview

This project uses a **derived versioning** approach specifically designed for trunk-based development workflows. The version is **derived directly from git merge history** at build time.

## Version Schema

```
MAJOR.MINOR.PATCH
```

| Component | Source | Meaning |
|-----------|--------|---------|
| **MAJOR** | Hardcoded in CI/CD workflow | Breaking changes requiring user action |
| **MINOR** | System-derived (count of `feat/` merges) | New features, backwards compatible |
| **PATCH** | System-derived (count of fixes since last feature) | Bug fixes, security patches |

## Branch Naming Conventions

The version calculator recognizes these branch prefixes:

| Prefix | Type | Version Impact |
|--------|------|----------------|
| `feat/` or `feature/` | Feature | Increments MINOR (resets PATCH to 0) |
| `bug/` or `fix/` | Bug fix | Increments PATCH |
| `hotfix/` | Hot fix | Increments PATCH (priority) |
| `security/` | Security patch | Increments PATCH (priority) |
| (other) | Other | No version impact |

## How It Works

### 1. Version Calculation

When a branch merges to `main`, the CI/CD pipeline:

1. Reads the hardcoded **major** version from workflow env (`MAJOR_VERSION`)
2. Counts ALL `feat/` branches ever merged to main → **minor**
3. Counts `bug/`/`hotfix/`/`security/` branches merged since the LAST `feat/` → **patch**
4. Publishes with that version

### 2. Example Workflow

```
main: (start)
      │
      ├── feat/auth → merged → v0.1.0 (published)
      │
      ├── feat/api  → merged → v0.2.0 (published)
      │
      ├── bug/fix-typo → merged → v0.2.1 (published)
      │
      └── hotfix/memory-leak → merged → v0.2.2 (published)
```

### 3. Parallel Development

Multiple branches can be developed in parallel without conflicts:

```
feat/auth ──┐
            ├──→ merged independently → version calculated at merge time
feat/api  ──┘

No VERSION file conflicts because version is derived, not stored.
```

## Bumping Major Version

When you need to make breaking changes:

1. Edit `.github/workflows/ci-cd.yml`
2. Change `MAJOR_VERSION: "0"` to the new major version (e.g., `"1"`)
3. Commit and push the workflow change
4. Subsequent merges will use the new major version

```yaml
env:
  PACKAGE_NAME: promptcli
  PYTHON_MIN_VERSION: "3.10"
  MAJOR_VERSION: "1"  # Changed from "0" to "1"
```

## Comparison: Traditional vs Derived

| Aspect | Traditional Semver | Derived Versioning |
|--------|-------------------|-------------------|
| **Version file** | `VERSION` or in `pyproject.toml` | None |
| **Merge conflicts** | Common on every PR | Never |
| **Parallel branches** | Requires coordination | Fully independent |
| **Prerelease tags** | `rc1`, `alpha`, `beta` | None needed |
| **Release tags** | Required for tracking | Not used |
| **Tag fragility** | Tags can be deleted/changed | Immune (history is immutable) |
| **Version meaning** | Often arbitrary | Directly maps to branch types |

## CI/CD Integration

### On Pull Request

- Version is calculated (clean semver like `2.3.1`)
- Package is built for verification only
- **NOT** published to PyPI

### On Merge to Main

- Version is calculated (e.g., `2.3.1`)
- Package is built and published to PyPI
- Version is embedded in the package itself

## FAQ

**Q: What happens if I forget the branch prefix?**
A: The merge won't affect version (reported as warning in CI). The next properly-named branch will version correctly.

**Q: Can I override the calculated version?**
A: No - the system is designed to be fully automated. The version reflects actual changes made.

**Q: What about cherry-picks?**
A: Cherry-picks don't create merge commits, so they don't affect version. Use proper hotfix branches instead.

**Q: How do I know what version is running?**
A: Check `pip show promptcli` or `prompt --version`. The version is in the package metadata.

**Q: Can I see version history?**
A: Use `git log --merges --oneline` to see what branches were merged when.

**Q: What if someone deletes or changes a tag?**
A: Irrelevant - we don't use tags. The version is derived from commit history which is immutable.
