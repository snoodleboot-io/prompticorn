---
name: "Hyperparameter Tuning"
description: "Optimize model performance through systematic hyperparameter search"
agent: "mlai"
category: "ml"
related_workflows:
  - model-evaluation-workflow
  - experiment-tracking-setup
  - model-retraining-strategy
---

# Hyperparameter Tuning

**Problem:** Find optimal hyperparameters to maximize model performance.

## Quick Steps

1. **Define Search Space:** Identify parameters and ranges
2. **Choose Strategy:** Grid, random, or Bayesian optimization
3. **Set Budget:** Time/resource constraints
4. **Configure CV:** Cross-validation strategy
5. **Run Search:** Execute optimization
6. **Analyze Results:** Compare parameter combinations
7. **Validate Best:** Test on holdout set

## Key Tools/Frameworks

- **Optuna:** Bayesian optimization framework
- **Ray Tune:** Distributed hyperparameter tuning
- **Hyperopt:** Sequential model-based optimization
- **scikit-learn GridSearchCV:** Basic grid/random search

## Common Pitfalls

- Overfitting to validation set
- Insufficient search budget
- Not using early stopping

## Example

```python
import optuna

def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 300),
        'max_depth': trial.suggest_int('max_depth', 3, 10)
    }
    return cross_val_score(model, X, y, **params).mean()
```