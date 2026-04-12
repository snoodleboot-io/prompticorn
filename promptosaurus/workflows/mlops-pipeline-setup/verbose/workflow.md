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

# MLOps Pipeline Setup - Comprehensive Guide

## Problem Context

MLOps pipelines automate the machine learning lifecycle from data preparation through model deployment and monitoring. A well-designed MLOps pipeline ensures reproducibility, enables continuous integration/deployment of models, and maintains model quality in production. This workflow guides you through setting up a complete MLOps infrastructure that handles versioning, testing, deployment, and monitoring.

## Prerequisites

- Git repository for code versioning
- Cloud platform account (AWS/GCP/Azure) or on-premise infrastructure
- Container registry access
- Basic understanding of CI/CD concepts
- Python environment with ML libraries

## Step-by-Step Implementation

### Step 1: Repository Structure and Version Control

#### 1.1 Project Structure
```bash
ml-project/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── train.yml
│       └── deploy.yml
├── data/
│   ├── raw/
│   ├── processed/
│   └── .dvc/
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── load_data.py
│   │   └── preprocess.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py
│   │   └── evaluate.py
│   ├── serving/
│   │   ├── __init__.py
│   │   └── api.py
│   └── monitoring/
│       ├── __init__.py
│       └── drift_detector.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── model/
├── configs/
│   ├── training_config.yaml
│   ├── serving_config.yaml
│   └── monitoring_config.yaml
├── notebooks/
│   └── exploratory/
├── docker/
│   ├── training.Dockerfile
│   └── serving.Dockerfile
├── kubernetes/
│   ├── training-job.yaml
│   └── serving-deployment.yaml
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .dvc
├── .gitignore
├── dvc.yaml
├── params.yaml
└── README.md
```

#### 1.2 Initialize Version Control
```bash
# Initialize Git
git init

# Initialize DVC for data versioning
pip install dvc[s3]  # or dvc[gdrive], dvc[azure]
dvc init

# Configure DVC remote storage
dvc remote add -d storage s3://my-bucket/dvc-storage
dvc remote modify storage access_key_id YOUR_KEY
dvc remote modify storage secret_access_key YOUR_SECRET

# Track data with DVC
dvc add data/raw/training_data.csv
git add data/raw/training_data.csv.dvc .gitignore
git commit -m "Add training data"
```

### Step 2: CI/CD Pipeline Configuration

#### 2.1 GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Cache dependencies
      uses: actions/cache@v2
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('requirements/*.txt') }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements/dev.txt
    
    - name: Run linting
      run: |
        flake8 src/
        black --check src/
        mypy src/
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
      with:
        file: ./coverage.xml

  validate-model:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Pull data with DVC
      run: |
        pip install dvc[s3]
        dvc pull
    
    - name: Validate model performance
      run: |
        python src/models/evaluate.py --threshold 0.85
```

#### 2.2 Training Pipeline
```yaml
# .github/workflows/train.yml
name: Model Training Pipeline

on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM
  workflow_dispatch:  # Manual trigger

jobs:
  train:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Pull latest data
      run: |
        pip install dvc[s3]
        dvc pull
    
    - name: Train model
      run: |
        python src/models/train.py \
          --config configs/training_config.yaml \
          --experiment-name weekly-training
    
    - name: Evaluate model
      run: |
        python src/models/evaluate.py \
          --model-path models/latest \
          --test-data data/processed/test.csv
    
    - name: Register model if improved
      run: |
        python scripts/register_model.py \
          --model-path models/latest \
          --registry mlflow \
          --stage staging
```

### Step 3: Experiment Tracking Setup

#### 3.1 MLflow Configuration
```python
# src/models/train.py
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import yaml
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

def setup_mlflow():
    """Configure MLflow tracking."""
    mlflow.set_tracking_uri("http://mlflow-server:5000")
    mlflow.set_experiment("model-training")
    
    # Enable autologging
    mlflow.sklearn.autolog()
    
    return MlflowClient()

