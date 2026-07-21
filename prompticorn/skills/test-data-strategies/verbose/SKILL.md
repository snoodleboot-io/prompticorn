# Test Data Strategies (Verbose)

## Core Patterns

### Fixtures, Factories, and Builders

These three are not interchangeable, and picking the wrong one is the root of a
surprising share of order-dependent failures.

**A fixture** is a prepared value handed to a test. It is the right tool when the
value is expensive to build and nobody mutates it — a loaded currency table, a
parsed schema, a started container.

```python
@pytest.fixture(scope="session")
def currency_table() -> Mapping[str, int]:
    return MappingProxyType(load_iso4217())    # read-only: safe to share
```

**A factory** is a function that returns a fresh object with sensible defaults
and accepts overrides. This is the default choice for domain objects, because
every test gets its own instance and names only the fields it cares about.

```python
_seq = itertools.count(1)

def make_customer(**overrides) -> Customer:
    n = next(_seq)
    defaults = dict(
        id=n,
        email=f"customer-{n}@example.test",
        tier="standard",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        credit_limit=Decimal("500.00"),
    )
    return Customer(**defaults | overrides)
```

**A builder** is a fluent chain, useful once an object has enough fields that
keyword soup becomes unreadable, or when construction has ordering rules.

```python
order = (
    OrderBuilder()
    .for_customer(make_customer(tier="gold"))
    .with_line("SKU-1", qty=2, unit_price=Decimal("19.99"))
    .with_line("SKU-2", qty=1, unit_price=Decimal("5.00"))
    .shipped_on(date(2026, 2, 3))
    .build()
)
```

Where established libraries exist, prefer them to hand-rolling: `factory_boy` in
Python, `factory.ts`/`fishery` in TypeScript, `FactoryBot` in Ruby. They handle
sequences, sub-factories, and post-generation hooks that hand-rolled factories
grow into badly.

### Shared Mutable State Is an Order Dependency

The single most common test-data bug is a fixture that is shared and mutated.

```python
# ❌
@pytest.fixture(scope="module")
def account():
    return Account(balance=Decimal(100))

def test_withdraw(account):
    account.withdraw(Decimal(40))
    assert account.balance == Decimal(60)

def test_cannot_overdraw(account):
    with pytest.raises(InsufficientFunds):
        account.withdraw(Decimal(80))     # passes only after test_withdraw ran
```

The second test passes for the wrong reason and will invert the moment someone
reorders the file, shards with xdist, or runs the tests in random order. Rules
that prevent this class entirely:

1. Function scope by default. Escalate scope only with evidence of cost.
2. If scope must be broader, the value must be immutable — frozen dataclass,
   `MappingProxyType`, a tuple, or an object you copy on handout.
3. State that lives outside the process (database rows, caches, temp files) needs
   explicit teardown, not merely a fresh Python object.

For database-backed tests, the cheapest isolation is a transaction rolled back
per test:

```python
@pytest.fixture
def session(connection):
    tx = connection.begin()
    s = Session(bind=connection)
    yield s
    s.close()
    tx.rollback()          # every row this test created disappears
```

This is fast and total, but it does not cover code that commits or manages its own
transactions; those tests need truncation between runs instead. Know which regime
each test is in — mixing them silently is how "passes locally" starts.

### Determinism

Any nondeterminism in test data eventually becomes a flake with a period measured
in weeks — long enough that nobody connects it to the data generator.

```python
@pytest.fixture(autouse=True)
def deterministic_data():
    seed = int(os.environ.get("TEST_SEED", "20260101"))
    random.seed(seed)
    Faker.seed(seed)
```

The subtle sources are worth enumerating, because seeding `random` alone does not
cover them:

- `uuid4()` — random, and it commonly ends up in a sort key or a dict order.
- `datetime.now()` inside a factory default — makes today's date part of the data.
- Set iteration order feeding a list comparison.
- Locale- or timezone-dependent formatting picked up from the host.
- A "pick one at random" default in a factory, e.g. a random `tier`.

Do not seed away the variety you actually want. Property-based testing
(Hypothesis, fast-check) is deliberately varied; its correctness model is that a
failing example is minimized and persisted, then promoted to an explicit
regression case. Keep it in its own tier and let it vary; keep example-based
tests fully deterministic.

### Intent-Revealing Data

Test data should say what the test is about and nothing else.

```python
# ❌ Which of these eleven values matters? The reader has to guess.
order = Order(
    id=7, customer_id=3, total=Decimal("250.00"), currency="USD",
    status="shipped", placed_at=..., shipped_at=..., carrier="UPS",
    tracking="1Z999", gift=False, notes="",
)
assert not can_cancel(order)

# ✅ One named override; everything else is irrelevant by construction
order = make_order(status="shipped")
assert not can_cancel(order)
```

