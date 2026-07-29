---
name: "workflow-testing-patterns"
description: Test workflows with unit, integration, and E2E tests
type: workflow
category: workflow-patterns
minimal: true
---

# Workflow Testing Patterns Workflow

Testing the orchestration — graph, gates, retries, compensation — not just the code
each step calls. Step logic is ordinary code; the wiring is what breaks in production.

## Core Concepts — the levels
- **Step unit:** one step, dependencies mocked
- **Graph:** the definition, no execution — cycles, bad refs, orphans
- **Orchestration:** full run with stubbed steps — order, gates, retry, compensation
- **Integration:** real dependencies, small data — contracts and permissions
- **End-to-end:** production-like shape and volume

**Graph and orchestration are the levels usually missing** — and the cheapest,
needing no real dependencies.

## Pattern Types
- **Static graph assertions:** acyclic, every `depends_on` resolves, no orphans
- **Executable invariants:** a retried step with side effects must declare an
  idempotency key; irreversible steps must come last
- **Stubbed-run tests:** assert compensation order, attempt counts, that permanent
  errors are not retried, that independent branches still finish
- **Injected clock:** advance time, never sleep; test DST, month ends, missed windows
- **Parity tests:** run old and new against a fixture, compare checksums — the CI
  form of a shadow run

## When to Use
- Every workflow definition, on every change, in CI

## Key Considerations
- **Always test empty input** — the most common untested path; workflows publish
  empty results over good ones
- **Sort before asserting** on fan-out results; asserting incidental order is the
  standard source of flaky workflow tests
- **Exercise compensation paths** — an unexecuted compensation is untested
- Pin stubs with contract tests, or they drift from real step behaviour
