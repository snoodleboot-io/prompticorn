---
name: "model-evaluation"
description: "Evaluate model performance with comprehensive metrics"
agent: "mlai"
category: "ml"
related_workflows:
  - model-serving-workflow
  - experiment-tracking-setup
  - model-interpretability-guide
---

# Model Evaluation Workflow - Comprehensive Guide

## Problem Context

Model evaluation is critical for understanding how well your ML model performs on unseen data. A comprehensive evaluation strategy goes beyond simple accuracy metrics to provide insights into model behavior, failure modes, and deployment readiness. This workflow establishes a systematic approach to evaluate models across multiple dimensions including performance, fairness, robustness, and interpretability.

## Prerequisites

- Trained model ready for evaluation
- Holdout test dataset (never seen during training)
- Understanding of relevant business metrics
- Python environment with evaluation libraries
- Access to baseline model for comparison

## Step-by-Step Implementation

### Step 1: Data Preparation

#### 1.1 Load and Validate Test Data
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Load test data
X_test = pd.read_csv('test_features.csv')
y_test = pd.read_csv('test_labels.csv')

# Validate data quality
assert X_test.isnull().sum().sum() == 0, "Test data contains nulls"
assert len(X_test) == len(y_test), "Feature/label mismatch"
```

#### 1.2 Check Data Distribution
```python
# Compare train/test distributions
from scipy import stats
for col in X_test.columns:
    statistic, p_value = stats.ks_2samp(X_train[col], X_test[col])
    if p_value < 0.05:
        print(f"Warning: {col} distribution shift detected")
```

### Step 2: Generate Predictions

#### 2.1 Load Model and Run Inference
```python
import joblib
import time

# Load model
model = joblib.load('model.pkl')

# Generate predictions with timing
start_time = time.time()
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)
inference_time = time.time() - start_time

print(f"Average inference time: {inference_time/len(X_test):.4f}s per sample")
```

### Step 3: Calculate Comprehensive Metrics

#### 3.1 Classification Metrics
```python
from sklearn.metrics import (
    accuracy_score, precision_recall_fscore_support,
    confusion_matrix, roc_auc_score, log_loss,
    matthews_corrcoef, cohen_kappa_score
)

# Basic metrics
accuracy = accuracy_score(y_test, y_pred)
precision, recall, f1, support = precision_recall_fscore_support(
    y_test, y_pred, average='weighted'
)

# Advanced metrics
mcc = matthews_corrcoef(y_test, y_pred)
kappa = cohen_kappa_score(y_test, y_pred)

# Probabilistic metrics
if y_proba is not None:
    auc_roc = roc_auc_score(y_test, y_proba, multi_class='ovr')
    logloss = log_loss(y_test, y_proba)
```

#### 3.2 Regression Metrics (if applicable)
```python
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error,
    r2_score, mean_absolute_percentage_error
)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)
mape = mean_absolute_percentage_error(y_test, y_pred)
```

### Step 4: Error Analysis

#### 4.1 Confusion Matrix Analysis
```python
import seaborn as sns
import matplotlib.pyplot as plt

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.savefig('confusion_matrix.png')
```

#### 4.2 Error Case Investigation
```python
# Identify misclassified samples
errors_mask = y_test != y_pred
error_indices = np.where(errors_mask)[0]

# Analyze error patterns
error_analysis = pd.DataFrame({
    'true': y_test[errors_mask],
    'predicted': y_pred[errors_mask],
    'confidence': y_proba[errors_mask].max(axis=1) if y_proba is not None else None
})

print("Top error patterns:")
print(error_analysis.groupby(['true', 'predicted']).size().sort_values(ascending=False).head(10))
```

### Step 5: Cross-Validation

```python
from sklearn.model_selection import cross_validate, StratifiedKFold

# Perform k-fold cross-validation
cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

cv_results = cross_validate(
    model, X_test, y_test,
    cv=cv_strategy,
    scoring=['accuracy', 'precision_weighted', 'recall_weighted', 'f1_weighted'],
    return_train_score=True
)

