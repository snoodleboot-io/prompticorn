---
name: code
version: 1.0
languages: [all]
subagents: [code/feature, code/bug-fix, test/unit]
---

# Code Implementation Workflow (Verbose)

## Overview

This workflow guides implementation of features and bug fixes with emphasis on planning, following conventions, and incremental development.

## Pre-Implementation Analysis

### Step 1: Understand the Requirement

Before writing any code, ensure you understand:

**What:**
- What specific functionality is being added or fixed?
- What are the acceptance criteria?
- What is the expected behavior?

**Why:**
- Why is this change needed?
- What problem does it solve?
- What value does it provide?

**Scope:**
- What is included in this change?
- What is explicitly out of scope?
- Where are the boundaries?

### Restate the Goal

Write the goal in your own words to confirm understanding:

**Example:**
```
User Request: "Add rate limiting to the auth endpoint"

Your Restatement:
"Implement rate limiting on POST /auth/login to prevent brute force 
attacks. Allow 5 login attempts per IP address per 5-minute window. 
Return 429 Too Many Requests when limit exceeded. Does NOT apply to 
other auth endpoints yet."
```

**Ask for Confirmation:**
- "Is this understanding correct?"
- "Should rate limiting apply per IP or per user?"
- "What should happen after the window expires?"

## Step 2: Read Existing Code

### Why Read First?

- Understand existing patterns
- Avoid reinventing solutions
- Match code style
- Identify potential conflicts

### What to Read

**Read these files before writing code:**

1. **Target file** - where changes will be made
2. **Similar implementations** - how related features work
3. **Imported dependencies** - what you'll be using
4. **Tests** - how existing code is tested

**Example (Python):**
```bash
# Read the file you'll modify
cat src/auth/service.py

# Read similar implementations
cat src/rate_limiting/limiter.py  # If exists
cat src/middleware/throttle.py   # Check for existing rate limiting

# Read tests to understand patterns
cat tests/unit/auth/test_service.py
```

### Identify Patterns

**Questions to answer:**
- How are errors handled in this module?
- What naming conventions are used?
- How are dependencies injected?
- What's the typical function length?
- How are tests organized?

**Example Pattern Recognition:**
```python
# Noticed pattern in existing code:
# 1. Services use dependency injection
# 2. Errors raise custom exceptions
# 3. All public methods have type hints
# 4. Tests use pytest fixtures

# Follow this pattern in new code
class RateLimiter:
    def __init__(self, cache: Cache):  # DI like other services
        self.cache = cache
    
    def check_limit(self, key: str) -> bool:  # Type hints
        if self._is_exceeded(key):
            raise RateLimitExceeded(key)  # Custom exception
        return True
```

## Step 3: Follow Conventions

### Naming Conventions

Consult your conventions documentation for:

**Files:**
```
Python:     snake_case.py
TypeScript: kebab-case.ts
Go:         lowercase.go
Java:       PascalCase.java
```

**Variables and Functions:**
```python
# Python: snake_case
user_count = get_active_users()

# TypeScript: camelCase
const userCount = getActiveUsers();

# Go: camelCase for private, PascalCase for public
func getUserCount() int { }      // private
func GetActiveUsers() []User { } // public
```

**Classes and Types:**
```python
# Python: PascalCase
class UserService:
    pass

# TypeScript: PascalCase
class UserService { }

# Go: PascalCase for exported
type UserService struct { }
```

### Type Hints and Annotations

**Python:**
```python
# Always type public functions
def create_user(email: str, name: str) -> User:
    return User(email=email, name=name)

# Type complex structures
from typing import Dict, List, Optional

def get_user_stats(user_id: int) -> Dict[str, int]:
    return {"login_count": 10, "posts": 5}

# Use | for unions (modern Python)
def find_user(email: str) -> User | None:
    return db.query(User).filter_by(email=email).first()
```

**TypeScript:**
```typescript
// Always type parameters and return values
function createUser(email: string, name: string): User {
  return { email, name, createdAt: new Date() };
}

// Type complex structures
interface UserStats {
  loginCount: number;
  posts: number;
}

function getUserStats(userId: number): UserStats {
  return { loginCount: 10, posts: 5 };
}

// Use union types for nullable
function findUser(email: string): User | null {
  return users.find(u => u.email === email) ?? null;
}
```

### Error Handling Patterns

