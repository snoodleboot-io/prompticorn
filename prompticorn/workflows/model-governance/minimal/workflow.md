---
name: "model-governance"
description: "Establish governance processes for ML model lifecycle"
agent: "mlai"
category: "ml"
related_workflows:
  - model-evaluation-workflow
  - production-ml-deployment
  - mlops-pipeline-setup
---

# Model Governance Workflow

**Problem:** Ensure models meet regulatory, ethical, and business standards throughout lifecycle.

## Quick Steps

1. **Define Standards:** Establish model requirements and criteria
2. **Documentation Requirements:** Model cards, risk assessments
3. **Approval Process:** Review gates and sign-offs
4. **Audit Trail:** Track all model changes and decisions
5. **Access Control:** Implement role-based permissions
6. **Compliance Checks:** Regulatory and ethical validation
7. **Retirement Process:** Procedures for model deprecation

## Key Tools/Frameworks

- **Model Cards:** Google's model documentation standard
- **MLflow Model Registry:** Centralized model management
- **DataRobot MLOps:** Governance platform
- **Fiddler AI:** Model monitoring and governance

## Common Pitfalls

- No clear ownership structure
- Missing documentation standards
- Inadequate audit logging

## Example

```python
model_governance = {
    'owner': 'data-science-team',
    'approvers': ['ml-lead', 'compliance'],
    'risk_level': 'high',
    'review_frequency': 'quarterly'
}
```