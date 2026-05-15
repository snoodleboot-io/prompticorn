---
name: test-coverage-categories
description: Comprehensive systematic approach to achieving complete test coverage through structured category-based testing
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
subagents: [test/unit, test/integration, code/feature]
tools_needed: [read, write]
---

## Coverage Categories

A systematic approach to comprehensive test coverage. Work through these categories in order to ensure your tests catch all failure modes, edge cases, and security issues.

---

### Category 1: HAPPY PATH

**Definition:** Expected inputs produce expected outputs with no errors.

**Purpose:** Verify core functionality works under normal conditions.

**What to test:**
- Valid, typical inputs
- Expected return values
- Expected side effects (DB writes, API calls)
- Expected state changes

**Example:**

```python
def test_create_user_happy_path():
    """Test creating user with valid data succeeds."""
    user_data = {
        "email": "alice@example.com",
        "name": "Alice",
        "password": "SecurePass123!",
    }
    
    user = create_user(user_data)
    
    # Assert expected return value
    assert user.email == "alice@example.com"
    assert user.name == "Alice"
    assert user.id is not None
    
    # Assert expected side effects
    assert db.users.count() == 1
    assert user.created_at is not None
```

**Common mistakes:**
- ❌ Only testing happy path (ignoring edge cases)
- ❌ Not verifying side effects (DB writes, logs, events)
- ❌ Using unrealistic inputs (test with production-like data)

---

### Category 2: BOUNDARY VALUES

**Definition:** Test at the edges of valid ranges (min, max, exactly at limit, one over limit).

**Purpose:** Catch off-by-one errors, overflow issues, and boundary-related bugs.

