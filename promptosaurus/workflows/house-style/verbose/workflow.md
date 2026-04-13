---
name: house-style
languages: ["python", "typescript", "javascript"]
subagents: ["review", "code"]
---

# House Style Enforcement Workflow (Comprehensive)

## Overview

House style refers to project-specific coding conventions beyond language standards. It ensures consistency across the codebase, making code easier to read, review, and maintain.

**House style covers:**
- Naming conventions (files, classes, functions, variables)
- Code organization (imports, exports, file structure)
- Error handling patterns
- Async/await usage
- Comment style
- Test organization

**Benefits:**
- Faster code review (focus on logic, not style)
- Easier onboarding (consistent patterns)
- Reduced cognitive load (code looks familiar)
- Better tooling (linters can enforce rules)

---

## Phase 1: Define House Style

### 1.1 Learn from Existing Code

**Before defining new rules, read existing code:**

```bash
# Find most common file types
find src/ -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn

# Sample files from each major module
ls src/services/*.py | head -3 | xargs cat
ls src/controllers/*.py | head -3 | xargs cat
ls src/models/*.py | head -3 | xargs cat
```

**Look for patterns:**
- How are files named? (snake_case, PascalCase, kebab-case)
- How are imports organized?
- How are errors handled? (exceptions, Result types, error codes)
- How are classes structured? (properties, methods, decorators)
- How are tests organized? (one file per module, grouped by feature)

### 1.2 Document Naming Conventions

**File naming:**
```markdown
## File Naming

**Python:**
- Modules: snake_case (user_service.py)
- Packages: snake_case (auth_module/)
- Tests: test_<module>.py (test_user_service.py)

**TypeScript:**
- Components: PascalCase (UserProfile.tsx)
- Services: PascalCase (UserService.ts)
- Utilities: camelCase (formatDate.ts)
- Tests: <module>.spec.ts (UserService.spec.ts)

**JavaScript:**
- Files: kebab-case (user-service.js)
- Tests: <module>.test.js (user-service.test.js)
```

**Class and function naming:**
```markdown
## Naming Conventions

**Classes:** PascalCase
- UserController
- ProductService
- OrderModel

**Functions:** snake_case (Python) or camelCase (TypeScript)
- Python: get_user_by_id()
- TypeScript: getUserById()

**Constants:** UPPER_SNAKE_CASE
- MAX_RETRY_ATTEMPTS
- DEFAULT_TIMEOUT

**Private methods:**
- Python: _internal_method()
- TypeScript: private internalMethod()
```

### 1.3 Define Import Organization

**Python import style:**
```python
# Standard library imports
import os
import sys
from typing import Optional, List

# Third-party imports
import requests
from fastapi import APIRouter, Depends

# Local application imports
from app.models import User
from app.services import UserService
from app.utils import validate_email

# Blank lines between groups
# Sorted alphabetically within each group
```

**TypeScript import style:**
```typescript
// External libraries
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import * as bcrypt from 'bcrypt';

// Internal modules
import { User } from '../entities/user.entity';
import { UserService } from '../services/user.service';
import { validateEmail } from '../utils/validation';

// Type imports (separate if using type-only imports)
import type { CreateUserDto } from '../dto/user.dto';
```

### 1.4 Error Handling Patterns

**Define project-wide error handling:**

**Option 1: Exceptions (Python, TypeScript)**
```python
# House rule: Use exceptions for error handling
class UserNotFoundError(Exception):
    """Raised when user does not exist."""
    pass

def get_user(user_id: int) -> User:
    user = db.query(User).get(user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
    return user
```

**Option 2: Result types (TypeScript/Rust style)**
```typescript
// House rule: Use Result<T, E> for error handling
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function getUser(userId: number): Result<User, UserNotFoundError> {
  const user = db.findOne(userId);
  if (!user) {
    return { ok: false, error: new UserNotFoundError(`User ${userId} not found`) };
  }
  return { ok: true, value: user };
}
```

**Document which pattern your project uses:**
```markdown
## Error Handling

**Pattern:** Exceptions (not Result types)

**Rules:**
1. Use typed exceptions (UserNotFoundError, ValidationError)
2. Never swallow errors silently (always log or re-raise)
3. Include context in error messages (user ID, operation)
4. Handle errors at boundaries (controllers, not services)
```

### 1.5 Async Patterns

**Document async/await usage:**

**Python async style:**
```markdown
## Async/Await

**When to use async:**
- I/O-bound operations (database, HTTP, file system)
- NOT for CPU-bound operations (use threading/multiprocessing)

**Rules:**
1. Always await async functions
2. Never use time.sleep() in async code (use asyncio.sleep())
3. Use async context managers for resources
4. Group async operations with asyncio.gather()

**Example:**
```python
async def fetch_users() -> List[User]:
    async with database_connection() as conn:
        results = await conn.fetch("SELECT * FROM users")
        return [User(**row) for row in results]
