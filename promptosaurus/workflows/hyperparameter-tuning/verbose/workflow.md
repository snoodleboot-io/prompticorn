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

# Hyperparameter Tuning - Comprehensive Guide

## Problem Context

Hyperparameter tuning is the process of finding the optimal configuration of hyperparameters that maximizes model performance. Unlike model parameters learned during training, hyperparameters control the learning process itself. Effective tuning can significantly improve model performance but requires systematic search strategies and careful evaluation to avoid overfitting.

## Prerequisites

- Trained baseline model
- Clear evaluation metrics
- Computational resources for search
- Cross-validation strategy
- Understanding of hyperparameter impacts

## Step-by-Step Implementation

### Step 1: Define Search Space

#### 1.1 Hyperparameter Configuration
```python
from typing import Dict, List, Any, Union
import numpy as np
from dataclasses import dataclass

@dataclass
class HyperparameterSpace:
    """Define hyperparameter search space."""
    
    name: str
    param_type: str  # continuous, discrete, categorical
    bounds: Union[List, Tuple]
    distribution: str  # uniform, log-uniform, normal
    
class SearchSpaceBuilder:
    def __init__(self, model_type: str):
        self.model_type = model_type
        self.search_space = {}
        
    def build_search_space(self) -> Dict[str, HyperparameterSpace]:
        """Build model-specific search space."""
        
        if self.model_type == 'random_forest':
            return {
                'n_estimators': HyperparameterSpace(
                    name='n_estimators',
                    param_type='discrete',
                    bounds=[50, 500],
                    distribution='uniform'
                ),
                'max_depth': HyperparameterSpace(
                    name='max_depth',
                    param_type='discrete',
                    bounds=[3, 20],
                    distribution='uniform'
                ),
                'min_samples_split': HyperparameterSpace(
                    name='min_samples_split',
                    param_type='discrete',
                    bounds=[2, 20],
                    distribution='uniform'
                ),
                'min_samples_leaf': HyperparameterSpace(
                    name='min_samples_leaf',
                    param_type='discrete',
                    bounds=[1, 10],
                    distribution='uniform'
                ),
                'max_features': HyperparameterSpace(
                    name='max_features',
                    param_type='categorical',
                    bounds=['sqrt', 'log2', None],
                    distribution='categorical'
                )
            }
        
        elif self.model_type == 'neural_network':
            return {
                'learning_rate': HyperparameterSpace(
                    name='learning_rate',
                    param_type='continuous',
                    bounds=[1e-5, 1e-1],
                    distribution='log-uniform'
                ),
                'batch_size': HyperparameterSpace(
                    name='batch_size',
                    param_type='categorical',
                    bounds=[16, 32, 64, 128, 256],
                    distribution='categorical'
                ),
                'num_layers': HyperparameterSpace(
                    name='num_layers',
                    param_type='discrete',
                    bounds=[2, 10],
                    distribution='uniform'
                ),
                'hidden_size': HyperparameterSpace(
                    name='hidden_size',
                    param_type='discrete',
                    bounds=[32, 512],
                    distribution='uniform'
                ),
                'dropout': HyperparameterSpace(
                    name='dropout',
                    param_type='continuous',
                    bounds=[0.0, 0.5],
                    distribution='uniform'
                ),
                'activation': HyperparameterSpace(
                    name='activation',
                    param_type='categorical',
                    bounds=['relu', 'tanh', 'sigmoid'],
                    distribution='categorical'
                )
            }
```

### Step 2: Search Strategy Implementation

