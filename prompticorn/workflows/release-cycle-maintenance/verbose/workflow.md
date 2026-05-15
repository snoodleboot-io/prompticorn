# Release Cycle Workflow
name: "release-cycle-maintenance"

**Version:** 1.0  
**Cadence:** Monthly (Last Friday of Month)  
**Owner:** Release Manager / Engineering Lead  
**Status:** Active

---

## Quick Reference

### Monthly Release Checklist (3 hours)

**Week Before Release (Thursday)**
```bash
# Prepare release branch
git checkout main
git pull origin main
git checkout -b release/v[MAJOR].[MINOR].[PATCH]
```

**Release Day (Friday)**
```bash
# 1. Verify all tests pass
pytest --cov -q

# 2. Update version
# File: prompticorn/__init__.py
# Change: __version__ = "x.y.z"

# 3. Update changelog
# File: CHANGELOG.md
# Add new version section with commits

# 4. Create release tag
git tag -a v[VERSION] -m "Release v[VERSION]"

# 5. Push and create PR
git push origin release/v[VERSION]
# Create PR for review

# 6. After approval, merge to main
git checkout main && git pull
git merge --no-ff release/v[VERSION]
git push origin main

# 7. Create release on GitHub
gh release create v[VERSION] --generate-notes
```

---

## Release Preparation (1 week before)

### 1. Release Planning (1 hour)
**What's included in this release?**

```bash
# Get commits since last release
git log v[LAST-VERSION]..HEAD --oneline

# Categorize by type:
# - feat: New features
# - fix: Bug fixes
# - refactor: Code improvements
# - docs: Documentation
# - test: Test additions
```

**Determine version bump:**
- MAJOR (x.0.0): Breaking changes
- MINOR (0.x.0): New features, backward compatible
- PATCH (0.0.x): Bug fixes only

### 2. Testing (2 hours)
```bash
# Full test suite
pytest --cov -q

# Integration tests
pytest tests/integration/ -q

# Performance check
time pytest --cov -q
```

**Must pass:**
- All tests: 100% pass
- Coverage: >= 64% (maintain or improve)
- No new warnings

### 3. Documentation (1 hour)
- [ ] Update CHANGELOG.md
- [ ] Update README.md if needed
- [ ] Update docs if API changed
- [ ] Update RELEASE_NOTES.md

### 4. Code Review (2 hours)
```bash
# What's new since last release?
git log v[LAST-VERSION]..HEAD --stat

# Quality check
ruff check .
pyright .
```

---

## Release Day Workflow

### 1. Create Release Branch (10 min)
```bash
git checkout main
git pull origin main
git checkout -b release/v[MAJOR].[MINOR].[PATCH]
```

### 2. Update Version (10 min)
**File:** `prompticorn/__init__.py`
```python
__version__ = "2.2.0"  # Update this
```

**Commit:**
```bash
git add prompticorn/__init__.py
git commit -m "chore(release): Bump version to 2.2.0"
```

### 3. Update CHANGELOG (20 min)
**File:** `CHANGELOG.md`

Format:
```markdown
## [2.2.0] - 2026-04-12

### Added
- New feature X
- New feature Y

### Fixed
- Bug fix A
- Bug fix B

### Changed
- Improvement C
- Improvement D

### Removed
- Deprecated feature E

### Security
- Security fix F
```

**Commit:**
```bash
git add CHANGELOG.md
git commit -m "docs(changelog): Update for v2.2.0 release"
```

### 4. Tag Release (5 min)
```bash
git tag -a v2.2.0 -m "Release v2.2.0

See CHANGELOG.md for details."

# Verify tag
git tag -l v2.2.0 -n
```

### 5. Create PR (5 min)
```bash
git push origin release/v2.2.0

# Create PR: release/v2.2.0 → main
gh pr create --title "Release v2.2.0" \
  --body "$(cat <<EOF
## Release v2.2.0

See CHANGELOG.md for complete details.

- Test results: ✅ All passing
- Coverage: X%
- Breaking changes: None/List

### Checklist
- [ ] All tests passing
- [ ] Coverage maintained
- [ ] CHANGELOG updated
- [ ] Documentation updated
- [ ] Version bumped
EOF
)"
```

