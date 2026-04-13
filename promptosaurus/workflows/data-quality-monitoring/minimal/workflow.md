---
name: data-quality-monitoring
description: "Monitor and ensure data quality throughout ML pipeline"
agent: "mlai"
category: "ml"
related_workflows:
  - feature-engineering-guide
  - ml-monitoring-observability
  - model-retraining-strategy
---

# Data Quality Monitoring

**Problem:** Detect and prevent data quality issues that can degrade model performance.

## Quick Steps

1. **Define Metrics:** Completeness, validity, consistency, accuracy
2. **Set Baselines:** Establish expected ranges and distributions
3. **Implement Checks:** Schema validation, statistical tests
4. **Detect Drift:** Monitor distribution shifts over time
5. **Create Alerts:** Configure thresholds and notifications
6. **Build Dashboard:** Visualize quality metrics
7. **Document Issues:** Track and resolve quality problems

## Key Tools/Frameworks

- **Great Expectations:** Data validation framework
- **Evidently:** Data and model monitoring
- **Deequ:** Data quality verification
- **WhyLabs:** Data observability platform

## Common Pitfalls

- No automated quality checks
- Ignoring gradual drift
- Missing data lineage tracking

## Example

```python
import great_expectations as ge

df = ge.read_csv('data.csv')
df.expect_column_values_to_not_be_null('id')
df.expect_column_values_to_be_between('age', 0, 120)
```