Follow language-specific error patterns:

**Python (Exceptions):**
```python
# Raise specific exceptions
def withdraw(account: Account, amount: float) -> None:
    if amount > account.balance:
        raise InsufficientFundsError(
            f"Cannot withdraw {amount}, balance is {account.balance}"
        )
    account.balance -= amount

# Use custom exception hierarchy
class InsufficientFundsError(ValueError):
    pass
```

**TypeScript (Throw or Result Type):**
```typescript
// Throw for exceptional cases
function withdraw(account: Account, amount: number): void {
  if (amount > account.balance) {
    throw new InsufficientFundsError(
      `Cannot withdraw ${amount}, balance is ${account.balance}`
    );
  }
  account.balance -= amount;
}

// Or use Result type for expected errors
type Result<T, E> = { ok: true; value: T } | { ok: false; error: E };

function withdraw(account: Account, amount: number): Result<void, string> {
  if (amount > account.balance) {
    return { ok: false, error: 'Insufficient funds' };
  }
  account.balance -= amount;
  return { ok: true, value: undefined };
}
```

**Go (Error Returns):**
```go
// Return errors explicitly
func Withdraw(account *Account, amount float64) error {
    if amount > account.Balance {
        return fmt.Errorf("insufficient funds: have %f, need %f", 
            account.Balance, amount)
    }
    account.Balance -= amount
    return nil
}
```

## Step 4: Inline Comments - Comment WHY, Not WHAT

### Good Comments

✓ **Explain WHY:**
```python
# Use exponential backoff to avoid overwhelming the API
# after temporary failures
retry_delay = 2 ** attempt_number

# Cache for 1 hour - balance between freshness and API quota
cache.set(key, value, ttl=3600)

# Intentionally not awaited - fire-and-forget analytics
asyncio.create_task(track_event(user_id, "login"))
```

✓ **Explain Non-Obvious Decisions:**
```typescript
// Using Set for O(1) lookup instead of array.includes() which is O(n)
const validIds = new Set(ids);

// Must process in reverse to avoid index shifting during deletion
for (let i = items.length - 1; i >= 0; i--) {
  if (shouldDelete(items[i])) {
    items.splice(i, 1);
  }
}
```

✓ **Document Gotchas:**
```python
# WARNING: This modifies the input list in-place
def sort_users(users: List[User]) -> List[User]:
    users.sort(key=lambda u: u.name)
    return users

# TODO: This will break if called concurrently - add locking
def update_counter():
    current = get_counter()
    set_counter(current + 1)
```

### Bad Comments

❌ **Restating Code:**
```python
# Bad - says WHAT (code already says this)
# Increment counter by 1
counter += 1

# Add user to database
db.add(user)

# Check if email is valid
if '@' in email:
```

❌ **Outdated Comments:**
```python
# Bad - comment doesn't match code anymore
# Returns list of active users
def get_users():
    return User.query.all()  # Returns ALL users, not just active
```

### Magic Numbers

Replace with named constants:

**Before:**
```python
# Bad - what is 86400?
if elapsed > 86400:
    refresh_cache()
```

**After:**
```python
# Good - clear meaning
SECONDS_PER_DAY = 86400

if elapsed > SECONDS_PER_DAY:
    refresh_cache()
```

## Step 5: Implement Incrementally

### One File at a Time

**Don't:**
- Modify 10 files simultaneously
- Write all code then test at the end

**Do:**
- Implement one file completely
- Run tests after each file
- Commit small working changes

**Example Workflow:**

**Commit 1: Add rate limiter class**
```bash
# Create src/rate_limiting/limiter.py
git add src/rate_limiting/limiter.py
git commit -m "feat: add RateLimiter class"
```

**Commit 2: Add tests**
```bash
# Create tests/unit/rate_limiting/test_limiter.py
git add tests/unit/rate_limiting/test_limiter.py
git commit -m "test: add RateLimiter tests"
```

**Commit 3: Integrate with auth service**
```bash
# Modify src/auth/service.py
git add src/auth/service.py
git commit -m "feat: integrate rate limiting in auth service"
```

### Run Tests Frequently

After each file change:

```bash
# Python
pytest tests/unit/rate_limiting/

# TypeScript
vitest run src/rate-limiting/

# Go
go test ./rate-limiting/...
```

If tests fail, fix immediately before continuing.

