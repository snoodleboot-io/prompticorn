---
type: subagent
agent: ask
name: testing
variant: verbose
version: 1.0.0
description: Generate tests for code with detailed examples
mode: subagent
tools: [read, write]
workflows:
  - testing-workflow
---

# Testing (Verbose)

Comprehensive guide for generating unit tests, integration tests, and test strategies.

---

## Test Organization

### Directory Structure

Mirror source code structure in tests:

```
src/
├── models/
│   └── user.py
├── services/
│   └── auth_service.py
└── api/
    └── auth.py

tests/
├── unit/
│   ├── models/
│   │   └── test_user.py
│   ├── services/
│   │   └── test_auth_service.py
│   └── api/
│       └── test_auth.py
├── integration/
│   └── test_auth_flow.py
├── slow/
│   └── test_load.py
└── security/
    └── test_auth_vulnerabilities.py
```

**Categories:**
- **unit/** — Fast, isolated tests (< 100ms each)
- **integration/** — Multi-component tests (< 5s each)
- **slow/** — Long-running tests (> 5s)
- **security/** — Security-focused tests (fuzzing, injection)

---

## Unit Tests

### What to Test

**Cover these scenarios:**

1. **Happy path** — Expected inputs produce expected outputs
2. **Edge cases** — Empty, zero, null, boundary values
3. **Error cases** — Invalid inputs, exceptions
4. **State interactions** — Side effects, mutations

### Example: User Model (Python)

```python
import pytest
from src.models.user import User

class TestUserModel:
    """Unit tests for User model."""
    
    def test_create_user_with_valid_data(self):
        """Happy path: User created with valid email and password."""
        user = User(email="alice@example.com", password="SecurePass123!")
        
        assert user.email == "alice@example.com"
        assert user.password_hash is not None
        assert user.password_hash != "SecurePass123!"  # Password is hashed
        assert user.role == "user"  # Default role
    
    def test_user_password_is_hashed_on_creation(self):
        """Password is hashed, not stored as plain text."""
        user = User(email="bob@example.com", password="password123")
        
        # Password hash should be bcrypt format (starts with $2b$)
        assert user.password_hash.startswith("$2b$")
        assert len(user.password_hash) == 60  # bcrypt hash length
    
    def test_create_user_with_custom_role(self):
        """User can be created with non-default role."""
        user = User(email="admin@example.com", password="AdminPass!", role="admin")
        
        assert user.role == "admin"
    
    def test_verify_password_returns_true_for_correct_password(self):
        """verify_password returns True when password matches."""
        user = User(email="charlie@example.com", password="MyPassword!")
        
        assert user.verify_password("MyPassword!") is True
    
    def test_verify_password_returns_false_for_incorrect_password(self):
        """verify_password returns False when password doesn't match."""
        user = User(email="charlie@example.com", password="MyPassword!")
        
        assert user.verify_password("WrongPassword") is False
    
    # Edge cases
    
    def test_create_user_with_empty_email_raises_error(self):
        """Empty email raises ValueError."""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            User(email="", password="password123")
    
    def test_create_user_with_invalid_email_format_raises_error(self):
        """Invalid email format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid email format"):
            User(email="not-an-email", password="password123")
    
    def test_create_user_with_short_password_raises_error(self):
        """Password shorter than 12 characters raises ValueError."""
        with pytest.raises(ValueError, match="Password must be at least 12 characters"):
            User(email="alice@example.com", password="short")
    
    def test_create_user_with_invalid_role_raises_error(self):
        """Invalid role raises ValueError."""
        with pytest.raises(ValueError, match="Role must be one of"):
            User(email="alice@example.com", password="ValidPass123!", role="invalid")
    
    # Boundary values
    
    def test_create_user_with_minimum_valid_password_length(self):
        """Password of exactly 12 characters is accepted."""
        user = User(email="alice@example.com", password="ExactlyTwlv!")
        
        assert user.password_hash is not None
    
    def test_create_user_with_very_long_email(self):
        """Email with 254 characters (max valid length) is accepted."""
        long_email = "a" * 243 + "@example.com"  # 254 chars total
        user = User(email=long_email, password="ValidPass123!")
        
        assert user.email == long_email
```

### Test Naming Convention

**Format:** `test_{method}_{scenario}_{expected_result}`

✅ **Good examples:**
- `test_create_user_with_valid_data`
- `test_verify_password_returns_true_for_correct_password`
- `test_create_user_with_empty_email_raises_error`

❌ **Bad examples:**
- `test1` — Not descriptive
- `test_user` — Too vague
- `test_create` — Missing scenario and outcome

---

## Integration Tests

### What to Test

**Test interactions between components:**
- API endpoint → Service → Model → Database
- Service → External API
- Multiple services coordinating

### Example: Authentication Flow (Python)

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import get_db

@pytest.fixture
def client():
    """Test client for API requests."""
    return TestClient(app)

@pytest.fixture
def db_session():
    """Database session that rolls back after each test."""
    session = get_db()
    yield session
    session.rollback()
    session.close()

class TestAuthenticationFlow:
    """Integration tests for complete authentication flow."""
    
    def test_user_can_register_and_login(self, client, db_session):
        """Complete flow: register → login → access protected endpoint."""
        
        # Step 1: Register new user
        register_response = client.post("/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecurePassword123!"
        })
        assert register_response.status_code == 201
        user_data = register_response.json()
        assert user_data["email"] == "newuser@example.com"
        assert "id" in user_data
        
        # Step 2: Login with registered credentials
        login_response = client.post("/auth/login", json={
            "email": "newuser@example.com",
            "password": "SecurePassword123!"
        })
        assert login_response.status_code == 200
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        
        # Step 3: Access protected endpoint with token
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        profile_response = client.get("/users/me", headers=headers)
        assert profile_response.status_code == 200
        profile = profile_response.json()
        assert profile["email"] == "newuser@example.com"
    
    def test_login_fails_with_wrong_password(self, client, db_session):
        """Login attempt with wrong password returns 401."""
        
        # Register user
        client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "CorrectPassword!"
        })
        
        # Attempt login with wrong password
        response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "WrongPassword!"
        })
        
        assert response.status_code == 401
        assert response.json()["error"] == "INVALID_CREDENTIALS"
    
    def test_protected_endpoint_rejects_missing_token(self, client):
        """Protected endpoint returns 401 when token is missing."""
        
        response = client.get("/users/me")
        
        assert response.status_code == 401
        assert response.json()["error"] == "MISSING_TOKEN"
    
    def test_token_refresh_extends_session(self, client, db_session):
        """Refresh token can be used to get new access token."""
        
        # Register and login
        client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "Password123!"
        })
        login_response = client.post("/auth/login", json={
            "email": "user@example.com",
            "password": "Password123!"
        })
        tokens = login_response.json()
        
        # Use refresh token to get new access token
        refresh_response = client.post("/auth/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        
        assert refresh_response.status_code == 200
        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert new_tokens["access_token"] != tokens["access_token"]  # New token
```

---

## Edge Cases

### Comprehensive Edge Case List

When asked for edge cases, cover:

1. **Boundary values**
   - Minimum value: `0`, `1`, `""`, `[]`
   - Maximum value: `INT_MAX`, very long strings
   - Exactly at limit: password length 12 (if min is 12)

2. **Empty/null/zero**
   - Empty string `""`
   - Null/None/undefined
   - Zero `0`
   - False boolean
   - Empty array `[]`
   - Empty object `{}`

3. **Type mismatches**
   - String where integer expected
   - Array where object expected
   - Null where string expected

4. **Oversized inputs**
   - Very long strings (1MB+)
   - Large arrays (10,000+ items)
   - Deeply nested objects (100+ levels)

5. **Special characters**
   - Unicode: emoji, Chinese characters
   - SQL injection: `' OR '1'='1`
   - XSS: `<script>alert('xss')</script>`
   - Path traversal: `../../etc/passwd`

6. **Injection attempts**
   - SQL injection
   - NoSQL injection
   - Command injection
   - LDAP injection

7. **Missing required fields**
   - Omit required field from JSON
   - Send partial data

8. **Logical contradictions**
   - Start date after end date
   - Negative age
   - Duplicate unique identifiers

### Example: Edge Case Tests

```python
class TestUserCreationEdgeCases:
    """Edge case tests for user creation."""
    
    # Boundary values
    
    def test_password_exactly_12_characters(self):
        """Minimum valid password length (exactly 12 chars)."""
        user = User(email="user@example.com", password="Exactly12Chr")
        assert user.password_hash is not None
    
    def test_email_at_maximum_length(self):
        """Email at maximum valid length (254 characters)."""
        email = "a" * 243 + "@example.com"
        user = User(email=email, password="ValidPass123!")
        assert len(user.email) == 254
    
    # Empty/null/zero
    
    def test_empty_email_raises_error(self):
        with pytest.raises(ValueError):
            User(email="", password="ValidPass123!")
    
    def test_none_email_raises_error(self):
        with pytest.raises(TypeError):
            User(email=None, password="ValidPass123!")
    
    # Type mismatches
    
    def test_integer_email_raises_error(self):
        with pytest.raises(TypeError):
            User(email=12345, password="ValidPass123!")
    
    # Oversized inputs
    
    def test_extremely_long_password(self):
        """Password of 10,000 characters."""
        long_password = "a" * 10000
        user = User(email="user@example.com", password=long_password)
        assert user.password_hash is not None
    
    # Special characters
    
    def test_email_with_unicode_characters(self):
        """Email with Unicode characters."""
        user = User(email="用户@example.com", password="ValidPass123!")
        assert user.email == "用户@example.com"
    
    def test_password_with_emoji(self):
        """Password containing emoji."""
        user = User(email="user@example.com", password="Password🔒123!")
        assert user.verify_password("Password🔒123!")
    
    # Injection attempts
    
    def test_sql_injection_in_email(self):
        """SQL injection attempt in email field."""
        malicious_email = "admin'--@example.com"
        # Should be treated as literal string, not SQL
        user = User(email=malicious_email, password="ValidPass123!")
        assert user.email == malicious_email
    
    def test_xss_in_email(self):
        """XSS attempt in email field."""
        xss_email = "<script>alert('xss')</script>@example.com"
        with pytest.raises(ValueError, match="Invalid email format"):
            User(email=xss_email, password="ValidPass123!")
```

---

## Test Data Management

### Fixtures (pytest)

```python
import pytest
from src.models import User, Order
from src.database import db

@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    user = User(email="testuser@example.com", password="TestPass123!")
    db.session.add(user)
    db.session.commit()
    yield user
    db.session.delete(user)
    db.session.commit()

@pytest.fixture
def user_with_orders(sample_user):
    """Create a user with 3 orders."""
    orders = [
        Order(user_id=sample_user.id, amount=100.00),
        Order(user_id=sample_user.id, amount=250.50),
        Order(user_id=sample_user.id, amount=75.25),
    ]
    db.session.add_all(orders)
    db.session.commit()
    yield sample_user
    db.session.delete_all(orders)
    db.session.commit()

def test_user_total_order_amount(user_with_orders):
    """User total order amount is sum of all orders."""
    total = user_with_orders.total_order_amount()
    assert total == 425.75  # 100.00 + 250.50 + 75.25
```

### Factories (factory_boy)

```python
import factory
from src.models import User, Order

class UserFactory(factory.Factory):
    class Meta:
        model = User
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = "TestPassword123!"
    role = "user"

class AdminUserFactory(UserFactory):
    role = "admin"

class OrderFactory(factory.Factory):
    class Meta:
        model = Order
    
    user = factory.SubFactory(UserFactory)
    amount = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    status = "pending"

# Usage in tests
def test_admin_can_view_all_orders():
    admin = AdminUserFactory()
    orders = [OrderFactory() for _ in range(5)]
    
    visible_orders = admin.get_visible_orders()
    assert len(visible_orders) == 5
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        run: pytest tests/unit/ --cov=src --cov-report=xml
      
      - name: Run integration tests
        run: pytest tests/integration/
      
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
      
      - name: Run slow tests (on main branch only)
        if: github.ref == 'refs/heads/main'
        run: pytest tests/slow/ -v
```

---

## Mutation Testing

### Example (using mutmut)

```bash
# Install
pip install mutmut

# Run mutation tests
mutmut run

# View results
mutmut show

# Example output:
# - SURVIVED: 5 mutations (tests didn't catch them)
# - KILLED: 95 mutations (tests caught them)
# - Mutation score: 95% (target: 80%+)
```

### Interpreting Results

**Mutation score = (Killed / Total) × 100**

- **80%+** — Good test quality
- **60-80%** — Acceptable
- **< 60%** — Tests are weak

**SURVIVED mutation example:**

```python
# Original code
def is_adult(age):
    return age >= 18

# Mutant: Changed >= to >
def is_adult(age):
    return age > 18  # ❌ Survives if no test for age=18

# Fix: Add boundary test
def test_is_adult_returns_true_for_exactly_18():
    assert is_adult(18) is True  # ✓ Kills mutant
```

---

## Anti-Patterns

### ❌ Testing Implementation Details

**Don't:**
```python
def test_user_password_hash_uses_bcrypt():
    user = User(email="test@example.com", password="pass")
    assert user._hash_algorithm == "bcrypt"  # ❌ Implementation detail
```

**Do:**
```python
def test_user_password_is_verified_correctly():
    user = User(email="test@example.com", password="pass")
    assert user.verify_password("pass") is True  # ✓ Public interface
```

### ❌ Over-Mocking

**Don't:**
```python
@patch('src.models.user.bcrypt')
@patch('src.models.user.validate_email')
def test_user_creation(mock_validate, mock_bcrypt):
    # ❌ Mocking everything means not testing real behavior
    ...
```

**Do:**
```python
def test_user_creation():
    # ✓ Use real implementations
    user = User(email="test@example.com", password="ValidPass!")
    assert user.email == "test@example.com"
```

### ❌ Tests Depending on Execution Order

**Don't:**
```python
def test_step_1():
    global user
    user = create_user()  # ❌ Shared state

def test_step_2():
    assert user.email == "..."  # ❌ Depends on test_step_1
```

**Do:**
```python
@pytest.fixture
def user():
    return create_user()

def test_step_1(user):
    assert user.id is not None  # ✓ Independent

def test_step_2(user):
    assert user.email == "..."  # ✓ Independent
```