#### 2.1 Bayesian Optimization with Optuna
```python
import optuna
from optuna.samplers import TPESampler
from sklearn.model_selection import cross_val_score
import mlflow

class OptunaHyperparameterTuner:
    def __init__(self, model_class, X, y, cv_folds=5, n_trials=100):
        self.model_class = model_class
        self.X = X
        self.y = y
        self.cv_folds = cv_folds
        self.n_trials = n_trials
        self.study = None
        self.best_params = None
        
    def objective(self, trial):
        """Optuna objective function."""
        
        # Sample hyperparameters
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 50, 500),
            'max_depth': trial.suggest_int('max_depth', 3, 20),
            'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
            'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 10),
            'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', None])
        }
        
        # Create model with suggested parameters
        model = self.model_class(**params)
        
        # Perform cross-validation
        scores = cross_val_score(
            model, self.X, self.y,
            cv=self.cv_folds,
            scoring='accuracy',
            n_jobs=-1
        )
        
        # Log to MLflow
        with mlflow.start_run(nested=True):
            mlflow.log_params(params)
            mlflow.log_metric('cv_mean_accuracy', scores.mean())
            mlflow.log_metric('cv_std_accuracy', scores.std())
        
        # Return negative for minimization
        return scores.mean()
    
    def optimize(self):
        """Run hyperparameter optimization."""
        
        # Create study with TPE sampler
        self.study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=42),
            study_name='hyperparameter_optimization'
        )
        
        # Optimize
        self.study.optimize(
            self.objective,
            n_trials=self.n_trials,
            show_progress_bar=True
        )
        
        # Get best parameters
        self.best_params = self.study.best_params
        
        return self.best_params
    
    def get_optimization_history(self):
        """Get optimization history for analysis."""
        
        return {
            'best_value': self.study.best_value,
            'best_params': self.study.best_params,
            'best_trial': self.study.best_trial,
            'n_trials': len(self.study.trials),
            'optimization_history': [
                {
                    'number': trial.number,
                    'value': trial.value,
                    'params': trial.params,
                    'state': trial.state
                }
                for trial in self.study.trials
            ]
        }
```

#### 2.2 Grid Search Implementation
```python
from sklearn.model_selection import GridSearchCV
import itertools

class GridSearchTuner:
    def __init__(self, model, param_grid, cv_folds=5):
        self.model = model
        self.param_grid = param_grid
        self.cv_folds = cv_folds
        self.grid_search = None
        
    def search(self, X, y):
        """Perform grid search."""
        
        # Calculate total combinations
        n_combinations = np.prod([
            len(v) if isinstance(v, list) else 1 
            for v in self.param_grid.values()
        ])
        
        print(f"Testing {n_combinations} parameter combinations")
        
        # Create GridSearchCV
        self.grid_search = GridSearchCV(
            self.model,
            self.param_grid,
            cv=self.cv_folds,
            scoring='accuracy',
            n_jobs=-1,
            verbose=2,
            return_train_score=True
        )
        
        # Fit
        self.grid_search.fit(X, y)
        
        return self.grid_search.best_params_
    
    def get_results_dataframe(self):
        """Convert results to DataFrame for analysis."""
        
        import pandas as pd
        
        results_df = pd.DataFrame(self.grid_search.cv_results_)
        
        # Sort by mean test score
        results_df = results_df.sort_values('mean_test_score', ascending=False)
        
        # Select relevant columns
        columns = ['rank_test_score', 'mean_test_score', 'std_test_score']
        columns += [col for col in results_df.columns if col.startswith('param_')]
        
        return results_df[columns]
```

### Step 3: Advanced Search Strategies

#### 3.1 Population-Based Training
```python
import ray
from ray import tune
from ray.tune.schedulers import PopulationBasedTraining

class PBTTuner:
    def __init__(self, train_function, config_space, num_samples=10):
        self.train_function = train_function
        self.config_space = config_space
        self.num_samples = num_samples
        
    def run_pbt(self):
        """Run population-based training."""
        
        # Define PBT scheduler
        pbt_scheduler = PopulationBasedTraining(
            time_attr='training_iteration',
            metric='accuracy',
            mode='max',
            perturbation_interval=5,
            hyperparam_mutations={
                'learning_rate': lambda: np.random.uniform(1e-5, 1e-1),
                'batch_size': [16, 32, 64, 128],
                'dropout': lambda: np.random.uniform(0.0, 0.5)
            }
        )
        
        # Run tuning
        analysis = tune.run(
            self.train_function,
            config=self.config_space,
            scheduler=pbt_scheduler,
            num_samples=self.num_samples,
            resources_per_trial={'cpu': 2, 'gpu': 0.5},
            stop={'training_iteration': 100},
            checkpoint_freq=10,
            keep_checkpoints_num=5
        )
        
        # Get best config
        best_config = analysis.get_best_config(metric='accuracy', mode='max')
        
        return best_config, analysis
```