## Step 6: Logging Best Practices

### What to Log

**Log:**
- Errors and exceptions (with context)
- Important state changes (user created, order completed)
- External API calls (with timing)
- Security events (login failures, permission denials)

**Don't Log:**
- Sensitive data (passwords, tokens, PII)
- High-frequency operations (every cache hit)
- Verbose debug info in production

### Logging Levels

**ERROR:** Something went wrong, requires attention
```python
logger.error(f"Failed to process payment for order {order_id}: {error}")
```

**WARNING:** Unexpected but handled
```python
logger.warning(f"Rate limit exceeded for IP {ip_address}")
```

**INFO:** Important business events
```python
logger.info(f"User {user_id} logged in from {ip_address}")
```

**DEBUG:** Detailed diagnostic info (development only)
```python
logger.debug(f"Cache hit for key {cache_key}")
```

### Structured Logging

**Python:**
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "user_login",
    user_id=user.id,
    ip_address=request.ip,
    user_agent=request.headers.get("User-Agent")
)
```

**TypeScript:**
```typescript
logger.info('user_login', {
  userId: user.id,
  ipAddress: request.ip,
  userAgent: request.headers['user-agent']
});
```

## Step 7: Performance Considerations

### When to Optimize

**Optimize:**
- Database queries in hot paths
- N+1 query problems
- Large collection operations
- Repeated calculations

**Don't Optimize:**
- Startup code
- Admin endpoints
- Code called rarely

### Common Performance Patterns

**Avoid N+1 Queries:**

**Bad (Python):**
```python
# N+1 problem - queries database for each user
users = User.query.all()
for user in users:
    print(user.role.name)  # Separate query for each user's role
```

**Good (Python):**
```python
# Single query with join
users = User.query.options(joinedload(User.role)).all()
for user in users:
    print(user.role.name)  # No additional queries
```

**Use Caching Wisely:**

```python
from functools import lru_cache

# Cache expensive pure functions
@lru_cache(maxsize=128)
def calculate_fibonacci(n: int) -> int:
    if n < 2:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)
```

**Batch Operations:**

**Bad:**
```python
# Individual inserts - slow
for item in items:
    db.session.add(item)
    db.session.commit()
```

**Good:**
```python
# Batch insert - fast
db.session.add_all(items)
db.session.commit()
```

## Step 8: Code Review Preparation

### Self-Review Checklist

Before requesting review:

- [ ] All tests pass locally
- [ ] No linter warnings or errors
- [ ] Code follows project conventions
- [ ] Type hints present on all public functions
- [ ] Error cases are handled
- [ ] Logging is appropriate
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Commit messages follow convention
- [ ] No secrets or API keys in code

### Commit Messages

Follow conventional commits:

```bash
# Format: <type>(<scope>): <description>

# Good examples:
feat(auth): add rate limiting to login endpoint
fix(user): prevent duplicate email registration
refactor(db): extract query builder to separate module
test(auth): add rate limiter integration tests
docs(api): update rate limiting documentation

# Bad examples:
update code         # Too vague
fixed bug          # No context
WIP                # Not a final commit message
```

## Common Implementation Mistakes

### Mistake 1: Not Reading Existing Code

❌ **Bad:**
```python
# Implements new pattern without checking existing code
def send_welcome_email(user):
    smtp = smtplib.SMTP('localhost')  # New SMTP connection
    smtp.send_message(email)
```

✓ **Good:**
```python
# Read existing code, discovered EmailService already exists
def send_welcome_email(user):
    email_service.send(  # Use existing service
        to=user.email,
        template='welcome',
        context={'name': user.name}
    )
```

### Mistake 2: Ignoring Type Safety

❌ **Bad (Python):**
```python
# No type hints - unclear what this accepts/returns
def process_data(data):
    return data['items']
```

✓ **Good (Python):**
```python
from typing import Dict, List, Any

def process_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    return data['items']
```

❌ **Bad (TypeScript):**
```typescript
// Using 'any' defeats type system
function processUser(user: any) {
  return user.name.toUpperCase();  // Runtime error if name is undefined
}
```

✓ **Good (TypeScript):**
```typescript
interface User {
  name: string;
  email: string;
}

