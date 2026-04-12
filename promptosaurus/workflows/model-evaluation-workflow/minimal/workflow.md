---
name: "Model Evaluation Workflow"
description: "Evaluate model performance with comprehensive metrics"
agent: "mlai"
category: "ml"
related_workflows:
  - model-serving-workflow
  - experiment-tracking-setup
  - model-interpretability-guide
---

# Model Evaluation Workflow

**Problem:** Comprehensively evaluate ML model performance across multiple metrics.

## Quick Steps

1. **Load Test Data:** Prepare holdout or validation dataset
2. **Generate Predictions:** Run inference on test set
3. **Calculate Metrics:** Compute accuracy, precision, recall, F1
4. **Analyze Errors:** Confusion matrix and error analysis
5. **Cross-Validation:** K-fold validation for robustness
6. **Compare Baselines:** Benchmark against baseline models
7. **Report Results:** Generate evaluation report

## Key Tools/Frameworks

- **scikit-learn:** Standard metrics library
- **MLflow:** Experiment tracking
- **TensorBoard:** Visualization
- **SHAP/LIME:** Model interpretability

## Common Pitfalls

- Data leakage between train/test sets
- Imbalanced class distribution ignored
- Single metric optimization

## Example

```python
from sklearn.metrics import classification_report
report = classification_report(y_true, y_pred)
```