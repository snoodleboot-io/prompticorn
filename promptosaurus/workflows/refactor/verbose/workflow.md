---
name: refactor
version: 1.0
languages: [all]
subagents: [code/refactor, test/unit, review/code]
---

# Refactor Workflow (Verbose)

## Overview

Refactoring is improving code structure without changing external behavior. This workflow ensures safe, incremental refactoring with tests as a safety net.

## When to Refactor

**Good Times:**
- Before adding a new feature to messy code
- After identifying duplicate code in code review
- When code becomes hard to understand or modify
- As part of regular maintenance

**Bad Times:**
- During an outage or incident
- When tests are missing or failing
- On code you don't understand yet
- Under tight deadline pressure

## Code Smells to Detect

### Long Method
Method does too many things, hard to understand.

**Example (Python):**
```python
# Bad - 50+ line method doing everything
def process_order(order_data):
    # Validate data (10 lines)
    # Calculate totals (15 lines)
    # Apply discounts (20 lines)
    # Save to database (10 lines)
    # Send email (15 lines)
    # Return response (5 lines)
```

### Duplicate Code
Same logic repeated in multiple places.

**Example (TypeScript):**
```typescript
// Bad - validation duplicated
function createUser(data) {
  if (!data.email || !data.email.includes('@')) {
    throw new Error('Invalid email');
  }
  // ...
}

function updateUser(data) {
  if (!data.email || !data.email.includes('@')) {
    throw new Error('Invalid email');
  }
  // ...
}
```

### God Object
Class knows or does too much.

**Example:**
```python
# Bad - User class does everything
class User:
    def save_to_database(self): ...
    def send_welcome_email(self): ...
    def calculate_permissions(self): ...
    def generate_api_token(self): ...
    def validate_password_strength(self): ...
```

### Magic Numbers
Unexplained constants in code.

**Example:**
```python
# Bad
if user.age < 18:
    return False

# Good
MINIMUM_AGE = 18
if user.age < MINIMUM_AGE:
    return False
```

## Step 1: Define Scope

### Identify the Problem

Be specific about what needs improvement:

- **Not:** "This code is messy"
- **Instead:** "This 200-line method has 5 responsibilities and should be split"

### Set Clear Goal

**Example Goals:**
- Extract validation logic into separate function
- Remove duplicate email sending code
- Rename variables for clarity
- Consolidate three similar classes into one

### Define What's NOT Changing

**Preserve:**
- Public API contracts
- External behavior
- Database schema (unless migration is planned)
- Configuration format

**Document:**
```python
# Refactoring Goal: Extract user validation logic
# What's changing: Internal implementation
# What's NOT changing: UserService.create_user() signature and return type
```

## Step 2: Write Tests First

### Why Test Before Refactoring?

Tests verify that refactoring didn't break behavior.

### Test Coverage Requirements

Before refactoring, ensure:
- [ ] All code paths are tested
- [ ] Edge cases are covered
- [ ] All tests pass
- [ ] Coverage ≥ 80% on code being refactored

**Example (Python):**
```python
# Before refactoring this method, write tests
def calculate_discount(amount, user_type, coupon_code):
    # Complex logic here - needs tests before refactoring
    pass

# Tests to write:
def test_calculate_discount_for_regular_user():
    assert calculate_discount(100, "regular", None) == 0

def test_calculate_discount_for_premium_user():
    assert calculate_discount(100, "premium", None) == 10

def test_calculate_discount_with_valid_coupon():
    assert calculate_discount(100, "regular", "SAVE20") == 20

def test_calculate_discount_with_invalid_coupon():
    assert calculate_discount(100, "regular", "INVALID") == 0
```

### Characterization Tests

For legacy code without tests, write "characterization tests" that capture current behavior (even if buggy):

```python
def test_current_behavior_of_legacy_function():
    # Document current behavior before refactoring
    result = legacy_function(input_data)
    assert result == expected_current_output  # Even if wrong
```

## Step 3: Safe Refactoring Patterns

### Extract Method

**Problem:** Long method doing multiple things

