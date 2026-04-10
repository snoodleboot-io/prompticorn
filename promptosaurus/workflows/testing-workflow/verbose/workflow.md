---
name: Testing Workflow
version: 1.0
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
subagents: [test/unit, test/integration, code/feature]
---

# Testing Workflow (Verbose)

## Overview

Comprehensive testing strategy covering unit tests, integration tests, and test quality verification.

## Test Organization

### Directory Structure
```
tests/
├── unit/           # Fast, isolated tests
├── integration/    # Multi-component tests
├── slow/          # Long-running tests
└── fixtures/      # Shared test data
```

### AAA Pattern

**Arrange → Act → Assert**

```python
def test_user_creation_sets_default_role():
    # Arrange
    user_service = UserService(db_session)
    user_data = {"email": "test@example.com", "name": "Test User"}
    
    # Act
    user = user_service.create_user(user_data)
    
    # Assert
    assert user.role == "member"
    assert user.email == "test@example.com"
    assert user.created_at is not None
```

## Step 1: Happy Path Tests

### Goal
Verify that the primary use case works with valid inputs.

### Implementation

**Test the main workflow:**
- Valid inputs produce expected outputs
- Side effects occur as expected (DB writes, API calls)
- Return values have correct structure and types

**Naming Convention:**
```python
# Good - describes what and when
def test_user_login_succeeds_with_valid_credentials()
def test_order_total_includes_tax_and_shipping()
def test_email_notification_sent_on_password_reset()

# Bad - vague
def test_login()
def test_calculate()
def test_send()
```

**Example (Python):**
```python
def test_checkout_creates_order_with_correct_total():
    # Arrange
    cart = ShoppingCart()
    cart.add_item(Product(id=1, price=10.00), quantity=2)
    cart.add_item(Product(id=2, price=5.00), quantity=1)
    
    # Act
    order = checkout_service.process(cart, tax_rate=0.08)
    
    # Assert
    assert order.subtotal == 25.00
    assert order.tax == 2.00
    assert order.total == 27.00
    assert order.status == "pending"
    assert len(order.items) == 2
```

**Example (TypeScript):**
```typescript
test('checkout creates order with correct total', () => {
  // Arrange
  const cart = new ShoppingCart();
  cart.addItem({ id: 1, price: 10.00 }, 2);
  cart.addItem({ id: 2, price: 5.00 }, 1);
  
  // Act
  const order = checkoutService.process(cart, { taxRate: 0.08 });
  
  // Assert
  expect(order.subtotal).toBe(25.00);
  expect(order.tax).toBe(2.00);
  expect(order.total).toBe(27.00);
  expect(order.status).toBe('pending');
  expect(order.items).toHaveLength(2);
});
```

## Step 2: Boundary Value Testing

### Goal
Test edge cases at the limits of valid input ranges.

### Boundary Types

**Numeric Boundaries:**
- Minimum value (0, -1, MIN_INT)
- Maximum value (100, MAX_INT)
- Just below minimum (-1 for unsigned)
- Just above maximum (101 for 0-100 range)

