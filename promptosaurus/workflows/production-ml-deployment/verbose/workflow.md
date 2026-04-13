---
name: "production-ml-deployment"
description: Deploy ML models to production with monitoring, versioning, and safety guardrails
type: workflow
category: workflow-patterns
minimal: false
---

# Production ML Deployment

## Overview
Getting models from development to production requires careful planning for reliability and safety.

## Deployment Strategies

### Batch Predictions
- Run predictions on schedule
- Process large datasets
- Asynchronous results
- Lower latency requirements
- Examples: daily scoring, periodic updates

### Real-Time API
- HTTP/REST endpoints
- Immediate predictions
- Low latency requirements
- Handle concurrent requests
- Examples: online classification, fraud detection

### Streaming Predictions
- Continuous data stream
- Real-time processing
- High throughput
- Examples: sensor data, event streams

### Embedded Models
- Model in application
- No external dependencies
- Lowest latency
- Limited model size/complexity

## Model Serving Platforms

### REST/HTTP Servers
- Flask/FastAPI application
- Simple deployment
- Standard HTTP interface
- Easy to monitor

### Model Serving Frameworks
- TensorFlow Serving
- Seldon Core
- KServe
- Multi-model support
- Built-in versioning

### Containerization (Docker)
- Standardized environment
- Reproducible deployment
- Easy scaling
- Cloud-native

### Kubernetes Orchestration
- Container orchestration
- Auto-scaling
- Load balancing
- Self-healing
- Enterprise-grade

## Version Management

### Model Registry
- Central repository
- Version tracking
- Stage management (dev/staging/prod)
- Metadata and lineage
- Rollback capability

### Semantic Versioning
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes
- Clear communication

### Canary Deployment
- 5% → 25% → 50% → 100%
- Monitor metrics at each stage
- Automated rollback on issues
- Risk mitigation

## Monitoring & Observability

### Performance Metrics
- Inference latency
- Throughput
- Error rates
- Resource usage (CPU, memory)

### Model Metrics
- Prediction confidence
- Output distribution
- Drift detection
- Accuracy monitoring

### Business Metrics
- Revenue impact
- User satisfaction
- Downstream metrics
- ROI tracking

### Alerting
- Set thresholds
- Alert on anomalies
- Escalation procedures
- On-call procedures

## Safety & Reliability

### Input Validation
- Type checking
- Range validation
- Schema validation
- Reject malformed inputs

### Prediction Confidence
- Return confidence scores
- Set minimum thresholds
- Fallback strategies
- Human review triggers

### Rate Limiting
- Prevent abuse
- Resource protection
- Fair usage
- Cost control

### Fallback Mechanisms
- Default predictions
- Previous model version
- Simple rule-based fallback
- Graceful degradation

## Data Management

### Input Data Logging
- Store all predictions
- Log input features
- Track actual outcomes
- Enable retraining

### Feature Consistency
- Same preprocessing
- Data source integrity
- Version consistency
- Quality checks

## Cost Optimization

### Model Compression
- Quantization
- Pruning
- Knowledge distillation
- Faster inference

### Batch Processing
- Group predictions
- Reduce overhead
- Better resource utilization
- Higher throughput

### Resource Allocation
- Right-size compute
- Auto-scaling policies
- Reserved capacity
- Cost tracking

## Best Practices

1. **Automate deployment:** Repeatable, consistent
2. **Comprehensive monitoring:** Know when things break
3. **Canary releases:** Test safely
4. **Rapid rollback:** Recover quickly
5. **Documentation:** Runbooks and guides
6. **Testing:** Pre-production validation
7. **Team readiness:** Training and procedures