**Before (Python):**
```python
def process_order(order_data):
    # Validate
    if not order_data.get('email'):
        raise ValueError("Email required")
    if not order_data.get('items'):
        raise ValueError("Items required")
    
    # Calculate total
    subtotal = sum(item['price'] * item['qty'] for item in order_data['items'])
    tax = subtotal * 0.08
    total = subtotal + tax
    
    # Save
    order = Order(email=order_data['email'], total=total)
    db.session.add(order)
    db.session.commit()
    
    return order
```

**After (Python):**
```python
def process_order(order_data):
    validate_order_data(order_data)
    total = calculate_order_total(order_data['items'])
    order = save_order(order_data['email'], total)
    return order

def validate_order_data(order_data):
    if not order_data.get('email'):
        raise ValueError("Email required")
    if not order_data.get('items'):
        raise ValueError("Items required")

def calculate_order_total(items):
    subtotal = sum(item['price'] * item['qty'] for item in items)
    tax = subtotal * 0.08
    return subtotal + tax

def save_order(email, total):
    order = Order(email=email, total=total)
    db.session.add(order)
    db.session.commit()
    return order
```

### Rename for Clarity

**Problem:** Unclear variable names

**Before (TypeScript):**
```typescript
function calc(a: number, b: number): number {
  const c = a * b;
  const d = c * 0.08;
  return c + d;
}
```

**After (TypeScript):**
```typescript
function calculateOrderTotal(subtotal: number, quantity: number): number {
  const itemTotal = subtotal * quantity;
  const tax = itemTotal * TAX_RATE;
  return itemTotal + tax;
}
```

### Extract Class

**Problem:** Class has too many responsibilities

**Before (Python):**
```python
class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password
    
    def save_to_database(self):
        db.session.add(self)
        db.session.commit()
    
    def send_welcome_email(self):
        send_email(self.email, "Welcome!", "Thanks for joining")
    
    def validate_password_strength(self):
        return len(self.password) >= 8
```

**After (Python):**
```python
class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

class UserRepository:
    def save(self, user: User):
        db.session.add(user)
        db.session.commit()

class EmailService:
    def send_welcome_email(self, user: User):
        send_email(user.email, "Welcome!", "Thanks for joining")

class PasswordValidator:
    def is_strong(self, password: str) -> bool:
        return len(password) >= 8
```

### Inline Unnecessary Abstraction

**Problem:** Over-engineered single-use abstraction

**Before (Python):**
```python
def get_user_email(user):
    return extract_email_from_user(user)

def extract_email_from_user(user):
    return user.email

# Usage
email = get_user_email(user)
```

**After (Python):**
```python
# Usage
email = user.email  # Direct access, no unnecessary wrapper
```

### Consolidate Duplicate Code

**Problem:** Same logic in multiple places

**Before (TypeScript):**
```typescript
function createUser(data: UserData) {
  if (!data.email?.includes('@')) {
    throw new Error('Invalid email');
  }
  // Create user...
}

function updateUser(id: string, data: UserData) {
  if (!data.email?.includes('@')) {
    throw new Error('Invalid email');
  }
  // Update user...
}
```

**After (TypeScript):**
```typescript
function validateEmail(email: string): void {
  if (!email?.includes('@')) {
    throw new Error('Invalid email');
  }
}

function createUser(data: UserData) {
  validateEmail(data.email);
  // Create user...
}

function updateUser(id: string, data: UserData) {
  validateEmail(data.email);
  // Update user...
}
```

## Step 4: Incremental Refactoring Process

### Micro-Steps

Make the smallest possible change at each step:

1. **Extract one method** → Run tests
2. **Rename one variable** → Run tests
3. **Move one responsibility** → Run tests

**Never:**
- Refactor multiple things at once
- Skip running tests between changes
- Make unrelated changes during refactoring

### Example Workflow

**Goal:** Refactor 200-line `process_order` method

**Step 1:** Extract validation (commit)
```bash
git commit -m "refactor: extract order validation logic"
```

**Step 2:** Extract total calculation (commit)
```bash
git commit -m "refactor: extract total calculation"
```

**Step 3:** Extract email sending (commit)
```bash
git commit -m "refactor: extract email notification"
```

Each commit is independently revertible if tests fail.

## Step 5: Working with Legacy Code

### Strategy for Code Without Tests

**Michael Feathers' Approach:**

1. **Identify change points** - where you need to modify
2. **Break dependencies** - make code testable
3. **Write tests** - cover current behavior
4. **Make changes** - refactor safely
5. **Refactor test code** - clean up tests