def train_model(config_path: str):
    """Train model with experiment tracking."""
    
    # Load configuration
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Setup MLflow
    client = setup_mlflow()
    
    with mlflow.start_run() as run:
        # Log parameters
        mlflow.log_params(config['model_params'])
        
        # Load and preprocess data
        X_train, y_train = load_training_data()
        
        # Train model
        model = RandomForestClassifier(**config['model_params'])
        model.fit(X_train, y_train)
        
        # Evaluate model
        X_val, y_val = load_validation_data()
        metrics = evaluate_model(model, X_val, y_val)
        
        # Log metrics
        mlflow.log_metrics(metrics)
        
        # Log model
        mlflow.sklearn.log_model(
            model, 
            "model",
            registered_model_name="production-model"
        )
        
        # Log artifacts
        mlflow.log_artifact("configs/training_config.yaml")
        
        return run.info.run_id
```

### Step 4: Automated Testing Framework

#### 4.1 Model Testing
```python
# tests/model/test_model_quality.py
import pytest
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score
import mlflow

class TestModelQuality:
    
    @pytest.fixture
    def trained_model(self):
        """Load the latest trained model."""
        client = mlflow.tracking.MlflowClient()
        model_version = client.get_latest_versions(
            "production-model", 
            stages=["Staging"]
        )[0]
        model = mlflow.sklearn.load_model(
            f"models:/{model_version.name}/{model_version.version}"
        )
        return model
    
    def test_model_accuracy(self, trained_model, test_data):
        """Test model accuracy meets threshold."""
        X_test, y_test = test_data
        predictions = trained_model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        assert accuracy > 0.85, f"Model accuracy {accuracy} below threshold"
    
    def test_model_inference_time(self, trained_model, test_data):
        """Test model inference speed."""
        X_test, _ = test_data
        import time
        
        start = time.time()
        _ = trained_model.predict(X_test[:100])
        inference_time = (time.time() - start) / 100
        
        assert inference_time < 0.01, f"Inference too slow: {inference_time}s"
    
    def test_model_robustness(self, trained_model):
        """Test model handles edge cases."""
        # Test with missing values
        X_missing = np.array([[np.nan, 1.0, 2.0]])
        try:
            _ = trained_model.predict(X_missing)
        except Exception as e:
            pytest.fail(f"Model failed on missing values: {e}")
        
        # Test with extreme values
        X_extreme = np.array([[1e10, -1e10, 0]])
        try:
            _ = trained_model.predict(X_extreme)
        except Exception as e:
            pytest.fail(f"Model failed on extreme values: {e}")
```

### Step 5: Model Registry and Promotion

#### 5.1 Model Registry Management
```python
# scripts/model_promotion.py
import mlflow
from mlflow.tracking import MlflowClient
import json

def promote_model(model_name: str, from_stage: str, to_stage: str):
    """
    Promote model from one stage to another after validation.
    """
    client = MlflowClient()
    
    # Get current model version in source stage
    versions = client.get_latest_versions(
        model_name, 
        stages=[from_stage]
    )
    
    if not versions:
        raise ValueError(f"No model in {from_stage} stage")
    
    version = versions[0]
    
    # Run validation checks
    validation_results = validate_model_for_production(version)
    
    if validation_results['passed']:
        # Transition model to new stage
        client.transition_model_version_stage(
            name=model_name,
            version=version.version,
            stage=to_stage,
            archive_existing_versions=True
        )
        
        # Log promotion
        client.set_model_version_tag(
            model_name,
            version.version,
            "promotion_date",
            datetime.now().isoformat()
        )
        
        print(f"Model {model_name} v{version.version} promoted to {to_stage}")
    else:
        print(f"Model failed validation: {validation_results['errors']}")
        raise ValueError("Model validation failed")

def validate_model_for_production(model_version):
    """Run comprehensive validation before production."""
    
    checks = {
        'performance': check_model_performance(model_version),
        'data_compatibility': check_data_compatibility(model_version),
        'api_compatibility': check_api_compatibility(model_version),
        'resource_usage': check_resource_usage(model_version)
    }
    
    passed = all(checks.values())
    errors = [k for k, v in checks.items() if not v]
    
    return {'passed': passed, 'errors': errors, 'checks': checks}
```

### Step 6: Deployment Automation

#### 6.1 Kubernetes Deployment
```yaml
# kubernetes/model-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-{{ .Values.environment }}
  labels:
    app: ml-model
    environment: {{ .Values.environment }}
