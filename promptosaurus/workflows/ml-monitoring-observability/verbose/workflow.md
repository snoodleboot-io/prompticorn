---
name: ml-monitoring-observability
description: "Monitor ML models and pipelines in production"
agent: "mlai"
category: "ml"
related_workflows:
  - data-quality-monitoring
  - model-serving-workflow
  - model-retraining-strategy
---

# ML Monitoring & Observability - Comprehensive Guide

## Problem Context

ML models in production require continuous monitoring to ensure they maintain performance, catch degradation early, and provide insights for improvement. Unlike traditional software, ML systems can fail silently - appearing to work while producing increasingly poor predictions. This workflow establishes comprehensive monitoring and observability for ML systems in production.

## Prerequisites

- Deployed ML models in production
- Access to model serving infrastructure
- Monitoring infrastructure (Prometheus, Grafana, etc.)
- Understanding of model metrics and KPIs
- Logging and storage systems

## Step-by-Step Implementation

### Step 1: Define Monitoring Metrics

#### 1.1 Core ML Metrics
```python
from dataclasses import dataclass
from typing import Dict, List, Any
import numpy as np

@dataclass
class MLMetrics:
    """Core metrics for ML monitoring."""
    
    # Model Performance
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    
    # Prediction Statistics
    prediction_count: int
    prediction_distribution: Dict[str, int]
    confidence_distribution: List[float]
    
    # Data Quality
    feature_distributions: Dict[str, Any]
    missing_features: Dict[str, float]
    out_of_range: Dict[str, int]
    
    # System Performance
    latency_p50: float
    latency_p95: float
    latency_p99: float
    throughput: float
    error_rate: float

class MetricsCollector:
    def __init__(self):
        self.metrics_buffer = []
        self.aggregation_window = 300  # 5 minutes
        
    def collect_prediction_metrics(
        self, 
        features: np.ndarray, 
        prediction: np.ndarray,
        confidence: float,
        latency: float
    ):
        """Collect metrics for a single prediction."""
        
        metric = {
            'timestamp': pd.Timestamp.now(),
            'prediction': prediction,
            'confidence': confidence,
            'latency': latency,
            'feature_stats': self._calculate_feature_stats(features)
        }
        
        self.metrics_buffer.append(metric)
        
        # Aggregate if window is full
        if len(self.metrics_buffer) >= self.aggregation_window:
            return self._aggregate_metrics()
        
        return None
    
    def _calculate_feature_stats(self, features: np.ndarray) -> Dict:
        """Calculate statistics for features."""
        
        return {
            'mean': np.mean(features),
            'std': np.std(features),
            'min': np.min(features),
            'max': np.max(features),
            'nulls': np.isnan(features).sum()
        }
    
    def _aggregate_metrics(self) -> MLMetrics:
        """Aggregate collected metrics."""
        
        df = pd.DataFrame(self.metrics_buffer)
        
        metrics = MLMetrics(
            accuracy=0,  # Calculate if ground truth available
            precision=0,
            recall=0,
            f1_score=0,
            auc_roc=0,
            prediction_count=len(df),
            prediction_distribution=df['prediction'].value_counts().to_dict(),
            confidence_distribution=df['confidence'].tolist(),
            feature_distributions={},  # Calculate from feature_stats
            missing_features={},
            out_of_range={},
            latency_p50=df['latency'].quantile(0.50),
            latency_p95=df['latency'].quantile(0.95),
            latency_p99=df['latency'].quantile(0.99),
            throughput=len(df) / 300,  # predictions per second
            error_rate=0  # Calculate from errors
        )
        
        self.metrics_buffer = []  # Clear buffer
        return metrics
```

### Step 2: Implement Monitoring Infrastructure