function processUser(user: User): string {
  return user.name.toUpperCase();  // Type-safe
}
```

### Mistake 3: Not Handling Errors

❌ **Bad:**
```python
def get_user_by_email(email):
    return db.query(User).filter_by(email=email).first()
    # Returns None if not found - caller must check
    # No error for invalid email format
```

✓ **Good:**
```python
def get_user_by_email(email: str) -> User:
    if not is_valid_email(email):
        raise ValueError(f"Invalid email format: {email}")
    
    user = db.query(User).filter_by(email=email).first()
    if user is None:
        raise UserNotFoundError(f"No user found with email: {email}")
    
    return user
```

### Mistake 4: Implementing Everything at Once

❌ **Bad:**
```bash
# Single massive commit
git commit -m "feat: complete rate limiting implementation"
# 15 files changed, 1200+ lines
```

✓ **Good:**
```bash
# Incremental commits
git commit -m "feat: add RateLimiter class"           # 1 file, 50 lines
git commit -m "test: add RateLimiter tests"          # 1 file, 100 lines
git commit -m "feat: integrate rate limiting in auth" # 2 files, 30 lines
git commit -m "docs: document rate limiting config"  # 1 file, 20 lines
```

### Mistake 5: Hardcoding Configuration

❌ **Bad:**
```python
def check_rate_limit(ip_address):
    max_requests = 5       # Hardcoded
    window_seconds = 300   # Hardcoded
    # ...
```

✓ **Good:**
```python
# Configuration file (config.yaml)
# rate_limiting:
#   max_requests: 5
#   window_seconds: 300

from config import settings

def check_rate_limit(ip_address):
    max_requests = settings.rate_limiting.max_requests
    window_seconds = settings.rate_limiting.window_seconds
    # ...
```

### Mistake 6: Poor Error Messages

❌ **Bad:**
```python
if amount <= 0:
    raise ValueError("Invalid amount")  # Vague
```

✓ **Good:**
```python
if amount <= 0:
    raise ValueError(
        f"Amount must be positive, got {amount}"  # Specific, actionable
    )
```

### Mistake 7: Skipping Tests

❌ **Bad:**
```python
# New feature without tests
def apply_discount(price, discount_percent):
    return price * (1 - discount_percent / 100)

# No test file created
```

✓ **Good:**
```python
# Implementation
def apply_discount(price: float, discount_percent: float) -> float:
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)

# Test file (tests/unit/test_pricing.py)
def test_apply_discount_reduces_price():
    assert apply_discount(100, 10) == 90

def test_apply_discount_rejects_invalid_percent():
    with pytest.raises(ValueError):
        apply_discount(100, 150)
```

### Mistake 8: Not Cleaning Up

❌ **Bad:**
```python
# Leaves commented-out code
def create_user(email, name):
    # old_user = User(email)
    # db.add(old_user)
    user = User(email=email, name=name)  # New approach
    print(f"Creating user: {email}")  # Debug print left in
    db.add(user)
    return user
```

✓ **Good:**
```python
def create_user(email: str, name: str) -> User:
    user = User(email=email, name=name)
    db.add(user)
    logger.info(f"Created user: {email}")  # Proper logging
    return user
```

## Step-by-Step Implementation Example

### Feature: Add Email Verification

**Step 1: Plan**
```
Goal: Add email verification to user registration

Changes needed:
1. Add verification_token and verified fields to User model
2. Generate token on user creation
3. Send verification email
4. Add verification endpoint
5. Add tests

Files to modify:
- models/user.py (add fields)
- services/user_service.py (generate token, send email)
- routes/auth.py (add verification endpoint)
- tests/unit/test_user_service.py (add tests)
```

**Step 2: Read Existing Code**
```bash
# Read user model
cat models/user.py

# Read user service
cat services/user_service.py

# Read existing email sending
cat services/email_service.py

# Read tests to understand patterns
cat tests/unit/test_user_service.py
```

**Step 3: Implement - Commit 1 (Model)**
```python
# models/user.py
from sqlalchemy import Column, String, Boolean
import secrets

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    verified = Column(Boolean, default=False)  # New field
    verification_token = Column(String, nullable=True)  # New field
    
    def generate_verification_token(self) -> str:
        """Generate secure random token for email verification."""
        self.verification_token = secrets.token_urlsafe(32)
        return self.verification_token
