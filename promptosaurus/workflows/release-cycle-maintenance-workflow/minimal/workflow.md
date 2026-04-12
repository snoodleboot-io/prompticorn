# Release Cycle Workflow

**Version:** 1.0

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
# File: promptosaurus/__init__.py
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