---
name: test-aaa-structure
description: Apply Arrange-Act-Assert pattern for clear, maintainable tests with detailed guidance
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
subagents: [test/unit, test/integration, code/feature]
tools_needed: [read, write]
---

## Instructions

### The AAA Pattern

**Arrange-Act-Assert** (AAA) is the gold standard for structuring tests. It makes tests:
- Easy to read and understand
- Simple to maintain
- Clear about what's being tested

### The Three Phases

#### 1. Arrange: Set Up

**Purpose:** Prepare everything needed for the test.

**What to do:**
- Create test data
- Set up mock objects
- Initialize dependencies
- Configure system state

**Example:**
```python
# Arrange
user = User(id="123", name="Alice", role="admin")
db.save(user)
mock_logger = Mock(Logger)
```

---

#### 2. Act: Execute

**Purpose:** Call the thing you're testing.

**What to do:**
- Call ONE function or method
- Capture the result
- Keep this section minimal (usually 1 line)

**Example:**
```python
# Act
result = get_user_by_id("123")
```

**Common Mistake:** ❌ Calling multiple functions in Act
**Correct:** ✅ One function call - if you need multiple, you need multiple tests

---

#### 3. Assert: Verify

**Purpose:** Check that the behavior is correct.

**What to do:**
- Verify return values
- Check side effects
- Validate state changes
- Confirm error handling

**Example:**
```python
# Assert
assert result.name == "Alice"
assert result.role == "admin"
assert mock_logger.log.called_once()
```

---

## Key Rules

### Rule 1: One Logical Assertion Per Test

Each test should verify ONE behavior.

**✅ Good:**
```python
def test_get_user_returns_correct_name():
    user = User(id="1", name="Alice")
    db.save(user)
    result = get_user_by_id("1")
    assert result.name == "Alice"

def test_get_user_returns_correct_role():
    user = User(id="1", role="admin")
    db.save(user)
    result = get_user_by_id("1")
    assert result.role == "admin"
```

**❌ Bad:**
```python
def test_get_user():  # What does this test? Unclear!
    user = User(id="1", name="Alice", role="admin")
    db.save(user)
    result = get_user_by_id("1")
    assert result.name == "Alice"  # Multiple unrelated assertions
    assert result.role == "admin"
    assert result.id == "1"
```

**Exception:** Multiple assertions are OK if testing a single concept:
```python
def test_user_creation_sets_all_required_fields():
    user = create_user(name="Alice", email="alice@example.com")
    assert user.name == "Alice"  # All part of "creation"
    assert user.email == "alice@example.com"
    assert user.created_at is not None
```

---

### Rule 2: Descriptive Test Names

Test names should read like documentation.

**Pattern:** `test_{what}_{does}_{when}_{condition}`

**✅ Good:**
- `test_get_user_returns_user_when_found`
- `test_get_user_returns_none_when_not_found`
- `test_get_user_raises_error_when_database_unavailable`

**❌ Bad:**
- `test_get_user` (what does it test?)
- `test1`, `test2` (meaningless)
- `test_success` (success of what?)

---

### Rule 3: Visual Separation

Separate AAA sections for readability.

**✅ Option 1: Comments**
```python
def test_calculate_total_includes_tax():
    # Arrange
    cart = Cart()
    cart.add_item(Item(price=100))
    
    # Act
    total = cart.calculate_total(tax_rate=0.1)
    
    # Assert
    assert total == 110
```

**✅ Option 2: Blank lines**
```python
def test_calculate_total_includes_tax():
    cart = Cart()
    cart.add_item(Item(price=100))
    
    total = cart.calculate_total(tax_rate=0.1)
    
    assert total == 110
```

**❌ Bad: No separation**
```python
def test_calculate_total_includes_tax():
    cart = Cart()
    cart.add_item(Item(price=100))
    total = cart.calculate_total(tax_rate=0.1)
    assert total == 110  # Hard to see structure
```

---

## Common Patterns

### Testing Exceptions

```python
def test_divide_raises_error_when_divisor_is_zero():
    # Arrange
    calculator = Calculator()
    
    # Act & Assert (combined for exceptions)
    with pytest.raises(ZeroDivisionError):
        calculator.divide(10, 0)
```

### Testing Side Effects

```python
def test_save_user_writes_to_database():
    # Arrange
    user = User(id="123", name="Alice")
    db = MockDatabase()
    
    # Act
    save_user(user, db)
    
    # Assert
    assert db.write_called_with(user)
```

### Testing Async Functions

```python
async def test_fetch_user_calls_api():
    # Arrange
    mock_client = Mock(ApiClient)
    mock_client.get.return_value = {"name": "Alice"}
    
    # Act
    result = await fetch_user("123", mock_client)
    
    # Assert
    assert result.name == "Alice"
    assert mock_client.get.called_with("/users/123")
```

---

## Anti-Patterns to Avoid

### ❌ Testing Implementation Instead of Behavior

**Bad:**
```python
def test_sort_uses_quicksort():  # Implementation detail!
    result = my_sort([3, 1, 2])
    assert used_quicksort_algorithm(result)
```

**Good:**
```python
def test_sort_returns_sorted_list():  # Behavior!
    result = my_sort([3, 1, 2])
    assert result == [1, 2, 3]
```

### ❌ Too Much Setup

**Bad:**
```python
def test_user_login():
    # Arrange (50 lines of setup!)
    db = Database()
    db.connect()
    db.create_schema()
    users_table = db.create_table("users")
    # ... 40 more lines ...
```

**Good:**
```python
def test_user_login():
    # Arrange (use fixtures/factories)
    user = create_test_user()  # Helper function
    # Act & Assert...
```

### ❌ Multiple Acts

**Bad:**
```python
def test_user_workflow():
    user = create_user()  # Act 1
    login(user)  # Act 2  
    result = get_profile(user)  # Act 3
    assert result.name == "Alice"
```

**Good:** Split into 3 tests (one per Act)

---

## Quick Reference

```
Arrange → Set up
Act     → Execute
Assert  → Verify
```

**Remember:**
- ✅ One behavior per test
- ✅ Descriptive test names
- ✅ Visual AAA separation
- ❌ No implementation testing
- ❌ No multiple Acts