**Collection Boundaries:**
- Empty collection ([], {})
- Single element ([1])
- Maximum size (if there's a limit)

**String Boundaries:**
- Empty string ""
- Single character "a"
- Maximum length (if validated)
- Special characters "@#$%"

**Example (Python):**
```python
def test_discount_calculation_at_boundaries():
    calculator = DiscountCalculator()
    
    # Zero amount
    assert calculator.apply_discount(0, 0.1) == 0
    
    # Minimum discount (0%)
    assert calculator.apply_discount(100, 0.0) == 100
    
    # Maximum discount (100%)
    assert calculator.apply_discount(100, 1.0) == 0
    
    # Just below max (99%)
    assert calculator.apply_discount(100, 0.99) == 1
```

**Example (TypeScript):**
```typescript
describe('pagination boundaries', () => {
  test('page 1 with single item', () => {
    const result = paginate(items, { page: 1, perPage: 10 });
    expect(result.currentPage).toBe(1);
    expect(result.totalPages).toBe(1);
  });
  
  test('last page with partial items', () => {
    const items = Array(25).fill('item');
    const result = paginate(items, { page: 3, perPage: 10 });
    expect(result.items).toHaveLength(5); // Last 5 items
  });
});
```

## Step 3: Empty/Null/Zero Cases

### Goal
Verify handling of absence - null, undefined, empty, zero.

### Test Cases

**Nullable Parameters:**
```python
def test_user_creation_with_optional_fields_missing():
    user = User(email="test@example.com", name=None, phone=None)
    assert user.name is None  # Should not error
    assert user.phone is None
```

**Empty Collections:**
```typescript
test('processing empty cart returns empty order', () => {
  const cart = new ShoppingCart(); // Empty
  const order = checkoutService.process(cart);
  
  expect(order.items).toHaveLength(0);
  expect(order.total).toBe(0);
});
```

**Zero Values:**
```python
def test_transfer_zero_amount_returns_error():
    with pytest.raises(ValueError, match="Amount must be positive"):
        account.transfer(amount=0, to_account=other_account)
```

**Missing Fields:**
```typescript
test('API rejects request with missing required field', async () => {
  const response = await api.createUser({ email: 'test@example.com' }); // Missing 'name'
  
  expect(response.status).toBe(400);
  expect(response.error).toContain('name is required');
});
```

## Step 4: Error Cases and Exception Handling

### Goal
Verify that errors are raised appropriately and contain useful information.

### Error Testing Patterns

**Python:**
```python
def test_invalid_email_raises_validation_error():
    with pytest.raises(ValidationError) as exc_info:
        User(email="not-an-email", name="Test")
    
    assert "Invalid email format" in str(exc_info.value)

def test_missing_file_returns_none():
    result = file_service.read("nonexistent.txt")
    assert result is None  # Graceful handling, not exception
```

**TypeScript:**
```typescript
test('division by zero throws error', () => {
  expect(() => calculator.divide(10, 0)).toThrow('Cannot divide by zero');
});

test('network failure retries then fails gracefully', async () => {
  mockApi.get.mockRejectedValue(new Error('Network error'));
  
  const result = await service.fetchData();
  
  expect(result).toBeNull();
  expect(mockApi.get).toHaveBeenCalledTimes(3); // Retried 3 times
});
```

## Step 5: Mocking and Fixtures

### When to Mock

**Always Mock:**
- External APIs and HTTP requests
- Database connections (use test DB or transactions)
- Filesystem operations (use temp directories or mocks)
- Current time (for deterministic tests)
- Random number generation

**Python Mocking:**
```python
from unittest.mock import Mock, patch

def test_weather_service_calls_api():
    # Mock HTTP client
    mock_http = Mock()
    mock_http.get.return_value = {"temp": 72, "condition": "sunny"}
    
    service = WeatherService(http_client=mock_http)
    result = service.get_forecast("Chicago")
    
    mock_http.get.assert_called_once_with("/weather?city=Chicago")
    assert result["temp"] == 72

@patch('time.time', return_value=1609459200)  # Fixed timestamp
def test_token_expiration(mock_time):
    token = generate_token(expires_in=3600)
    assert token.expires_at == 1609462800
```

**TypeScript Mocking (Vitest):**
```typescript
import { vi } from 'vitest';

test('email service sends notification', async () => {
  const mockMailer = {
    send: vi.fn().mockResolvedValue({ success: true })
  };
  
  const service = new NotificationService(mockMailer);
  await service.notifyUser(user, 'Welcome!');
  
  expect(mockMailer.send).toHaveBeenCalledWith({
    to: user.email,
    subject: 'Welcome!',
    body: expect.any(String)
  });
});
```

### Fixtures and Factories

**Python (pytest fixtures):**
```python
@pytest.fixture
def sample_user():
    return User(id=1, email="test@example.com", name="Test User")

@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.rollback()  # Cleanup
    session.close()

def test_user_update(db_session, sample_user):
    db_session.add(sample_user)
    sample_user.name = "Updated Name"
    db_session.commit()
    
    assert db_session.query(User).first().name == "Updated Name"
```

## Step 6: Coverage Analysis

### Running Coverage

**Python (pytest-cov):**
```bash
pytest --cov=src --cov-branch --cov-report=html
```

**TypeScript (Vitest):**
```bash
vitest run --coverage
```

### Coverage Targets

| Metric | Target | Critical Code Target |
|--------|--------|---------------------|
| Line Coverage | 80% | 95% |
| Branch Coverage | 70% | 90% |
| Function Coverage | 90% | 100% |

### Interpreting Coverage

**Good Coverage:**
```python
# 100% coverage - all paths tested
def calculate_discount(amount, is_member):
    if is_member:
        return amount * 0.9  # ✓ Tested
    return amount            # ✓ Tested
```

**Missing Branch:**
```python
# 50% branch coverage - member path not tested
def calculate_discount(amount, is_member):
    if is_member:
        return amount * 0.9  # ✗ NOT tested
    return amount            # ✓ Tested
```

## Step 7: Integration Tests

### Characteristics

- Test multiple components together
- Use real implementations where possible
- Mock only external services (third-party APIs)
- Include database operations (use test DB or transactions)

**Example (Python with test DB):**
```python
@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()

def test_user_registration_flow(test_db):
    # Integration test: controller + service + repository + DB
    user_service = UserService(test_db)
    email_service = FakeEmailService()  # Fake, not mock
    controller = UserController(user_service, email_service)
    
    response = controller.register({
        "email": "new@example.com",
        "password": "securepass123"
    })
    
    assert response.status == 201
    assert test_db.query(User).count() == 1
    assert email_service.sent_emails[0]["to"] == "new@example.com"
```

## Property-Based Testing

### Concept
Generate hundreds of random inputs to find edge cases.

**Python (Hypothesis):**
```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert a + b == b + a

@given(st.text(), st.text())
def test_string_concat_length(s1, s2):
    result = s1 + s2
    assert len(result) == len(s1) + len(s2)
```

## Mutation Testing

### Purpose
Verify that tests actually catch bugs.

**Process:**
1. Introduce small bugs (mutations) into code
2. Run tests - they should FAIL
3. If tests still pass, mutation "survived" - tests are weak

**Python (mutmut):**
```bash
pip install mutmut
mutmut run
mutmut report
```

**Target:** 80%+ mutation score on critical code

## Common Testing Mistakes

### Mistake 1: Testing Implementation, Not Behavior

❌ **Bad:**
```python
def test_user_service_calls_repository():
    mock_repo = Mock()
    service = UserService(mock_repo)
    service.get_user(1)
    
    mock_repo.find_by_id.assert_called_once()  # Testing internal call
```

✓ **Good:**
```python
def test_user_service_returns_user_when_found():
    repo = FakeUserRepository(users=[User(id=1, name="Test")])
    service = UserService(repo)
    
    user = service.get_user(1)
    
    assert user.name == "Test"  # Testing behavior
```

### Mistake 2: Shared Mutable State

❌ **Bad:**
```python
global_user = User(id=1, name="Test")

def test_user_update():
    global_user.name = "Updated"  # Mutates global state
    assert global_user.name == "Updated"

def test_user_creation():
    assert global_user.name == "Test"  # FAILS if run after test_user_update
```

✓ **Good:**
```python
@pytest.fixture
def user():
    return User(id=1, name="Test")  # Fresh instance per test

def test_user_update(user):
    user.name = "Updated"
    assert user.name == "Updated"

def test_user_creation(user):
    assert user.name == "Test"  # Always passes
```

### Mistake 3: Over-Mocking

❌ **Bad:**
```python
def test_calculate_total():
    mock_math = Mock()
    mock_math.add.return_value = 15  # Mocking basic math!
    
    result = mock_math.add(10, 5)
    assert result == 15  # Useless test
```

✓ **Good:**
```python
def test_calculate_total():
    cart = ShoppingCart()
    cart.add_item(10)
    cart.add_item(5)
    
    assert cart.total() == 15  # Real implementation
```

### Mistake 4: Unclear Test Names

❌ **Bad:**
```python
def test_user(): ...
def test_create(): ...
def test_bad_input(): ...
```

✓ **Good:**
```python
def test_user_login_succeeds_with_valid_credentials(): ...
def test_user_creation_fails_with_duplicate_email(): ...
def test_discount_calculation_rejects_negative_amount(): ...
```

### Mistake 5: Not Testing Error Messages

❌ **Bad:**
```python
def test_invalid_email():
    with pytest.raises(ValueError):
        User(email="invalid")
```

✓ **Good:**
```python
def test_invalid_email():
    with pytest.raises(ValueError, match="Invalid email format"):
        User(email="invalid")
```

### Mistake 6: Ignoring Test Performance

❌ **Bad:**
```python
def test_user_query():
    time.sleep(5)  # Simulating slow DB
    # Test takes 5 seconds
```

✓ **Good:**
```python
@pytest.mark.slow  # Mark slow tests
def test_user_query_performance():
    # Or move to integration test suite
    # Or use faster in-memory DB for unit tests
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests with coverage
        run: pytest --cov=src --cov-branch --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Test Frameworks by Language

| Language | Unit Testing | Mocking | Coverage |
|----------|-------------|---------|----------|
| Python | pytest | unittest.mock | pytest-cov |
| TypeScript | Vitest / Jest | vitest/mock | @vitest/coverage-v8 |
| JavaScript | Vitest / Jest | jest.mock | @vitest/coverage-v8 |
| Go | testing | testify/mock | go test -cover |
| Rust | cargo test | mockall | cargo tarpaulin |
| Java | JUnit 5 | Mockito | JaCoCo |
| C# | xUnit / NUnit | Moq | Coverlet |
| PHP | PHPUnit | PHPUnit mocks | PHPUnit coverage |
| Ruby | RSpec | rspec-mocks | SimpleCov |

## Summary Checklist

Before completing testing:

- [ ] Happy path tested with valid inputs
- [ ] Boundary values tested (min, max, empty)
- [ ] Null/undefined/zero cases handled
- [ ] Error cases raise appropriate exceptions
- [ ] Error messages are descriptive
- [ ] Coverage ≥ 80% line, ≥ 70% branch
- [ ] Tests are isolated (no shared state)
- [ ] External dependencies mocked
- [ ] Test names are descriptive
- [ ] Tests pass in any order
- [ ] Integration tests cover key workflows
- [ ] CI runs all tests on every commit
