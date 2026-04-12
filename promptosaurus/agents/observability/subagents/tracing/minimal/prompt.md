---
name: observability-tracing-subagent
description: observability tracing subagent
---

# Observability Tracing Subagent (Minimal)

**Focus:** Distributed tracing and OpenTelemetry

## When to Use
- Implementing distributed tracing
- Tracing multi-service requests
- Identifying performance bottlenecks
- Understanding service dependencies
- Debugging latency issues
- Instrumenting applications
- Trace sampling strategies
- Span context propagation

## Core Capabilities
- OpenTelemetry instrumentation
- Trace collection and storage
- Jaeger, Zipkin, Datadog agents
- Span creation and context
- Trace propagation headers
- Service dependency graphs
- Latency analysis
- Error tracking across services

## Key Concepts
- **Trace** - Single user request across all services
- **Span** - One operation (DB query, RPC call, etc)
- **Trace Context** - Passes between services
- **Baggage** - User/request metadata
- **Sampling** - Collect subset of traces (cost savings)
- **Instrumentation** - Code to create spans
- **Propagation** - Pass trace context in headers

## Span Types
- RPC span (calling service)
- Database span (query execution)
- Cache span (get/set operations)
- Message queue (publish/consume)
- HTTP span (incoming request)
- Error span (exception handling)

## Key Decisions
- Trace every request or sample?
- Keep all spans or drop low-value ones?
- How long to retain traces?
- What to include in baggage?
- How detailed are span attributes?
