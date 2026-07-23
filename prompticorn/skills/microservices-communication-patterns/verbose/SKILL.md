# Microservices Communication Patterns (Verbose)

## Core Patterns

### The Cost of a Synchronous Hop

Every synchronous call does two things beyond transferring data: it adds the
callee's latency to yours, and it makes your availability the product of both.

For a serial chain of N dependencies each at availability *a*, the composite is
*a*^N:

| Depth | 99% each | 99.9% each | Downtime/month at 99% |
|---|---|---|---|
| 1 | 99.0% | 99.9% | 7.2 h |
| 3 | 97.0% | 99.7% | 21.6 h |
| 5 | 95.1% | 99.5% | 35.6 h |
| 10 | 90.4% | 99.0% | 69.1 h |

Latency behaves worse than the naive sum suggests. If each of five hops has a p99
of 100 ms, the end-to-end p99 is not 500 ms — a request is slow when *any* hop is
slow, so the probability of hitting at least one tail event rises with depth. Tail
latency amplification is why deep call graphs feel unpredictable even when every
service's own dashboard looks fine.

This arithmetic, not throughput, is the real argument for asynchronous
communication. It is also an argument for shallower graphs: a service that must
call four others to answer one question is usually a boundary drawn in the wrong
place.

### Choosing the Interaction Style

| Style | Coupling | Caller waits | Failure of callee | Fits |
|---|---|---|---|---|
| Sync request/response (HTTP, gRPC) | Temporal + availability | Yes | Caller fails or degrades | Reads the caller needs now |
| Async command (queue, one consumer) | Contract only | No | Message waits | Work that must happen, not now |
| Event pub/sub (broker, N consumers) | Schema only | No | Consumer lags | Notifying an open set of listeners |
| Request/reply over broker | Contract + correlation | Logically | Reply times out | Long-running jobs with a result |

The useful question is: *what does the caller do with the response?* If it needs the
value to build its own answer, the call is synchronous and you should focus on
bounding it. If it merely triggers work elsewhere, publishing is strictly better —
the caller's success no longer depends on the consumer being up.

gRPC versus REST is a much smaller decision than sync versus async. gRPC buys
binary framing, streaming, and generated clients from a schema; REST buys
debuggability and universal tooling. Both are synchronous, and both carry the
availability multiplication above.

### Events as Facts, Not Commands

```json
{
  "event": "order.placed",
  "schema_version": 2,
  "occurred_at": "2026-07-19T10:03:11Z",
  "event_id": "01J8ZQ5N2K",
  "data": {"order_id": "8812", "customer_id": "441", "total_cents": 4200}
}
```

Name events in the past tense, after a fact that occurred in the producer's own
domain. The producer must not know or care who subscribes. Contrast:

❌ `order.send_confirmation_email` — the producer now knows email exists. Adding
a loyalty-points reaction means changing the order service.
✅ `order.placed` — email, loyalty, analytics, and fraud each subscribe
independently, and the producer never changes again.

That is the actual decoupling: the *set of consumers can grow without touching the
producer*. Publishing a command over a broker keeps the original coupling and adds
a network component; you have moved the problem, not solved it.

Include enough data in the event that common consumers do not have to call back for
details. A thin event (`{"order_id": "8812"}`) forces every consumer into a
synchronous callback to the producer — reintroducing the fan-in you were avoiding,
now with a race against the producer's own commit.

### Delivery Semantics and Idempotency

Brokers offer at-most-once or at-least-once. Anything worth building uses
at-least-once, which means duplicates are not an edge case — they are guaranteed
by the design. Redelivery happens when a consumer crashes after processing but
before acking, when a partition rebalances mid-batch, and when a visibility timeout
expires because a message took longer than expected.

Vendor "exactly-once" features are exactly-once *within their own boundary* (for
example, a Kafka read-process-write transaction across topics). The moment your
handler charges a card or calls a third party, the transport cannot help — the
consumer must deduplicate.

```python
def handle(msg):
    # Producer-assigned id, stable across redeliveries.
    inserted = db.execute(
        "INSERT INTO processed_events (event_id) VALUES (%s) "
        "ON CONFLICT DO NOTHING",
        msg.event_id,
    ).rowcount
    if not inserted:
        return                      # duplicate: ack and stop

    charge_card(msg.data)
```

Note the ordering constraint: the dedupe claim and the side effect should share a
transaction where possible, or the claim should be committed only after the effect
succeeds — otherwise a crash between them makes the work permanently skipped. The
full design space, including keys for synchronous APIs, is in the
`idempotency-patterns` skill.

Ordering deserves the same skepticism. Kafka guarantees order within a partition,
not across a topic; SQS standard queues guarantee nothing. If a consumer needs
per-entity order, partition by entity id and accept that one slow key blocks its
partition.

### Bounding Synchronous Calls

```python
# Timeout, retry, breaker, and a dedicated pool — all four, explicitly.
resp = http.get(
    "https://pricing/v1/quote",
    timeout=(0.2, 0.8),      # connect, read — always set both
)
```

**Timeouts** must be explicit and must shrink as you go deeper. If your own SLA to
the caller is 1 s and you make two dependent calls, neither can be allowed 900 ms.
A library default of "no timeout" is the single most common cause of thread-pool
exhaustion cascading into an outage.

**Retries** are only safe on idempotent operations. Always exponential, always
jittered: synchronized retries from thousands of clients are how a service that has
just recovered is immediately knocked down again. Cap total attempts, and never
retry at multiple layers simultaneously — three layers each retrying three times is
27 requests for one logical call.

