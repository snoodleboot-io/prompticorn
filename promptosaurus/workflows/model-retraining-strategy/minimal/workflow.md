---
name: model-retraining-strategy
description: "Define when and how to retrain ML models in production"
agent: "mlai"
category: "ml"
related_workflows:
  - data-quality-monitoring
  - ml-monitoring-observability
  - mlops-pipeline-setup
---

# Model Retraining Strategy

**Problem:** Maintain model performance over time through strategic retraining.

## Quick Steps

1. **Define Triggers:** Performance degradation, drift, schedule
2. **Data Strategy:** How much historical data to use
3. **Validation Approach:** Ensure new model is better
4. **Rollback Plan:** Quick reversion if issues arise
5. **Gradual Rollout:** Canary or shadow deployment
6. **Performance Comparison:** A/B testing framework
7. **Documentation:** Track retraining decisions

## Key Tools/Frameworks

- **Airflow:** Schedule retraining workflows
- **MLflow:** Track experiments and models
- **Evidently:** Monitor drift and trigger retraining
- **Kubeflow Pipelines:** Orchestrate retraining

## Common Pitfalls

- Retraining too frequently
- Not validating retrained models
- Losing historical performance

## Example

```yaml
retraining:
  triggers:
    - type: performance
      threshold: 0.85
    - type: drift
      p_value: 0.05
    - type: schedule
      frequency: monthly
```