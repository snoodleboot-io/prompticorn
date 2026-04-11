# Core Conventions LogQL

Language: LogQL (Loki Query Language)
Database: Loki
Style: Clear selectors and filters

## Log Selection

### Label Matchers
```logql
# Exact match
{job="api"}

# Regex match
{job=~"api|auth"}

# Negative match
{job!="test"}
```

### Log Filters
```logql
# Contains
{job="api"} |= "error"

# Doesn't contain
{job="api"} != "warning"

# Regex
{job="api"} |~ "ERROR.*timeout"
```

## Common Queries

### Error Logs
```logql
{service="api"} |= "ERROR" |= "timeout"
```

### Aggregations
```logql
sum(rate({service="api"} |= "ERROR"[5m])) by (endpoint)
```

### Metrics Extraction
```logql
{service="api"} |= "duration=" | 
  metrics duration_ms extracted
```

## Structured Logging
Always use structured logging (JSON):
```json
{
  "timestamp": "2026-04-10T14:30:00Z",
  "service": "api",
  "level": "ERROR",
  "message": "Order processing failed",
  "order_id": "12345",
  "error": "payment_timeout",
  "duration_ms": 5000
}
```

## Best Practices
- Use consistent label names across services
- Include trace_id for correlation
- Filter as much as possible (reduce data scanned)
- Use metrics extraction for common patterns
- Set retention policy to balance cost/retention

## Anti-Patterns
❌ DEBUG logs in production (costs money)
✅ INFO+ only in prod, DEBUG in dev

❌ No trace_id for debugging
✅ Include trace_id in every log

❌ Unbounded log retention
✅ Set retention: 30 days default, 90 for errors