**Circuit breakers** convert slow failure into fast failure. Once the error rate
over a window crosses a threshold, reject immediately for a cooldown, then allow a
trickle of probes. This protects the *caller's* capacity as much as the callee's.

**Bulkheads** — a separate connection pool or semaphore per dependency — stop one
slow callee from consuming every worker and taking down request paths that do not
even touch it.

**Fallbacks** decide what "degraded" means. Cached prices, a default
recommendation, or an explicit partial response all beat a 500. Choose per call
site; there is no generic answer.

### Sagas Instead of Distributed Transactions

You cannot hold a transaction across services. The replacement is a sequence of
local transactions, each with a compensating action:

```
reserve_inventory   → compensate: release_inventory
charge_payment      → compensate: refund_payment
schedule_shipment   → compensate: cancel_shipment
```

Choreographed sagas (each step emits an event the next step consumes) have no
central component but are hard to observe — nobody can answer "where is order 8812
stuck?" without reconstructing it from logs. Orchestrated sagas put one coordinator
in charge; it is another service to run, and it is worth it beyond three steps.

Compensations are business operations, not rollbacks. Refunding is not the inverse
of charging: the money moved, the customer saw a statement line, and the ledger must
show both. Design them as first-class domain actions.

### Publishing Reliably: The Outbox

Writing to your database and publishing to a broker are two systems, so a crash
between them leaves state without an event (or an event without state).

```sql
BEGIN;
  INSERT INTO orders (id, total_cents) VALUES ('8812', 4200);
  INSERT INTO outbox (event_id, topic, payload)
    VALUES ('01J8ZQ5N2K', 'order.placed', '{"order_id":"8812"}');
COMMIT;
-- A relay polls outbox and publishes, marking rows sent.
```

One transaction, one atomic outcome. The relay may publish a row twice after its
own crash — which is fine, because consumers are idempotent already.

### Discovery, Mesh, and Observability

Service meshes (Envoy-based sidecars) can supply retries, timeouts, mTLS, and
circuit breaking without application code. The trade is real: another control plane
to operate, added per-hop latency, and failure modes that are invisible from inside
the application. Adopt one for uniform mTLS and traffic policy across many
services; do not adopt one to obtain a retry policy three services need.

Whatever the transport, propagate a trace context (W3C `traceparent`) through both
HTTP calls and message headers. Without it, a five-hop request is five unrelated log
streams. See `distributed-tracing-instrumentation`.

## Common Anti-Patterns

❌ **Deep synchronous chains.** A request traversing five services inherits the
product of five availabilities and the union of five tail latencies.
✅ Fetch what you need in parallel, cache aggressively, or restructure so the data
is local. Reconsider the service boundary.

❌ **Calls with no timeout.** One slow dependency saturates the thread pool and
converts a partial degradation into a total outage.
✅ Explicit connect and read timeouts on every call, shrinking with depth.

❌ **Retrying non-idempotent operations.** The classic double charge: the response
was lost, not the request.
✅ Retry only idempotent operations, or make the operation idempotent first.

❌ **Retries at every layer.** Client, gateway, and service each retry three times:
27 requests hit a service that is already failing.
✅ Retry at exactly one layer, with jitter and a total attempt cap.

❌ **Assuming exactly-once delivery.** Consumers written as if duplicates cannot
occur will process duplicates in production.
✅ Deduplicate on a producer-assigned id; treat redelivery as normal.

❌ **Commands disguised as events.** `order.send_confirmation_email` leaves the
producer knowing its consumers.
✅ Past-tense facts. Consumers decide what a fact means for them.

❌ **Async that hides rather than removes coupling.** The producer publishes and
then polls for a status change: a synchronous call with extra latency and no error
path.
✅ Async only where the producer's work is genuinely complete at publish time.

❌ **Shared database between services.** The fastest integration and the hardest to
undo — every schema change becomes a cross-team negotiation.
✅ One writer per store; publish changes as events.

❌ **Dual writes to database and broker.** A crash between them silently diverges
your state from your event stream.
✅ Transactional outbox.

❌ **No dead-letter queue.** A poison message blocks a partition forever or is
dropped silently.
✅ DLQ after bounded retries, with an alert on depth and a documented replay path.

❌ **Unversioned event schemas.** A producer adds a field and consumers deserialize
into exceptions — asynchronously, so nothing 400s and the failure surfaces as
mysterious lag.
✅ `schema_version` on every event; consumers as tolerant readers. See
`api-versioning-strategy`.

## Service Communication Checklist

- [ ] Each interaction justified as sync or async by what the caller does with the result
- [ ] Synchronous call-chain depth measured and kept shallow
- [ ] Explicit connect and read timeouts on every outbound call, shrinking with depth
- [ ] Retries only on idempotent operations, with exponential backoff and jitter
- [ ] Retry logic at exactly one layer, with a total attempt cap
- [ ] Circuit breaker and per-dependency connection pool for each external call
- [ ] Documented fallback or degraded response for every dependency failure
- [ ] Consumers idempotent on a producer-assigned event id
- [ ] Ordering requirements explicit; partitioning key chosen to match them
- [ ] Events named as past-tense facts, carrying enough data to avoid callbacks
- [ ] Event payloads versioned; consumers tolerate unknown fields
- [ ] Transactional outbox wherever a state change and a publish must agree
- [ ] Dead-letter queue configured, alerted on, and replayable
- [ ] Multi-service workflows modeled as sagas with real compensating actions
- [ ] Trace context propagated across HTTP calls and message headers
- [ ] No shared database tables across service boundaries
