---
name: production-ml-deployment
description: "Deploy ML models to production with best practices"
agent: "mlai"
category: "ml"
related_workflows:
  - model-serving-workflow
  - ml-monitoring-observability
  - mlops-pipeline-setup
---

# Production ML Deployment

**Problem:** Successfully deploy ML models to production environments.

## Quick Steps

1. **Pre-deployment Checks:** Validate model and dependencies
2. **Deployment Strategy:** Blue-green, canary, or shadow
3. **Infrastructure Setup:** Provision resources
4. **Deploy Model:** Push to production environment
5. **Smoke Tests:** Verify basic functionality
6. **Monitor Rollout:** Track metrics during deployment
7. **Post-deployment Validation:** Ensure expected performance

## Key Tools/Frameworks

- **Kubernetes:** Container orchestration
- **Seldon Core:** ML deployment platform
- **AWS SageMaker:** Managed ML service
- **TFX:** TensorFlow Extended for production

## Common Pitfalls

- No rollback strategy
- Missing monitoring setup
- Inadequate load testing

## Example

```yaml
deployment:
  strategy: canary
  stages:
    - traffic: 5%
      duration: 1h
    - traffic: 25%
      duration: 2h
    - traffic: 100%
```