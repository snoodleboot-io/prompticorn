---
name: observability-tracing-subagent
description: observability tracing subagent
---

# Observability Tracing Subagent (Verbose)

**Focus:** Comprehensive distributed tracing and OpenTelemetry implementation

## Overview

Distributed tracing follows a single request through multiple services, showing the full path and timing. This is essential for understanding how services interact and where latency occurs.

## When to Use

- **Multi-service requests** - Understanding end-to-end flow
- **Performance debugging** - Where is time spent?
- **Service dependency mapping** - How services connect
- **Error diagnosis** - Where did request fail?
- **Latency analysis** - Finding bottlenecks
- **Implementing OpenTelemetry** - Standardized instrumentation
- **Trace sampling** - Cost optimization
- **Root cause analysis** - Tracing through failures

## Core Concepts

### Trace Structure

**One User Request → One Trace → Multiple Spans**

```
User Request [Trace ID: abc-123]
├── API Service [Span 1: 100ms]
│   ├── Auth Service [Span 2: 10ms]
│   │   └── Database [Span 3: 5ms]
│   └── User Service [Span 4: 80ms]
│       └── Cache [Span 5: 2ms]
│       └── Database [Span 6: 78ms]
└── Total: 100ms
```

**Trace:** Complete journey of one request
**Span:** One operation (RPC call, DB query, HTTP request)
**Span Context:** Metadata passed between services

### Span Attributes

**Standard Attributes:**
- `trace_id` - Unique request ID (shared across all spans)
- `span_id` - Unique operation ID (within trace)
- `parent_span_id` - Which span called this?
- `start_time` - When operation started
- `end_time` - When operation finished
- `duration` - How long (ms, μs)
- `status` - OK, ERROR, UNSET
- `attributes` - Custom fields (user_id, query, etc)

**Error Handling:**
- `error=true` - Mark span as error
- `exception` - Exception details
- `error.kind` - Exception class name
- `error.message` - Exception message
- `error.stack_trace` - Stack trace

### Trace Context Propagation

**Problem:**
```
Client → Service A → Service B
How does Service B know this is part of same trace?
```

**Solution: Propagate Headers**

```
HTTP Headers:
  traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
  tracestate: vendor=data

Service A reads header, gets trace_id
Service A makes request to Service B
Service A sets headers with trace_id
Service B reads headers, continues same trace
```

**Standard:** W3C Trace Context
```
traceparent: version-trace_id-parent_id-trace_flags
```

**Implementation:**
```python
# Service A receives request
trace_id = request.headers.get('traceparent')

# Service A makes downstream call
with tracer.start_as_current_span("call_service_b") as span:
    response = requests.get(
        "http://service-b/api",
        headers={
            'traceparent': trace_context.to_headers()
        }
    )
```

### Baggage (Request-Level Context)

**Problem:** Need to pass metadata (user_id, tenant_id) through all spans

**Solution: Baggage**
```
Baggage: user_id=123, tenant_id=acme, request_priority=high

Service A logs with baggage
  → Calls Service B
  → Service B logs with same baggage
  → Service B calls Service C
  → Service C logs with same baggage
```

**Usage:**
```python
# Set baggage
baggage.set("user_id", "123")
baggage.set("tenant_id", "acme")

# All subsequent spans automatically include baggage
with tracer.start_as_current_span("operation"):
    pass  # This span automatically has user_id and tenant_id
```

### Sampling

**Problem:** Tracing every request = massive storage and cost
```
1M requests/sec = Too much data to store
```

**Solution: Sampling**

**Head Sampling:**
- Decide at request entry point
- Either trace whole request or none
- Pro: Efficient, consistent
- Con: Might miss interesting traces
- Typical: 1-10% of requests

```python
# Trace 1% of requests
if random() < 0.01:
    collect_trace()
else:
    skip_trace()
```

**Tail Sampling:**
- Collect all traces initially
- Decide which to keep based on content
- Pro: Can keep "interesting" traces (errors)
- Con: More storage initially, then filter
- Typical: Keep 100% errors, 1% successes

```
Collect all traces
  ↓ (analyze)
Keep if: error=true OR duration > 1s OR user_id == vip
Drop if: success AND duration < 100ms AND regular_user
```

**Sampling Strategies:**
- Always sample errors
- Sample 1-10% of successful requests
- Sample 100% of slow requests (P99 latency)
- Probabilistic sampling (based on headers)

