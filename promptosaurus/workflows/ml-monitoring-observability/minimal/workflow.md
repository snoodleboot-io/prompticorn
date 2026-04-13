---
name: ml-monitoring-observability
description: "Monitor ML models and pipelines in production"
agent: "mlai"
category: "ml"
related_workflows:
  - data-quality-monitoring
  - model-serving-workflow
  - model-retraining-strategy
---

# ML Monitoring & Observability

**Problem:** Monitor model performance, data quality, and system health in production.

## Quick Steps

1. **Define Metrics:** Performance, drift, business KPIs
2. **Setup Monitoring:** Configure collection and storage
3. **Create Dashboards:** Visualize key metrics
4. **Configure Alerts:** Set thresholds and notifications
5. **Log Predictions:** Track inputs and outputs
6. **Monitor Resources:** CPU, memory, latency
7. **Incident Response:** Define escalation procedures

## Key Tools/Frameworks

- **Prometheus/Grafana:** Metrics and dashboards
- **Evidently AI:** ML monitoring platform
- **Arize AI:** Model observability
- **WhyLabs:** AI observability platform

## Common Pitfalls

- Monitoring only accuracy
- No baseline for comparison
- Alert fatigue from poor thresholds

## Example

```python
from prometheus_client import Counter, Histogram

prediction_counter = Counter('model_predictions_total', 'Total predictions')
latency_histogram = Histogram('model_latency_seconds', 'Prediction latency')
```