#### 2.1 Prometheus Metrics
```python
from prometheus_client import Counter, Histogram, Gauge, Summary
import time

class PrometheusMonitoring:
    def __init__(self, model_name: str, model_version: str):
        self.model_name = model_name
        self.model_version = model_version
        
        # Define Prometheus metrics
        self.prediction_counter = Counter(
            'ml_predictions_total',
            'Total number of predictions',
            ['model', 'version', 'status']
        )
        
        self.prediction_latency = Histogram(
            'ml_prediction_duration_seconds',
            'Prediction latency in seconds',
            ['model', 'version'],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
        )
        
        self.model_confidence = Summary(
            'ml_prediction_confidence',
            'Prediction confidence scores',
            ['model', 'version']
        )
        
        self.feature_drift = Gauge(
            'ml_feature_drift',
            'Feature drift score',
            ['model', 'version', 'feature']
        )
        
        self.model_accuracy = Gauge(
            'ml_model_accuracy',
            'Model accuracy on recent predictions',
            ['model', 'version']
        )
        
        self.data_quality_score = Gauge(
            'ml_data_quality_score',
            'Input data quality score',
            ['model', 'version']
        )
    
    def record_prediction(
        self, 
        prediction: Any,
        confidence: float,
        latency: float,
        status: str = 'success'
    ):
        """Record metrics for a prediction."""
        
        # Increment counter
        self.prediction_counter.labels(
            model=self.model_name,
            version=self.model_version,
            status=status
        ).inc()
        
        # Record latency
        self.prediction_latency.labels(
            model=self.model_name,
            version=self.model_version
        ).observe(latency)
        
        # Record confidence
        self.model_confidence.labels(
            model=self.model_name,
            version=self.model_version
        ).observe(confidence)
    
    def update_drift_metrics(self, drift_scores: Dict[str, float]):
        """Update feature drift metrics."""
        
        for feature, score in drift_scores.items():
            self.feature_drift.labels(
                model=self.model_name,
                version=self.model_version,
                feature=feature
            ).set(score)
    
    def update_model_metrics(self, accuracy: float, data_quality: float):
        """Update model performance metrics."""
        
        self.model_accuracy.labels(
            model=self.model_name,
            version=self.model_version
        ).set(accuracy)
        
        self.data_quality_score.labels(
            model=self.model_name,
            version=self.model_version
        ).set(data_quality)
```

### Step 3: Data and Prediction Drift Detection

#### 3.1 Drift Monitoring
```python
from scipy import stats
import pandas as pd

class DriftMonitor:
    def __init__(self, reference_data: pd.DataFrame, threshold: float = 0.05):
        self.reference_data = reference_data
        self.threshold = threshold
        self.drift_history = []
        
    def detect_feature_drift(self, current_data: pd.DataFrame) -> Dict[str, Dict]:
        """Detect drift in feature distributions."""
        
        drift_results = {}
        
        for column in current_data.columns:
            if column in self.reference_data.columns:
                ref_values = self.reference_data[column].dropna()
                curr_values = current_data[column].dropna()
                
                if pd.api.types.is_numeric_dtype(ref_values):
                    # KS test for numerical features
                    statistic, p_value = stats.ks_2samp(ref_values, curr_values)
                else:
                    # Chi-square test for categorical features
                    ref_counts = ref_values.value_counts()
                    curr_counts = curr_values.value_counts()
                    
                    # Align categories
                    all_categories = set(ref_counts.index) | set(curr_counts.index)
                    ref_aligned = [ref_counts.get(cat, 0) for cat in all_categories]
                    curr_aligned = [curr_counts.get(cat, 0) for cat in all_categories]
                    
                    statistic, p_value = stats.chisquare(curr_aligned, ref_aligned)
                
                drift_detected = p_value < self.threshold
                
                drift_results[column] = {
                    'drift_detected': drift_detected,
                    'p_value': p_value,
                    'statistic': statistic,
                    'drift_score': 1 - p_value  # Higher score = more drift
                }
        
        # Record in history
        self.drift_history.append({
            'timestamp': pd.Timestamp.now(),
            'results': drift_results
        })
        
        return drift_results
    
    def detect_prediction_drift(
        self, 
        recent_predictions: pd.Series,
        reference_predictions: pd.Series
    ) -> Dict:
        """Detect drift in model predictions."""
        
        # Statistical test
        statistic, p_value = stats.ks_2samp(
            reference_predictions, 
            recent_predictions
        )
        
        # Distribution comparison
        ref_dist = reference_predictions.value_counts(normalize=True)
        curr_dist = recent_predictions.value_counts(normalize=True)
        
        # Calculate KL divergence
        kl_divergence = self._calculate_kl_divergence(ref_dist, curr_dist)
        
        return {
            'drift_detected': p_value < self.threshold,
            'p_value': p_value,
            'statistic': statistic,
            'kl_divergence': kl_divergence,
            'distribution_change': (curr_dist - ref_dist).to_dict()
        }
    
    def _calculate_kl_divergence(self, p: pd.Series, q: pd.Series) -> float:
        """Calculate KL divergence between two distributions."""
        
        # Align distributions
        all_categories = set(p.index) | set(q.index)
        p_aligned = pd.Series([p.get(cat, 1e-10) for cat in all_categories])
        q_aligned = pd.Series([q.get(cat, 1e-10) for cat in all_categories])
        
        return np.sum(p_aligned * np.log(p_aligned / q_aligned))
```

