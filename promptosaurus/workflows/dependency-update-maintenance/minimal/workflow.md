# Dependency Update Workflow
name: "dependency-update-maintenance"

**Version:** 1.0

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