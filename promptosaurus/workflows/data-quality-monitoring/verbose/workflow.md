---
name: "Data Quality Monitoring"
description: "Monitor and ensure data quality throughout ML pipeline"
agent: "mlai"
category: "ml"
related_workflows:
  - feature-engineering-guide
  - ml-monitoring-observability
  - model-retraining-strategy
---

# Data Quality Monitoring - Comprehensive Guide

## Problem Context

Data quality directly impacts model performance and reliability. Poor data quality can lead to incorrect predictions, model degradation, and business losses. This workflow establishes a comprehensive monitoring system to detect data quality issues early, track data drift, and maintain high-quality inputs for machine learning models throughout their lifecycle.

## Prerequisites

- Access to data pipeline and storage systems
- Understanding of data schema and expected patterns
- Monitoring infrastructure (logging, alerting)
- Python environment with monitoring libraries
- Historical data for baseline establishment

## Step-by-Step Implementation

### Step 1: Define Data Quality Dimensions

#### 1.1 Quality Metrics Framework
```python
from dataclasses import dataclass
from typing import Dict, List, Any
import pandas as pd
import numpy as np

@dataclass
class DataQualityDimensions:
    """Core dimensions of data quality."""
    
    completeness: float  # Percentage of non-null values
    validity: float      # Percentage meeting validation rules
    accuracy: float      # Percentage of correct values
    consistency: float   # Percentage following consistent patterns
    timeliness: float    # Data freshness score
    uniqueness: float    # Percentage of unique records

class QualityMetricsCalculator:
    def __init__(self, reference_data: pd.DataFrame = None):
        self.reference_data = reference_data
        self.metrics_history = []
        
    def calculate_completeness(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate completeness for each column."""
        
        completeness = {}
        for col in df.columns:
            non_null_pct = (df[col].notna().sum() / len(df)) * 100
            completeness[col] = non_null_pct
        
        return completeness
    
    def calculate_validity(self, df: pd.DataFrame, rules: Dict) -> Dict[str, float]:
        """Check validity against predefined rules."""
        
        validity = {}
        for col, rule in rules.items():
            if col in df.columns:
                if rule['type'] == 'range':
                    valid = df[col].between(rule['min'], rule['max'])
                elif rule['type'] == 'regex':
                    valid = df[col].str.match(rule['pattern'])
                elif rule['type'] == 'values':
                    valid = df[col].isin(rule['allowed'])
                else:
                    valid = pd.Series([True] * len(df))
                
                validity[col] = (valid.sum() / len(df)) * 100
        
        return validity
    
    def calculate_uniqueness(self, df: pd.DataFrame, key_columns: List[str]) -> float:
        """Calculate uniqueness for key columns."""
        
        if not key_columns:
            return 100.0
        
        duplicates = df[key_columns].duplicated().sum()
        uniqueness = ((len(df) - duplicates) / len(df)) * 100
        
        return uniqueness
```

### Step 2: Establish Data Quality Rules

#### 2.1 Define Validation Rules
```python
import yaml
from typing import Dict, Any

class DataQualityRules:
    def __init__(self, config_path: str = None):
        self.rules = self.load_rules(config_path) if config_path else self.default_rules()
        
    def default_rules(self) -> Dict:
        """Default validation rules."""
        
        return {
            'schema': {
                'expected_columns': ['id', 'timestamp', 'value', 'category'],
                'required_columns': ['id', 'timestamp'],
                'data_types': {
                    'id': 'int64',
                    'timestamp': 'datetime64',
                    'value': 'float64',
                    'category': 'object'
                }
            },
            'values': {
                'id': {'type': 'range', 'min': 1, 'max': 1000000},
                'value': {'type': 'range', 'min': 0, 'max': 1000},
                'category': {'type': 'values', 'allowed': ['A', 'B', 'C', 'D']},
                'email': {'type': 'regex', 'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'}
            },
            'statistics': {
                'value': {
                    'mean': {'min': 45, 'max': 55},
                    'std': {'min': 5, 'max': 15},
                    'quantiles': {
                        '0.01': {'min': 10, 'max': 20},
                        '0.99': {'min': 80, 'max': 90}
                    }
                }
            },
            'freshness': {
                'max_age_hours': 24,
                'timestamp_column': 'timestamp'
            }
        }
    
    def load_rules(self, config_path: str) -> Dict:
        """Load rules from configuration file."""
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def validate_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate dataframe schema."""
        
        results = {
            'missing_columns': [],
            'extra_columns': [],
            'type_mismatches': {},
            'passed': True
        }
        
        expected = set(self.rules['schema']['expected_columns'])
        actual = set(df.columns)
        
        results['missing_columns'] = list(expected - actual)
        results['extra_columns'] = list(actual - expected)
        
        # Check data types
        for col, expected_type in self.rules['schema']['data_types'].items():
            if col in df.columns:
                actual_type = str(df[col].dtype)
                if actual_type != expected_type:
                    results['type_mismatches'][col] = {
                        'expected': expected_type,
                        'actual': actual_type
                    }
        
        results['passed'] = (not results['missing_columns'] and 
                           not results['type_mismatches'])
        
        return results
```