**What to test:**
- Minimum valid value
- Maximum valid value
- Exactly at limit (e.g., string length exactly 255 if that's the limit)
- One below minimum (should fail)
- One above maximum (should fail)
- Empty collections (length 0)
- Single-item collections (length 1)

**Example:**

```python
def test_username_length_boundaries():
    """Test username validation at boundary values."""
    
    # Minimum length (3 chars) - valid
    assert is_valid_username("abc") is True
    
    # Below minimum (2 chars) - invalid
    assert is_valid_username("ab") is False
    
    # Maximum length (20 chars) - valid
    assert is_valid_username("a" * 20) is True
    
    # Above maximum (21 chars) - invalid
    assert is_valid_username("a" * 21) is False
    
    # Empty string - invalid
    assert is_valid_username("") is False


def test_pagination_boundaries():
    """Test pagination at boundary values."""
    
    # Page size = 1 (minimum)
    results = get_users(page=1, size=1)
    assert len(results) == 1
    
    # Page size = 100 (maximum)
    results = get_users(page=1, size=100)
    assert len(results) <= 100
    
    # Page size = 0 (invalid)
    with pytest.raises(ValidationError):
        get_users(page=1, size=0)
    
    # Page size = 101 (over max)
    with pytest.raises(ValidationError):
        get_users(page=1, size=101)
```

**Common boundary conditions:**
- String length (min, max)
- Numeric ranges (min, max, 0, negative, positive)
- Collection size (0, 1, max)
- Date ranges (start, end, exactly at cutoff)
- Pagination (first page, last page, page beyond last)

---

### Category 3: EMPTY / NULL / ZERO

**Definition:** Test with absent, null, zero, or empty values for each nullable input.

**Purpose:** Catch null pointer exceptions, division by zero, and missing data handling bugs.

**What to test:**
- `None` / `null` / `undefined` for nullable fields
- Empty strings (`""`)
- Empty collections (`[]`, `{}`)
- Zero values (`0`, `0.0`)
- False boolean values

**Example:**

```python
def test_calculate_average_with_empty_list():
    """Test average calculation with empty list."""
    # Empty list should raise or return None (depending on design)
    with pytest.raises(ValueError, match="Cannot calculate average of empty list"):
        calculate_average([])


def test_get_user_by_email_with_none():
    """Test user lookup with None email."""
    with pytest.raises(ValidationError, match="Email cannot be None"):
        get_user_by_email(None)


def test_format_address_with_missing_fields():
    """Test address formatting with missing optional fields."""
    address = {
        "street": "123 Main St",
        "city": "Springfield",
        "state": None,  # Optional field
        "zip": "",      # Empty string
    }
    
    # Should handle missing fields gracefully
    formatted = format_address(address)
    assert "123 Main St" in formatted
    assert "Springfield" in formatted
    # Should not include state or zip if missing


def test_divide_by_zero():
    """Test division with zero divisor."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

**Checklist for nullable inputs:**
- [ ] Test each nullable parameter with `None`
- [ ] Test each string parameter with `""`
- [ ] Test each list parameter with `[]`
- [ ] Test each dict parameter with `{}`
- [ ] Test each numeric parameter with `0`

---

### Category 4: ERROR CASES

**Definition:** Test when dependencies fail, resources are unavailable, or external calls raise exceptions.

**Purpose:** Verify error handling, logging, and graceful degradation.

**What to test:**
- Database connection failures
- Network timeouts
- External API errors (4xx, 5xx)
- File not found
- Permission denied
- Resource exhaustion (out of memory, disk full)
- Invalid state transitions

**Example:**

```python
def test_save_user_when_database_unavailable(mocker):
    """Test user save handles DB connection failure gracefully."""
    # Mock database to raise connection error
    mocker.patch.object(db, "save", side_effect=ConnectionError("DB unavailable"))
    
    user = User(email="alice@example.com")
    
    # Should raise specific error (not generic exception)
    with pytest.raises(DatabaseError, match="Failed to save user"):
        save_user(user)
    
    # Should log error
    assert "DB unavailable" in captured_logs


def test_fetch_user_when_api_returns_500(mocker):
    """Test user fetch handles API 500 error."""
    mocker.patch("requests.get", return_value=MockResponse(status=500))
    
    with pytest.raises(ExternalAPIError):
        fetch_user_from_external_api("user123")


def test_process_payment_when_gateway_timeout(mocker):
    """Test payment processing handles gateway timeout."""
    mocker.patch.object(
        payment_gateway,
        "charge",
        side_effect=TimeoutError("Gateway timeout"),
    )
    
    result = process_payment(amount=100, card_token="tok_123")
    
    # Should return failure result (not raise)
    assert result.status == "failed"
    assert "timeout" in result.error.lower()
    
    # Should not charge user
    assert payment_gateway.charge.call_count == 1  # No retries on timeout
```

**Common error scenarios:**
- Network failures (timeout, connection refused, DNS error)
- Authentication failures (invalid token, expired token)
- Authorization failures (insufficient permissions)
- Validation failures (invalid input format)
- Resource not found (404)
- Conflict (409 - duplicate, race condition)
- Rate limiting (429)
- Server errors (500, 502, 503)

---

### Category 5: CONCURRENT / ORDERING

**Definition:** If function has state or depends on execution order, test with different orderings or concurrent access.

**Purpose:** Catch race conditions, deadlocks, and state corruption from concurrent access.

**What to test:**
- Concurrent reads
- Concurrent writes
- Read-modify-write races
- Order of operations (does A→B produce same result as B→A?)
- State transitions (valid vs invalid sequences)

**Example:**

```python
import asyncio
import pytest

@pytest.mark.asyncio
async def test_concurrent_counter_increments():
    """Test counter handles concurrent increments correctly."""
    counter = Counter()
    
    # Run 100 concurrent increments
    tasks = [counter.increment() for _ in range(100)]
    await asyncio.gather(*tasks)
    
    # Should be exactly 100 (no lost updates)
    assert counter.value == 100


def test_order_state_transitions():
    """Test order state transitions enforce valid sequences."""
    order = Order()
    
    # Valid sequence: pending → confirmed → shipped → delivered
    order.confirm()
    assert order.status == OrderStatus.CONFIRMED
    
    order.ship()
    assert order.status == OrderStatus.SHIPPED
    
    order.deliver()
    assert order.status == OrderStatus.DELIVERED
    
    
def test_order_invalid_state_transition():
    """Test order prevents invalid state transitions."""
    order = Order()
    
    # Invalid: skip from pending directly to delivered
    with pytest.raises(InvalidStateTransitionError):
        order.deliver()  # Must confirm and ship first


@pytest.mark.asyncio
async def test_concurrent_stock_updates():
    """Test concurrent stock updates don't oversell."""
    product = Product(stock=10)
    
    # 20 concurrent purchase attempts (should only succeed 10 times)
    tasks = [product.purchase(quantity=1) for _ in range(20)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Exactly 10 should succeed
    successes = [r for r in results if not isinstance(r, Exception)]
    assert len(successes) == 10
    
    # Stock should be 0
    assert product.stock == 0
```

**When to test concurrency:**
- ✅ Shared mutable state (counters, caches, inventories)
- ✅ Database writes (race conditions, lost updates)
- ✅ File writes (concurrent modifications)
- ✅ Resource pools (connection pools, thread pools)

**When to skip:**
- ❌ Pure functions (no side effects)
- ❌ Read-only operations
- ❌ Single-threaded contexts

---

### Category 6: AUTHORIZATION BOUNDARIES

**Definition:** Test that functions enforce access control (who can call it, what they can access).

**Purpose:** Catch security vulnerabilities where unauthorized users can access restricted resources.

**What to test:**
- Unauthenticated access (no token)
- Authenticated but unauthorized (wrong role/permissions)
- Accessing resources owned by other users
- Privilege escalation attempts

**Example:**

```python
def test_get_user_requires_authentication():
    """Test user retrieval requires authentication."""
    # No auth token provided
    with pytest.raises(Unauthenticated):
        get_user(user_id="123", auth_token=None)


def test_update_user_requires_ownership():
    """Test user update requires ownership or admin role."""
    alice = create_user(email="alice@example.com")
    bob = create_user(email="bob@example.com")
    
    # Bob tries to update Alice's profile (should fail)
    with pytest.raises(Forbidden):
        update_user(
            user_id=alice.id,
            data={"name": "Hacked"},
            auth_user_id=bob.id,
        )


def test_delete_order_requires_admin_role():
    """Test order deletion requires admin role."""
    user = create_user(email="user@example.com", role="user")
    admin = create_user(email="admin@example.com", role="admin")
    
    order = create_order(user_id=user.id)
    
    # Regular user cannot delete order
    with pytest.raises(Forbidden):
        delete_order(order_id=order.id, auth_user_id=user.id)
    
    # Admin can delete order
    delete_order(order_id=order.id, auth_user_id=admin.id)
    assert get_order(order.id) is None


def test_list_users_filters_by_organization():
    """Test user list enforces organization boundary."""
    org_a = create_organization(name="Org A")
    org_b = create_organization(name="Org B")
    
    alice = create_user(email="alice@a.com", org_id=org_a.id)
    bob = create_user(email="bob@b.com", org_id=org_b.id)
    
    # Alice should only see users in Org A
    users = list_users(auth_user_id=alice.id)
    assert len(users) == 1
    assert users[0].id == alice.id
```

**Authorization patterns to test:**
- Resource ownership (user can only access their own data)
- Role-based access (admin vs user vs guest)
- Permission-based access (specific permissions required)
- Organization/tenant boundaries (multi-tenant isolation)
- Hierarchical access (manager can access subordinates' data)

---

### Category 7: ADVERSARIAL INPUTS

**Definition:** Test with malicious or malformed inputs designed to exploit vulnerabilities.

**Purpose:** Catch security vulnerabilities (SQL injection, XSS, path traversal, etc.) and robustness issues.

**What to test:**
- **SQL injection:** SQL fragments in string inputs
- **XSS:** Script tags, JavaScript in text fields
- **Path traversal:** `../../../etc/passwd` in file paths
- **Command injection:** Shell metacharacters in system calls
- **Unicode/emoji:** Non-ASCII characters
- **Control characters:** Null bytes (`\0`), newlines, tabs
- **Extremely long strings:** 1MB strings, 10K-character names
- **Format string attacks:** `%s`, `%n` in format strings
- **LDAP injection:** LDAP query fragments
- **XML injection:** XML entities, CDATA

**Example:**

```python
def test_search_users_with_sql_injection_attempt():
    """Test user search is protected against SQL injection."""
    # Attempt SQL injection
    malicious_query = "'; DROP TABLE users; --"
    
    # Should NOT execute SQL, should treat as literal string
    results = search_users(query=malicious_query)
    
    # Should return empty results (no match) or error, NOT drop table
    assert isinstance(results, list)
    # Verify table still exists
    assert db.table_exists("users")


def test_create_user_with_xss_in_name():
    """Test user creation sanitizes XSS in name field."""
    malicious_name = "<script>alert('XSS')</script>"
    
    user = create_user(email="test@example.com", name=malicious_name)
    
    # Should escape or strip script tags
    assert "<script>" not in user.name
    assert user.name in [
        "&lt;script&gt;alert('XSS')&lt;/script&gt;",  # Escaped
        "alert('XSS')",  # Stripped tags
        "",  # Rejected entirely
    ]


def test_read_file_with_path_traversal_attempt():
    """Test file read prevents path traversal."""
    malicious_path = "../../../etc/passwd"
    
    # Should reject or normalize path
    with pytest.raises(SecurityError, match="Invalid file path"):
        read_file(malicious_path)


def test_username_with_unicode_and_emoji():
    """Test username handles unicode and emoji correctly."""
    unicode_names = [
        "用户名",  # Chinese characters
        "Müller",  # Umlaut
        "José",  # Accented character
        "🎉🎊",  # Emoji
        "café",  # Combining characters
    ]
    
    for name in unicode_names:
        # Should either accept or reject gracefully (not crash)
        try:
            user = create_user(email=f"{name}@example.com", name=name)
            assert user.name is not None
        except ValidationError as e:
            # If rejected, should have clear error message
            assert "character" in str(e).lower() or "unicode" in str(e).lower()


def test_comment_with_extremely_long_string():
    """Test comment field handles extremely long input."""
    # 10MB string
    huge_comment = "a" * (10 * 1024 * 1024)
    
    # Should reject or truncate
    with pytest.raises(ValidationError, match="too long|exceeds maximum"):
        create_comment(text=huge_comment)


def test_email_with_null_bytes():
    """Test email validation rejects null bytes."""
    malicious_email = "test@example.com\x00@evil.com"
    
    # Should reject null bytes
    with pytest.raises(ValidationError):
        create_user(email=malicious_email)
```

**Adversarial input checklist:**
- [ ] SQL injection patterns (`'; DROP TABLE`, `1' OR '1'='1`)
- [ ] XSS patterns (`<script>`, `javascript:`, `onerror=`)
- [ ] Path traversal (`../`, `..\\`, absolute paths)
- [ ] Command injection (`;`, `|`, `&&`, backticks)
- [ ] Unicode edge cases (emoji, combining characters, RTL)
- [ ] Control characters (null byte, newline, carriage return)
- [ ] Extremely long strings (1MB+)
- [ ] Format string attacks (`%s`, `%n`, `%x`)

---

## Workflow

### Step 1: Create Category Checklist

For the function/module being tested, create a checklist:

```markdown
## Test Coverage for `create_order()`

- [ ] HAPPY PATH - Valid order creation
- [ ] BOUNDARY VALUES - Min/max item count, price ranges
- [ ] EMPTY/NULL - Empty items list, null user_id
- [ ] ERROR CASES - DB failure, payment gateway error
- [ ] CONCURRENT - Multiple orders from same user
- [ ] AUTHORIZATION - Only authenticated users can create orders
- [ ] ADVERSARIAL - XSS in product name, huge item counts
```

### Step 2: Implement Tests for Each Category

Work through the checklist, implementing tests for each applicable category.

### Step 3: Document Excluded Categories

If a category doesn't apply, document why:

```markdown
## Test Coverage for `calculate_tax()`

- [x] HAPPY PATH - Valid tax calculation
- [x] BOUNDARY VALUES - 0 amount, max amount
- [x] EMPTY/NULL - null amount
- [x] ERROR CASES - Invalid tax rate
- [ ] CONCURRENT - N/A (pure function, no state)
- [ ] AUTHORIZATION - N/A (internal utility, no auth)
- [ ] ADVERSARIAL - N/A (validated numeric input only)
```

### Step 4: Flag Coverage Gaps

If you can't test a category, explain why and how the risk is mitigated:

```markdown
## Test Coverage for `process_payment()`

- [x] HAPPY PATH
- [x] ERROR CASES - Gateway timeout, card declined
- [ ] CONCURRENT - **GAP**: Concurrent payments from same user not tested
  - **Mitigation**: Payment gateway handles idempotency
  - **Risk**: Low (gateway prevents double-charge)
  - **TODO**: Add test when we migrate to new gateway (Q3 2026)
```

---

## Common Mistakes

### ❌ Mistake 1: Only Testing Happy Path

**Problem:** Tests pass with valid inputs but fail in production with edge cases.

**Fix:** Use this category framework to ensure comprehensive coverage.

---

### ❌ Mistake 2: Skipping Boundary Value Tests

**Problem:** Off-by-one errors, overflow bugs slip through.

**Example:**
- Password length validation allows 21-character password when max is 20
- Pagination returns 101 items when max is 100

**Fix:** Always test min, max, exactly-at-limit, and one-over-limit.

---

### ❌ Mistake 3: Not Testing Error Cases

**Problem:** Production errors crash the app instead of being handled gracefully.

**Fix:** Mock dependencies to throw exceptions and verify error handling.

---

### ❌ Mistake 4: Ignoring Security Tests

**Problem:** SQL injection, XSS, path traversal vulnerabilities discovered in production.

**Fix:** Test adversarial inputs for all user-facing functions.

---

## Summary

**Seven Categories for Comprehensive Coverage:**

1. **HAPPY PATH** - Normal operation
2. **BOUNDARY VALUES** - Edge cases (min, max, limits)
3. **EMPTY/NULL/ZERO** - Missing data
4. **ERROR CASES** - Failures and exceptions
5. **CONCURRENT/ORDERING** - Race conditions, state transitions
6. **AUTHORIZATION** - Access control
7. **ADVERSARIAL** - Security vulnerabilities

**Usage:**
1. Create category checklist for each function/module
2. Implement tests for applicable categories
3. Document excluded categories with rationale
4. Flag coverage gaps and mitigation strategies

**Benefits:**
- Systematic approach prevents missed edge cases
- Security testing is built-in
- Clear documentation of test coverage
- Easy to identify gaps and risks