### Step 4: Create Monitoring Dashboard

#### 4.1 Grafana Dashboard Configuration
```python
import json

class DashboardBuilder:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.dashboard = {
            'title': f'ML Model Monitoring - {model_name}',
            'panels': [],
            'refresh': '30s',
            'time': {'from': 'now-6h', 'to': 'now'}
        }
    
    def add_performance_panel(self) -> 'DashboardBuilder':
        """Add model performance metrics panel."""
        
        panel = {
            'title': 'Model Performance',
            'type': 'graph',
            'gridPos': {'x': 0, 'y': 0, 'w': 12, 'h': 8},
            'targets': [
                {
                    'expr': f'ml_model_accuracy{{model="{self.model_name}"}}',
                    'legendFormat': 'Accuracy'
                },
                {
                    'expr': f'rate(ml_predictions_total{{model="{self.model_name}",status="error"}}[5m])',
                    'legendFormat': 'Error Rate'
                }
            ]
        }
        
        self.dashboard['panels'].append(panel)
        return self
    
    def add_latency_panel(self) -> 'DashboardBuilder':
        """Add latency metrics panel."""
        
        panel = {
            'title': 'Prediction Latency',
            'type': 'graph',
            'gridPos': {'x': 12, 'y': 0, 'w': 12, 'h': 8},
            'targets': [
                {
                    'expr': f'histogram_quantile(0.5, ml_prediction_duration_seconds_bucket{{model="{self.model_name}"}})',
                    'legendFormat': 'p50'
                },
                {
                    'expr': f'histogram_quantile(0.95, ml_prediction_duration_seconds_bucket{{model="{self.model_name}"}})',
                    'legendFormat': 'p95'
                },
                {
                    'expr': f'histogram_quantile(0.99, ml_prediction_duration_seconds_bucket{{model="{self.model_name}"}})',
                    'legendFormat': 'p99'
                }
            ]
        }
        
        self.dashboard['panels'].append(panel)
        return self
    
    def add_drift_panel(self) -> 'DashboardBuilder':
        """Add drift monitoring panel."""
        
        panel = {
            'title': 'Feature Drift',
            'type': 'heatmap',
            'gridPos': {'x': 0, 'y': 8, 'w': 24, 'h': 8},
            'targets': [
                {
                    'expr': f'ml_feature_drift{{model="{self.model_name}"}}',
                    'format': 'heatmap',
                    'legendFormat': '{{feature}}'
                }
            ]
        }
        
        self.dashboard['panels'].append(panel)
        return self
    
    def add_throughput_panel(self) -> 'DashboardBuilder':
        """Add throughput metrics panel."""
        
        panel = {
            'title': 'Prediction Throughput',
            'type': 'graph',
            'gridPos': {'x': 0, 'y': 16, 'w': 12, 'h': 8},
            'targets': [
                {
                    'expr': f'rate(ml_predictions_total{{model="{self.model_name}"}}[5m])',
                    'legendFormat': 'Predictions/sec'
                }
            ]
        }
        
        self.dashboard['panels'].append(panel)
        return self
    
    def build(self) -> str:
        """Build the dashboard JSON."""
        return json.dumps(self.dashboard, indent=2)

# Create dashboard
dashboard = DashboardBuilder('customer_churn_model')
dashboard_json = (
    dashboard
    .add_performance_panel()
    .add_latency_panel()
    .add_drift_panel()
    .add_throughput_panel()
    .build()
)
```

### Step 5: Alerting Configuration

