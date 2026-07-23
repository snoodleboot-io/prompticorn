# Flaky Test Remediation (Verbose)

## Core Patterns

### Measure the Suite, Not the Test

A flaky test is one that produces different results on unchanged code and an
unchanged environment. The instinct is to treat each one as a small local
annoyance. The arithmetic says otherwise, because independent failure
probabilities compound across the suite:

```
P(suite green) = (1 - p) ** n

n = 500,  p = 0.001  ->  0.999 ** 500  = 0.606     ~40% of runs red
n = 500,  p = 0.01   ->  0.99  ** 500  = 0.0066    ~99.3% of runs red
n = 2000, p = 0.001  ->  0.999 ** 2000 = 0.135     ~86% of runs red
```

Two consequences follow. First, a per-test flake rate that sounds acceptable in
isolation is fatal at scale — for a 2000-test suite to be green 95% of the time,
each test must flake less than once in about 39,000 runs. Second, the only
meaningful target is a suite-level one: pick "95% of CI runs green", divide
backwards, and you have your per-test budget.

Instrument first. Record every test outcome per run, then rank:

```sql
SELECT test_id,
       COUNT(*) FILTER (WHERE outcome = 'failed') AS failures,
       COUNT(*) AS runs,
       COUNT(*) FILTER (WHERE outcome = 'failed')::float / COUNT(*) AS flake_rate
FROM test_results
WHERE commit_sha IN (SELECT sha FROM commits WHERE merged_to_main)
GROUP BY test_id
HAVING COUNT(*) FILTER (WHERE outcome = 'failed') > 0
ORDER BY flake_rate DESC
LIMIT 20;
```

Restricting to merged commits matters: failures on a feature branch are usually
real, failures on green main are usually flakes. The top ten rows typically
account for most of the pain — flakiness is heavily Pareto-distributed, and
fixing three tests often takes a suite from unusable to trustworthy.

### The Taxonomy of Causes

Almost every flake reduces to one of six causes, and each has a distinct
fingerprint that tells you which one you have before you read any code.

**Time and clock.** Fingerprint: fails in a narrow window — near midnight, on the
last day of a month, across a DST boundary, on Feb 29, or only in CI because CI
runs in UTC and you do not. The bug is usually a test that computes its
expectation from the same `now()` the code under test reads, or an assertion on a
naive datetime.

```python
# ❌ Two calls to now() straddling midnight yield different dates
assert report.day == date.today()

# ✅ One injected clock, one fixed instant
def test_report_uses_current_day(monkeypatch):
    frozen = datetime(2026, 3, 8, 23, 59, 59, tzinfo=UTC)
    monkeypatch.setattr(billing.clock, "now", lambda: frozen)
    assert billing.build_report().day == date(2026, 3, 8)
```

Give production code a clock seam — a `clock.now()` module function or an
injected callable — rather than sprinkling `datetime.now()` through it. Freezing
libraries such as `freezegun` and `time-machine` patch the stdlib globally; they
are useful, but a seam you own is easier to reason about and does not fight C
extensions that read the clock directly.

**Ordering and shared state.** Fingerprint: passes alone, fails in the full
suite, or the reverse. Also: fails only under `pytest-xdist` sharding, because
sharding changes which tests share a worker process.

```python
# ❌ Module-level mutable state leaks between tests
CACHE = {}

def test_a():
    CACHE["user"] = build_user()
    assert lookup("user") is not None

def test_b():
    assert lookup("user") is None    # passes only if test_a did not run first
```

Fixes in order of preference: eliminate the global; make the fixture
function-scoped; add explicit teardown. Session-scoped fixtures are not banned,
but they must be immutable. A session-scoped fixture any test can mutate is an
order dependency waiting to be discovered on the day someone inserts a test in
the middle of the file.

Prove isolation by randomizing order in CI permanently:

```bash
pytest -p randomly                             # pytest-randomly: shuffle + reseed
pytest -p randomly --randomly-seed=20260319    # reproduce one specific shuffle
```

The seed is printed in the header of every run, so a red CI log always contains
what you need to reproduce it locally.

**Async races.** Fingerprint: fails more on slow or loaded runners, more at higher
parallelism, and essentially never on a developer laptop. The cause is nearly
always a test that waits a fixed duration and hopes.

```python
# ❌ A bet on the machine being fast enough
await queue.publish(msg)
await asyncio.sleep(0.2)
assert handler.received == [msg]

# ✅ Wait for the event the system actually emits
await queue.publish(msg)
await asyncio.wait_for(handler.processed.wait(), timeout=5)
assert handler.received == [msg]
```

The generalization: **wait on a condition, bounded by a timeout**. A generous
timeout costs nothing when the code is correct — it is only paid on real failures
— whereas a sleep is paid on every run and is still a guess.

**Network and external services.** Fingerprint: several unrelated tests fail
together in one run, then all pass on the next. Any test that resolves DNS or
opens a socket to something you do not control is partly a test of someone else's
uptime. Block egress in the unit tier so this cannot happen silently:

```python
@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def deny(*args, **kwargs):
        raise RuntimeError("network access attempted in a unit test")
    monkeypatch.setattr(socket.socket, "connect", deny)
```

Keep genuine third-party integration in a separate, non-blocking job, and see
`test-mocking-rules` for where to place the stub boundary.

