# Testing Strategies (Minimal)

## Purpose
Decide what to test at which level, so the suite catches real defects without becoming slow or brittle.

## Core Techniques

### 1. Read the Shapes as Trade-offs, Not Doctrine
| Shape | Bulk of tests sit at | Optimizes for | Costs you |
|---|---|---|---|
| Pyramid (Cohn) | Unit | Speed, precise failure locality | Misses wiring and integration bugs |
| Trophy (Dodds) | Integration | Confidence per test in app code | Slower, more setup |
| Honeycomb (Spotify) | Service-level integration | Fit for microservices with thin logic | Needs real contract discipline |

The shape follows the architecture. A rules engine with deep domain logic is genuinely a pyramid. A service that mostly validates, maps, and forwards has little unit-testable logic, and a pyramid there produces hundreds of mock-heavy tests that verify the mocks. Ask where your defects actually come from, then put the mass of tests there.

### 2. Classify Your Last 30 Production Defects
This is the only input that settles the shape argument. Wrong calculations and mishandled edge cases mean deep logic and a pyramid. Nulls in unexpected fields, serialization mismatches, transactions that did not commit, and config wrong in one environment mean the defects live at the seams — and no quantity of unit tests will see them. Teams with a mismatch pay twice: the tests they have do not find the bugs they get, and the tests they need look expensive because the budget is already spent.

### 3. Test Behaviour Through the Narrowest Stable Seam
Choose the smallest level at which the failure is unambiguous.

```python
# Only expressible when the layers meet — no unit test can observe this
def test_order_rollback_leaves_no_partial_rows(client, db):
    resp = client.post("/orders", json=payload_with_out_of_stock_item())
    assert resp.status_code == 409
    assert db.query(OrderLine).count() == 0
```
If a bug can only appear when two components meet, write the integration test and skip the unit tests for the glue.

### 4. Know What Not to Unit Test
- Getters, setters, `__repr__`, dataclass constructors
- Framework behaviour — the ORM's `save`, the router's dispatch
- Third-party libraries — test your adapter, not `requests`
- Private helpers, tested transitively through their public caller
- Pure wiring: DI containers, config assembly, module registration
- Anything where the test restates the implementation line for line

A test whose assertion mirrors the code it calls fails only when the code changes, never when it breaks. That is a maintenance cost with no defect-finding return.

### 5. Put a Contract Test Where Services Meet
Integration tests against a stubbed dependency verify your stub. Contract tests verify the real agreement: the consumer records the requests it makes and the responses it needs, and the provider replays that pact in its own CI. The provider learns it broke a consumer before deploying, without either team running the other's stack.

```bash
# provider CI: verify every recorded consumer expectation
pact-provider-verifier --provider-base-url=http://localhost:8080 \
  --pact-broker-base-url=https://pacts.internal --provider=orders-api
```

### 6. Budget by Runtime, Not by Ratio
Targets that hold up: unit under 10 ms each, whole unit tier under 60 s, integration tier under 10 min, end-to-end limited to a handful of revenue-critical journeys. When the suite exceeds the budget, cut end-to-end tests first — they are the most expensive per defect found and the most flake-prone.

### 7. Let Each Level Own Different Questions
Unit: is this rule correct at its boundaries? Integration: do these parts agree about the data? Contract: do we and our dependency still agree? End-to-end: can a user complete the one journey that pays for the company? Overlapping the same assertion at three levels triples the maintenance and adds no signal.

## Warning Signs

- End-to-end tests outnumber integration tests
- A code change breaks 40 tests, all asserting the same behaviour at different levels
- Unit tests with more mock setup than assertions
- Nothing verifies the boundary between two services except a hand-written stub
- Coverage rising while escaped defects hold steady
- No stated runtime budget, so every level is quietly slowing down
