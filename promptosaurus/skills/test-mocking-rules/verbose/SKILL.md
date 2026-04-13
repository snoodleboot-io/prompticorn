---
name: test-mocking-rules
description: Comprehensive guidelines for when and how to use mocks, stubs, and fakes in tests
languages: [python, typescript, javascript, go, rust, java, csharp, php, ruby]
subagents: [test/unit, test/integration]
tools_needed: []
---

## Test Mocking Rules

Mocking is a testing technique that replaces real implementations with controlled substitutes. This guide defines when to mock, what to mock, and common anti-patterns to avoid.

---

## Core Principle: Mock at Boundaries, Not Internals

**The Golden Rule:** Mock only external dependencies (I/O boundaries), never internal logic.

**Why?**
- Mocking internal logic = testing implementation, not behavior
- Over-mocking = brittle tests that break when refactoring
- Under-mocking = slow, flaky tests dependent on external services

---

## When to Mock

### ✓ Mock These (Process Boundaries)

#### 1. Database Connections
**Reason:** Tests should be fast, isolated, and not require running database

**Example (Python with pytest):**
```python
from unittest.mock import Mock
import pytest

def test_get_user_by_id():
    # Mock the database connection
    mock_db = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = {
        'id': '123',
        'email': 'test@example.com'
    }
    
    user_service = UserService(db=mock_db)
    user = user_service.get_user_by_id('123')
    
    assert user['email'] == 'test@example.com'
    mock_db.query.assert_called_once()
```

**Exception:** Integration tests should use REAL database (test database or in-memory)

---

#### 2. Network Calls (HTTP, External APIs)
**Reason:** External APIs are slow, cost money, have rate limits, can be down

**Example (TypeScript with Vitest):**
```typescript
import { describe, it, expect, vi } from 'vitest'
import { PaymentService } from './payment-service'

describe('PaymentService', () => {
  it('processes payment via Stripe API', async () => {
    // Mock the HTTP client
    const mockHttpClient = {
      post: vi.fn().mockResolvedValue({
        data: { id: 'charge_123', status: 'succeeded' }
      })
    }
    
    const paymentService = new PaymentService(mockHttpClient)
    const result = await paymentService.charge(100, 'tok_visa')
    
    expect(result.status).toBe('succeeded')
    expect(mockHttpClient.post).toHaveBeenCalledWith(
      '/v1/charges',
      expect.objectContaining({ amount: 100, source: 'tok_visa' })
    )
  })
})
```

**Better Alternative:** Use a mock server library (MSW, nock, WireMock)

---

#### 3. Filesystem Operations
**Reason:** File I/O is slow, tests should not depend on disk state

**Example (Python):**
```python
from unittest.mock import mock_open, patch

def test_read_config():
    mock_file_content = "database_url=postgres://localhost"
    
    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        config = ConfigLoader.load('/etc/config.txt')
        assert config['database_url'] == 'postgres://localhost'
```

**Alternative:** Use temp directories for integration tests

---

#### 4. Time/Date Functions
**Reason:** Tests should be deterministic, not dependent on current time

**Example (Python):**
```python
from unittest.mock import patch
from datetime import datetime

def test_is_expired():
    # Mock datetime.now() to return fixed time
    fixed_time = datetime(2026, 1, 1, 12, 0, 0)
    
    with patch('myapp.utils.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time
        
        token = Token(expires_at=datetime(2025, 12, 31))
        assert token.is_expired() is True
```

**Better Alternative:** Inject clock/time provider

---

#### 5. Random Number Generation
**Reason:** Tests should be reproducible

**Example (TypeScript):**
```typescript
import { vi } from 'vitest'

it('generates random session ID', () => {
  vi.spyOn(Math, 'random').mockReturnValue(0.5)
  
  const sessionId = generateSessionId()
  
  expect(sessionId).toBe('expected-deterministic-id')
})
```

**Better Alternative:** Inject random number generator

---

#### 6. External Services (Email, SMS, Cloud Storage)
**Reason:** Should not send real emails/SMS during tests

**Example (Python):**
```python
from unittest.mock import Mock

def test_send_welcome_email():
    mock_email_client = Mock()
    
    user_service = UserService(email_client=mock_email_client)
    user_service.register_user('test@example.com', 'password')
    
    mock_email_client.send.assert_called_once_with(
        to='test@example.com',
        subject='Welcome!',
        body=expect.any(str)
    )
```

---

## What NOT to Mock

### ✗ Never Mock These

#### 1. The Thing Under Test
**Problem:** Defeats the purpose of the test

