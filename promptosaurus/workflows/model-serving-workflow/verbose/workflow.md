---
name: "Model Serving Workflow"
description: "Deploy and serve ML models in production environments"
agent: "mlai"
category: "ml"
related_workflows:
  - production-ml-deployment
  - ml-monitoring-observability
  - model-evaluation-workflow
---

# Model Serving Workflow - Comprehensive Guide

## Problem Context

Model serving is the process of deploying machine learning models to production environments where they can process real-world data and generate predictions. This involves packaging models, creating APIs, ensuring scalability, and maintaining high availability. A robust serving infrastructure must handle varying loads, provide low latency, and integrate with existing systems while maintaining model performance and reliability.

## Prerequisites

- Trained and validated model
- Understanding of deployment environment (cloud/on-premise)
- Docker and Kubernetes knowledge
- API design principles
- Performance requirements defined

## Step-by-Step Implementation

### Step 1: Model Packaging and Serialization

#### 1.1 Serialize Model
```python
import joblib
import torch
import tensorflow as tf
import mlflow

# For scikit-learn models
joblib.dump(model, 'model.pkl')

# For PyTorch models
torch.save(model.state_dict(), 'model.pth')

# For TensorFlow models
tf.saved_model.save(model, 'saved_model')

# Using MLflow for any framework
mlflow.sklearn.save_model(model, "model_path")
```

#### 1.2 Create Model Artifact Bundle
```python
import json
import shutil
from pathlib import Path

# Create model bundle directory
model_bundle = Path('model_bundle')
model_bundle.mkdir(exist_ok=True)

# Copy model files
shutil.copy('model.pkl', model_bundle / 'model.pkl')
shutil.copy('preprocessing.pkl', model_bundle / 'preprocessing.pkl')

# Save model metadata
metadata = {
    'model_version': '1.2.3',
    'framework': 'scikit-learn',
    'python_version': '3.9',
    'created_at': '2024-01-15T10:00:00Z',
    'input_schema': {
        'features': ['feature1', 'feature2', 'feature3'],
        'types': ['float', 'float', 'int']
    },
    'output_schema': {
        'prediction': 'float',
        'confidence': 'float'
    }
}

with open(model_bundle / 'metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)
```

### Step 2: API Development

#### 2.1 Create FastAPI Service
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import numpy as np
import joblib
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize app
app = FastAPI(title="ML Model Service", version="1.0.0")

# Load model at startup
model = None
preprocessor = None

@app.on_event("startup")
async def load_model():
    global model, preprocessor
    try:
        model = joblib.load('model_bundle/model.pkl')
        preprocessor = joblib.load('model_bundle/preprocessing.pkl')
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

# Input/Output schemas
class PredictionRequest(BaseModel):
    features: List[float] = Field(..., description="Input features")
    request_id: Optional[str] = Field(None, description="Request tracking ID")

class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    model_version: str = "1.2.3"
    request_id: Optional[str]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": model is not None}

# Prediction endpoint
@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        # Preprocess input
        features = np.array(request.features).reshape(1, -1)
        features_processed = preprocessor.transform(features)
        
        # Generate prediction
        prediction = model.predict(features_processed)[0]
        confidence = model.predict_proba(features_processed).max()
        
        logger.info(f"Prediction generated for request {request.request_id}")
        
        return PredictionResponse(
            prediction=float(prediction),
            confidence=float(confidence),
            request_id=request.request_id
        )
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Batch prediction endpoint
@app.post("/predict_batch")
async def predict_batch(requests: List[PredictionRequest]):
    results = []
    for request in requests:
        try:
            result = await predict(request)
            results.append(result)
        except Exception as e:
            results.append({"error": str(e), "request_id": request.request_id})
    return results
```

### Step 3: Containerization

#### 3.1 Create Dockerfile
```dockerfile
# Multi-stage build for smaller image
FROM python:3.9-slim as builder

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Make sure scripts in .local are callable
ENV PATH=/root/.local/bin:$PATH

# Create non-root user
RUN useradd -m -u 1000 mlservice && chown -R mlservice:mlservice /app
USER mlservice

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3.2 Build and Test Container
```bash
# Build image
docker build -t ml-model-service:1.2.3 .

# Run container locally
docker run -p 8000:8000 ml-model-service:1.2.3

# Test endpoint
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"features": [1.0, 2.0, 3.0]}'
```

### Step 4: Kubernetes Deployment