**Randomness.** Fingerprint: fails roughly 1 in N with no environmental
correlation. Sources include the obvious `random` and `numpy.random`, and the
less obvious: iteration order over a set, UUID-derived sort orders, hash-based
sharding, and property-based tools generating a fresh case each run. Seed
centrally and record the seed:

```python
@pytest.fixture(autouse=True)
def deterministic():
    seed = int(os.environ.get("TEST_SEED", "0"))
    random.seed(seed)
    numpy.random.seed(seed)
```

Property-based testing is the deliberate exception: generating new inputs is the
entire value, so do not freeze it. Instead ensure the failing example is
persisted (Hypothesis writes to `.hypothesis/examples`) and promote it to an
explicit regression test once found.

**Resource exhaustion.** Fingerprint: failures cluster late in the run and never
early; the mode is a timeout, "too many open files", "connection pool exhausted",
or an OOM kill. The failing test is a victim, not the culprit — it is the one
unlucky enough to run after the leak accumulated. Find the leak by checking a
resource count around every test rather than by reading the test that failed.

```python
@pytest.fixture(autouse=True)
def no_leaked_fds():
    before = len(os.listdir("/proc/self/fd"))
    yield
    assert len(os.listdir("/proc/self/fd")) <= before + 1
```

### Reproduce Before Fixing

A fix you cannot verify is a guess.

```bash
# Repeat one test many times in one process (pytest-repeat)
pytest tests/test_orders.py::test_expiry --count=500

# Repeat under the suite's real ordering
pytest -p randomly --randomly-seed=last tests/

# Suspected order dependency: run the suspect after a candidate prefix
pytest tests/test_cache.py tests/test_orders.py::test_expiry
```

For order dependencies, bisect the prefix: run the first half of the suite plus
the failing test, then narrow. A handful of iterations isolates the exact pair,
which is nearly always enough to see the shared state.

### Quarantine Beats Retry

Automatic retry is the most common response and the most damaging one. Consider
what three reruns do to a test failing 5% of the time because of a genuine race in
a connection pool: the chance all three attempts fail is 0.05³ = 0.000125, so the
build goes green 99.99% of the time and the race becomes invisible. You did not
fix a test — you disabled a detector for a bug your users will hit in production,
where there are no reruns.

The decision rule: **retrying a flaky test is a decision to accept losing the real
bug underneath it.** Occasionally that trade is correct, for a known third-party
timeout you cannot control. It is never correct by default, and never silently.

Quarantine makes the same short-term pain go away while keeping the signal:

```python
@pytest.mark.quarantine    # PRO-411, owner: payments, expires 2026-08-15
def test_concurrent_checkout_settles():
    ...
```

```toml
[tool.pytest.ini_options]
markers = ["quarantine: known-flaky; excluded from the merge gate"]
addopts = "-m 'not quarantine'"
```

Quarantine has three non-negotiable properties: the test still runs in a
non-blocking job so data keeps accumulating; it has a named owner; and it has a
deadline, after which it is fixed or deleted. A permanent quarantine is worse
than deletion — it burns CI minutes and implies coverage that does not exist.

## Common Anti-Patterns

❌ **A rerun plugin in the default CI command** — hides intermittent production
bugs behind a green check.
✅ Quarantine with an owner and a deadline; keep the failure data visible.

❌ **`time.sleep(2)` to let something settle** — slow on every run, still a guess
on a loaded runner.
✅ Poll a condition or await an event, with a generous timeout.

❌ **Session-scoped mutable fixtures shared across a file** — order dependence
that surfaces months later when a test is inserted above.
✅ Function-scoped by default; session scope only for immutable data.

❌ **Fixing the test that failed** when the symptom is exhaustion or leakage — you
are patching the victim.
✅ Find the test that leaks; assert cleanup with an autouse fixture.

❌ **Numbered test ordering (`test_01_create`, `test_02_read`)** — encodes a
dependency chain into filenames.
✅ Each test arranges its own preconditions; see `test-aaa-structure`.

❌ **Deleting the flaky test quietly** — coverage drops and nobody notices the gap.
✅ Delete deliberately, at the deadline, with a ticket recording what is no longer
covered.

❌ **Comparing floats with `==`** — genuine nondeterminism when summation order
varies with platform or thread count.
✅ `pytest.approx(expected, rel=1e-9)` with a tolerance you can defend.

❌ **Treating flakiness as an individual's cleanup chore** — nobody owns the
suite, so the rate ratchets upward.
✅ A standing flake budget, reviewed with the same seriousness as build time.

## Flakiness Checklist

- [ ] Per-test outcomes recorded per CI run; top-20 flake ranking exists
- [ ] Suite-level green-rate target set, per-test budget derived from it
- [ ] Test order randomized in CI, seed printed and reproducible
- [ ] No `time.sleep` outside a bounded poll loop
- [ ] Every clock read in production code goes through an injectable seam
- [ ] All randomness seeded from one place; seed logged on failure
- [ ] Network egress blocked in the unit tier
- [ ] Fixtures function-scoped unless provably immutable
- [ ] Autouse fixture asserts no leaked descriptors or connections
- [ ] No retry/rerun plugin in the blocking gate
- [ ] Quarantine marker exists, with owner and deadline recorded per test
- [ ] Quarantined tests still execute in a non-blocking job
- [ ] Failure reproduced deterministically before any fix is merged