### Step 3: Implement Data Profiling

#### 3.1 Statistical Profiling
```python
class DataProfiler:
    def __init__(self):
        self.profile = {}
        
    def profile_dataset(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive data profile."""
        
        profile = {
            'overview': self._get_overview(df),
            'columns': {},
            'correlations': self._get_correlations(df),
            'quality_scores': {}
        }
        
        for col in df.columns:
            profile['columns'][col] = self._profile_column(df[col])
        
        return profile
    
    def _get_overview(self, df: pd.DataFrame) -> Dict:
        """Get dataset overview."""
        
        return {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': df.memory_usage(deep=True).sum() / 1024**2,  # MB
            'duplicates': df.duplicated().sum(),
            'missing_cells': df.isnull().sum().sum(),
            'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        }
    
    def _profile_column(self, series: pd.Series) -> Dict:
        """Profile individual column."""
        
        profile = {
            'dtype': str(series.dtype),
            'missing': series.isnull().sum(),
            'missing_pct': (series.isnull().sum() / len(series)) * 100,
            'unique': series.nunique(),
            'unique_pct': (series.nunique() / len(series)) * 100
        }
        
        if series.dtype in ['int64', 'float64']:
            profile.update({
                'mean': series.mean(),
                'std': series.std(),
                'min': series.min(),
                'max': series.max(),
                'quantiles': {
                    '0.01': series.quantile(0.01),
                    '0.25': series.quantile(0.25),
                    '0.50': series.quantile(0.50),
                    '0.75': series.quantile(0.75),
                    '0.99': series.quantile(0.99)
                },
                'skewness': series.skew(),
                'kurtosis': series.kurtosis(),
                'zeros': (series == 0).sum(),
                'negative': (series < 0).sum()
            })
        
        elif series.dtype == 'object':
            profile.update({
                'top_values': series.value_counts().head(10).to_dict(),
                'mode': series.mode()[0] if not series.mode().empty else None
            })
        
        return profile
    
    def _get_correlations(self, df: pd.DataFrame) -> Dict:
        """Calculate correlations between numerical columns."""
        
        numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
        
        if len(numerical_cols) < 2:
            return {}
        
        corr_matrix = df[numerical_cols].corr()
        
        # Find high correlations
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.7:
                    high_corr.append({
                        'col1': corr_matrix.columns[i],
                        'col2': corr_matrix.columns[j],
                        'correlation': corr_matrix.iloc[i, j]
                    })
        
        return {'high_correlations': high_corr}
```

### Step 4: Data Drift Detection