❌ **Wrong:**
```python
def test_calculate_total():
    mock_calculator = Mock()
    mock_calculator.calculate_total.return_value = 100
    
    # Not testing anything!
    assert mock_calculator.calculate_total([10, 20, 30]) == 100
```

✓ **Correct:**
```python
def test_calculate_total():
    calculator = Calculator()
    
    # Actually tests the logic
    assert calculator.calculate_total([10, 20, 30]) == 60
```

---

#### 2. Internal Helper Functions
**Problem:** Tests implementation, not behavior

❌ **Wrong:**
```python
def test_process_order():
    mock_validate = Mock(return_value=True)
    
    with patch('myapp.order.validate_order', mock_validate):
        result = process_order(order_data)
        
    # Not testing validation logic!
    assert result.status == 'processed'
```

✓ **Correct:**
```python
def test_process_order():
    # Test through public interface - validation happens internally
    result = process_order(valid_order_data)
    assert result.status == 'processed'
    
def test_process_order_with_invalid_data():
    # Test validation by providing invalid data
    with pytest.raises(ValidationError):
        process_order(invalid_order_data)
```

**Lesson:** Test internal helpers indirectly through public API

---

#### 3. Your Own Database (in integration tests)
**Problem:** Integration tests should test real database interactions

❌ **Wrong:**
```typescript
// Integration test with mocked database
it('creates user in database', async () => {
  const mockDb = { insert: vi.fn().mockResolvedValue({ id: '123' }) }
  
  const userRepo = new UserRepository(mockDb)
  await userRepo.create({ email: 'test@example.com' })
  
  // Not actually testing database!
})
```

✓ **Correct:**
```typescript
// Integration test with real test database
it('creates user in database', async () => {
  const testDb = await setupTestDatabase()
  
  const userRepo = new UserRepository(testDb)
  const user = await userRepo.create({ email: 'test@example.com' })
  
  // Verify by querying database
  const found = await testDb.query('SELECT * FROM users WHERE id = $1', [user.id])
  expect(found.email).toBe('test@example.com')
  
  await teardownTestDatabase(testDb)
})
```

**For unit tests:** Mock database. For integration tests: Use real database.

---

#### 4. Language Standard Library
**Problem:** Standard library is well-tested, mocking adds no value

❌ **Wrong:**
```python
from unittest.mock import patch

def test_parse_json():
    with patch('json.loads', return_value={'key': 'value'}):
        result = parse_config('{"key": "value"}')
        
    # Not testing anything - json.loads is mocked!
```

✓ **Correct:**
```python
def test_parse_json():
    # Use real json.loads - it's fast and reliable
    result = parse_config('{"key": "value"}')
    assert result['key'] == 'value'
```

---

#### 5. Simple Data Structures
**Problem:** Mocking adds complexity without benefit

❌ **Wrong:**
```typescript
it('calculates cart total', () => {
  const mockCart = {
    items: vi.fn().mockReturnValue([
      { price: 10 },
      { price: 20 }
    ])
  }
  
  // Overly complex
})
```

✓ **Correct:**
```typescript
it('calculates cart total', () => {
  const cart = new Cart()
  cart.addItem({ price: 10 })
  cart.addItem({ price: 20 })
  
  expect(cart.total()).toBe(30)
})
```

---

## Mock Types: Mocks, Stubs, Fakes, Spies

### Stub
**Definition:** Returns fixed data, no behavior verification

**When to use:** Simple test cases where you only care about return value

**Example:**
```python
def test_get_user():
    # Stub: returns fixed data
    stub_db = Mock()
    stub_db.get_user.return_value = User(id='123', email='test@example.com')
    
    service = UserService(db=stub_db)
    user = service.get_user('123')
    
    assert user.email == 'test@example.com'
    # No verification of how stub was called
```

---

### Mock
**Definition:** Returns data AND verifies behavior (method calls, arguments)

**When to use:** When you need to verify interactions

**Example:**
```python
def test_send_notification():
    # Mock: verify it was called correctly
    mock_email = Mock()
    
    notifier = Notifier(email_client=mock_email)
    notifier.send_welcome('test@example.com')
    
    # Verify behavior
    mock_email.send.assert_called_once_with(
        to='test@example.com',
        subject='Welcome',
        body=expect.stringContaining('welcome')
    )
```

---

### Fake
**Definition:** Working implementation with shortcuts (in-memory database, fake API)

**When to use:** When you need realistic behavior without external dependencies

