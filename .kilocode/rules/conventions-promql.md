# Core Conventions PromQL

Language: PromQL (Prometheus Query Language)
Database: Prometheus
Style: Clear variable names, comments for complex queries

## Query Types

### Instant Queries
Return single value at timestamp
```promql
# Current value
up{job="api"}
```

### Range Queries
Return values over time period
```promql
# Last 5 minutes
up{job="api"}[5m]
```

### Aggregations
```promql
# Sum across services
sum(rate(http_requests_total[5m])) by (service)
```

## Common Patterns

### RED Method
```promql
# Rate
rate(http_requests_total[5m])

# Errors
rate(http_requests_total{status=~"5.."}[5m])

# Duration
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### USE Method
```promql
# Utilization
container_memory_usage_bytes / container_spec_memory_limit_bytes

# Saturation
rate(disk_read_ops_total[5m])

# Errors
rate(disk_errors_total[5m])
```

## Best Practices
- Always specify time window [5m], [1h], [1d]
- Use label matching for filtering
- Avoid high-cardinality labels
- Test on staging before production alerts
- Document complex queries with comments

## Anti-Patterns
❌ No time window [5m]
✅ Always specify: rate(metric[5m])

❌ Using raw counter values
✅ Always use rate() for counters

❌ Over-aggregating
✅ Keep dimensions (by job, region)