#### 4.1 Statistical Drift Detection
```python
from scipy import stats
from typing import Tuple

class DriftDetector:
    def __init__(self, reference_data: pd.DataFrame, threshold: float = 0.05):
        self.reference_data = reference_data
        self.threshold = threshold
        self.reference_profile = DataProfiler().profile_dataset(reference_data)
        
    def detect_drift(self, current_data: pd.DataFrame) -> Dict:
        """Detect various types of drift."""
        
        drift_report = {
            'data_drift': self._detect_data_drift(current_data),
            'schema_drift': self._detect_schema_drift(current_data),
            'statistical_drift': self._detect_statistical_drift(current_data),
            'prediction_drift': None  # Implement if predictions available
        }
        
        drift_report['overall_drift_detected'] = any([
            drift_report['data_drift']['drift_detected'],
            drift_report['schema_drift']['drift_detected'],
            drift_report['statistical_drift']['drift_detected']
        ])
        
        return drift_report
    
    def _detect_data_drift(self, current_data: pd.DataFrame) -> Dict:
        """Detect drift in data distributions."""
        
        drift_results = {'columns': {}, 'drift_detected': False}
        
        for col in current_data.columns:
            if col in self.reference_data.columns:
                if current_data[col].dtype in ['int64', 'float64']:
                    # Kolmogorov-Smirnov test for numerical features
                    statistic, p_value = stats.ks_2samp(
                        self.reference_data[col].dropna(),
                        current_data[col].dropna()
                    )
                    
                    drift_detected = p_value < self.threshold
                    
                elif current_data[col].dtype == 'object':
                    # Chi-square test for categorical features
                    ref_counts = self.reference_data[col].value_counts()
                    curr_counts = current_data[col].value_counts()
                    
                    # Align categories
                    all_categories = set(ref_counts.index) | set(curr_counts.index)
                    ref_aligned = pd.Series([ref_counts.get(cat, 0) for cat in all_categories])
                    curr_aligned = pd.Series([curr_counts.get(cat, 0) for cat in all_categories])
                    
                    if len(all_categories) > 1:
                        statistic, p_value = stats.chisquare(curr_aligned, ref_aligned)
                        drift_detected = p_value < self.threshold
                    else:
                        statistic, p_value, drift_detected = 0, 1, False
                
                else:
                    continue
                
                drift_results['columns'][col] = {
                    'drift_detected': drift_detected,
                    'p_value': p_value,
                    'statistic': statistic
                }
                
                if drift_detected:
                    drift_results['drift_detected'] = True
        
        return drift_results
    
    def _detect_schema_drift(self, current_data: pd.DataFrame) -> Dict:
        """Detect changes in data schema."""
        
        ref_columns = set(self.reference_data.columns)
        curr_columns = set(current_data.columns)
        
        schema_drift = {
            'columns_added': list(curr_columns - ref_columns),
            'columns_removed': list(ref_columns - curr_columns),
            'type_changes': {},
            'drift_detected': False
        }
        
        # Check for type changes
        for col in ref_columns & curr_columns:
            ref_type = str(self.reference_data[col].dtype)
            curr_type = str(current_data[col].dtype)
            
            if ref_type != curr_type:
                schema_drift['type_changes'][col] = {
                    'reference': ref_type,
                    'current': curr_type
                }
        
        schema_drift['drift_detected'] = bool(
            schema_drift['columns_added'] or 
            schema_drift['columns_removed'] or 
            schema_drift['type_changes']
        )
        
        return schema_drift
    
    def _detect_statistical_drift(self, current_data: pd.DataFrame) -> Dict:
        """Detect drift in statistical properties."""
        
        current_profile = DataProfiler().profile_dataset(current_data)
        statistical_drift = {'columns': {}, 'drift_detected': False}
        
        for col in current_data.columns:
            if col in self.reference_data.columns and \
               current_data[col].dtype in ['int64', 'float64']:
                
                ref_stats = self.reference_profile['columns'][col]
                curr_stats = current_profile['columns'][col]
                
                # Check if statistics differ significantly
                mean_change = abs(curr_stats['mean'] - ref_stats['mean']) / (ref_stats['std'] + 1e-8)
                std_change = abs(curr_stats['std'] - ref_stats['std']) / (ref_stats['std'] + 1e-8)
                
                drift_detected = mean_change > 2 or std_change > 0.5
                
                statistical_drift['columns'][col] = {
                    'mean_change': mean_change,
                    'std_change': std_change,
                    'drift_detected': drift_detected
                }
                
                if drift_detected:
                    statistical_drift['drift_detected'] = True
        
        return statistical_drift
```

### Step 5: Quality Monitoring Dashboard

