---
name: house-style
description: Code - house-style
mode: subagent
tools: [read, write]
workflows:
  - house-style-workflow
---

# Subagent - Code House Style

Check or enforce house style when writing code or auditing existing code.

## Goal

Ensure new code matches the established patterns in the codebase. House style is the collection of conventions, patterns, and idioms that this specific codebase follows — beyond what's in Core Conventions.

---

## Before Writing in Unfamiliar Module

**Never write code in an unfamiliar module without reading established patterns first.**

### Process:

1. **Read 2-3 existing files** from the same layer (API, service, model, etc.)
2. **Observe patterns:**
   - File naming conventions
   - Import ordering and grouping
   - Error handling approach
   - Async/await usage
   - Function/method organization
   - Comment style
3. **Match those patterns** in your new code

### Example: Observing Patterns

**Reading `services/user_service.py`, `services/order_service.py`, `services/payment_service.py`:**

Patterns observed:
- All service files use `snake_case` naming
- All services have a class with `Service` suffix (`UserService`, `OrderService`)
- All methods are async
- All methods log entry/exit at debug level
- All errors are raised as custom exception types from `exceptions/`
- All database queries use repository pattern (no direct ORM calls)
- All imports grouped: stdlib → third-party → local, separated by blank lines

**Now write new service matching this pattern:**

```python
# ✓ Matches observed pattern
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ProductNotFoundError
from app.repositories.product_repository import ProductRepository

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository
    
    async def get_product(self, product_id: str) -> Optional[Product]:
        logger.debug(f"Fetching product {product_id}")
        product = await self.repository.find_by_id(product_id)
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        logger.debug(f"Product {product_id} fetched successfully")
        return product
```