```

```bash
git add models/user.py
git commit -m "feat(user): add email verification fields to User model"
```

**Step 4: Implement - Commit 2 (Service)**
```python
# services/user_service.py
from services.email_service import EmailService

class UserService:
    def __init__(self, db_session, email_service: EmailService):
        self.db = db_session
        self.email_service = email_service
    
    def create_user(self, email: str, name: str) -> User:
        user = User(email=email, name=name)
        token = user.generate_verification_token()
        
        self.db.add(user)
        self.db.commit()
        
        # Send verification email
        self.email_service.send(
            to=user.email,
            template='verify_email',
            context={'token': token, 'name': user.name}
        )
        
        return user
    
    def verify_email(self, token: str) -> User:
        user = self.db.query(User).filter_by(
            verification_token=token
        ).first()
        
        if not user:
            raise InvalidTokenError("Invalid verification token")
        
        user.verified = True
        user.verification_token = None  # Clear token after use
        self.db.commit()
        
        return user
```

```bash
git add services/user_service.py
git commit -m "feat(user): add email verification to user service"
```

**Step 5: Implement - Commit 3 (Endpoint)**
```python
# routes/auth.py
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post('/verify-email')
def verify_email(token: str):
    try:
        user = user_service.verify_email(token)
        return {'message': 'Email verified successfully'}
    except InvalidTokenError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

```bash
git add routes/auth.py
git commit -m "feat(auth): add email verification endpoint"
```

**Step 6: Add Tests - Commit 4**
```python
# tests/unit/test_user_service.py
def test_create_user_sends_verification_email():
    mock_email = Mock()
    service = UserService(db_session, mock_email)
    
    user = service.create_user("test@example.com", "Test User")
    
    assert user.verified is False
    assert user.verification_token is not None
    mock_email.send.assert_called_once()

def test_verify_email_sets_user_as_verified():
    user = User(email="test@example.com", name="Test")
    token = user.generate_verification_token()
    db_session.add(user)
    db_session.commit()
    
    service = UserService(db_session, Mock())
    verified_user = service.verify_email(token)
    
    assert verified_user.verified is True
    assert verified_user.verification_token is None

def test_verify_email_with_invalid_token_raises_error():
    service = UserService(db_session, Mock())
    
    with pytest.raises(InvalidTokenError):
        service.verify_email("invalid_token")
```

```bash
git add tests/unit/test_user_service.py
git commit -m "test(user): add email verification tests"
```

**Step 7: Verify**
```bash
# Run all tests
pytest

# Check coverage
pytest --cov=services --cov=models --cov-report=term

# Run linter
ruff check .

# Check types
pyright
```

## Quality Verification Checklist

Before marking implementation as complete:

### Functionality
- [ ] Feature works as expected in happy path
- [ ] Edge cases are handled
- [ ] Error cases return appropriate errors
- [ ] Input validation is present

### Code Quality
- [ ] Follows project conventions
- [ ] Type hints on all public functions
- [ ] Appropriate comments (WHY, not WHAT)
- [ ] No magic numbers (use named constants)
- [ ] No commented-out code
- [ ] No debug print statements

### Testing
- [ ] Unit tests written for new code
- [ ] All tests pass
- [ ] Coverage ≥ 80% on new code
- [ ] Edge cases tested
- [ ] Error cases tested

### Performance
- [ ] No N+1 queries introduced
- [ ] Database queries optimized
- [ ] No obvious performance issues

### Security
- [ ] No secrets in code
- [ ] Input validation present
- [ ] SQL injection prevented (use parameterized queries)
- [ ] XSS prevented (escape output)

### Documentation
- [ ] Inline comments for complex logic
- [ ] API documentation if public endpoint
- [ ] README updated if needed
- [ ] Changelog entry if applicable

### Git
- [ ] Commits are small and focused
- [ ] Commit messages follow convention
- [ ] No unrelated changes included
- [ ] Ready for code review

## Summary

Successful implementation requires:

1. **Plan first** - understand requirements, confirm approach
2. **Read existing code** - follow established patterns
3. **Follow conventions** - naming, types, error handling
4. **Implement incrementally** - one file at a time, test frequently
5. **Write quality code** - type hints, error handling, logging
6. **Test thoroughly** - happy path, edge cases, errors
7. **Verify before review** - self-review, run all checks
8. **Clean up** - remove debug code, commented lines

Quality code is readable, maintainable, tested, and follows conventions.