print("Cross-validation results:")
for metric, scores in cv_results.items():
    if 'test_' in metric:
        print(f"{metric}: {scores.mean():.3f} (+/- {scores.std() * 2:.3f})")
```

### Step 6: Fairness and Bias Analysis

```python
# Evaluate model fairness across sensitive attributes
if 'gender' in X_test.columns:
    for gender in X_test['gender'].unique():
        mask = X_test['gender'] == gender
        gender_accuracy = accuracy_score(y_test[mask], y_pred[mask])
        print(f"Accuracy for {gender}: {gender_accuracy:.3f}")
```

### Step 7: Model Comparison

```python
# Compare with baseline model
baseline_model = joblib.load('baseline_model.pkl')
baseline_pred = baseline_model.predict(X_test)

comparison = pd.DataFrame({
    'Metric': ['Accuracy', 'Precision', 'Recall', 'F1'],
    'Current Model': [accuracy, precision, recall, f1],
    'Baseline': [
        accuracy_score(y_test, baseline_pred),
        precision_score(y_test, baseline_pred, average='weighted'),
        recall_score(y_test, baseline_pred, average='weighted'),
        f1_score(y_test, baseline_pred, average='weighted')
    ]
})

comparison['Improvement'] = (
    (comparison['Current Model'] - comparison['Baseline']) / comparison['Baseline'] * 100
)
print(comparison)
```

### Step 8: Generate Evaluation Report

```python
import json
from datetime import datetime

evaluation_report = {
    'timestamp': datetime.now().isoformat(),
    'model_version': 'v1.2.3',
    'dataset': 'test_set_2024',
    'metrics': {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'auc_roc': float(auc_roc) if 'auc_roc' in locals() else None,
        'mcc': float(mcc),
        'cohen_kappa': float(kappa)
    },
    'inference_performance': {
        'avg_time_per_sample': inference_time / len(X_test),
        'total_samples': len(X_test)
    },
    'cross_validation': {
        metric: {'mean': float(scores.mean()), 'std': float(scores.std())}
        for metric, scores in cv_results.items()
        if 'test_' in metric
    }
}

with open('evaluation_report.json', 'w') as f:
    json.dump(evaluation_report, f, indent=2)
```

## Best Practices

1. **Version Everything:** Track model versions, data versions, and evaluation code
2. **Stratified Sampling:** Ensure test set represents population distribution
3. **Multiple Metrics:** Never rely on a single metric for decision making
4. **Statistical Significance:** Use confidence intervals and hypothesis testing
5. **Business Metrics:** Align technical metrics with business KPIs
6. **Reproducibility:** Set random seeds and document environment

## Anti-Patterns to Avoid

1. **Data Leakage:** Never let test data influence training
2. **Cherry-Picking:** Don't select only favorable metrics
3. **Overfitting to Test Set:** Avoid multiple evaluation rounds on same test set
4. **Ignoring Class Imbalance:** Use appropriate metrics for imbalanced data
5. **Missing Confidence Intervals:** Always report uncertainty

## Integration Points

- **Experiment Tracking:** Log results to MLflow or Weights & Biases
- **Model Registry:** Update model metadata with evaluation results
- **CI/CD Pipeline:** Automate evaluation in deployment pipeline
- **Monitoring:** Use evaluation metrics as baseline for production monitoring

## Troubleshooting

### Issue: Metrics don't match production performance
**Solution:** Check for data drift, ensure test set represents production distribution

### Issue: High variance in cross-validation
**Solution:** Increase number of folds, check for data quality issues

### Issue: Model performs worse than baseline
**Solution:** Review feature engineering, check for bugs in preprocessing

## Related Workflows

- [Experiment Tracking Setup](../experiment-tracking-setup) for logging evaluations
- [Model Interpretability Guide](../model-interpretability-guide) for understanding predictions
- [ML Monitoring & Observability](../ml-monitoring-observability) for production tracking