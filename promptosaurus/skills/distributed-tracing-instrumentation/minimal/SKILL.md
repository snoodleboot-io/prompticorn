# Distributed Tracing Instrumentation (Minimal)

## Basic Setup

```python
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup Jaeger exporter
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
```

## Creating Spans

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

# Manual span
with tracer.start_as_current_span("process_order") as span:
    span.set_attribute("order.id", order_id)
    order = process(order_id)
```

## Propagating Context

```python
from opentelemetry.propagate import inject, extract
import requests

# Inject context into HTTP headers
headers = {}
inject(headers)
response = requests.get(url, headers=headers)

# Extract context from received headers
ctx = extract(headers)
# Now spans in this service linked to upstream
```

## Common Attributes

```python
span.set_attribute("service.name", "order-service")
span.set_attribute("span.kind", "server")
span.set_attribute("http.method", "POST")
span.set_attribute("http.status_code", 200)
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.statement", "SELECT...")
```

## Events (Logging in Spans)

```python
span.add_event("order_created", {"order_id": 123})
span.record_exception(exception)
```
