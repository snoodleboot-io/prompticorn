# Microservices Communication Patterns (Minimal)

## Purpose
Choose how services talk to each other, given that every synchronous call adds latency and borrows the callee's availability.

## Core Techniques

### 1. Do the Availability Arithmetic

A synchronous chain multiplies. Five services at 99% each, called in series, yield 0.99^5 ≈ 95.1% — roughly 36 hours of downtime a month, from components that each look healthy.

Latency composes the same way, and worse at the tail: five hops of p99 = 100 ms is not a 100 ms p99 end to end, because a request is slow if *any* hop is slow.

| Chain depth | Availability (99% each) | Downtime/month |
|---|---|---|
| 1 | 99.0% | 7.2 h |
| 3 | 97.0% | 21.6 h |
| 5 | 95.1% | 35.6 h |

This is the core argument for asynchrony: not throughput, availability.

### 2. Match the Pattern to the Question

| Pattern | Use when | Cost |
|---|---|---|
| Sync request/response | Caller needs the answer to proceed | Latency and availability coupling |
| Async command (queue) | Work must happen, caller need not wait | Requires idempotent consumers |
| Event publish/subscribe | Others may care that something happened | Eventual consistency |
| Request/reply over a broker | Long-running work with a result | Correlation and timeout handling |

Ask what the caller does with the response. If the answer is "nothing, it just logs it," the call should not be synchronous.

### 3. Publish Events, Do Not Send Commands Dressed as Events

```
# ✅ Event: a fact, past tense, no assumption about who listens
order.placed        {"order_id": "8812", "total_cents": 4200}

# ❌ Command in disguise: names the consumer and its behavior
order.send_confirmation_email_to_customer
```

The distinction is who owns the decision. An event says what happened; each consumer decides what that means for it. A command names a consumer, which means adding a second reaction requires changing the producer — you have kept the coupling and merely moved it onto a broker.

### 4. At-Least-Once Delivery Makes Idempotency Mandatory

Every real broker redelivers: after a consumer crash before ack, a rebalance, or a visibility timeout expiring on slow work. "Exactly once" end to end is not something the transport can give you — it is something the consumer implements by deduplicating.

```python
def handle(msg):
    if not claim(msg.id):     # INSERT ... ON CONFLICT DO NOTHING
        return                # already processed; ack and move on
    charge_card(...)
```

Use a stable, producer-assigned id, not a broker-generated one that changes on redelivery. See the `idempotency-patterns` skill for the full treatment.

### 5. Bound Every Synchronous Call

An unbounded call is how one slow dependency exhausts your thread pool and takes you down with it:

- **Timeout** shorter than your own caller's timeout, always set explicitly
- **Retry** only on idempotent operations, with exponential backoff and jitter — synchronized retries are how a recovering service gets knocked over again
- **Circuit breaker** so a failing dependency fails fast instead of consuming capacity
- **Bulkhead** — a separate connection pool per dependency, so one slow callee cannot starve the rest

### 6. Know Where Async Only Hides the Coupling

Replacing a call with an event does not decouple anything if the caller still cannot proceed without the result. If the producer publishes and then polls for a status change, you have built a synchronous call with worse latency and no error path. Genuine decoupling means the producer's work is complete at publish time.

## Warning Signs

- A user request that fans out into a chain of four or more synchronous hops
- Any HTTP or gRPC call with no explicit timeout
- Retries on non-idempotent operations, or without jitter
- Consumers that assume each message is delivered exactly once
- Event names in the imperative, naming a specific consumer's action
- Services sharing a database table to avoid writing an interface
- A distributed transaction spanning services (no saga, no compensations)
- Event schemas with no version field and no tolerance for unknown fields
