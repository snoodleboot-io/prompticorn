# Flaky Test Remediation (Minimal)

## Purpose
Diagnose why a test passes and fails on identical code, and fix the cause rather than the symptom.

## Core Techniques

### 1. Do the Compounding Arithmetic First
A "1% flake rate" sounds harmless. It is not, because failures compound across the suite:

```
P(green run) = (1 - 0.01) ** 500 = 0.99 ** 500 ≈ 0.0066
```

At 500 tests each flaking 1% of the time, only **1 CI run in 152 is green**. Inverting it: to hold a 95% green rate over 500 tests, per-test flakiness has to stay under ~0.01%. Track the number as a suite-level probability, not a per-test one — 1% reads as fine and is catastrophic.

### 2. Classify by Fingerprint
| Cause | Fingerprint | Fix |
|---|---|---|
| Time / clock | Fails near midnight, month end, DST, or leap day | Inject a clock; freeze time |
| Order / shared state | Passes alone, fails in the full run (or vice versa) | Function-scoped fixtures; no module globals |
| Async race | Fails under load or on slower CI runners | Wait on a condition, never a duration |
| Network / external | Fails in bursts across unrelated tests | Stub at the boundary |
| Randomness | Fails ~1 in N with no pattern | Seed deterministically, log the seed |
| Resource exhaustion | Fails late in the run, never early | Close handles; assert cleanup |

### 3. Reproduce Before You Fix
```bash
pytest tests/test_orders.py::test_expiry --count=200        # pytest-repeat
pytest -p no:randomly tests/                                # ordering off
pytest -x --ff                                              # failed-first
```
Bisect an order dependency by running a shrinking prefix of the suite before the failing test. If it only fails in the full run, the cause is state, not the test.

### 4. Kill Wall-Clock Waits
```python
# ❌ Sleeps guess. On a loaded runner the guess is wrong.
time.sleep(0.5)
assert job.status == "done"

# ✅ Poll a condition with a timeout and a real error
deadline = time.monotonic() + 5
while time.monotonic() < deadline:
    if job.reload().status == "done":
        break
    time.sleep(0.01)
else:
    raise AssertionError(f"job stuck in {job.status}")
```

### 5. Freeze Time and Seed Randomness
```python
def test_token_expires(monkeypatch):
    monkeypatch.setattr(clock, "now", lambda: datetime(2026, 3, 1, tzinfo=UTC))
    assert issue_token().expires_at == datetime(2026, 3, 1, 0, 15, tzinfo=UTC)
```
Seed every generator from one place and print the seed on failure, so a red run is reproducible: `pytest -p randomly --randomly-seed=1234`.

### 6. Quarantine With a Deadline — Never Auto-Retry
Auto-retry (`--reruns 3`) converts a real intermittent bug into a green build. A test that fails 1 in 20 times is often reporting a genuine race your users will hit. Quarantine instead: move it out of the blocking gate, file a ticket with an owner and a date, and **delete the test if the deadline passes**. A quarantine with no deadline is deletion with extra steps.

## Warning Signs

- `pytest-rerunfailures` in the default CI invocation
- `time.sleep` anywhere outside a poll loop
- Tests that must run in file order, or a `test_01_` naming scheme
- Module-level or session-scoped mutable fixtures
- `datetime.now()` / `random()` called inside assertions
- "Just re-run it" as a standing response in code review
- No record of which tests failed last week, so no flake ranking exists
