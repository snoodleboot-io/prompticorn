# Test Data Strategies (Minimal)

## Purpose
Produce test data that is deterministic, isolated per test, and states its intent in the test that uses it.

## Core Techniques

### 1. Choose the Right Construct
| Construct | Shape | Use when |
|---|---|---|
| Fixture | One prepared value, reused | Immutable reference data, expensive setup |
| Factory | Function returning a fresh object with defaults | The common case — most objects |
| Builder | Fluent chain of overrides | Objects with many fields where a few matter |

Default to factories. Fixtures are for things nobody mutates; builders earn their keep once an object has ten-plus fields.

### 2. Never Share Mutable Fixtures
```python
# ❌ Session-scoped and mutable: test order now decides the result
@pytest.fixture(scope="session")
def user():
    return User(name="Alice", credits=100)

def test_spend(user):
    user.credits -= 50          # mutates the shared object
    assert user.credits == 50   # passes, and poisons every later test
```
Function scope is the default for a reason. If a fixture must be session-scoped for cost, make it frozen or hand each test a copy.

### 3. Build Fresh Objects With Explicit Overrides
```python
def make_order(**overrides) -> Order:
    defaults = dict(
        id=next(_ids),
        customer_id=next(_ids),
        total=Decimal("100.00"),
        status="pending",
        placed_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    return Order(**defaults | overrides)

def test_refund_rejected_for_shipped_order():
    order = make_order(status="shipped")     # only the field under test is named
    with pytest.raises(RefundNotAllowed):
        refund(order)
```
The override *is* the documentation: a reader sees instantly that `status` is what this test is about.

### 4. Make Generated Data Deterministic
```python
fake = Faker()
Faker.seed(20260101)      # same names, addresses, emails on every run
```
Unseeded generators turn a data-dependent bug into a flake that appears once a month. Seed everything; if you want variety, vary the seed deliberately and log it.

### 5. Keep Uniqueness Explicit
Collisions on unique columns are a classic order-dependent failure. Use a per-run counter rather than random values, which collide by birthday paradox sooner than people expect:
```python
_ids = itertools.count(1)
email = f"user-{next(_ids)}@example.test"
```

### 6. Treat Production Data as Radioactive
A production dump in a test database is a breach waiting for a misconfigured bucket. Naive masking does not help: replacing names while keeping birth date, ZIP code, and sex leaves records re-identifiable, and free-text fields, JSON blobs, and logs carry PII that a column-level masker never sees. Generate synthetic data by default. If real data is unavoidable, restrict to a subset, transform irreversibly, keep it inside the same trust boundary as production, and give it an expiry.

## Warning Signs

- `scope="session"` on a fixture whose object gets mutated
- Tests that pass alone and fail in the suite, or vice versa
- Unseeded `Faker`, `random`, or UUIDs in setup
- One `conftest.py` mega-fixture that most tests use and none needs entirely
- Assertions on values the test never set — inherited from fixture defaults
- Real customer names or emails visible in test data or CI logs
- Test data loaded from a checked-in SQL dump nobody can regenerate
