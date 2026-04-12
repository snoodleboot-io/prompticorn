---
name: "MLOps Pipeline Setup"
description: "Establish end-to-end MLOps pipeline for continuous model delivery"
agent: "mlai"
category: "ml"
related_workflows:
  - experiment-tracking-setup
  - model-retraining-strategy
  - production-ml-deployment
---

# MLOps Pipeline Setup

**Problem:** Create automated pipeline for continuous model training, validation, and deployment.

## Quick Steps

1. **Version Control:** Setup Git for code and DVC for data
2. **CI/CD Pipeline:** Configure GitHub Actions/GitLab CI
3. **Experiment Tracking:** Integrate MLflow/Weights & Biases
4. **Automated Testing:** Unit tests for code, validation for models
5. **Model Registry:** Central repository for model artifacts
6. **Deployment Pipeline:** Automated deployment to staging/prod
7. **Monitoring Setup:** Configure drift detection and alerts

## Key Tools/Frameworks

- **Kubeflow/MLflow:** Orchestration platforms
- **DVC/Git-LFS:** Data version control
- **Airflow/Prefect:** Workflow orchestration
- **GitHub Actions/Jenkins:** CI/CD automation

## Common Pitfalls

- Not versioning training data
- Manual deployment processes
- Missing rollback procedures

## Example

```yaml
# .github/workflows/ml-pipeline.yml
on: [push]
jobs:
  train:
    steps:
      - run: python train.py
      - run: python evaluate.py
      - run: mlflow models serve
```