#### 5.1 Alert Rules
```python
from typing import Optional
import smtplib
from email.mime.text import MIMEText

class AlertManager:
    def __init__(self, config: Dict):
        self.config = config
        self.alert_rules = self._define_alert_rules()
        self.alert_history = []
        
    def _define_alert_rules(self) -> List[Dict]:
        """Define alert rules for ML monitoring."""
        
        return [
            {
                'name': 'model_accuracy_low',
                'condition': lambda metrics: metrics.accuracy < 0.85,
                'severity': 'critical',
                'message': 'Model accuracy dropped below 85%',
                'cooldown_minutes': 30
            },
            {
                'name': 'high_latency',
                'condition': lambda metrics: metrics.latency_p95 > 1.0,
                'severity': 'warning',
                'message': 'P95 latency exceeds 1 second',
                'cooldown_minutes': 15
            },
            {
                'name': 'feature_drift_detected',
                'condition': lambda drift: any(f['drift_detected'] for f in drift.values()),
                'severity': 'warning',
                'message': 'Feature drift detected',
                'cooldown_minutes': 60
            },
            {
                'name': 'error_rate_high',
                'condition': lambda metrics: metrics.error_rate > 0.05,
                'severity': 'critical',
                'message': 'Error rate exceeds 5%',
                'cooldown_minutes': 15
            },
            {
                'name': 'throughput_low',
                'condition': lambda metrics: metrics.throughput < 10,
                'severity': 'info',
                'message': 'Throughput below 10 predictions/sec',
                'cooldown_minutes': 60
            }
        ]
    
    def check_alerts(self, metrics: MLMetrics, drift_results: Dict) -> List[Dict]:
        """Check if any alert conditions are met."""
        
        triggered_alerts = []
        
        for rule in self.alert_rules:
            # Check cooldown
            if self._in_cooldown(rule['name']):
                continue
            
            # Check condition
            try:
                if 'drift' in rule['name']:
                    condition_met = rule['condition'](drift_results)
                else:
                    condition_met = rule['condition'](metrics)
                
                if condition_met:
                    alert = {
                        'name': rule['name'],
                        'severity': rule['severity'],
                        'message': rule['message'],
                        'timestamp': pd.Timestamp.now(),
                        'metrics': metrics.__dict__ if metrics else None
                    }
                    
                    triggered_alerts.append(alert)
                    self.alert_history.append(alert)
                    
            except Exception as e:
                print(f"Error checking alert rule {rule['name']}: {e}")
        
        return triggered_alerts
    
    def _in_cooldown(self, alert_name: str) -> bool:
        """Check if alert is in cooldown period."""
        
        for alert in reversed(self.alert_history):
            if alert['name'] == alert_name:
                cooldown = next(
                    r['cooldown_minutes'] 
                    for r in self.alert_rules 
                    if r['name'] == alert_name
                )
                
                time_since = pd.Timestamp.now() - alert['timestamp']
                return time_since.total_seconds() < cooldown * 60
        
        return False
    
    def send_alerts(self, alerts: List[Dict]):
        """Send alerts through configured channels."""
        
        for alert in alerts:
            if alert['severity'] == 'critical':
                self._send_pagerduty(alert)
                self._send_email(alert)
            elif alert['severity'] == 'warning':
                self._send_slack(alert)
            else:
                self._log_alert(alert)
    
    def _send_email(self, alert: Dict):
        """Send email alert."""
        
        msg = MIMEText(f"""
        Alert: {alert['name']}
        Severity: {alert['severity']}
        Message: {alert['message']}
        Timestamp: {alert['timestamp']}
        
        Please check the ML monitoring dashboard for details.
        """)
        
        msg['Subject'] = f"ML Alert: {alert['name']}"
        msg['From'] = self.config['email']['from']
        msg['To'] = ', '.join(self.config['email']['to'])
        
        # Send email
        print(f"Email alert sent: {alert['message']}")
    
    def _send_slack(self, alert: Dict):
        """Send Slack notification."""
        
        webhook_url = self.config['slack']['webhook_url']
        
        payload = {
            'text': f":warning: ML Model Alert",
            'attachments': [{
                'color': 'warning',
                'fields': [
                    {'title': 'Alert', 'value': alert['name']},
                    {'title': 'Severity', 'value': alert['severity']},
                    {'title': 'Message', 'value': alert['message']}
                ]
            }]
        }
        
        # Send to Slack
        print(f"Slack alert sent: {alert['message']}")
    
    def _send_pagerduty(self, alert: Dict):
        """Trigger PagerDuty incident."""
        
        # PagerDuty integration
        print(f"PagerDuty alert triggered: {alert['message']}")
    
    def _log_alert(self, alert: Dict):
        """Log alert to file."""
        
        with open('ml_alerts.log', 'a') as f:
            f.write(f"{alert['timestamp']} - {json.dumps(alert)}\n")
```