```

**TypeScript async style:**
```markdown
## Async/Await

**When to use async:**
- API calls, database queries, file I/O

**Rules:**
1. Prefer async/await over raw Promises
2. Always await async functions (no floating promises)
3. Use Promise.all() for parallel operations
4. Handle errors with try/catch

**Example:**
```typescript
async function fetchUsers(): Promise<User[]> {
  try {
    const response = await fetch('/api/users');
    return await response.json();
  } catch (error) {
    logger.error('Failed to fetch users', error);
    throw new UserFetchError('Could not fetch users');
  }
}
```

### 1.6 Comment Style

**Define when and how to comment:**

```markdown
## Comment Style

**When to comment:**
- WHY something is done (not WHAT)
- Non-obvious decisions or trade-offs
- Workarounds and TODOs
- Public APIs (docstrings)

**When NOT to comment:**
- Self-explanatory code
- Restating what code does

**Examples:**

✓ Good:
```python
# Intentionally not awaited — fire and forget analytics event
asyncio.create_task(track_event(user_id, "login"))

# TODO: Refactor to use background queue (PROJ-123)
send_email(user.email, "Welcome!")

# Query optimized for read-heavy workload (90% reads, 10% writes)
result = await db.execute(query.with_hint("use_index(idx_user_email)"))
```

✗ Bad:
```python
# Get user from database
user = db.get(user_id)

# Loop through users
for user in users:
    # Print user name
    print(user.name)
```

---

## Phase 2: Automated Enforcement

### 2.1 Configure Linters

**Python (Ruff + Pyright):**

**pyproject.toml:**
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort (import sorting)
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["app"]
section-order = ["future", "standard-library", "third-party", "first-party", "local-folder"]

[tool.pyright]
typeCheckingMode = "strict"
reportMissingTypeStubs = false
pythonVersion = "3.11"
```

**Run linter:**
```bash
# Check for violations
ruff check src/

# Auto-fix violations
ruff check src/ --fix

# Format code
ruff format src/

# Type check
pyright src/
```

**TypeScript/JavaScript (ESLint + Prettier):**

**.eslintrc.json:**
```json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "project": "./tsconfig.json"
  },
  "rules": {
    "@typescript-eslint/explicit-function-return-type": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-floating-promises": "error",
    "no-console": "warn",
    "prefer-const": "error"
  }
}
```

**.prettierrc:**
```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "printWidth": 100,
  "trailingComma": "es5"
}
```

**Run linter:**
```bash
# Check for violations
npm run lint

# Auto-fix
npm run lint -- --fix

# Format code
npm run format
```

### 2.2 Pre-Commit Hooks

**Install pre-commit framework:**

**Python (.pre-commit-config.yaml):**
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

**Install:**
```bash
pip install pre-commit
pre-commit install
```

**JavaScript/TypeScript (.husky/pre-commit):**
```bash
#!/bin/bash
npm run lint
npm run type-check
npm run test:quick
```

**Install:**
```bash
npm install -D husky
npx husky install
npx husky add .husky/pre-commit "npm run lint"
```

### 2.3 CI Integration

**GitHub Actions workflow:**

```yaml
# .github/workflows/lint.yml

on: [push, pull_request]

jobs:
  python-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install ruff pyright
      
      - name: Run Ruff
        run: ruff check src/ --exit-non-zero-on-fix
      
      - name: Run Pyright
        run: pyright src/
  
  typescript-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run ESLint
        run: npm run lint
      
      - name: Run TypeScript compiler
        run: npm run type-check
```

---

## Phase 3: Manual Code Review

### 3.1 Style Audit Process

**When reviewing code:**

1. **Automated checks first:**
   - Run linter, formatter, type checker
   - Fix all automated violations before manual review

2. **Manual review for patterns:**
   - Does file naming match convention?
   - Are imports organized correctly?
   - Does error handling match project pattern?
   - Are comments useful (WHY not WHAT)?

3. **Classify violations:**

**MUST FIX (blocking):**
- Breaks project conventions (will confuse maintainers)
- Type safety violations (any, missing types)
- Incorrect error handling pattern
- Security issues

**NIT (non-blocking):**
- Minor naming preferences
- Comment wording
- Overly verbose code (still correct)

**Example review comments:**

```markdown
## MUST FIX

**src/services/user_service.py:15**
File should be named `user_service.py` not `UserService.py`.
Our Python convention is snake_case for files (see STYLE_GUIDE.md).

**src/controllers/auth.ts:42**
Missing return type annotation.
```typescript
// Current
async login(credentials) {
  ...
}

// Required
async login(credentials: LoginDto): Promise<AuthResponse> {
  ...
}
```

## NIT

**src/utils/format.py:23**
This comment restates what the code does.
```python
# Loop through users (← remove this)
for user in users:
    ...
```
```