❌ **Bad (Doesn't Match Pattern):**

```python
# ❌ Doesn't match codebase patterns
from app.models import Product
import logging

def get_product(product_id):  # ❌ Not async, not a class
    # ❌ No debug logging
    # ❌ Direct ORM query instead of repository
    product = Product.query.filter_by(id=product_id).first()
    if not product:
        return None  # ❌ Returns None instead of raising custom exception
    return product
```

---

## When Auditing Code for Style

Check against **two sources:**
1. **Core Conventions** (universal rules)
2. **Codebase patterns** (house style)

### Report Format:

For each issue found, report:
- **Location:** file:line
- **Issue:** what doesn't match
- **Severity:** MUST FIX or NIT
- **Fix:** what to change

### Severity Levels:

**MUST FIX** - Will confuse maintainers or violates Core Conventions
- Breaks Core Conventions
- Inconsistent with 90%+ of similar code
- Makes code harder to understand

**NIT** - Minor preference, not critical
- Slightly different style but still readable
- Personal preference
- Doesn't affect maintainability

---

## Example Audit Report

### Code Being Audited: `api/routes/products.py`

```python
from fastapi import APIRouter
import logging
from app.services.product_service import ProductService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/products/{product_id}")
def get_product(product_id: str):
    logger.info(f"Getting product {product_id}")
    service = ProductService()
    product = service.get_product(product_id)
    if product == None:
        return {"error": "not found"}
    return product
```

### Audit Report

**MUST FIX Issues:**

1. **api/routes/products.py:1-3**
   - Issue: Import ordering doesn't match house style
   - Expected: stdlib → third-party → local (with blank lines)
   - Observed pattern: All other routes follow this ordering
   - Fix:
     ```python
     import logging
     
     from fastapi import APIRouter
     
     from app.services.product_service import ProductService
     ```

2. **api/routes/products.py:7**
   - Issue: Route handler is not async
   - Expected: All route handlers in codebase are async
   - Observed pattern: 47/47 other routes use `async def`
   - Fix: Change `def get_product` → `async def get_product`

3. **api/routes/products.py:9**
   - Issue: Service instantiated directly instead of dependency injection
   - Expected: Services injected via `Depends(get_product_service)`
   - Observed pattern: All other routes use dependency injection
   - Fix:
     ```python
     @router.get("/products/{product_id}")
     async def get_product(
         product_id: str,
         service: ProductService = Depends(get_product_service)
     ):
     ```

4. **api/routes/products.py:10**
   - Issue: Service method called without await
   - Expected: All async service methods must be awaited
   - Severity: MUST FIX (will cause runtime error)
   - Fix: `product = await service.get_product(product_id)`

5. **api/routes/products.py:11**
   - Issue: Using `== None` instead of `is None`
   - Expected: Core Conventions specify `is None` for None checks
   - Fix: `if product is None:`

6. **api/routes/products.py:12**
   - Issue: Returning error dict instead of raising HTTPException
   - Expected: All routes raise HTTPException for errors
   - Observed pattern: 45/47 routes raise HTTPException
   - Fix:
     ```python
     if product is None:
         raise HTTPException(status_code=404, detail="Product not found")
     ```

**NIT Issues:**

1. **api/routes/products.py:8**
   - Issue: Log level is `info`, most routes use `debug`
   - Severity: NIT (minor preference)
   - Observed: 80% of routes log at debug level
   - Suggested fix: `logger.debug(f"Getting product {product_id}")`

---

## When Writing New Code

**Match observed patterns.** Don't introduce new patterns without asking first.

### Decision Tree:

```
Is this pattern in Core Conventions?
├─ YES → Follow Core Conventions exactly
└─ NO → Check codebase
    ├─ Pattern exists (used in 3+ places) → Match it
    └─ Pattern doesn't exist → Ask user before inventing
```

### Example: Choosing Error Handling Pattern

**Scenario:** Need to handle validation errors in new API endpoint

**Step 1: Check Core Conventions**
- Core Conventions say: "Use typed errors, not generic Exception"
- Doesn't specify HOW to handle in API layer

**Step 2: Check Codebase**
- Read 3 existing API endpoints
- All raise `HTTPException` with status 422 for validation errors
- All include field name in error message
- Pattern found in 12/12 endpoints

**Step 3: Match Pattern**

```python
# ✓ Matches observed pattern
from fastapi import HTTPException

@router.post("/products")
async def create_product(data: ProductCreate):
    if not data.name:
        raise HTTPException(
            status_code=422,
            detail="name field is required"
        )
    # ...
```

❌ **Bad (New Pattern Without Asking):**

```python
# ❌ Introduces new error handling pattern
@router.post("/products")
async def create_product(data: ProductCreate):
    if not data.name:
        return {"error": {"field": "name", "message": "required"}}  # Different from rest of codebase!
```

---

## Summarizing House Style for New Contributors

If asked to document house style for new contributors:

### Process:

1. **Read 3-4 representative source files**
   - Pick from different layers (API, service, repository, models)
   - Pick files that are well-written, not legacy code

2. **Produce brief style guide** covering:
   - File and folder naming
   - Import ordering
   - Error handling pattern
   - Async style
   - Module structure (imports, exports)
   - Testing patterns
   - Logging patterns
   - Dependency injection approach

---

## Example House Style Summary

```markdown
# Project House Style Guide

## File and Folder Naming

- **Files:** `snake_case.py` (e.g., `user_service.py`)
- **Classes:** `PascalCase` (e.g., `UserService`)
- **Functions/methods:** `snake_case` (e.g., `get_user()`)
- **Test files:** `test_<module>.py` (e.g., `test_user_service.py`)

## Import Ordering

Three groups separated by blank lines:
1. Standard library
2. Third-party packages
3. Local application imports

```python
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repository import UserRepository
```

## Error Handling

### API Layer (FastAPI)
- Raise `HTTPException` for all errors
- Use appropriate status codes:
  - 400: Bad request (malformed input)
  - 401: Unauthorized
  - 403: Forbidden
  - 404: Not found
  - 422: Validation error
  - 500: Internal server error

```python
if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

### Service Layer
- Raise custom exceptions from `app/exceptions/`
- Never return None for errors — always raise
- Log errors at appropriate level

```python
from app.exceptions import UserNotFoundError

if not user:
    logger.error(f"User {user_id} not found")
    raise UserNotFoundError(f"User {user_id} not found")
```

## Async Style

- **All API routes:** async
- **All service methods:** async
- **All repository methods:** async
- **Always await async calls** — no fire-and-forget

```python
# ✓ Correct
async def get_user(user_id: str) -> User:
    user = await repository.find_by_id(user_id)
    return user

# ❌ Incorrect
def get_user(user_id: str) -> User:  # Not async
    user = repository.find_by_id(user_id)  # Not awaited
    return user
```

## Dependency Injection

- Use FastAPI `Depends()` for all dependencies
- Define dependency factories in `app/dependencies.py`

```python
from fastapi import Depends
from app.dependencies import get_user_service

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    return await service.get_user(user_id)
```

## Logging

- Use module-level logger: `logger = logging.getLogger(__name__)`
- Log levels:
  - **debug:** Entry/exit of functions, variable values
  - **info:** Significant events (user registered, order placed)
  - **warning:** Recoverable errors
  - **error:** Unrecoverable errors
- Include context in log messages (IDs, usernames, etc.)

```python
logger.debug(f"Fetching user {user_id}")
logger.info(f"User {user_id} successfully registered")
logger.error(f"Failed to send email to {email}: {error}")
```

## Testing Patterns

- Test files mirror source: `app/services/user_service.py` → `tests/unit/services/test_user_service.py`
- Use pytest fixtures for common setup
- Test names: `test_<function>_<scenario>_<expected>`

```python
def test_get_user_when_exists_returns_user():
    # Arrange
    user_id = "123"
    
    # Act
    user = service.get_user(user_id)
    
    # Assert
    assert user.id == user_id
```

## Database Access

- **Never call ORM directly** from API or service layer
- Always use repository pattern
- Repositories in `app/repositories/`

```python
# ✓ Correct (via repository)
user = await user_repository.find_by_id(user_id)

# ❌ Incorrect (direct ORM)
user = await db.query(User).filter(User.id == user_id).first()
```
```

---

## Common House Style Violations

### Violation 1: Inconsistent Error Handling

❌ **Inconsistent:**
```python
# File A: Raises HTTPException
if not user:
    raise HTTPException(status_code=404, detail="Not found")

# File B: Returns None
if not user:
    return None

# File C: Returns error dict
if not user:
    return {"error": "not found"}
```

✓ **Consistent (Pick One and Use Everywhere):**
```python
# All files raise HTTPException
if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

---

### Violation 2: Mixed Sync/Async

❌ **Inconsistent:**
```python
# File A: async
async def get_user(user_id: str):
    return await repository.find(user_id)

# File B: sync (in same layer)
def get_product(product_id: str):
    return repository.find(product_id)
```

✓ **Consistent (All Async in This Layer):**
```python
# All service methods async
async def get_user(user_id: str):
    return await repository.find(user_id)

async def get_product(product_id: str):
    return await repository.find(product_id)
```

---

### Violation 3: Inconsistent Import Ordering

❌ **Inconsistent:**
```python
# No grouping or blank lines
from app.models import User
import logging
from fastapi import APIRouter
from typing import Optional
```

✓ **Consistent (Grouped with Blank Lines):**
```python
import logging
from typing import Optional

from fastapi import APIRouter

from app.models import User
```

---

## Workflow: Style Check Before Commit

Before committing code:

1. **Read 1-2 similar files** from same layer
2. **Compare your code** to those patterns
3. **Check:**
   - Import ordering matches
   - Error handling matches
   - Async/sync matches
   - Naming matches
   - Logging style matches
4. **Fix deviations** before committing

---

## When to Ask About Introducing New Pattern

Ask user before introducing a new pattern if:

- ✓ No existing pattern found for this case
- ✓ Existing pattern seems wrong or outdated
- ✓ You want to improve on existing pattern
- ✓ Core Conventions conflict with house style

**Example:**
```
I noticed all services return None when entity not found, but Core Conventions 
recommend raising typed errors. Should I:
A) Match existing pattern (return None)
B) Follow Core Conventions (raise exception)
C) Update all existing code to raise exceptions
```

---

## Anti-Patterns to Avoid

❌ **Assuming without reading:**
```
"I'll just write it how I think it should be"
```
(Read existing code first)

❌ **Inventing new patterns without asking:**
```python
# Everyone else uses HTTPException, but I prefer this:
return Response(status_code=404, content="Not found")
```

❌ **Mixing styles in same file:**
```python
def function_one():  # sync
    pass

async def function_two():  # async
    pass
```
(Be consistent within file)

❌ **Ignoring 90% consensus:**
```
"45 files do it one way, but I think my way is better"
```
(Match the majority unless there's a good reason)