### Step 6: Logging and Auditing

#### 6.1 Prediction Logging
```python
import hashlib
import json
from pathlib import Path

class PredictionLogger:
    def __init__(self, log_dir: str = 'prediction_logs'):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.current_log = None
        self.log_buffer = []
        self.buffer_size = 1000
        
    def log_prediction(
        self,
        request_id: str,
        features: Dict,
        prediction: Any,
        confidence: float,
        model_version: str,
        latency: float,
        metadata: Optional[Dict] = None
    ):
        """Log a single prediction."""
        
        log_entry = {
            'request_id': request_id,
            'timestamp': pd.Timestamp.now().isoformat(),
            'model_version': model_version,
            'features': features,
            'prediction': prediction,
            'confidence': confidence,
            'latency_ms': latency * 1000,
            'metadata': metadata or {},
            'feature_hash': self._hash_features(features)
        }
        
        self.log_buffer.append(log_entry)
        
        # Flush buffer if full
        if len(self.log_buffer) >= self.buffer_size:
            self._flush_buffer()
    
    def _hash_features(self, features: Dict) -> str:
        """Create hash of features for deduplication."""
        
        feature_str = json.dumps(features, sort_keys=True)
        return hashlib.md5(feature_str.encode()).hexdigest()
    
    def _flush_buffer(self):
        """Write buffer to disk."""
        
        if not self.log_buffer:
            return
        
        # Create daily log file
        date_str = pd.Timestamp.now().strftime('%Y%m%d')
        log_file = self.log_dir / f'predictions_{date_str}.jsonl'
        
        # Append to file
        with open(log_file, 'a') as f:
            for entry in self.log_buffer:
                f.write(json.dumps(entry) + '\n')
        
        self.log_buffer = []
    
    def query_predictions(
        self,
        start_time: pd.Timestamp,
        end_time: pd.Timestamp,
        filters: Optional[Dict] = None
    ) -> pd.DataFrame:
        """Query logged predictions."""
        
        # Find relevant log files
        log_files = self._get_log_files_in_range(start_time, end_time)
        
        # Load and filter logs
        predictions = []
        for log_file in log_files:
            with open(log_file, 'r') as f:
                for line in f:
                    entry = json.loads(line)
                    timestamp = pd.Timestamp(entry['timestamp'])
                    
                    if start_time <= timestamp <= end_time:
                        if self._matches_filters(entry, filters):
                            predictions.append(entry)
        
        return pd.DataFrame(predictions)
    
    def _get_log_files_in_range(
        self, 
        start_time: pd.Timestamp, 
        end_time: pd.Timestamp
    ) -> List[Path]:
        """Get log files within time range."""
        
        log_files = []
        current_date = start_time.date()
        
        while current_date <= end_time.date():
            date_str = current_date.strftime('%Y%m%d')
            log_file = self.log_dir / f'predictions_{date_str}.jsonl'
            
            if log_file.exists():
                log_files.append(log_file)
            
            current_date += pd.Timedelta(days=1)
        
        return log_files
    
    def _matches_filters(self, entry: Dict, filters: Optional[Dict]) -> bool:
        """Check if entry matches filters."""
        
        if not filters:
            return True
        
        for key, value in filters.items():
            if key not in entry or entry[key] != value:
                return False
        
        return True
```

### Step 7: Integration and Automation