### OpenTelemetry

**What is OpenTelemetry?**
- Standardized instrumentation library
- Works with any backend (Jaeger, Datadog, Honeycomb)
- Vendor-neutral
- Pre-built integrations for popular frameworks

**Components:**
- **API** - What you call in code
- **SDK** - Implementation details
- **Exporters** - Send to backend
- **Instrumentation** - Pre-built for frameworks

**Basic Usage:**

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# Use
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("my_operation") as span:
    span.set_attribute("user_id", 123)
    # do work
```

**Automatic Instrumentation:**
```python
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Automatically tracks HTTP requests
FlaskInstrumentor().instrument()
RequestsInstrumentor().instrument()
```

### Span Creation Patterns

**Standard Span:**
```python
with tracer.start_as_current_span("operation") as span:
    span.set_attribute("key", "value")
    # Do work
    # Span automatically closed on exit
```

**Async Span:**
```python
async def async_operation():
    with tracer.start_as_current_span("async_op") as span:
        result = await async_work()
        return result
```

**Manual Span Management:**
```python
span = tracer.start_span("operation")
try:
    do_work()
    span.set_status(Status(StatusCode.OK))
finally:
    span.end()
```

**Nested Spans:**
```python
with tracer.start_as_current_span("parent") as parent:
    do_parent_work()
    
    with tracer.start_as_current_span("child") as child:
        do_child_work()
        # child span is linked to parent
    
    # parent span continues
```

### Common Span Types

**HTTP Request:**
```python
with tracer.start_as_current_span("http.request") as span:
    span.set_attribute("http.method", "GET")
    span.set_attribute("http.url", "/api/users")
    span.set_attribute("http.status_code", 200)
    span.set_attribute("http.duration_ms", 145)
```

**Database Query:**
```python
with tracer.start_as_current_span("db.query") as span:
    span.set_attribute("db.system", "postgresql")
    span.set_attribute("db.statement", "SELECT * FROM users")
    span.set_attribute("db.rows_affected", 42)
```

**Cache Operation:**
```python
with tracer.start_as_current_span("cache.get") as span:
    span.set_attribute("cache.system", "redis")
    span.set_attribute("cache.key", "user:123")
    span.set_attribute("cache.hit", True)
```

**Error Span:**
```python
with tracer.start_as_current_span("process_order") as span:
    try:
        process_order(order_id)
    except ValidationError as e:
        span.set_status(Status(StatusCode.ERROR))
        span.set_attribute("error", True)
        span.set_attribute("error.kind", "ValidationError")
        span.set_attribute("error.message", str(e))
        raise
```

### Trace Analysis

**Questions Traces Help Answer:**

1. **Where is latency?**
   - Find slowest span
   - Investigate that service/operation

2. **What failed?**
   - Find span with error=true
   - Check attributes for error details
   - Trace back to root cause

3. **What services are called?**
   - View service dependency graph
   - Identify unexpected dependencies

4. **Is there queueing?**
   - Gap between request arrival and processing start
   - Indicates service saturation

5. **Are retries happening?**
   - Multiple spans for same operation
   - Indicates transient failures

**Performance Optimization:**
- Slow database query? Optimize query
- Slow RPC? Check network latency
- Slow cache? High miss rate?
- Slow deserialization? Use faster codec

### Common Mistakes

- **Too fine-grained spans** - One span per line (overkill)
- **Too coarse spans** - One span per request (not useful)
- **Missing context** - Spans without attributes
- **Unsampled errors** - Dropping error traces
- **No correlation** - Can't link to logs/metrics
- **Sampling too aggressive** - Lose visibility
- **No propagation** - Traces break at service boundaries
- **Memory leaks** - Not cleaning up spans
- **Performance impact** - Tracing overhead too high

### Trace Backends

**Jaeger:**
- Open source, CNCF project
- Good visualization, affordable
- Self-hosted or managed
- Good for: On-premise, cost-conscious

**Zipkin:**
- Older, simpler than Jaeger
- Good for: Simple use cases
- Cons: Fewer features than newer options

**Datadog:**
- Commercial, comprehensive
- Integrated with metrics/logs
- Good for: Complete observability platform

**Honeycomb:**
- Commercial, trace-focused
- Good for: High-cardinality tracing
- Expensive but powerful

**AWS X-Ray:**
- AWS-native
- Integrated with Lambda, ECS, etc
- Good for: AWS-first organizations
