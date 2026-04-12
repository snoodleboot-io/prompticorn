# Dependency Update Workflow

**Version:** 1.0  
**Cadence:** Weekly (Monday)  
**Owner:** Engineering Team  
**Status:** Active

---

## Quick Reference

### Weekly Dependency Check
```bash
cd /home/john_aven/Documents/software/promptosaurus
uv pip list --outdated
uv pip compile pyproject.toml --dry-run
```

### Monthly Security Audit
```bash
pip-audit  # Check for known vulnerabilities
```

### Update Command
```bash
# Update all dependencies
uv sync --upgrade

# Test after update
pytest --cov

# If tests pass: commit changes
git add pyproject.toml uv.lock
git commit -m "chore(deps): Update dependencies [automated]"
```

---

## Monthly Scheduled Update (First Monday of Month)

**Timeline:** 2 hours

1. **Check outdated packages** (5 min)
   - Run: `uv pip list --outdated`
   - Identify major vs minor updates
   - Flag breaking changes (major version bumps)

2. **Update dependencies** (10 min)
   - Run: `uv sync --upgrade`
   - Review lock file changes

3. **Run test suite** (20 min)
   - Full: `pytest --cov` (should complete in ~20 sec)
   - If failures: investigate, may need code changes
   - Check coverage hasn't dropped

4. **Security audit** (5 min)
   - Run: `pip-audit`
   - Flag any CVEs in dependencies

5. **Commit and document** (10 min)
   - Commit: `git commit -m "chore(deps): Monthly dependency update [automated]"`
   - Update MAINTENANCE_LOG.md with summary
   - Log: # of packages updated, vulnerabilities fixed

6. **Verify in CI** (5 min)
   - Push to main
   - Wait for GitHub Actions to pass
   - Confirm all workflows green

---

## Weekly Security Check (Every Wednesday)

**Timeline:** 15 minutes

```bash
# Check for vulnerabilities
pip-audit --desc

# If vulnerabilities found:
# 1. Update the vulnerable package
# 2. Rerun tests
# 3. Commit immediately
# 4. Alert team if critical
```

---

## Decision Tree

**Does update have breaking changes?**
- NO: Apply it immediately
- YES: Create PR for review, test thoroughly

**Do tests fail after update?**
- NO: Proceed to CI verification
- YES: Investigate, may need code changes or dependency constraint

**Are new vulnerabilities detected?**
- NO: Continue normal workflow
- YES: Prioritize patching (P0 if critical, P1 if high)

---

## Rollback Procedure

If update breaks something:
```bash
# Revert lock file
git checkout HEAD~1 uv.lock pyproject.toml

# Reinstall previous versions
uv sync

# Verify tests pass
pytest

# Commit rollback with explanation
git commit -m "chore(deps): Revert update to X due to breaking changes

- Specific issue encountered
- Need to evaluate alternative approach"
```

---

## Troubleshooting

**Issue:** Tests fail after update
- Check git diff for actual code changes needed
- Some updates require code migration (e.g., API changes)
- Revert and check changelog if issue unclear

**Issue:** Security tool shows CVE but package says resolved
- Verify CVE date vs package release date
- May be false positive or tool lag
- Check GitHub security advisory

**Issue:** Update blocked by version conflict
- Use `uv pip show [package]` to see dependency tree
- May need to constrain version of other package
- Document constraint and reason in code comment

