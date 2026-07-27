# Message Queue Selection (Minimal)

## Purpose
Choose a messaging system by what your consumers need — delivery guarantee, ordering, retention, fan-out — not by brand familiarity.

## Core Techniques

### 1. Know the Three Shapes: Queue, Pub/Sub, Log
They solve different problems; picking the wrong shape is the root mistake.

- **Work queue** — each message goes to *one* consumer, then is deleted. For distributing tasks across workers. (SQS, Cloud Tasks.)
- **Pub/sub (fan-out)** — each message is delivered to *every* subscriber, then gone. For notifying N independent consumers of an event. (SNS, Pub/Sub topics.)
- **Log** — an ordered, *retained* record consumers read by offset; messages survive being read and can be re-read. For replay, multiple independent readers at their own pace, and event sourcing. (Kafka, Kinesis.)

Ask: one worker or many? Consumed-and-gone or retained-and-replayable? That picks the shape.

### 2. Accept That Exactly-Once Is Mostly a Lie
Distributed messaging is **at-least-once** in practice: to guarantee delivery, a system must redeliver when an ack is lost — so consumers *will* see duplicates. "Exactly-once" offerings are narrow (specific-broker, specific-path) and don't extend to your side effects.

Design for at-least-once and make consumers **idempotent** so a duplicate is harmless. This is the single most important messaging discipline. See `idempotency-patterns`.

### 3. Only Buy Ordering Where You Need It
Strict global ordering costs throughput and parallelism (it serializes). Most systems need ordering only *per key* (per account, per order), not globally.

- Need per-entity order → partition/group by that key (FIFO group, Kafka partition key). Order holds within a key; keys run in parallel.
- Don't need order → take the unordered, higher-throughput path.

### 4. Always Wire a Dead-Letter Queue
A message that fails repeatedly will otherwise retry forever, block its partition, or vanish silently. Route it to a **DLQ** after N attempts so the pipeline keeps moving and the poison message is captured for inspection — not lost, not looping.

### 5. Plan for Backpressure
Producers can outrun consumers. Decide what happens when the queue grows: consumers autoscale on **backlog depth** (not CPU), producers slow down, or messages expire. An unbounded, unmonitored queue converts a slow consumer into an outage and, for retained logs, silent data loss when retention expires before you catch up.

## Warning Signs
- Consumer assumes each message arrives exactly once
- Global ordering required when per-key would do (throughput bottleneck)
- No dead-letter queue — failures retry forever or disappear
- Pub/sub used where you needed retention/replay (or a log where simple fan-out sufficed)
- Queue depth and consumer lag not monitored or alerted
- No idempotency key on operations with side effects
- Retention shorter than worst-case consumer downtime

## See Also
- `idempotency-patterns` — making at-least-once delivery safe
- `microservices-communication-patterns` — sync vs async, event-driven design