The corollary is a rule about assertions: **never assert on a value the test did
not set.** An assertion against a factory default is a hidden coupling — change
the default and unrelated tests fail with a message that points nowhere near the
cause.

Keep magic values out of both sides. If a test needs a boundary, name it:

```python
FREE_SHIPPING_THRESHOLD = Decimal("50.00")

def test_no_free_shipping_below_threshold():
    order = make_order(total=FREE_SHIPPING_THRESHOLD - Decimal("0.01"))
    assert shipping_cost(order) > 0
```

### Production Data: Hazards

Copying production into a test environment is tempting because the data is real
and the edge cases are free. It is also the way most test-environment data
breaches happen, and the hazards are less obvious than "remove the names".

**Pseudonymization is not anonymization.** Replacing identifiers while keeping
quasi-identifiers leaves records re-identifiable by linkage. Sweeney's well-known
result is that the combination of ZIP code, birth date, and sex uniquely
identifies the large majority of the US population — later work on the 2000
census puts it around 63%, still catastrophic for a "de-identified" dataset. The
AOL search-log release in 2006 and the Netflix Prize dataset were both
re-identified by linking to outside sources despite having removed direct
identifiers.

**Free text and blobs defeat column maskers.** A masker configured over
`users.email` does not touch the support-ticket body containing the same address,
the JSONB `metadata` column, the audit log payload, or the base64 attachment.
Any masking approach that enumerates columns will miss these.

**Referential integrity breaks under subsetting.** Take 1% of orders and you have
orders pointing at absent customers. Correct subsetting follows the foreign-key
graph from chosen roots, which is a real tool (or a real script), not a
`LIMIT 10000`.

**The copy inherits production's sensitivity, not the test environment's
controls.** A production extract sitting in a staging bucket with developer-wide
read access is a production-severity exposure with staging-grade protection.

Practical policy, in order of preference:

1. **Synthetic by default.** Factories plus seeded generators cover the
   overwhelming majority of tests, and they encode intent, which real data never
   does.
2. **Synthetic-with-production-shape** for performance and load work: mirror
   cardinalities, value distributions, and skew without carrying real values.
   See `load-testing` for the workload side of this.
3. **Real data only under controls**: irreversible transformation, generalization
   of quasi-identifiers (age bands rather than birth dates), the same access
   controls and network boundary as production, an expiry date, and an approved,
   auditable extraction process.

Add a guardrail that fails the build rather than trusting policy — a test that
scans fixture files and seed data for patterns that look like real personal data
costs an hour and catches the accidental paste.

## Common Anti-Patterns

❌ **Session-scoped mutable fixture** — the test that ran before yours decides
whether yours passes.
✅ Function scope by default; immutable values only for wider scope.

❌ **A single `conftest.py` mega-fixture** every test depends on — coupling
everything to one shape, so no test can be read locally.
✅ Small factories, composed per test, overriding what matters.

❌ **Unseeded generators** — a data-dependent bug becomes a monthly mystery flake.
✅ Seed centrally in an autouse fixture; log the seed.

❌ **Asserting a factory default** — changing the default breaks distant tests.
✅ Assert only on values the test explicitly set.

❌ **Random values for unique columns** — collisions appear far sooner than
intuition suggests.
✅ A monotonic per-run sequence.

❌ **Checked-in SQL dumps as the fixture set** — unreadable, unmaintainable, and
stale the day after they land.
✅ Code-defined factories under version control alongside the tests.

❌ **"Anonymized" production copies that keep birth date, ZIP, and sex** — trivially
re-identifiable by linkage.
✅ Generalize or synthesize quasi-identifiers, not just direct identifiers.

❌ **Building test data by calling the API under test** — the test cannot
distinguish a broken setup path from a broken assertion path.
✅ Construct state directly through factories or the repository layer.

## Test Data Checklist

- [ ] Factories are the default construct; fixtures reserved for immutable values
- [ ] No fixture wider than function scope is mutable
- [ ] Database tests isolated by rollback or truncation, chosen deliberately
- [ ] External state (files, caches, queues) has explicit teardown
- [ ] All generators seeded in one autouse fixture; seed overridable and logged
- [ ] No `uuid4()` or `now()` in factory defaults where it can reach an assertion
- [ ] Unique fields use a monotonic sequence, not randomness
- [ ] Each test names only the fields under test; the rest come from defaults
- [ ] No assertion depends on a value the test did not set
- [ ] Boundary values named as constants, not repeated literals
- [ ] Test data is synthetic unless real data is formally approved
- [ ] Any real-data extract is transformed irreversibly, scoped, and expiring
- [ ] Subsetting follows the foreign-key graph, preserving referential integrity
- [ ] A CI check scans fixtures and seeds for real-looking personal data