#### 7.1 Complete Monitoring Pipeline
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MLMonitoringPipeline:
    def __init__(self, config: Dict):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.prometheus_monitor = PrometheusMonitoring(
            config['model_name'],
            config['model_version']
        )
        self.drift_monitor = DriftMonitor(
            reference_data=pd.read_csv(config['reference_data_path'])
        )
        self.alert_manager = AlertManager(config['alerting'])
        self.prediction_logger = PredictionLogger()
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    async def process_prediction(
        self,
        request_id: str,
        features: np.ndarray,
        model
    ) -> Dict:
        """Process prediction with full monitoring."""
        
        # Start timing
        start_time = time.time()
        
        try:
            # Make prediction
            prediction = model.predict(features)
            confidence = model.predict_proba(features).max()
            
            # Calculate latency
            latency = time.time() - start_time
            
            # Record metrics
            self.prometheus_monitor.record_prediction(
                prediction=prediction,
                confidence=confidence,
                latency=latency,
                status='success'
            )
            
            # Collect metrics
            aggregated = self.metrics_collector.collect_prediction_metrics(
                features=features,
                prediction=prediction,
                confidence=confidence,
                latency=latency
            )
            
            # Check for drift (async)
            asyncio.create_task(self._check_drift(features))
            
            # Log prediction (async)
            asyncio.create_task(self._log_prediction(
                request_id=request_id,
                features=features.tolist(),
                prediction=prediction,
                confidence=confidence,
                latency=latency
            ))
            
            # Check alerts if metrics aggregated
            if aggregated:
                asyncio.create_task(self._check_alerts(aggregated))
            
            return {
                'request_id': request_id,
                'prediction': prediction,
                'confidence': confidence,
                'latency': latency
            }
            
        except Exception as e:
            # Record error
            self.prometheus_monitor.record_prediction(
                prediction=None,
                confidence=0,
                latency=time.time() - start_time,
                status='error'
            )
            
            # Log error
            print(f"Prediction error: {e}")
            raise
    
    async def _check_drift(self, features: np.ndarray):
        """Check for feature drift asynchronously."""
        
        loop = asyncio.get_event_loop()
        
        # Run drift detection in thread pool
        drift_results = await loop.run_in_executor(
            self.executor,
            self.drift_monitor.detect_feature_drift,
            pd.DataFrame([features])
        )
        
        # Update metrics
        drift_scores = {
            col: result['drift_score'] 
            for col, result in drift_results.items()
        }
        self.prometheus_monitor.update_drift_metrics(drift_scores)
    
    async def _log_prediction(self, **kwargs):
        """Log prediction asynchronously."""
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            self.executor,
            self.prediction_logger.log_prediction,
            **kwargs
        )
    
    async def _check_alerts(self, metrics: MLMetrics):
        """Check and send alerts asynchronously."""
        
        # Check alert conditions
        alerts = self.alert_manager.check_alerts(metrics, {})
        
        # Send alerts
        if alerts:
            self.alert_manager.send_alerts(alerts)
    
    def start_monitoring_server(self, port: int = 8000):
        """Start Prometheus metrics server."""
        
        from prometheus_client import start_http_server
        start_http_server(port)
        print(f"Metrics server started on port {port}")

# Usage
config = {
    'model_name': 'customer_churn',
    'model_version': 'v1.2.3',
    'reference_data_path': 'reference_data.csv',
    'alerting': {
        'email': {'from': 'ml@company.com', 'to': ['team@company.com']},
        'slack': {'webhook_url': 'https://hooks.slack.com/...'},
    }
}

monitoring = MLMonitoringPipeline(config)
monitoring.start_monitoring_server()

# Process prediction
result = await monitoring.process_prediction(
    request_id='req_123',
    features=np.array([1.0, 2.0, 3.0]),
    model=model
)
```

## Best Practices

1. **Monitor Everything:** Track predictions, features, performance, and system metrics
2. **Set Baselines:** Establish normal behavior before alerting
3. **Version Everything:** Track model versions, configurations, and thresholds
4. **Automate Response:** Have automated remediation for common issues
5. **Regular Reviews:** Periodically review monitoring effectiveness
6. **Test Monitoring:** Ensure monitoring itself is reliable

## Anti-Patterns to Avoid

1. **Monitoring Only Accuracy:** Need comprehensive metrics
2. **No Historical Context:** Always compare to baselines
3. **Alert Fatigue:** Too many low-value alerts
4. **No Action Plan:** Alerts without clear remediation steps
5. **Ignoring Drift:** Small changes compound over time

## Integration Points

- **Model Serving:** Integrate with serving infrastructure
- **Data Pipeline:** Monitor input data quality
- **Training Pipeline:** Trigger retraining based on monitoring
- **Incident Management:** Connect to PagerDuty, Jira, etc.

## Troubleshooting

### Issue: High false positive alerts
**Solution:** Adjust thresholds based on historical data, implement smart alerting

### Issue: Monitoring overhead affects latency
**Solution:** Use async logging, sample predictions for monitoring

### Issue: Storage costs for logs
**Solution:** Implement retention policies, compress old logs

## Related Workflows

- [Data Quality Monitoring](../data-quality-monitoring) for input data monitoring
- [Model Serving Workflow](../model-serving-workflow) for deployment monitoring
- [Model Retraining Strategy](../model-retraining-strategy) for automated retraining