# Mutation Testing (Minimal)

## Purpose
Test the tests: deliberately break the production code and check that some test notices.

## Core Techniques

### 1. Understand Why Coverage Lies
Coverage says a line executed. It never says an assertion depended on it.

```python
def apply_discount(total, is_member):
    if total > 100 and is_member:
        return total * 0.9
    return total

def test_discount():
    assert apply_discount(150, True) == 135      # 100% line coverage
```

Mutate `>` to `>=`: still 135, mutant survives. Mutate `and` to `or`: 150 with a non-member now returns 135, but no test passes a non-member, so that survives too. Full line coverage, and the boundary and the conjunction are both untested.

### 2. Know the Standard Operators
| Operator | Example mutation |
|---|---|
| Conditional boundary | `a > b` → `a >= b` |
| Negate conditional | `a == b` → `a != b` |
| Math | `a + b` → `a - b` |
| Return value | `return x` → `return None` |
| Constant | `0` → `1`, `""` → `"XX"` |
| Removed call | `logger.warn(...)` → deleted |

### 3. Read the Score Correctly
```
mutation score = killed / (generated - equivalent)
```
A *killed* mutant made a test fail — good. A *survivor* is either a missing assertion or an equivalent mutant (semantically identical, e.g. `i < n` → `i != n` in a loop that increments by one). Equivalent mutants cannot be detected automatically in general, so a 100% score is not the target. 80% on core business logic is a strong result; the useful artifact is the survivor list, not the number.

### 4. Run It, Read the Survivors
```bash
# Python
mutmut run --paths-to-mutate src/billing/
mutmut results
mutmut show 47              # exact diff of one surviving mutant

# JavaScript / TypeScript
npx stryker run --mutate 'src/pricing/**/*.ts'
```

### 5. Scope It — Full Runs Are Unaffordable
Cost is roughly `mutants × suite runtime`. A 900-mutant module against a 40-second suite is ~10 hours serially. Make it tractable by scoping to the diff and running nightly, not per-commit:

```bash
npx stryker run --since=main --incremental
```
Tools reduce the constant by running only the tests that cover each mutated line, but the shape stays multiplicative. Point it at logic that would be expensive to get wrong — pricing, permissions, state machines — never at serializers or wiring.

### 6. Fix Survivors With Assertions, Not Tests
A survivor usually means an existing test exercised the line without checking its effect. Strengthen the assertion first; add a new case only when a genuine input class is missing.

## Warning Signs

- High coverage paired with regular escaped production bugs
- Tests with no assertion, or asserting only "did not raise"
- Every boundary tested at one point only, never both sides
- Mutation run wired into the per-commit gate, so it gets disabled for slowness
- Survivors triaged by raising the threshold instead of reading the diffs
- Equivalent mutants re-litigated every run because nothing marks them resolved