spec:
  replicas: {{ .Values.replicas }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: ml-model
      environment: {{ .Values.environment }}
  template:
    metadata:
      labels:
        app: ml-model
        environment: {{ .Values.environment }}
        version: {{ .Values.modelVersion }}
    spec:
      containers:
      - name: model-server
        image: {{ .Values.image.repository }}:{{ .Values.modelVersion }}
        ports:
        - containerPort: 8080
        env:
        - name: MODEL_NAME
          value: {{ .Values.modelName }}
        - name: MODEL_VERSION
          value: {{ .Values.modelVersion }}
        - name: MLFLOW_TRACKING_URI
          value: {{ .Values.mlflow.trackingUri }}
        resources:
          requests:
            memory: {{ .Values.resources.requests.memory }}
            cpu: {{ .Values.resources.requests.cpu }}
          limits:
            memory: {{ .Values.resources.limits.memory }}
            cpu: {{ .Values.resources.limits.cpu }}
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 5
```

### Step 7: Monitoring and Alerting

#### 7.1 Drift Detection
```python
# src/monitoring/drift_detector.py
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any
import mlflow

class DriftDetector:
    def __init__(self, reference_data: pd.DataFrame, threshold: float = 0.05):
        self.reference_data = reference_data
        self.threshold = threshold
        self.feature_stats = self._calculate_reference_stats()
    
    def _calculate_reference_stats(self) -> Dict[str, Any]:
        """Calculate statistics for reference data."""
        stats_dict = {}
        for col in self.reference_data.columns:
            stats_dict[col] = {
                'mean': self.reference_data[col].mean(),
                'std': self.reference_data[col].std(),
                'min': self.reference_data[col].min(),
                'max': self.reference_data[col].max()
            }
        return stats_dict
    
    def detect_drift(self, current_data: pd.DataFrame) -> Dict[str, Any]:
        """Detect data drift using statistical tests."""
        drift_results = {}
        
        for col in current_data.columns:
            if col in self.reference_data.columns:
                # Kolmogorov-Smirnov test
                statistic, p_value = stats.ks_2samp(
                    self.reference_data[col],
                    current_data[col]
                )
                
                drift_detected = p_value < self.threshold
                
                drift_results[col] = {
                    'drift_detected': drift_detected,
                    'p_value': p_value,
                    'statistic': statistic,
                    'current_mean': current_data[col].mean(),
                    'reference_mean': self.feature_stats[col]['mean']
                }
        
        # Log drift to MLflow
        with mlflow.start_run():
            mlflow.log_metrics({
                f"drift_{col}": result['p_value']
                for col, result in drift_results.items()
            })
            
            drift_count = sum(
                1 for r in drift_results.values() 
                if r['drift_detected']
            )
            mlflow.log_metric("total_drift_features", drift_count)
        
        return drift_results
```

## Best Practices

1. **Automate Everything:** From training to deployment
2. **Version Control:** Track code, data, and models
3. **Test Rigorously:** Unit, integration, and model quality tests
4. **Monitor Continuously:** Track drift, performance, and errors
5. **Document Thoroughly:** Configuration, processes, and decisions
6. **Implement Rollback:** Quick reversion to previous versions

## Anti-Patterns to Avoid

1. **Manual Deployments:** Always automate deployment process
2. **Unversioned Data:** Track all data changes with DVC
3. **Missing Tests:** Never deploy without comprehensive tests
4. **No Monitoring:** Always monitor models in production
5. **Tight Coupling:** Keep components modular and replaceable

## Integration Points

- **Source Control:** GitHub/GitLab for code versioning
- **Experiment Tracking:** MLflow/Weights & Biases
- **Container Registry:** Docker Hub/ECR/GCR
- **Orchestration:** Kubernetes/Kubeflow
- **Monitoring:** Prometheus/Grafana/DataDog

## Troubleshooting

### Issue: Pipeline fails intermittently
**Solution:** Add retry logic, check for resource constraints

### Issue: Model performance degrades in production
**Solution:** Implement drift detection, schedule regular retraining

### Issue: Slow deployment process
**Solution:** Optimize Docker images, implement caching

## Related Workflows

- [Experiment Tracking Setup](../experiment-tracking-setup) for detailed tracking configuration
- [Model Retraining Strategy](../model-retraining-strategy) for automated retraining
- [Production ML Deployment](../production-ml-deployment) for deployment best practices