**Example (Python):**
```python
# Legacy code - hard to test (tight coupling)
class OrderProcessor:
    def process(self, order_data):
        db = Database()  # Hard-coded dependency
        email = EmailService()  # Hard-coded dependency
        # ... complex logic
```

**Step 1: Break dependencies (dependency injection)**
```python
class OrderProcessor:
    def __init__(self, db, email_service):
        self.db = db
        self.email_service = email_service
    
    def process(self, order_data):
        # ... same logic, now testable
```

**Step 2: Write tests with mocks**
```python
def test_order_processor():
    mock_db = Mock()
    mock_email = Mock()
    processor = OrderProcessor(mock_db, mock_email)
    
    processor.process(sample_order_data)
    
    mock_db.save.assert_called_once()
```

**Step 3: Refactor safely**

## Step 6: Performance vs Readability

### When Performance Matters

**Optimize:**
- Hot paths (called millions of times)
- Database queries
- Network calls
- Critical user-facing operations

**Don't Optimize:**
- Startup code
- Admin operations
- Code called infrequently

### Trade-offs

**Example: Readability First**
```python
# Readable but slower (creates intermediate lists)
def get_adult_names(users):
    adults = [u for u in users if u.age >= 18]
    names = [u.name for u in adults]
    return sorted(names)
```

**Example: Performance First (if profiled and proven necessary)**
```python
# Faster but less readable (single pass, generator)
def get_adult_names(users):
    return sorted(u.name for u in users if u.age >= 18)
```

**Rule:** Readability first, optimize only when profiling shows a real bottleneck.

## When NOT to Refactor

### Situations to Avoid

❌ **Don't refactor when:**
- Production is down
- Tests are failing
- You don't understand the code yet
- No tests exist and you can't write them
- Under extreme time pressure
- It's code you'll delete soon anyway

✓ **Instead:**
- Fix the immediate issue
- Add a TODO comment for refactoring later
- Schedule refactoring as a separate task

## IDE Refactoring Tools

Modern IDEs provide safe automated refactoring:

### VS Code / IntelliJ / PyCharm

- **Extract Method** - F2 / Ctrl+Alt+M
- **Rename Symbol** - F2 / Shift+F6
- **Inline Variable** - Ctrl+Alt+N
- **Move to File** - F6

**Always prefer IDE refactoring over manual editing** - IDEs update all references automatically.

## Common Refactoring Mistakes

### Mistake 1: Changing Behavior During Refactoring

❌ **Bad:**
```python
# Original
def calculate_total(items):
    return sum(item.price for item in items)

# Refactored - WRONG, added tax (behavior change)
def calculate_total(items):
    subtotal = sum(item.price for item in items)
    return subtotal * 1.08  # Added tax - NOT refactoring!
```

✓ **Good:**
```python
# Refactored - same behavior, clearer structure
def calculate_total(items):
    prices = [item.price for item in items]
    return sum(prices)
```

### Mistake 2: Refactoring Too Much at Once

❌ **Bad:**
```bash
git commit -m "refactor: complete rewrite of order processing"
# 50 files changed, 3000 lines changed
```

✓ **Good:**
```bash
git commit -m "refactor: extract order validation"  # 2 files, 30 lines
git commit -m "refactor: extract total calculation"  # 1 file, 20 lines
git commit -m "refactor: rename variables for clarity"  # 3 files, 15 lines
```

### Mistake 3: Not Running Tests

❌ **Bad:**
```
1. Refactor 5 methods
2. Run tests once at the end
3. Tests fail
4. Can't identify which change broke it
```

✓ **Good:**
```
1. Refactor one method
2. Run tests - pass ✓
3. Commit
4. Refactor next method
5. Run tests - pass ✓
6. Commit
```

### Mistake 4: Over-Engineering

❌ **Bad:**
```python
# Over-engineered for simple use case
class EmailValidatorFactory:
    def create_validator(self, type: str) -> EmailValidator:
        if type == "strict":
            return StrictEmailValidator()
        return SimpleEmailValidator()

class EmailValidator(ABC):
    @abstractmethod
    def validate(self, email: str) -> bool: pass

class StrictEmailValidator(EmailValidator):
    def validate(self, email: str) -> bool:
        return '@' in email and '.' in email

class SimpleEmailValidator(EmailValidator):
    def validate(self, email: str) -> bool:
        return '@' in email
```