#### 4.1 Create Kubernetes Manifests
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-service
  labels:
    app: ml-model-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-model-service
  template:
    metadata:
      labels:
        app: ml-model-service
    spec:
      containers:
      - name: model-service
        image: ml-model-service:1.2.3
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ml-model-service
spec:
  selector:
    app: ml-model-service
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ml-model-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ml-model-service
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Step 5: Load Testing and Optimization

#### 5.1 Load Testing with Locust
```python
# locustfile.py
from locust import HttpUser, task, between
import json
import random

class ModelServiceUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(10)
    def predict_single(self):
        payload = {
            "features": [random.random() for _ in range(3)],
            "request_id": f"test_{random.randint(1000, 9999)}"
        }
        
        self.client.post(
            "/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
    
    @task(2)
    def predict_batch(self):
        batch_size = random.randint(5, 20)
        payload = [
            {
                "features": [random.random() for _ in range(3)],
                "request_id": f"batch_{i}"
            }
            for i in range(batch_size)
        ]
        
        self.client.post(
            "/predict_batch",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
    
    @task(1)
    def health_check(self):
        self.client.get("/health")

# Run: locust -f locustfile.py --host http://localhost:8000
```

### Step 6: Model Versioning and Canary Deployment

```yaml
# canary-deployment.yaml
apiVersion: v1
kind: Service
metadata:
  name: ml-model-service
spec:
  selector:
    app: ml-model
  ports:
    - port: 80
      targetPort: 8000
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-v1
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ml-model
      version: v1
  template:
    metadata:
      labels:
        app: ml-model
        version: v1
    spec:
      containers:
      - name: model
        image: ml-model-service:1.2.3
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-model-v2-canary
spec:
  replicas: 1  # Start with 1 replica for canary
  selector:
    matchLabels:
      app: ml-model
      version: v2
  template:
    metadata:
      labels:
        app: ml-model
        version: v2
    spec:
      containers:
      - name: model
        image: ml-model-service:2.0.0
```

### Step 7: Monitoring and Observability

```python
# Add metrics to FastAPI service
from prometheus_client import Counter, Histogram, generate_latest
import time

# Define metrics
prediction_counter = Counter(
    'model_predictions_total',
    'Total number of predictions',
    ['model_version', 'status']
)

prediction_latency = Histogram(
    'model_prediction_duration_seconds',
    'Prediction latency',
    ['model_version']
)

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type="text/plain")

@app.post("/predict")
async def predict(request: PredictionRequest):
    start_time = time.time()
    
    try:
        # ... prediction logic ...
        
        prediction_counter.labels(
            model_version="1.2.3",
            status="success"
        ).inc()
        
        return response
    
    except Exception as e:
        prediction_counter.labels(
            model_version="1.2.3",
            status="error"
        ).inc()
        raise
    
    finally:
        prediction_latency.labels(model_version="1.2.3").observe(
            time.time() - start_time
        )
```

## Best Practices

1. **Model Versioning:** Always version models and APIs
2. **Graceful Degradation:** Implement fallback strategies
3. **Resource Limits:** Set appropriate CPU/memory limits
4. **Security:** Use HTTPS, authenticate requests, validate inputs
5. **Caching:** Cache predictions for repeated inputs
6. **Monitoring:** Track latency, throughput, and error rates

## Anti-Patterns to Avoid

1. **Loading Model Per Request:** Load once at startup
2. **No Health Checks:** Always implement health endpoints
3. **Synchronous Batch Processing:** Use async for large batches
4. **Missing Input Validation:** Validate all inputs
5. **No Rate Limiting:** Implement rate limits to prevent abuse

## Integration Points

- **Model Registry:** Pull models from MLflow or similar
- **Feature Store:** Fetch features from centralized store
- **Monitoring:** Export metrics to Prometheus/Grafana
- **Logging:** Centralized logging with ELK stack

## Troubleshooting

### Issue: High latency spikes
**Solution:** Check for cold starts, implement model warming

### Issue: Out of memory errors
**Solution:** Optimize batch sizes, increase resources

### Issue: Inconsistent predictions
**Solution:** Verify preprocessing consistency, check model versions

## Related Workflows

- [Production ML Deployment](../production-ml-deployment) for full deployment pipeline
- [ML Monitoring & Observability](../ml-monitoring-observability) for monitoring setup
- [Model Evaluation Workflow](../model-evaluation-workflow) for pre-deployment validation