### 3.2 Spotting Inconsistencies

**Compare new code to existing code:**

**Example: Import order inconsistency**

**Existing files:**
```python
# src/services/product_service.py
from typing import List
import requests
from app.models import Product
```

**New file:**
```python
# src/services/order_service.py
from app.models import Order  # ← Wrong order!
import requests
from typing import List
```

**Review comment:**
```markdown
Import order doesn't match project convention. Should be:
1. Standard library (typing)
2. Third-party (requests)
3. Local (app.models)

See src/services/product_service.py for reference.
```

### 3.3 House Style Summary

**For new contributors, generate project-specific style guide:**

**Read 3-4 representative files:**
```bash
cat src/services/user_service.py
cat src/controllers/auth_controller.py
cat src/models/user.py
cat tests/unit/test_user_service.py
```

**Summarize observed patterns:**

```markdown
# {Project Name} Code Style Guide

## File Structure
```
src/
├── models/          # Data models (SQLAlchemy)
├── services/        # Business logic
├── controllers/     # HTTP request handlers
├── utils/           # Shared utilities
└── tests/
    ├── unit/
    └── integration/
```

## Naming
- Files: snake_case (user_service.py)
- Classes: PascalCase (UserService)
- Functions: snake_case (get_user_by_id)
- Constants: UPPER_SNAKE_CASE (MAX_RETRIES)

## Imports
Always in this order:
1. Standard library
2. Third-party
3. Local

Example:
```python
from typing import Optional
import requests
from app.models import User
```

## Error Handling
Use exceptions, not Result types.
- Define custom exceptions (UserNotFoundError)
- Include context in error messages
- Never swallow errors without logging

## Async
- Use async for I/O operations
- Always await async functions
- Never time.sleep() in async code (use asyncio.sleep())

## Tests
- One test file per module (test_user_service.py)
- Group tests by method (TestUserServiceGetById)
- Use descriptive test names (test_get_user_by_id_returns_user_when_found)

## Comments
- Comment WHY, not WHAT
- Use TODO for known issues (include ticket number)
- Use docstrings for public APIs
```

---

## Phase 4: Enforcement Strategy

### 4.1 Incremental Adoption

**For existing codebases with inconsistent style:**

**Option 1: File-by-file enforcement**
```bash
# Only run linter on changed files
git diff --name-only main | xargs ruff check
```

**Option 2: Module-by-module migration**
```bash
# Enforce on one module at a time
ruff check src/services/  # Start here
# Once clean, add to CI
# Then move to next module
```

**Option 3: New code only**
```yaml
# CI enforces style on new/changed files only
- name: Lint changed files
  run: |
    git diff --name-only origin/main... | grep '\.py$' | xargs ruff check
```

### 4.2 Team Education

**Onboarding checklist:**
- [ ] Read STYLE_GUIDE.md
- [ ] Install pre-commit hooks
- [ ] Configure editor with linter/formatter
- [ ] Review 2-3 example files
- [ ] Submit first PR and receive style feedback

**Editor configuration:**

**VS Code (settings.json):**
```json
{
  "editor.formatOnSave": true,
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff",
  "typescript.tsdk": "node_modules/typescript/lib",
  "eslint.autoFixOnSave": true
}
```

**PyCharm:**
- Settings → Tools → External Tools → Add Ruff
- Settings → Editor → Code Style → Python → Set line length to 100

### 4.3 Handling Exceptions

**When to break house style:**

**Valid reasons:**
1. External API compatibility (must match their naming)
2. Performance optimization (profiled, documented)
3. Framework convention (follows Next.js, Django patterns)

**How to document exceptions:**
```python
# house-style-exception: External API requires camelCase
def getUserById(userId: int) -> User:
    """Matches external UserService API naming."""
    ...
```

**Invalid reasons:**
1. "I prefer it this way"
2. "It's faster to write"
3. "The old code did it differently"

---

## Tools and Resources

**Linters:**
- Python: Ruff (ruff.rs), Pylint (pylint.org), Flake8 (flake8.pycqa.org)
- TypeScript/JavaScript: ESLint (eslint.org), TSLint (deprecated)
- Multi-language: EditorConfig (editorconfig.org)

**Formatters:**
- Python: Ruff Format, Black (black.readthedocs.io)
- TypeScript/JavaScript: Prettier (prettier.io)
- Go: gofmt (built-in)

**Type checkers:**
- Python: Pyright (microsoft.com/pyright), mypy (mypy-lang.org)
- TypeScript: tsc (built-in)

**Pre-commit frameworks:**
- pre-commit (pre-commit.com) - Multi-language
- Husky (typicode.github.io/husky) - JavaScript/TypeScript

**Style guides (for reference):**
- Google Style Guides: google.github.io/styleguide/
- Airbnb JavaScript Style Guide: github.com/airbnb/javascript
- PEP 8 (Python): peps.python.org/pep-0008/
