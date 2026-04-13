---
name: code-quality-maintenance
type: workflow
category: workflow-patterns
minimal: true
---
# Code Quality Workflow

**Version:** 1.0

### Pre-Commit Checks (Automated)

```bash
# All of these run automatically on git commit
# (hooks configured in .git/hooks/pre-commit)

# 1. Formatting
ruff format .

# 2. Linting
ruff check . --fix

# 3. Type checking
pyright .

# 4. Test execution
pytest -q
```

### Manual PR Review Checklist

- [ ] Code follows naming conventions (snake_case, PascalCase)
- [ ] No hardcoded secrets or constants (use config)
- [ ] Tests added or updated
- [ ] Coverage hasn't dropped
- [ ] Docstrings on public functions
- [ ] No console.log or print statements (except logging)
- [ ] Error handling is explicit
- [ ] Code follows existing patterns
- [ ] No type: ignore without explanation
- [ ] Documentation updated