# Serverless Architecture (Minimal)

## Purpose
Build systems from managed, event-driven, scale-to-zero compute (FaaS plus
managed backing services) so you pay per use and manage no servers — and know the
workload shapes where that is the wrong choice.

## Core Techniques

### 1. Know What Serverless Buys — and Where It Loses
Functions-as-a-service (Lambda, Cloud Functions, Cloud Run, Azure Functions)
give you no server management, automatic scaling including scale-to-zero, and
per-invocation billing. That wins decisively for **spiky, low-baseline, or
event-driven** load — you pay nothing while idle.

It loses for **steady high-throughput** workloads: an always-on container or VM
running near capacity is usually cheaper per request than millions of billed
invocations, and it avoids cold-start latency. Serverless is a load-shape
decision, not a modernity decision.

### 2. Design for Statelessness and Short Lives
A function instance is ephemeral and may be frozen or destroyed between calls.
Keep no durable state in local memory or disk; push it to a managed store
(see managed-database-selection, distributed-caching-design). Every function has
a per-invocation timeout you must design around — long jobs must be broken up or
handed to a batch/queue system.

### 3. Manage Cold Starts
A cold start is the latency to initialize a fresh runtime before your handler
runs. It grows with package size, heavy initialization, and VPC attachment.
Reduce it by trimming dependencies, moving one-time setup out of the hot path,
choosing a lighter runtime, and using provisioned/warmed concurrency for
latency-sensitive paths. Accept it where a little tail latency is fine.

### 4. Compose Around Events, Not Calls
Trigger functions from events: an HTTP request via an API gateway, a queue or
topic message, an object-created notification, a schedule. Keep each function
single-purpose. Fan out through a queue or pub/sub topic rather than one function
directly invoking the next.

### 5. Orchestrate Multi-Step Work Explicitly
Do not chain functions by having one synchronously invoke the next — you pay for
both while the caller waits, and you couple their timeouts. Use a workflow
orchestrator (AWS Step Functions, Google Workflows, Azure Durable Functions) to
run a state machine with retries, branching, and visible progress.

### 6. Assume At-Least-Once Delivery
Event sources and queues generally deliver at least once, so a function can run
twice on the same message. Make handlers idempotent (see idempotency-patterns)
and route repeated failures to a dead-letter queue for inspection.

## Warning Signs
- Reaching for serverless on a steady, high-throughput service to look modern
- Local/in-memory state assumed to survive between invocations
- A long-running job fighting the invocation timeout instead of being split
- Function A synchronously calling B calling C — double billing and coupled
  timeouts where an orchestrator belongs
- Non-idempotent handlers on an at-least-once source, so retries corrupt data
- Cold-start latency discovered in production because nobody load-tested the
  scale-from-zero path
- No dead-letter queue, so failed events vanish silently
