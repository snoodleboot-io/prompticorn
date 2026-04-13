# Distributed Tracing Instrumentation (Verbose)

## End-to-End Request Flow

```
User Request
    ↓
API Gateway (span: api-request)
    ├─ Authenticate (span: auth)
    ├─ Validate (span: validate)
    └─ Route to Service (span: route)
        ↓
Application Service (span: process-order)
        ├─ Database query (span: db-select)
        ├─ Cache lookup (span: cache-get)
        └─ External API call (span: payment-api)
            ↓
Trace contains all spans with timing
```

## Implementation Pattern

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# 1. Setup exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger.example.com",
    agent_port=6831,
)

# 2. Create tracer
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))
trace.set_tracer_provider(provider)

# 3. Use tracer
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("process_order") as span:
    span.set_attribute("order.id", order_id)
    span.set_attribute("customer.id", customer_id)
    
    # Nested span (automatic parent-child relationship)
    with tracer.start_as_current_span("fetch_customer") as span:
        customer = fetch_from_db(customer_id)
```

## Span Attributes (Context)

```python
# Semantic conventions (standard across languages)
span.set_attribute("service.name", "order-service")
span.set_attribute("service.version", "1.2.3")

# HTTP request
span.set_attribute("http.method", "POST")
span.set_attribute("http.url", "/api/orders")
span.set_attribute("http.status_code", 201)
span.set_attribute("http.client_ip", "192.168.1.1")

# Database
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.statement", "SELECT * FROM orders WHERE id = ?")
span.set_attribute("db.rows_affected", 1)

# Business logic
span.set_attribute("order.id", "12345")
span.set_attribute("order.total", 99.99)
```

## Trace Context Propagation

```python
# Service A: Create trace context in headers
from opentelemetry.propagate import inject
import requests

headers = {}
inject(headers)  # Adds: traceparent, tracestate
response = requests.post(url, headers=headers)

# Service B: Extract trace context from headers
from opentelemetry.propagate import extract
from opentelemetry import trace

ctx = extract(request.headers)
trace.get_current_span().update_from_context(ctx)
# Now spans in B are children of A's spans
```

## Sampling Strategy

```python
# Always sample critical paths
class CriticalPathSampler(Sampler):
    def should_sample(self, trace_id, attributes):
        # Always trace payment operations
        if attributes.get("operation") == "payment":
            return True
        
        # 1% of normal traffic
        return random.random() < 0.01

# Adaptive sampling (high traffic = lower sample %)
class AdaptiveSampler(Sampler):
    def should_sample(self, trace_id, attributes):
        traffic_per_minute = get_current_traffic()
        
        if traffic_per_minute < 100:
            return True  # Low traffic, sample all
        elif traffic_per_minute < 1000:
            return random.random() < 0.1  # 10%
        else:
            return random.random() < 0.01  # 1%
```

## Events and Exceptions

```python
# Log events within span
span.add_event("payment_initiated", 
    {"amount": 99.99, "currency": "USD"}
)
span.add_event("payment_completed",
    {"transaction_id": "tx_123"}
)

# Record exceptions
try:
    process_order()
except Exception as e:
    span.record_exception(e)
    span.set_attribute("error", True)
    raise
```

## Debugging with Traces

```
Trace ID: 3aa14d3baad17f2f
Spans:
  1. api-gateway (0-50ms)
      └─ auth (0-5ms) ✓
      └─ validate (5-10ms) ✓
      └─ route (10-50ms) ✓
  
  2. order-service (50-400ms)
      └─ fetch-customer (50-80ms) ✓
      └─ calculate-price (80-150ms) ✓
      └─ payment-api (150-350ms) ⚠ SLOW!
      └─ update-db (350-400ms) ✓

Total latency: 400ms
Bottleneck: payment-api (200ms, 50% of total)
```

## Common Mistakes

❌ Tracing every single function (too many spans)  
✅ Trace logical operations only (API calls, DB queries)

❌ Including sensitive data in spans  
✅ Filter PII (passwords, tokens, credit cards)

❌ No sampling in high-volume services  
✅ Sample 1-10% in production