✓ **Good:**
```python
# Simple solution for simple problem
def is_valid_email(email: str) -> bool:
    return '@' in email and '.' in email
```

### Mistake 5: Refactoring Without Understanding

❌ **Bad:**
```python
# "This looks messy, I'll clean it up"
# Removes code that was actually necessary
def process_data(data):
    # Removed this line - seemed redundant
    # data = data.strip()  # Actually prevented a bug!
    return data.upper()
```

✓ **Good:**
```python
# First understand WHY code exists
# Write test to verify behavior
# Then refactor with confidence
```

### Mistake 6: Mixing Refactoring with Features

❌ **Bad:**
```
git commit -m "Add discount feature and refactor pricing"
# Hard to review, hard to revert, hard to debug
```

✓ **Good:**
```
git commit -m "refactor: extract pricing calculation"
git commit -m "feat: add discount feature"
# Clear separation, easy to review/revert
```

## Refactoring Checklist

Before completing refactoring:

- [ ] All tests pass
- [ ] No behavior changes (external contracts unchanged)
- [ ] Code is more readable than before
- [ ] Duplication is reduced
- [ ] Method/variable names are clearer
- [ ] Each commit is small and focused
- [ ] Performance hasn't degraded (if critical path)
- [ ] Documentation updated if needed
- [ ] No new warnings or errors
- [ ] Reviewed changes yourself before requesting review

## Example: Complete Refactoring Session

### Before
```python
def handle_order(data):
    if not data['email']:
        return {'error': 'Email required'}
    if not data['items']:
        return {'error': 'Items required'}
    
    total = 0
    for item in data['items']:
        total += item['price'] * item['qty']
    tax = total * 0.08
    total = total + tax
    
    order = Order()
    order.email = data['email']
    order.total = total
    db.session.add(order)
    db.session.commit()
    
    msg = f"Thank you for your order of ${total}"
    send_email(data['email'], "Order Confirmation", msg)
    
    return {'order_id': order.id, 'total': total}
```

### After (Step-by-Step Refactoring)

**Commit 1: Extract validation**
```python
def validate_order_data(data):
    if not data.get('email'):
        raise ValueError('Email required')
    if not data.get('items'):
        raise ValueError('Items required')

def handle_order(data):
    validate_order_data(data)
    
    # ... rest of code unchanged
```

**Commit 2: Extract calculation**
```python
def calculate_total_with_tax(items):
    subtotal = sum(item['price'] * item['qty'] for item in items)
    tax = subtotal * TAX_RATE
    return subtotal + tax

def handle_order(data):
    validate_order_data(data)
    total = calculate_total_with_tax(data['items'])
    
    # ... rest of code unchanged
```

**Commit 3: Extract order creation**
```python
def create_order(email, total):
    order = Order(email=email, total=total)
    db.session.add(order)
    db.session.commit()
    return order

def handle_order(data):
    validate_order_data(data)
    total = calculate_total_with_tax(data['items'])
    order = create_order(data['email'], total)
    
    # ... email sending unchanged
```

**Commit 4: Extract email notification**
```python
def send_order_confirmation(email, total, order_id):
    message = f"Thank you for your order of ${total}"
    send_email(email, "Order Confirmation", message)

def handle_order(data):
    validate_order_data(data)
    total = calculate_total_with_tax(data['items'])
    order = create_order(data['email'], total)
    send_order_confirmation(data['email'], total, order.id)
    
    return {'order_id': order.id, 'total': total}
```

**Final Result:**
```python
def handle_order(data):
    validate_order_data(data)
    total = calculate_total_with_tax(data['items'])
    order = create_order(data['email'], total)
    send_order_confirmation(data['email'], total, order.id)
    return {'order_id': order.id, 'total': total}
```

Each function is now single-purpose, testable, and reusable.

## Summary

Refactoring improves code structure without changing behavior. Keys to success:

1. **Write tests first** - safety net
2. **Small steps** - one change at a time
3. **Run tests frequently** - after every micro-change
4. **Commit often** - easy to revert
5. **Understand before changing** - don't refactor blindly
6. **Readability over cleverness** - optimize only when necessary