**Example:**
```typescript
// Fake in-memory database
class FakeDatabase {
  private users: Map<string, User> = new Map()
  
  async insert(user: User): Promise<User> {
    this.users.set(user.id, user)
    return user
  }
  
  async findById(id: string): Promise<User | null> {
    return this.users.get(id) || null
  }
}

it('creates and retrieves user', async () => {
  const fakeDb = new FakeDatabase()
  const repo = new UserRepository(fakeDb)
  
  await repo.create({ id: '123', email: 'test@example.com' })
  const user = await repo.findById('123')
  
  expect(user?.email).toBe('test@example.com')
})
```

**Benefits:**
- More realistic than mocks
- Tests actual logic flow
- Fast (in-memory)

---

### Spy
**Definition:** Wraps real object to record calls while preserving real behavior

**When to use:** When you want real behavior but also need to verify calls

**Example:**
```typescript
import { vi } from 'vitest'

it('logs errors when payment fails', async () => {
  const logger = new Logger()
  const loggerSpy = vi.spyOn(logger, 'error')
  
  const service = new PaymentService(logger)
  await service.charge(100, 'invalid_token')
  
  // Logger actually logs AND we can verify it was called
  expect(loggerSpy).toHaveBeenCalledWith(
    'Payment failed',
    expect.objectContaining({ token: 'invalid_token' })
  )
})
```

---

## Mocking Patterns

### Pattern 1: Dependency Injection

**Principle:** Pass dependencies as constructor/function arguments

✓ **Good (testable):**
```python
class UserService:
    def __init__(self, db, email_client):
        self.db = db
        self.email_client = email_client
    
    def register(self, email, password):
        user = self.db.insert_user(email, password)
        self.email_client.send_welcome(email)
        return user

# Easy to test - inject mocks
def test_register():
    mock_db = Mock()
    mock_email = Mock()
    
    service = UserService(db=mock_db, email_client=mock_email)
    service.register('test@example.com', 'password')
    
    mock_db.insert_user.assert_called_once()
    mock_email.send_welcome.assert_called_once()
```

❌ **Bad (hard to test):**
```python
class UserService:
    def __init__(self):
        # Hard-coded dependencies
        self.db = Database()
        self.email_client = EmailClient()
    
    def register(self, email, password):
        # Can't inject mocks!
        user = self.db.insert_user(email, password)
        self.email_client.send_welcome(email)
        return user
```

---

### Pattern 2: Interface/Protocol-Based Mocking

**Principle:** Define interfaces, mock implementations

**Example (TypeScript):**
```typescript
// Define interface
interface PaymentGateway {
  charge(amount: number, token: string): Promise<ChargeResult>
}

// Real implementation
class StripeGateway implements PaymentGateway {
  async charge(amount: number, token: string): Promise<ChargeResult> {
    // Real Stripe API call
  }
}

// Mock implementation
class MockPaymentGateway implements PaymentGateway {
  async charge(amount: number, token: string): Promise<ChargeResult> {
    return { id: 'mock_charge', status: 'succeeded' }
  }
}

// Service uses interface
class PaymentService {
  constructor(private gateway: PaymentGateway) {}
  
  async processPayment(amount: number, token: string) {
    const result = await this.gateway.charge(amount, token)
    return result
  }
}

// Test with mock
it('processes payment', async () => {
  const mockGateway = new MockPaymentGateway()
  const service = new PaymentService(mockGateway)
  
  const result = await service.processPayment(100, 'tok_visa')
  expect(result.status).toBe('succeeded')
})
```

---

### Pattern 3: Builder Pattern for Test Data

**Principle:** Use builders to create test objects with sensible defaults

**Example:**
```python
class UserBuilder:
    def __init__(self):
        self.id = 'default-id'
        self.email = 'default@example.com'
        self.is_active = True
    
    def with_id(self, id):
        self.id = id
        return self
    
    def with_email(self, email):
        self.email = email
        return self
    
    def inactive(self):
        self.is_active = False
        return self
    
    def build(self):
        return User(id=self.id, email=self.email, is_active=self.is_active)

# Clean test code
def test_send_email_to_active_users():
    active_user = UserBuilder().with_email('active@example.com').build()
    inactive_user = UserBuilder().inactive().build()
    
    email_service.send_newsletter([active_user, inactive_user])
    
    # Only active user receives email
    assert_email_sent_to('active@example.com')
    assert_email_not_sent_to('inactive@example.com')
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Mocking Everything

**Problem:** Tests become brittle, don't test real behavior

❌ **Wrong:**
```python
def test_process_order():
    mock_validate = Mock(return_value=True)
    mock_calculate = Mock(return_value=100)
    mock_save = Mock()
    mock_email = Mock()
    
    with patch.multiple('myapp.order',
                        validate=mock_validate,
                        calculate_total=mock_calculate,
                        save_order=mock_save,
                        send_confirmation=mock_email):
        process_order(order_data)
    
    # Not testing any real logic!
