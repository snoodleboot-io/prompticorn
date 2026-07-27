# Autoscaling Strategies (Minimal)

## Purpose
Match capacity to demand automatically, on a signal that actually tracks load, without flapping or starving requests during the ramp.

## Core Techniques

### 1. Pick the Trigger Type: Reactive, Scheduled, Predictive
- **Reactive** — respond to a live metric crossing a threshold. Simple, always correct after the fact, but always *late* by the ramp-up time.
- **Scheduled** — change capacity by clock/calendar (business hours, a known campaign). Zero lag when the pattern is genuinely periodic; useless for surprises.
- **Predictive** — forecast load from history and pre-provision. Hides ramp latency, but a wrong forecast over- or under-provisions with confidence.

Combine them: scheduled floor for known cycles, reactive on top for the unexpected.

### 2. Scale on the Signal That Represents Load
CPU is a proxy, and often a bad one. An I/O-bound service saturates at 30% CPU; a queue consumer's real backlog is invisible to CPU entirely.

- Request-driven service → requests-per-second or in-flight concurrency.
- Queue worker → **queue depth** (or oldest-message age / backlog per consumer).
- Latency-sensitive tier → p95 latency as a guardrail alongside the primary signal.

Scale on the thing that hurts users, not the thing that is easy to graph.

### 3. Scale Out Before You Scale Up
- **Scale out (horizontal)** — add instances. Preferred: fault-tolerant, near-unbounded, no restart. Requires stateless (or externalized-state) workloads.
- **Scale up (vertical)** — bigger instance. For stateful singletons that cannot shard, or to fix a genuine per-instance resource wall. Usually needs a restart and hits a ceiling.

Default to horizontal; reach for vertical only when the unit of work cannot be split.

### 4. Plan for Cold Start
New capacity is not instantly useful: instance boot, image pull, runtime warm-up, JIT, cache fill, connection pools. If the ramp is slower than the traffic rise, reactive scaling always arrives late.

- Keep a **warm pool** / minimum replica floor so scale-up adds to a running base.
- Pre-provision ahead of scheduled peaks rather than chasing them.
- For serverless, use provisioned/warm concurrency for latency-critical paths.

### 5. Damp the Feedback Loop to Stop Thrashing
An autoscaler is a control loop; a twitchy one oscillates — scaling out, seeing load drop, scaling in, load returns. Each cycle pays cold-start and churns connections.

- Asymmetric behavior: scale **out fast**, scale **in slow**.
- Use a stabilization/cooldown window on scale-in.
- Keep the metric window long enough to smooth spikes, short enough to stay responsive.

For Kubernetes HPA specifics (utilization-relative-to-requests, stabilization windows), see `kubernetes-resource-management`.

## Warning Signs
- Scaling on CPU for an I/O-bound or queue-driven service
- Replica count oscillating every few minutes (flapping)
- `minReplicas`/floor of zero on a latency-sensitive path — every burst eats a cold start
- Scale-in as aggressive as scale-out
- `max` set below real peak, so the autoscaler silently caps and requests queue
- No forecast or schedule for a load pattern that is obviously periodic
- Predictive scaling with no reactive fallback when the forecast is wrong