#### 5.1 Create Monitoring Metrics
```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime

class QualityMonitoringDashboard:
    def __init__(self):
        self.metrics_history = []
        
    def update_metrics(self, df: pd.DataFrame, timestamp: datetime.datetime = None):
        """Update monitoring metrics."""
        
        if timestamp is None:
            timestamp = datetime.datetime.now()
        
        profiler = DataProfiler()
        profile = profiler.profile_dataset(df)
        
        metrics = {
            'timestamp': timestamp,
            'row_count': len(df),
            'column_count': len(df.columns),
            'missing_percentage': profile['overview']['missing_percentage'],
            'duplicate_percentage': (profile['overview']['duplicates'] / len(df)) * 100,
            'schema_valid': True,  # Implement schema validation
            'data_quality_score': self._calculate_quality_score(df)
        }
        
        self.metrics_history.append(metrics)
        
        return metrics
    
    def _calculate_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate overall data quality score."""
        
        scores = []
        
        # Completeness score
        completeness = (df.notna().sum().sum() / (len(df) * len(df.columns))) * 100
        scores.append(completeness)
        
        # Uniqueness score (for ID columns)
        if 'id' in df.columns:
            uniqueness = (df['id'].nunique() / len(df)) * 100
            scores.append(uniqueness)
        
        # Validity score (simplified)
        validity = 90  # Placeholder - implement actual validation
        scores.append(validity)
        
        return np.mean(scores)
    
    def create_dashboard(self) -> go.Figure:
        """Create interactive monitoring dashboard."""
        
        if not self.metrics_history:
            return go.Figure()
        
        df_metrics = pd.DataFrame(self.metrics_history)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Data Quality Score Over Time',
                'Row Count Trend',
                'Missing Data Percentage',
                'Duplicate Records'
            )
        )
        
        # Quality Score
        fig.add_trace(
            go.Scatter(
                x=df_metrics['timestamp'],
                y=df_metrics['data_quality_score'],
                mode='lines+markers',
                name='Quality Score',
                line=dict(color='green')
            ),
            row=1, col=1
        )
        
        # Row Count
        fig.add_trace(
            go.Scatter(
                x=df_metrics['timestamp'],
                y=df_metrics['row_count'],
                mode='lines+markers',
                name='Row Count',
                line=dict(color='blue')
            ),
            row=1, col=2
        )
        
        # Missing Percentage
        fig.add_trace(
            go.Scatter(
                x=df_metrics['timestamp'],
                y=df_metrics['missing_percentage'],
                mode='lines+markers',
                name='Missing %',
                line=dict(color='orange')
            ),
            row=2, col=1
        )
        
        # Duplicate Percentage
        fig.add_trace(
            go.Scatter(
                x=df_metrics['timestamp'],
                y=df_metrics['duplicate_percentage'],
                mode='lines+markers',
                name='Duplicate %',
                line=dict(color='red')
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            title='Data Quality Monitoring Dashboard',
            height=600,
            showlegend=False
        )
        
        return fig
```

### Step 6: Alerting System

#### 6.1 Configure Alerts
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