### Step 4: Early Stopping and Pruning

#### 4.1 Implement Early Stopping
```python
class EarlyStoppingCallback:
    def __init__(self, patience=10, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_score = None
        self.counter = 0
        self.should_stop = False
        
    def __call__(self, study, trial):
        """Optuna pruning callback."""
        
        current_score = trial.value
        
        if self.best_score is None:
            self.best_score = current_score
        elif current_score > self.best_score + self.min_delta:
            self.best_score = current_score
            self.counter = 0
        else:
            self.counter += 1
            
        if self.counter >= self.patience:
            self.should_stop = True
            study.stop()
            print(f"Early stopping triggered after {trial.number} trials")

class SuccessiveHalvingPruner:
    def __init__(self, min_resource=1, reduction_factor=3, min_early_stopping_rate=0):
        self.min_resource = min_resource
        self.reduction_factor = reduction_factor
        self.min_early_stopping_rate = min_early_stopping_rate
        
    def should_prune(self, trial_scores, current_step):
        """Determine if trial should be pruned."""
        
        # Get all trial scores at current step
        scores_at_step = [s for s in trial_scores if s['step'] == current_step]
        
        if len(scores_at_step) < 2:
            return False
        
        # Sort scores
        sorted_scores = sorted(scores_at_step, key=lambda x: x['value'])
        
        # Calculate percentile for pruning
        n_to_keep = max(
            int(len(sorted_scores) / self.reduction_factor),
            self.min_resource
        )
        
        # Prune if in bottom portion
        threshold = sorted_scores[n_to_keep - 1]['value']
        
        return trial_scores[-1]['value'] < threshold
```

### Step 5: Multi-Objective Optimization

#### 5.1 Pareto-Optimal Solutions
```python
class MultiObjectiveTuner:
    def __init__(self, objectives: List[str]):
        self.objectives = objectives
        self.pareto_front = []
        
    def objective(self, trial):
        """Multi-objective function."""
        
        params = self._sample_params(trial)
        
        # Evaluate multiple objectives
        results = {}
        
        # Accuracy
        accuracy = self._evaluate_accuracy(params)
        results['accuracy'] = accuracy
        
        # Inference time
        inference_time = self._evaluate_inference_time(params)
        results['inference_time'] = inference_time
        
        # Model size
        model_size = self._evaluate_model_size(params)
        results['model_size'] = model_size
        
        # Return tuple for multi-objective optimization
        return accuracy, -inference_time, -model_size
    
    def find_pareto_front(self, solutions):
        """Find Pareto-optimal solutions."""
        
        pareto_front = []
        
        for i, sol1 in enumerate(solutions):
            dominated = False
            
            for j, sol2 in enumerate(solutions):
                if i != j:
                    # Check if sol2 dominates sol1
                    if all(sol2[obj] >= sol1[obj] for obj in self.objectives) and \
                       any(sol2[obj] > sol1[obj] for obj in self.objectives):
                        dominated = True
                        break
            
            if not dominated:
                pareto_front.append(sol1)
        
        self.pareto_front = pareto_front
        return pareto_front
```

### Step 6: Visualization and Analysis

