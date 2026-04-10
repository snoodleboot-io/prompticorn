---
languages: ["python", "typescript", "javascript"]
subagents: ["review", "code"]
---

# House Style Enforcement Workflow (Minimal)

## 1. Define House Style
Document project-specific conventions:
- File and folder naming (snake_case, kebab-case, PascalCase)
- Import ordering and grouping
- Error handling patterns (exceptions vs Result types)
- Async patterns (promises, async/await)
- Comment style and when to comment
- Test organization and naming

## 2. Read Existing Code
Before writing new code in unfamiliar module:
```bash
# Find similar files
find src/services/ -name "*.py" | head -3 | xargs cat

# Check for patterns
grep -r "def __init__" src/models/
```
- Note naming patterns
- Note structure (class vs functional)
- Note error handling approach

## 3. Configure Automated Tools
Set up linters and formatters:
```bash
# Python
pip install ruff pyright
# Configure in pyproject.toml

# TypeScript/JavaScript
npm install -D eslint prettier
# Configure in .eslintrc.json, .prettierrc
```

## 4. Run Linters on Pre-Commit
Install Git hooks:
```bash
# Using pre-commit framework
pip install pre-commit
pre-commit install

# Manual hook (.git/hooks/pre-commit)
#!/bin/bash
ruff check src/
pyright src/
```

## 5. Enforce in CI
Add linting step to CI pipeline:
```yaml
# .github/workflows/lint.yml
- name: Run linter
  run: ruff check src/ --exit-non-zero-on-fix

- name: Run type checker
  run: pyright src/
```

## 6. Audit Code for Style Violations
When reviewing code:
- Check against Core Conventions
- Check against observed patterns in codebase
- Flag deviations: MUST FIX vs NIT (minor preference)
- Suggest consistent alternative

## 7. Document House Style Guide
Create STYLE_GUIDE.md:
```markdown
# Project Code Style

## File Naming
- Python: snake_case (user_service.py)
- TypeScript: PascalCase (UserService.ts)

## Import Order
1. Standard library
2. Third-party
3. Local imports
(Blank line between groups)

## Error Handling
Use exceptions, not Result types.
Never swallow errors without logging.
```