```

✓ **Better:**
```python
def test_process_order():
    # Only mock external dependencies
    mock_db = Mock()
    mock_email = Mock()
    
    service = OrderService(db=mock_db, email=mock_email)
    result = service.process_order(order_data)
    
    # Real validation and calculation happen
    assert result.total == 100
    mock_db.save.assert_called_once()
    mock_email.send.assert_called_once()
```

---

### Anti-Pattern 2: Overly Specific Mocks

**Problem:** Tests break when irrelevant details change

❌ **Brittle:**
```python
mock_api.post.assert_called_once_with(
    '/users',
    headers={'Content-Type': 'application/json', 'User-Agent': 'MyApp/1.0'},
    json={'email': 'test@example.com', 'name': 'Test', 'age': 25},
    timeout=30
)
```

✓ **Resilient:**
```python
mock_api.post.assert_called_once()
call_args = mock_api.post.call_args
assert call_args[0][0] == '/users'
assert call_args[1]['json']['email'] == 'test@example.com'
# Don't assert on headers, timeout unless critical
```

---

### Anti-Pattern 3: Testing Mock Configuration

**Problem:** Test verifies mock setup, not actual logic

❌ **Wrong:**
```python
def test_mock_returns_correct_value():
    mock_service = Mock()
    mock_service.get_user.return_value = User(id='123')
    
    # This just tests that the mock works - useless!
    assert mock_service.get_user().id == '123'
```

---

### Anti-Pattern 4: Not Resetting Mocks Between Tests

**Problem:** Test pollution - tests affect each other

❌ **Wrong:**
```python
mock_db = Mock()  # Shared across tests

def test_create_user():
    service = UserService(db=mock_db)
    service.create_user('test@example.com')
    
    assert mock_db.insert.call_count == 1

def test_create_another_user():
    service = UserService(db=mock_db)
    service.create_user('test2@example.com')
    
    # Fails! call_count is 2 because previous test's call is still tracked
    assert mock_db.insert.call_count == 1
```

✓ **Correct:**
```python
import pytest

@pytest.fixture
def mock_db():
    # Fresh mock for each test
    return Mock()

def test_create_user(mock_db):
    service = UserService(db=mock_db)
    service.create_user('test@example.com')
    
    assert mock_db.insert.call_count == 1
```

---

## Language-Specific Best Practices

### Python (pytest + unittest.mock)
```python
from unittest.mock import Mock, patch, MagicMock
import pytest

# Use fixtures for mocks
@pytest.fixture
def mock_db():
    return Mock()

# Use patch for global dependencies
def test_with_patching():
    with patch('myapp.utils.send_email') as mock_email:
        send_welcome_email('test@example.com')
        mock_email.assert_called_once()

# Use MagicMock for magic methods
def test_context_manager():
    mock_file = MagicMock()
    with mock_file as f:
        f.read.return_value = 'content'
```

---

### TypeScript/JavaScript (Vitest/Jest)
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('UserService', () => {
  let mockDb: any
  
  beforeEach(() => {
    mockDb = {
      insert: vi.fn(),
      findById: vi.fn()
    }
  })
  
  it('creates user', async () => {
    mockDb.insert.mockResolvedValue({ id: '123' })
    
    const service = new UserService(mockDb)
    const user = await service.create({ email: 'test@example.com' })
    
    expect(user.id).toBe('123')
    expect(mockDb.insert).toHaveBeenCalledOnce()
  })
})
```

---

## Summary Checklist

Before adding a mock to your test, ask:

- [ ] Is this an external dependency (database, API, filesystem)?
- [ ] Can I use a fake instead of a mock?
- [ ] Am I mocking the thing under test? (Don't!)
- [ ] Am I mocking internal helpers? (Don't!)
- [ ] Will this make my test brittle?
- [ ] Is dependency injection set up correctly?
- [ ] Are mocks reset between tests?

**Golden Rules:**
1. Mock at boundaries (I/O), not internals
2. Prefer fakes over mocks when possible
3. Use dependency injection
4. Keep mocks simple and resilient
5. Integration tests use real dependencies
