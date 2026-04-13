---
name: slo-sli-definition
type: skill
category: technical-skill
minimal: true
---
# SLO/SLI Definition (Minimal)

## Key Terms

**SLO (Service Level Objective):** Target (99.9% availability)  
**SLI (Service Level Indicator):** Measurement (actual 99.95%)  
**Error Budget:** (1 - SLO) × time (0.1% × month = 43 minutes)

## Defining SLOs

```
API Service SLO:
- Availability: 99.9% (43 min/month downtime)
- Latency: p95 < 200ms
- Error rate: < 0.1%
```

## Measuring SLIs

```promql
# Availability SLI
sum(rate(http_requests_total{status="200"}[30d])) /
sum(rate(http_requests_total[30d]))

# Latency SLI
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[30d])
)
```

## Error Budget Tracking

```
Monthly budget: 43 minutes downtime
Consumed so far: 8 minutes (19%)
Remaining: 35 minutes (81%)
Safe to deploy: YES
```

## Common SLOs by Industry

| Type | SLO | Budget/Month |
|------|-----|--------------|
| Internal tool | 99.0% | 7.2 hours |
| SaaS | 99.9% | 43 minutes |
| Financial | 99.99% | 4 minutes |
| Infrastructure | 99.999% | 26 seconds |