#### 6.1 Hyperparameter Importance Analysis
```python
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

class HyperparameterAnalyzer:
    def __init__(self, study):
        self.study = study
        
    def plot_optimization_history(self):
        """Plot optimization history."""
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 5))
        
        # Plot objective value history
        trials = self.study.trials
        x = [trial.number for trial in trials]
        y = [trial.value for trial in trials]
        
        axes[0].plot(x, y, 'b-', alpha=0.5)
        axes[0].scatter(x, y, c='blue', s=20)
        axes[0].axhline(y=self.study.best_value, color='red', linestyle='--')
        axes[0].set_xlabel('Trial')
        axes[0].set_ylabel('Objective Value')
        axes[0].set_title('Optimization History')
        
        # Plot best value over time
        best_values = []
        current_best = float('-inf')
        
        for trial in trials:
            if trial.value > current_best:
                current_best = trial.value
            best_values.append(current_best)
        
        axes[1].plot(x, best_values, 'g-', linewidth=2)
        axes[1].set_xlabel('Trial')
        axes[1].set_ylabel('Best Value')
        axes[1].set_title('Best Value Over Time')
        
        plt.tight_layout()
        return fig
    
    def calculate_param_importance(self):
        """Calculate hyperparameter importance."""
        
        # Extract trials data
        trials_df = self.study.trials_dataframe()
        
        # Prepare features and target
        param_cols = [col for col in trials_df.columns if col.startswith('params_')]
        X = trials_df[param_cols].fillna(0)
        y = trials_df['value']
        
        # Train random forest to estimate importance
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        # Get feature importance
        importance = pd.DataFrame({
            'parameter': [col.replace('params_', '') for col in param_cols],
            'importance': rf.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance
    
    def plot_param_relationships(self):
        """Plot parameter relationships."""
        
        optuna.visualization.plot_parallel_coordinate(self.study)
        optuna.visualization.plot_slice(self.study)
        optuna.visualization.plot_param_importances(self.study)
```

### Step 7: Deployment of Best Model

#### 7.1 Final Model Training and Validation
```python
class FinalModelBuilder:
    def __init__(self, best_params, model_class):
        self.best_params = best_params
        self.model_class = model_class
        self.final_model = None
        
    def train_final_model(self, X_train, y_train, X_val, y_val):
        """Train final model with best parameters."""
        
        # Create model with best parameters
        self.final_model = self.model_class(**self.best_params)
        
        # Train on full training set
        self.final_model.fit(X_train, y_train)
        
        # Validate
        train_score = self.final_model.score(X_train, y_train)
        val_score = self.final_model.score(X_val, y_val)
        
        print(f"Final Model Performance:")
        print(f"Training Score: {train_score:.4f}")
        print(f"Validation Score: {val_score:.4f}")
        
        # Check for overfitting
        if train_score - val_score > 0.05:
            print("Warning: Possible overfitting detected")
        
        return self.final_model
    
    def save_model_and_config(self, path):
        """Save model and hyperparameter configuration."""
        
        import joblib
        import json
        
        # Save model
        joblib.dump(self.final_model, f'{path}/model.pkl')
        
        # Save hyperparameters
        with open(f'{path}/hyperparameters.json', 'w') as f:
            json.dump(self.best_params, f, indent=2)
        
        # Save metadata
        metadata = {
            'model_class': str(self.model_class),
            'hyperparameters': self.best_params,
            'timestamp': datetime.datetime.now().isoformat(),
            'framework': 'scikit-learn'
        }
        
        with open(f'{path}/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
```

## Best Practices

1. **Start Simple:** Begin with random search or grid search
2. **Use Cross-Validation:** Avoid overfitting to validation set
3. **Log Everything:** Track all experiments for reproducibility
4. **Set Budgets:** Define time/resource limits upfront
5. **Validate Thoroughly:** Test best params on holdout set
6. **Consider Trade-offs:** Balance performance with training time

## Anti-Patterns to Avoid

1. **Overfitting to Validation:** Too many iterations on same data
2. **Ignoring Computational Cost:** Not considering training time
3. **Too Narrow Search Space:** Missing optimal regions
4. **No Early Stopping:** Wasting resources on poor trials
5. **Single Metric Focus:** Ignoring other important metrics

## Integration Points

- **Experiment Tracking:** Log all trials to MLflow/W&B
- **Model Registry:** Store best models and configs
- **CI/CD Pipeline:** Automate tuning in pipelines
- **Cloud Resources:** Use cloud for parallel search

## Troubleshooting

### Issue: Search takes too long
**Solution:** Use early stopping, reduce search space, increase parallelism

### Issue: No improvement found
**Solution:** Expand search space, try different search strategy

### Issue: Overfitting to validation set
**Solution:** Use nested cross-validation, larger validation set

## Related Workflows

- [Model Evaluation Workflow](../model-evaluation-workflow) for performance validation
- [Experiment Tracking Setup](../experiment-tracking-setup) for logging experiments
- [Model Retraining Strategy](../model-retraining-strategy) for periodic retuning