### 6. Code Review (30 min)
- Verify all changes are release-related
- Confirm tests still passing in CI
- Review changelog for accuracy

### 7. Merge to Main (10 min)
**After PR approved:**
```bash
git checkout main
git pull origin main
git merge --no-ff release/v2.2.0
git push origin main

# Delete release branch
git branch -d release/v2.2.0
git push origin --delete release/v2.2.0
```

### 8. Create GitHub Release (5 min)
```bash
# Create release with auto-generated notes
gh release create v2.2.0 --generate-notes

# Or with custom notes
gh release create v2.2.0 \
  --title "Version 2.2.0" \
  --notes "See CHANGELOG.md for details"
```

---

## Post-Release (Next Monday)

### Verify Release
```bash
# Confirm tag exists
git tag -l | grep v2.2.0

# Confirm it's published
gh release view v2.2.0

# Test installation (optional)
pip install prompticorn==2.2.0
```

### Create Next Development Cycle
```bash
# Create dev branch for next cycle
git checkout main
git pull origin main
git checkout -b feat/next-cycle

# Update version to next development version
# In __init__.py: __version__ = "2.3.0-dev"

git add prompticorn/__init__.py
git commit -m "chore(dev): Start development cycle for v2.3.0"
git push origin feat/next-cycle
```

---

## Release Notes Template

**File:** `RELEASE_NOTES_v2.2.0.md`

```markdown
# Release Notes v2.2.0

**Release Date:** April 12, 2026

## Summary
[1-2 sentence description of this release]

## What's New

### Features
- [Feature 1]: Description
- [Feature 2]: Description

### Improvements
- [Improvement 1]: Description
- [Improvement 2]: Description

### Bug Fixes
- [Bug 1]: Description
- [Bug 2]: Description

## Upgrade Guide

### From v2.1.x to v2.2.0

No breaking changes. Standard upgrade:
```bash
pip install --upgrade prompticorn
```

[If breaking changes, detailed upgrade guide here]

## Known Issues
- [Known issue 1]
- [Known issue 2]

## Deprecations
[Any deprecated features]

## Contributors
- @contributor1
- @contributor2

## Links
- [Full Changelog](CHANGELOG.md)
- [Issues/PRs](https://github.com/org/prompticorn)
```

---

## Decision Tree

**Any test failures found?**
- YES: Fix issues, create new commit, update CHANGELOG
- NO: Proceed to version bump

**Is this a breaking change?**
- YES: Bump MAJOR version, document migration
- NO: Bump MINOR (features) or PATCH (fixes)

**Coverage decreased since last release?**
- YES: Decision: block release or accept decline
- NO: Proceed to tag and release

**Multiple blockers found?**
- YES: Defer release to next cycle
- NO: Proceed to release

---

## Versioning Scheme

**Semantic Versioning:** MAJOR.MINOR.PATCH

- **MAJOR:** Breaking changes, major refactors
- **MINOR:** New features, backward compatible
- **PATCH:** Bug fixes, documentation, no feature changes

**Example progression:**
- v1.0.0 → v1.1.0 (new feature)
- v1.1.0 → v1.1.1 (bug fix)
- v1.1.1 → v2.0.0 (breaking change)

---

## Release Checklist

```markdown
# Release v[X.Y.Z] Checklist

- [ ] All tests passing
- [ ] Coverage >= 64% (maintain or improve)
- [ ] CHANGELOG.md updated
- [ ] Version number updated in __init__.py
- [ ] Release notes created
- [ ] No new deprecation warnings
- [ ] Documentation reviewed
- [ ] PR reviewed and approved
- [ ] Merged to main
- [ ] Tag created and pushed
- [ ] GitHub release created
- [ ] Published to PyPI (if applicable)
```

