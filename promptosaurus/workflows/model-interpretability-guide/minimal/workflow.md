---
name: "model-interpretability-guide"
description: "Make ML model decisions explainable and interpretable"
agent: "mlai"
category: "ml"
related_workflows:
  - model-evaluation-workflow
  - model-governance-workflow
  - production-ml-deployment
---

# Model Interpretability Guide

**Problem:** Understand and explain how ML models make predictions.

## Quick Steps

1. **Choose Methods:** SHAP, LIME, feature importance
2. **Global Interpretation:** Overall model behavior
3. **Local Interpretation:** Individual predictions
4. **Feature Analysis:** Impact of each feature
5. **Visualize Results:** Create interpretability dashboards
6. **Validate Insights:** Cross-check with domain knowledge
7. **Document Findings:** Create explanation reports

## Key Tools/Frameworks

- **SHAP:** SHapley Additive exPlanations
- **LIME:** Local Interpretable Model-agnostic Explanations
- **ELI5:** Debug machine learning classifiers
- **InterpretML:** Microsoft's interpretability toolkit

## Common Pitfalls

- Over-interpreting importance scores
- Ignoring interaction effects
- Not validating explanations

## Example

```python
import shap

explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)
shap.summary_plot(shap_values, X)
```