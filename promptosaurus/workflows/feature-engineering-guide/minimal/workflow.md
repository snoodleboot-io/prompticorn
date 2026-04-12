---
name: "Feature Engineering Guide"
description: "Transform raw data into meaningful features for ML models"
agent: "mlai"
category: "ml"
related_workflows:
  - data-quality-monitoring
  - model-evaluation-workflow
  - experiment-tracking-setup
---

# Feature Engineering Guide

**Problem:** Transform raw data into features that improve model performance.

## Quick Steps

1. **Data Analysis:** Understand distributions and relationships
2. **Handle Missing Values:** Imputation or removal strategies
3. **Encode Categories:** One-hot, label, or target encoding
4. **Scale Features:** Normalization or standardization
5. **Create Features:** Polynomial, interaction, domain-specific
6. **Select Features:** Remove redundant/irrelevant features
7. **Validate Pipeline:** Test on holdout data

## Key Tools/Frameworks

- **pandas/numpy:** Data manipulation
- **scikit-learn:** Preprocessing transformers
- **Featuretools:** Automated feature engineering
- **category_encoders:** Advanced encoding methods

## Common Pitfalls

- Data leakage from test set
- Over-engineering features
- Not handling outliers properly

## Example

```python
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

pipeline = Pipeline([
    ('imputer', SimpleImputer()),
    ('scaler', StandardScaler())
])
```