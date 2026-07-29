# Workflow Testing Patterns Workflow

Testing orchestration itself — the graph, the gates, the retries, the compensation
— not just the code each step calls.

Step logic is ordinary code and is tested the ordinary way. What goes untested, and
what breaks in production, is the wiring: an edge pointing at the wrong task, a
retry on a non-idempotent step, a compensation that was never executed once.

---

## 1. The testing pyramid for workflows

| Level | Scope | Speed | What it catches |
|-------|-------|-------|-----------------|
| **Step unit** | One step, dependencies mocked | ms | Step logic errors |
| **Graph** | The definition, no execution | ms | Cycles, bad refs, unreachable tasks |
| **Orchestration** | Full run, steps stubbed | s | Wrong order, missing gates, bad retry config |
| **Integration** | Real dependencies, small data | min | Contract mismatches, permissions |
| **End-to-end** | Production-like, real data shape | min–h | Volume and semantics problems |

The **graph and orchestration levels are the ones usually missing**, and they are
the cheapest of the five. They need no real dependencies and run in milliseconds.

---

## 2. Graph tests — validate the definition statically

### Characteristics:
No execution at all. Assertions against the parsed definition.

### Implementation:
```python
def test_graph_is_acyclic():
    assert not find_cycles(load_workflow("nightly_rollup"))

def test_every_dependency_exists():
    wf = load_workflow("nightly_rollup")
    ids = {t.id for t in wf.tasks}
    for task in wf.tasks:
        assert set(task.depends_on) <= ids, f"{task.id} references a missing task"

def test_every_side_effecting_step_is_idempotent_or_not_retried():
    for task in load_workflow("nightly_rollup").tasks:
        if task.has_side_effects and task.retry.max_attempts > 1:
            assert task.idempotency_key, f"{task.id} retries without an idempotency key"

def test_irreversible_steps_come_last():
    wf = load_workflow("nightly_rollup")
    assert all(not t.compensate for t in downstream_of(wf, first_irreversible(wf)))
```

That third test encodes the rule from `workflow-error-handling-patterns` as an
executable invariant. This is the highest-value category here: it catches the
duplicate-charge class of bug before anything runs.

### Use Cases:
- Every workflow, in CI, on every change to a definition

---

## 3. Orchestration tests — run the graph with stubbed steps

Replace each step with a stub that records its invocation and returns a canned
result. Assert on the *sequence and decisions*, not on step output.

### Implementation:
```python
def test_failure_triggers_compensation_in_reverse():
    run = execute(
        workflow="checkout",
        stubs={"reserve_stock": ok(), "charge_card": ok(), "book_courier": fail()},
    )
    assert run.compensations == ["refund_card", "release_stock"]   # reverse order

def test_transient_failure_retries_then_succeeds():
    run = execute("sync", stubs={"fetch": fails(2).then(ok())})
    assert run.steps["fetch"].attempts == 3
    assert run.status == "succeeded"

def test_permanent_failure_is_not_retried():
    run = execute("sync", stubs={"fetch": fail(ValidationError)})
    assert run.steps["fetch"].attempts == 1

def test_independent_branch_completes_when_sibling_fails():
    run = execute("nightly", stubs={"branch_a": fail()}, on_failure="skip_dependents")
    assert run.steps["branch_b"].status == "succeeded"
```

### Advantages & Disadvantages:
- **Advantage:** Tests the parts that actually break, in milliseconds
- **Advantage:** Failure injection is trivial — no fault-injection infrastructure
- **Disadvantage:** Stubs can drift from real step behaviour; pin them with
  contract tests at the integration level

---

## 4. Testing time

Scheduled workflows are full of time-dependent logic, and real clocks make those
tests slow and flaky.

```python
def test_missed_window_is_backfilled(clock):
    clock.set("2026-07-14T02:00:00Z")
    clock.advance(hours=26)          # simulate a 26h outage
    assert scheduler.pending_runs() == ["2026-07-14", "2026-07-15"]
```

- **Inject the clock.** Never call the system clock inside a workflow definition.
- **Advance time, do not sleep.** A test that sleeps for a retry backoff is a test
  nobody will run.
- Test the boundaries explicitly: DST transitions, month ends, leap days, and the
  missed-window policy.

---

## 5. Data and determinism

### Implementation Strategy:
```yaml
test_data:
  fixtures: small, committed, covering the shapes that matter
  cases: [empty_input, single_row, duplicate_keys, null_in_required, oversized_batch]
  determinism:
    seed: fixed
    clock: injected
    ordering: sorted_before_assert     # never assert on incidental order
```

Test the empty input case first. "Zero rows" is the single most common untested
path, and workflows routinely divide by it or publish an empty result over a good one.

Sort before asserting. Assertions on the incidental ordering of a concurrent
fan-out are the standard source of flaky workflow tests.

---

## 6. Parity testing for changes

When changing a workflow rather than writing a new one, assert equivalence rather
than re-specifying behaviour.

```yaml
parity_test:
  run: [old_version, new_version]
  input: fixed_fixture
  compare: [output_checksum, row_count, side_effects_recorded]
  ignore: [timestamps, run_id, ordering]
```

This is the offline form of the shadow run in `workflow-migration-patterns`, and it
belongs in CI where it is cheap.

---

## Best Practices

1. **Test the graph statically in CI** — cycles, refs, orphans, on every change.
2. **Encode failure-handling rules as executable invariants** (retry implies
   idempotency; irreversible steps last).
3. **Test orchestration with stubbed steps.** It is fast, and it is where the bugs are.
4. **Inject the clock; advance rather than sleep.**
5. **Always test the empty-input case.**
6. **Sort before asserting** on any fan-out result.
7. **Test compensation paths.** An unexecuted compensation is an untested one.
8. **Parity-test changes** rather than rewriting expectations.

---

## Common Pitfalls

- **Only testing step logic.** The wiring is what fails in production.
- **Never exercising compensation.** It is first run during a real incident.
- **Real sleeps for retry backoff.** Slow suite, then a disabled suite.
- **Asserting on concurrent completion order.** Flaky by construction.
- **No empty-input test.** The workflow publishes an empty result over a good one.
- **Stubs that drifted from reality.** Green tests, broken integration — pin with
  contract tests.
- **E2E-only coverage.** Slow, flaky, and it localizes nothing when it fails.

---

## Related Patterns

- `workflow-error-handling-patterns` — the retry and compensation rules to assert
- `workflow-dependency-management` — the graph invariants to validate
- `workflow-migration-patterns` — shadow runs, of which parity tests are the CI form
- `testing` — general test structure and coverage conventions