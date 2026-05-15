# Prometheus Query Patterns (Minimal)

## Core Queries

### Request Rate (per second)
```promql
rate(http_requests_total[5m])
```
- rate(): Extracts per-second value
- [5m]: 5-minute window

### Error Rate
```promql
rate(http_requests_total{status=~"5.."}[5m]) / 
rate(http_requests_total[5m])
```

### Latency (P95)
```promql
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)
```

### Availability
```promql
sum(rate(http_requests_total{status="200"}[1h])) /
sum(rate(http_requests_total[1h]))
```

## Common Functions

| Function | Purpose | Example |
|----------|---------|---------|
| rate() | Per-second rate | rate(counter[5m]) |
| increase() | Total increase | increase(counter[1h]) |
| histogram_quantile() | Percentile | histogram_quantile(0.99, histogram) |
| sum() | Add series | sum(metric) |
| avg() | Average series | avg(metric) |

## Alerts

```promql
# Error rate alert
rate(errors_total[5m]) > 0.01  # >1% error rate

# Latency alert
histogram_quantile(0.95, latency) > 0.5  # >500ms
```