class DataQualityAlerting:
    def __init__(self, config: Dict):
        self.config = config
        self.alert_history = []
        
    def check_alerts(self, metrics: Dict, drift_report: Dict) -> List[Dict]:
        """Check if any alert conditions are met."""
        
        alerts = []
        
        # Check quality score threshold
        if metrics['data_quality_score'] < self.config['thresholds']['quality_score']:
            alerts.append({
                'type': 'quality_score',
                'severity': 'high',
                'message': f"Data quality score dropped to {metrics['data_quality_score']:.1f}%",
                'value': metrics['data_quality_score']
            })
        
        # Check missing data threshold
        if metrics['missing_percentage'] > self.config['thresholds']['missing_percentage']:
            alerts.append({
                'type': 'missing_data',
                'severity': 'medium',
                'message': f"Missing data increased to {metrics['missing_percentage']:.1f}%",
                'value': metrics['missing_percentage']
            })
        
        # Check drift detection
        if drift_report and drift_report['overall_drift_detected']:
            drifted_columns = [
                col for col, info in drift_report['data_drift']['columns'].items()
                if info['drift_detected']
            ]
            alerts.append({
                'type': 'data_drift',
                'severity': 'high',
                'message': f"Data drift detected in columns: {', '.join(drifted_columns)}",
                'columns': drifted_columns
            })
        
        return alerts
    
    def send_alerts(self, alerts: List[Dict]):
        """Send alerts via configured channels."""
        
        for alert in alerts:
            # Log alert
            self.alert_history.append({
                'timestamp': datetime.datetime.now(),
                'alert': alert
            })
            
            # Send based on severity
            if alert['severity'] == 'high':
                self._send_email_alert(alert)
                self._send_slack_alert(alert)
            elif alert['severity'] == 'medium':
                self._send_slack_alert(alert)
            else:
                self._log_alert(alert)
    
    def _send_email_alert(self, alert: Dict):
        """Send email alert."""
        
        if not self.config.get('email'):
            return
        
        msg = MIMEMultipart()
        msg['From'] = self.config['email']['from']
        msg['To'] = ', '.join(self.config['email']['to'])
        msg['Subject'] = f"Data Quality Alert: {alert['type']}"
        
        body = f"""
        Alert Type: {alert['type']}
        Severity: {alert['severity']}
        Message: {alert['message']}
        Timestamp: {datetime.datetime.now()}
        
        Please check the data quality dashboard for more details.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email (simplified - add actual SMTP configuration)
        print(f"Email alert sent: {alert['message']}")
    
    def _send_slack_alert(self, alert: Dict):
        """Send Slack alert."""
        
        if not self.config.get('slack'):
            return
        
        # Implement Slack webhook integration
        webhook_url = self.config['slack']['webhook_url']
        
        payload = {
            'text': f":warning: Data Quality Alert",
            'attachments': [{
                'color': 'danger' if alert['severity'] == 'high' else 'warning',
                'fields': [
                    {'title': 'Type', 'value': alert['type'], 'short': True},
                    {'title': 'Severity', 'value': alert['severity'], 'short': True},
                    {'title': 'Message', 'value': alert['message']}
                ]
            }]
        }
        
        # Send to Slack (simplified)
        print(f"Slack alert sent: {alert['message']}")
    
    def _log_alert(self, alert: Dict):
        """Log alert to file."""
        
        with open('data_quality_alerts.log', 'a') as f:
            f.write(f"{datetime.datetime.now()} - {json.dumps(alert)}\n")
```

### Step 7: Integration and Automation

#### 7.1 Automated Monitoring Pipeline
```python
import schedule
import time
from pathlib import Path

class DataQualityMonitoringPipeline:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.rules = DataQualityRules()
        self.profiler = DataProfiler()
        self.drift_detector = None  # Initialize with reference data
        self.dashboard = QualityMonitoringDashboard()
        self.alerting = DataQualityAlerting(self.config['alerting'])
        
    def run_monitoring(self, data_path: str):
        """Run complete monitoring pipeline."""
        
        print(f"Running data quality monitoring at {datetime.datetime.now()}")
        
        # Load data
        df = pd.read_csv(data_path)
        
        # Schema validation
        schema_results = self.rules.validate_schema(df)
        
        # Data profiling
        profile = self.profiler.profile_dataset(df)
        
        # Update metrics
        metrics = self.dashboard.update_metrics(df)
        
        # Drift detection (if reference data exists)
        drift_report = None
        if self.drift_detector:
            drift_report = self.drift_detector.detect_drift(df)
        
        # Check alerts
        alerts = self.alerting.check_alerts(metrics, drift_report)
        
        # Send alerts
        if alerts:
            self.alerting.send_alerts(alerts)
        
        # Save results
        self._save_results({
            'timestamp': datetime.datetime.now(),
            'schema_validation': schema_results,
            'profile': profile,
            'metrics': metrics,
            'drift_report': drift_report,
            'alerts': alerts
        })
        
        print(f"Monitoring complete. {len(alerts)} alerts generated.")
        
        return metrics
    
    def _save_results(self, results: Dict):
        """Save monitoring results."""
        
        output_dir = Path('monitoring_results')
        output_dir.mkdir(exist_ok=True)
        
        timestamp = results['timestamp'].strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f'monitoring_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    def schedule_monitoring(self, data_path: str, interval_minutes: int = 60):
        """Schedule periodic monitoring."""
        
        schedule.every(interval_minutes).minutes.do(
            self.run_monitoring, data_path=data_path
        )
        
        print(f"Monitoring scheduled every {interval_minutes} minutes")
        
        while True:
            schedule.run_pending()
            time.sleep(1)

# Usage
if __name__ == "__main__":
    pipeline = DataQualityMonitoringPipeline('config/monitoring_config.yaml')
    
    # Run once
    pipeline.run_monitoring('data/current_batch.csv')
    
    # Or schedule periodic monitoring
    # pipeline.schedule_monitoring('data/current_batch.csv', interval_minutes=30)
```

## Best Practices

1. **Establish Baselines:** Use historical data to set realistic thresholds
2. **Monitor Incrementally:** Start with critical metrics, expand gradually
3. **Automate Everything:** Manual checks don't scale
4. **Version Control Rules:** Track changes to validation rules
5. **Document Issues:** Keep detailed logs of quality problems
6. **Act on Alerts:** Don't ignore alerts - investigate and resolve

## Anti-Patterns to Avoid

1. **Alert Fatigue:** Too many low-priority alerts
2. **Static Thresholds:** Not adapting to seasonal patterns
3. **Ignoring Drift:** Small changes compound over time
4. **No Root Cause Analysis:** Fixing symptoms not causes
5. **Manual Monitoring:** Relying on human checks

## Integration Points

- **Data Pipeline:** Integrate checks at ingestion points
- **Model Training:** Validate data before training
- **Feature Store:** Monitor feature quality
- **Production Systems:** Real-time quality checks

## Troubleshooting

### Issue: Too many false positive alerts
**Solution:** Adjust thresholds based on historical patterns

### Issue: Drift detection too sensitive
**Solution:** Use longer reference windows, adjust significance levels

### Issue: Performance impact on pipeline
**Solution:** Sample data for monitoring, run async checks

## Related Workflows

- [Feature Engineering Guide](../feature-engineering-guide) for feature quality
- [ML Monitoring & Observability](../ml-monitoring-observability) for model monitoring
- [Model Retraining Strategy](../model-retraining-strategy) for handling drift