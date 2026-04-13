---
name: grafana-dashboard-design
type: skill
category: technical-skill
minimal: true
---
# Grafana Dashboard Design (Minimal)

## Dashboard Layout

**Top Section:** Overview
- Service health: Green/Red status
- Key metrics at a glance (requests/sec, latency, error rate)

**Middle Section:** Details
- Time-series graphs
- Heatmaps for distribution
- Tables for lists

**Bottom Section:** Debugging
- Logs (if connected)
- Traces (if connected)
- Raw data tables

## Visualization Types

| Type | Use For | Example |
|------|---------|---------|
| Graph | Trends | CPU over time |
| Gauge | Current value | Memory % |
| Stat | Single number | 1,234 req/sec |
| Heatmap | Distribution | Latency percentiles |
| Table | Lists | Top errors |
| Logs | Debugging | Error messages |

## Key Metrics

```
RED Method for APIs:
- Rate: Requests per second
- Errors: Error rate %
- Duration: Latency p95

USE Method for Resources:
- Utilization: CPU/Memory %
- Saturation: Queue depth
- Errors: Failed operations
```

## Dashboard Example

```
┌─────────────────────────────────────────┐
│ API Service Health Dashboard            │
├─────────────────────────────────────────┤
│ Status: ✓ HEALTHY │ Uptime: 99.95%     │
├──────────────────┬──────────────────────┤
│ Requests/sec: 1234 │ Latency p95: 145ms  │
│ Error rate: 0.08% │ Availability: 99.95% │
├──────────────┬──────────────┬───────────┤
│ Rate (5m)    │ Error Rate    │ Latency   │
│ [GRAPH]      │ [GRAPH]       │ [GRAPH]   │
├──────────────┴──────────────┴───────────┤
│ Top Errors │ Top Slowest Endpoints     │
│ [TABLE]    │ [TABLE]                   │
└─────────────────────────────────────────┘
```

## Best Practices

- ✅ Use consistent colors (green=good, red=bad)
- ✅ Add thresholds/alerts visually
- ✅ Include units (ms, %, req/sec)
- ❌ Don't clutter with too many panels (max 12)
- ❌ Don't use low-level metrics (use aggregates)
