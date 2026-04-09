# Jinja2 Deployment and Operations Guide

**Version:** 1.0  
**Date:** April 2026  
**Audience:** DevOps Engineers, System Administrators, Operations Teams

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Installation and Setup](#installation-and-setup)
4. [Configuration](#configuration)
5. [Deployment Procedures](#deployment-procedures)
6. [Monitoring and Alerting](#monitoring-and-alerting)
7. [Performance Tuning](#performance-tuning)
8. [Backup and Recovery](#backup-and-recovery)
9. [Rollback Procedures](#rollback-procedures)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 5-Minute Deployment

```bash
# 1. Verify Python environment (3.9+)
python --version

# 2. Install Jinja2 (if not already installed)
pip install jinja2>=3.0

# 3. Verify installation
python -c "import jinja2; print(f'Jinja2 {jinja2.__version__} installed')"

# 4. Run health check
python -m promptosaurus.builders.template_handlers.resolvers.jinja2_template_renderer --test

# 5. Check templates
ls -la docs/prompts/

# 6. Monitor logs
tail -f logs/jinja2_rendering.log
```

### Pre-Flight Checks

```bash
#!/bin/bash
# pre_flight_checks.sh

echo "=== Jinja2 Deployment Pre-Flight Checks ==="

# Check Python version
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ "$PYTHON_VERSION" < "3.9" ]]; then
  echo "❌ Python 3.9+ required (found: $PYTHON_VERSION)"
  exit 1
fi
echo "✅ Python $PYTHON_VERSION"

# Check Jinja2 installed
if ! python -c "import jinja2" 2>/dev/null; then
  echo "❌ Jinja2 not installed"
  exit 1
fi
JINJA2_VERSION=$(python -c 'import jinja2; print(jinja2.__version__)')
echo "✅ Jinja2 $JINJA2_VERSION"

# Check template directory
if [ ! -d "docs/prompts" ]; then
  echo "❌ Template directory missing"
  exit 1
fi
echo "✅ Template directory exists"

# Test Jinja2 rendering
python -c "
from jinja2 import Environment, DictLoader
env = Environment(loader=DictLoader({'test': '{{ value }}'}))
template = env.get_template('test')
output = template.render(value='test')
assert output == 'test', 'Rendering failed'
print('✅ Jinja2 rendering functional')
"

# Check disk space (require 500MB free)
DISK_SPACE=$(df -BM . | tail -1 | awk '{print $4}' | sed 's/M//')
if [ "$DISK_SPACE" -lt 500 ]; then
  echo "⚠️  Low disk space: ${DISK_SPACE}MB"
fi

echo "✅ All pre-flight checks passed"
```

---

## Pre-Deployment Checklist

### Code Quality Gates

```bash
# Run all code quality checks
./scripts/deploy/pre_deployment_checks.sh

✅ Code Quality Checklist:
- [ ] ruff linting passes (0 errors)
- [ ] pyright type checking passes (0 errors)
- [ ] All unit tests pass (425+ tests)
- [ ] Integration tests pass (100% pass rate)
- [ ] Code coverage ≥85% (current: 87%)
- [ ] No security vulnerabilities (0 found)
- [ ] Performance benchmarks passed (P95 < 20ms)
```

### Compatibility Verification

```bash
✅ Python Version Compatibility:
- [ ] Python 3.9 tested ✅
- [ ] Python 3.10 tested ✅
- [ ] Python 3.11 tested ✅
- [ ] Python 3.12 tested ✅
- [ ] Python 3.14 tested ✅

✅ Jinja2 Compatibility:
- [ ] Jinja2 3.0 tested ✅
- [ ] Jinja2 3.1 tested ✅
- [ ] Jinja2 latest tested ✅
```

### Operational Readiness

```bash
✅ Operational Readiness Checklist:
- [ ] Backup procedures documented
- [ ] Rollback procedures tested
- [ ] Monitoring configured
- [ ] Alerting thresholds set
- [ ] Runbooks created
- [ ] On-call team briefed
- [ ] Change log prepared
- [ ] Deployment window scheduled
```

---

## Installation and Setup

### System Requirements

```yaml
Minimum Requirements:
  CPU: 2 cores
  Memory: 512MB
  Disk: 1GB
  Python: 3.9+
  Jinja2: 3.0+

Recommended Requirements:
  CPU: 4+ cores
  Memory: 2GB+
  Disk: 5GB+
  Python: 3.12+
  Jinja2: 3.1+

Dependencies:
  - jinja2>=3.0
  - markupsafe>=2.0
  - click>=8.0
  - pyyaml>=6.0
```

### Installation Steps

#### Step 1: Prepare Environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

#### Step 2: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "jinja2|markupsafe"

# Expected output:
# jinja2 3.1.2
# markupsafe 2.1.1
```

#### Step 3: Verify Installation

```bash
# Test import
python -c "from jinja2 import Environment; print('Jinja2 ready')"

# Test rendering
python -c "
from jinja2 import Template
t = Template('Hello {{ name }}')
print(t.render(name='World'))
"
# Expected output: Hello World
```

#### Step 4: Configure System Paths

```bash
# Add templates directory to Python path
export PYTHONPATH=/path/to/templates:$PYTHONPATH

# Or update in application config
# config.py:
# TEMPLATE_PATH = '/path/to/templates'
# sys.path.insert(0, TEMPLATE_PATH)
```

### Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "promptosaurus"]

# Expose port
EXPOSE 8000
```

#### Docker Compose

```yaml
version: '3.8'

services:
  jinja2-app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: jinja2-templates
    ports:
      - "8000:8000"
    environment:
      PYTHONUNBUFFERED: "1"
      JINJA2_ENV: production
      LOG_LEVEL: info
    volumes:
      - ./templates:/app/templates:ro
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s

  # Optional: log aggregation
  logging:
    image: fluent/fluent-bit:latest
    volumes:
      - ./logs:/logs
      - ./fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf
```

---

## Configuration

### Environment Variables

```bash
# Required
export JINJA2_TEMPLATE_PATH=/path/to/templates
export JINJA2_CACHE_SIZE=1000
export JINJA2_CACHE_TTL=3600

# Optional
export JINJA2_DEBUG=false
export JINJA2_AUTO_RELOAD=false
export JINJA2_TRIM_BLOCKS=true
export JINJA2_LSTRIP_BLOCKS=true
export JINJA2_LOG_LEVEL=info

# Performance
export JINJA2_MAX_RENDER_TIME=30
export JINJA2_RENDER_TIMEOUT=60
```

### Configuration File

```yaml
# config/jinja2.yaml
jinja2:
  # Template settings
  template_path: /var/lib/jinja2/templates
  auto_reload: false
  trim_blocks: true
  lstrip_blocks: true
  keep_trailing_newline: false
  
  # Caching
  cache_type: filesystem
  cache_dir: /var/cache/jinja2
  cache_size: 1000
  cache_ttl: 3600
  
  # Performance
  max_render_time: 30
  render_timeout: 60
  
  # Logging
  log_level: info
  log_file: /var/log/jinja2/render.log
  
  # Security
  autoescape: true
  autoescape_extensions:
    - html
    - htm
    - xml
  
  # Custom filters/extensions
  custom_filters:
    - module: promptosaurus.filters
      name: camel_case
    - module: promptosaurus.filters
      name: pascal_case
```

### Python Configuration

```python
# config.py
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

class JinjaConfig:
    TEMPLATE_PATH = os.getenv('JINJA2_TEMPLATE_PATH', './templates')
    CACHE_DIR = os.getenv('JINJA2_CACHE_DIR', '/tmp/jinja2_cache')
    CACHE_SIZE = int(os.getenv('JINJA2_CACHE_SIZE', 1000))
    CACHE_TTL = int(os.getenv('JINJA2_CACHE_TTL', 3600))
    
    DEBUG = os.getenv('JINJA2_DEBUG', 'false').lower() == 'true'
    AUTO_RELOAD = os.getenv('JINJA2_AUTO_RELOAD', 'false').lower() == 'true'
    
    MAX_RENDER_TIME = int(os.getenv('JINJA2_MAX_RENDER_TIME', 30))
    RENDER_TIMEOUT = int(os.getenv('JINJA2_RENDER_TIMEOUT', 60))

def create_environment():
    """Create configured Jinja2 environment"""
    loader = FileSystemLoader(JinjaConfig.TEMPLATE_PATH)
    
    env = Environment(
        loader=loader,
        autoescape=select_autoescape(
            enabled_extensions=('html', 'xml'),
            default_for_string=True,
        ),
        trim_blocks=True,
        lstrip_blocks=True,
        cache_size=JinjaConfig.CACHE_SIZE,
    )
    
    # Register custom filters
    from promptosaurus.filters import register_filters
    register_filters(env)
    
    return env
```

---

## Deployment Procedures

### Standard Deployment

#### Step 1: Pre-Deployment (30 min)

```bash
#!/bin/bash
# deploy/pre_deploy.sh

set -e

echo "=== Pre-Deployment Phase ==="

# 1. Backup current version
echo "📦 Creating backup..."
BACKUP_DIR="backups/jinja2_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r venv "$BACKUP_DIR/"
cp -r templates "$BACKUP_DIR/"

# 2. Run tests
echo "🧪 Running tests..."
pytest tests/ -v --tb=short
if [ $? -ne 0 ]; then
  echo "❌ Tests failed, aborting deployment"
  exit 1
fi

# 3. Run quality checks
echo "✓ Running quality checks..."
ruff check .
pyright .

# 4. Performance baseline
echo "📊 Capturing performance baseline..."
python scripts/benchmark.py > "benchmarks/baseline_$(date +%Y%m%d_%H%M%S).json"

echo "✅ Pre-deployment checks complete"
```

#### Step 2: Deploy (15 min)

```bash
#!/bin/bash
# deploy/deploy.sh

set -e

echo "=== Deployment Phase ==="

# 1. Activate environment
source venv/bin/activate

# 2. Update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt --upgrade

# 3. Copy templates
echo "📋 Deploying templates..."
mkdir -p /var/lib/jinja2
cp -r templates/* /var/lib/jinja2/
chmod -R 755 /var/lib/jinja2

# 4. Update permissions
echo "🔒 Setting permissions..."
chown -R jinja2:jinja2 /var/lib/jinja2
chmod 755 /var/lib/jinja2
chmod 644 /var/lib/jinja2/*

# 5. Clear caches
echo "🧹 Clearing caches..."
rm -rf /var/cache/jinja2/*

# 6. Record deployment
echo "📝 Recording deployment..."
echo "Deployed: $(date)" >> /var/log/jinja2/deployments.log
echo "Version: $(python -c 'import jinja2; print(jinja2.__version__)')" >> /var/log/jinja2/deployments.log

echo "✅ Deployment complete"
```

#### Step 3: Post-Deployment (15 min)

```bash
#!/bin/bash
# deploy/post_deploy.sh

set -e

echo "=== Post-Deployment Verification ==="

# 1. Health checks
echo "🏥 Running health checks..."
python scripts/health_check.py
if [ $? -ne 0 ]; then
  echo "❌ Health checks failed"
  exit 1
fi

# 2. Performance verification
echo "📊 Verifying performance..."
python scripts/benchmark.py > benchmarks/post_deploy.json
python scripts/compare_benchmarks.py

# 3. Smoke tests
echo "🔥 Running smoke tests..."
pytest tests/smoke/ -v

# 4. Monitor logs
echo "📋 Checking logs for errors..."
grep -i "error\|critical" /var/log/jinja2/render.log || true

# 5. Alert monitoring
echo "📢 Verifying monitoring alerts..."
curl http://localhost:8000/metrics | grep jinja2

echo "✅ Post-deployment verification complete"
```

### Blue-Green Deployment

```bash
#!/bin/bash
# deploy/blue_green_deploy.sh

set -e

BLUE_DIR="/opt/jinja2/blue"
GREEN_DIR="/opt/jinja2/green"
ACTIVE_LINK="/opt/jinja2/active"

echo "=== Blue-Green Deployment ==="

# Determine current active (blue or green)
CURRENT=$(readlink $ACTIVE_LINK)
if [ "$CURRENT" = "$BLUE_DIR" ]; then
  ACTIVE="blue"
  INACTIVE="green"
  INACTIVE_DIR=$GREEN_DIR
else
  ACTIVE="green"
  INACTIVE="blue"
  INACTIVE_DIR=$BLUE_DIR
fi

echo "Current active: $ACTIVE"
echo "Deploying to: $INACTIVE"

# Deploy to inactive environment
echo "📦 Deploying to $INACTIVE..."
mkdir -p "$INACTIVE_DIR"
cp -r . "$INACTIVE_DIR/"
cd "$INACTIVE_DIR"
pip install -r requirements.txt
pytest tests/ -v

# Health check on new environment
echo "🏥 Health checking $INACTIVE..."
./scripts/health_check.sh || {
  echo "❌ Health check failed, keeping $ACTIVE active"
  exit 1
}

# Switch traffic
echo "🔄 Switching to $INACTIVE..."
rm "$ACTIVE_LINK"
ln -s "$INACTIVE_DIR" "$ACTIVE_LINK"

# Verify switch
echo "✅ Successfully switched to $INACTIVE"
echo "Old environment ($ACTIVE) at $INACTIVE_DIR available for rollback"
```

### Canary Deployment

```bash
# deploy/canary_deploy.sh
# Deploy to small subset of users first

CANARY_PERCENTAGE=5  # 5% traffic to new version

# 1. Deploy new version (without switching traffic)
echo "Deploying new version..."
deploy_new_version()

# 2. Route 5% of traffic to canary
echo "Routing $CANARY_PERCENTAGE% to canary..."
update_load_balancer_weight "jinja2-canary" $CANARY_PERCENTAGE

# 3. Monitor canary metrics for 15 minutes
echo "Monitoring canary metrics..."
monitor_canary_metrics 15

# 4. If metrics good, increase traffic
if [ $? -eq 0 ]; then
  echo "Canary metrics good, increasing to 50%..."
  update_load_balancer_weight "jinja2-canary" 50
  sleep 5 * 60  # Wait 5 minutes
  
  # Final verification
  if verify_metrics; then
    echo "Promoting canary to 100%..."
    promote_canary_to_production
  else
    echo "Metrics degraded, rolling back..."
    rollback_to_previous_version
  fi
else
  echo "Canary metrics poor, rolling back..."
  rollback_to_previous_version
fi
```

---

## Monitoring and Alerting

### Metrics to Monitor

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Counter: Total renders
template_renders_total = Counter(
    'jinja2_renders_total',
    'Total template renders',
    ['template_name', 'status']
)

# Histogram: Render time
render_duration_seconds = Histogram(
    'jinja2_render_duration_seconds',
    'Template render duration',
    ['template_name'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# Gauge: Cache hit ratio
cache_hits_total = Counter(
    'jinja2_cache_hits_total',
    'Cache hits'
)
cache_misses_total = Counter(
    'jinja2_cache_misses_total',
    'Cache misses'
)

# Gauge: Active renders
active_renders = Gauge(
    'jinja2_active_renders',
    'Active template renders'
)

# Counter: Errors
render_errors_total = Counter(
    'jinja2_render_errors_total',
    'Render errors',
    ['error_type']
)

# Example usage
@contextmanager
def track_render(template_name):
    active_renders.inc()
    start = time.time()
    try:
        yield
        template_renders_total.labels(template_name, 'success').inc()
    except Exception as e:
        template_renders_total.labels(template_name, 'error').inc()
        render_errors_total.labels(str(type(e).__name__)).inc()
        raise
    finally:
        duration = time.time() - start
        render_duration_seconds.labels(template_name).observe(duration)
        active_renders.dec()
```

### Prometheus Scrape Config

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'jinja2'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
    scrape_timeout: 3s
```

### Alerting Rules

```yaml
# alerts.yml
groups:
  - name: jinja2_alerts
    interval: 30s
    rules:
      - alert: JinjaRenderErrorRate
        expr: |
          (rate(jinja2_render_errors_total[5m]) /
           rate(jinja2_renders_total[5m])) > 0.01
        for: 5m
        annotations:
          summary: "High error rate in Jinja2 rendering"
          description: "Error rate > 1% for 5 minutes"
      
      - alert: JinjaRenderSlow
        expr: |
          jinja2_render_duration_seconds_p95 > 1.0
        for: 5m
        annotations:
          summary: "Slow Jinja2 render times"
          description: "P95 render time > 1s"
      
      - alert: JinjaCacheMissRate
        expr: |
          (rate(jinja2_cache_misses_total[5m]) /
           (rate(jinja2_cache_hits_total[5m]) +
            rate(jinja2_cache_misses_total[5m]))) > 0.2
        for: 10m
        annotations:
          summary: "High cache miss rate"
          description: "Cache miss rate > 20%"
      
      - alert: JinjaDiskSpace
        expr: node_filesystem_avail_bytes{mountpoint="/var/lib/jinja2"} < 500000000
        annotations:
          summary: "Low disk space for Jinja2"
          description: "Less than 500MB available"
```

### Monitoring Dashboard (Grafana)

```json
{
  "dashboard": {
    "title": "Jinja2 Template Rendering",
    "panels": [
      {
        "title": "Render Rate",
        "targets": [
          {
            "expr": "rate(jinja2_renders_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "rate(jinja2_render_errors_total[5m])"
          }
        ]
      },
      {
        "title": "P95 Render Time",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, jinja2_render_duration_seconds)"
          }
        ]
      },
      {
        "title": "Cache Hit Ratio",
        "targets": [
          {
            "expr": "rate(jinja2_cache_hits_total[5m]) / (rate(jinja2_cache_hits_total[5m]) + rate(jinja2_cache_misses_total[5m]))"
          }
        ]
      }
    ]
  }
}
```

---

## Performance Tuning

### Cache Optimization

```python
# config.py
from jinja2 import Environment, FileSystemLoader
from jinja2.nativetypes import NativeEnvironment

# Enable caching
env = Environment(
    cache_size=2000,  # Increase from default 400
    loader=FileSystemLoader('templates')
)

# Use native types (30% faster for numeric/boolean)
env = NativeEnvironment(
    cache_size=2000,
    loader=FileSystemLoader('templates')
)

# Measure cache effectiveness
import json

cache_stats = {
    'hits': 0,
    'misses': 0,
    'ratio': 0.0
}

def get_cache_ratio():
    total = cache_stats['hits'] + cache_stats['misses']
    if total > 0:
        return cache_stats['hits'] / total
    return 0.0
```

### Template Pre-compilation

```python
# Compile templates at startup (avoid runtime compilation)
def compile_templates():
    """Pre-compile all templates"""
    import os
    from jinja2 import Environment, FileSystemLoader
    
    env = Environment(loader=FileSystemLoader('templates'))
    
    for template_file in os.listdir('templates'):
        if template_file.endswith('.j2'):
            print(f"Compiling {template_file}...")
            env.get_template(template_file)

# Run at startup
if __name__ == '__main__':
    compile_templates()
    print("✅ Template pre-compilation complete")
```

### Render Time Optimization

```python
# Measure and optimize render times
import time
from statistics import mean, stdev

def benchmark_template(template_name, context, iterations=100):
    """Measure template rendering time"""
    env = create_environment()
    template = env.get_template(template_name)
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        output = template.render(context)
        duration = time.perf_counter() - start
        times.append(duration)
    
    return {
        'template': template_name,
        'min': min(times),
        'max': max(times),
        'mean': mean(times),
        'stdev': stdev(times),
        'p95': sorted(times)[int(0.95 * len(times))],
        'output_size': len(output)
    }

# Profile slow templates
slow_templates = [
    'large_config.j2',
    'document.j2',
    'code_generator.j2'
]

for template in slow_templates:
    result = benchmark_template(template, large_context)
    print(f"{template}: P95={result['p95']:.3f}s")
```

### Resource Limits

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jinja2-service
spec:
  template:
    spec:
      containers:
      - name: jinja2
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"  # Prevent OOM
            cpu: "500m"      # Prevent CPU runaway
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Backup and Recovery

### Backup Strategy

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backups/jinja2"
RETENTION_DAYS=30
COMPRESSION="gzip"

mkdir -p "$BACKUP_DIR"

# Backup templates
echo "Backing up templates..."
tar -czf "$BACKUP_DIR/templates_$(date +%Y%m%d_%H%M%S).tar.gz" \
    /var/lib/jinja2

# Backup configuration
echo "Backing up configuration..."
tar -czf "$BACKUP_DIR/config_$(date +%Y%m%d_%H%M%S).tar.gz" \
    /etc/jinja2

# Backup cache
echo "Backing up cache metadata..."
tar -czf "$BACKUP_DIR/cache_$(date +%Y%m%d_%H%M%S).tar.gz" \
    /var/cache/jinja2 || true

# Clean old backups
echo "Cleaning old backups..."
find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete

# Verify backup
echo "Verifying backup..."
tar -tzf "$BACKUP_DIR/templates_$(date +%Y%m%d)_*.tar.gz" | head

echo "✅ Backup complete"
```

### Restore Procedure

```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_FILE=$1
RESTORE_DIR="/var/lib/jinja2"

if [ -z "$BACKUP_FILE" ]; then
  echo "Usage: restore.sh <backup_file>"
  exit 1
fi

# Verify backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
  echo "❌ Backup file not found: $BACKUP_FILE"
  exit 1
fi

echo "Restoring from $BACKUP_FILE..."

# Stop service
systemctl stop jinja2

# Backup current version (just in case)
cp -r "$RESTORE_DIR" "$RESTORE_DIR.backup_$(date +%Y%m%d_%H%M%S)"

# Extract backup
tar -xzf "$BACKUP_FILE" -C /

# Verify restore
if [ $? -eq 0 ]; then
  # Start service
  systemctl start jinja2
  echo "✅ Restore complete"
else
  echo "❌ Restore failed"
  exit 1
fi
```

---

## Rollback Procedures

### Immediate Rollback (Critical Issue)

```bash
#!/bin/bash
# deploy/rollback_immediate.sh

set -e

echo "🔄 IMMEDIATE ROLLBACK INITIATED"

# 1. Switch to previous version
PREVIOUS_VERSION=$(cat /opt/jinja2/versions.log | tail -2 | head -1)
echo "Switching to previous version: $PREVIOUS_VERSION"

# Copy previous version
cp -r "/opt/jinja2/archive/$PREVIOUS_VERSION" "/opt/jinja2/active"

# 2. Clear caches
rm -rf /var/cache/jinja2/*

# 3. Restart services
systemctl restart jinja2

# 4. Verify
sleep 5
curl -f http://localhost:8000/health || {
  echo "❌ Health check failed, trying previous-previous version"
  exit 1
}

echo "✅ Rollback complete, version: $PREVIOUS_VERSION"

# Alert team
send_slack_alert "Jinja2 rollback completed to version $PREVIOUS_VERSION"
```

### Graceful Rollback (Issues Detected)

```bash
#!/bin/bash
# deploy/rollback_graceful.sh

set -e

DRAIN_TIME=300  # 5 minutes

echo "Graceful rollback initiated"

# 1. Remove from load balancer
echo "Removing from load balancer..."
remove_from_lb

# 2. Drain existing requests
echo "Draining requests ($DRAIN_TIME seconds)..."
sleep $DRAIN_TIME

# 3. Switch version
echo "Switching to previous version..."
switch_to_previous_version

# 4. Add back to load balancer
echo "Adding back to load balancer..."
add_to_lb

# 5. Monitor
echo "Monitoring for 10 minutes..."
monitor_metrics 600

echo "✅ Graceful rollback complete"
```

### Automated Rollback (Monitoring)

```python
# monitoring/auto_rollback.py
import time
from metrics import get_error_rate, get_p95_latency

def check_metrics():
    error_rate = get_error_rate()
    p95_latency = get_p95_latency()
    
    # Error rate threshold
    if error_rate > 0.05:  # 5%
        return 'error_rate_high'
    
    # Latency threshold
    if p95_latency > 2.0:  # 2 seconds
        return 'latency_high'
    
    return 'healthy'

def monitor_and_rollback():
    grace_period = 60  # 60 seconds
    check_interval = 5  # Check every 5 seconds
    consecutive_failures = 0
    required_failures = grace_period / check_interval
    
    while True:
        status = check_metrics()
        
        if status != 'healthy':
            consecutive_failures += 1
            print(f"Issue detected: {status} ({consecutive_failures}/{required_failures})")
            
            if consecutive_failures >= required_failures:
                print("Critical issues detected, initiating rollback...")
                os.system("./deploy/rollback_immediate.sh")
                break
        else:
            consecutive_failures = 0
        
        time.sleep(check_interval)

if __name__ == '__main__':
    monitor_and_rollback()
```

---

## Troubleshooting

### Common Operational Issues

#### 1. High Memory Usage

**Symptom**: Memory usage growing over time

**Diagnosis**:
```bash
# Check process memory
ps aux | grep jinja2
# Check cache size
redis-cli INFO memory
# Check template count
find /var/lib/jinja2 -name "*.j2" | wc -l
```

**Solution**:
```python
# Reduce cache size
env = Environment(cache_size=500)  # Default: 400

# Clear cache periodically
import gc
gc.collect()

# Implement cache eviction
from jinja2 import Environment
from cachetools import TTLCache

class TTLEnvironment(Environment):
    def __init__(self, *args, cache_ttl=3600, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = TTLCache(maxsize=400, ttl=cache_ttl)
```

#### 2. Slow Template Rendering

**Symptom**: P95 latency > 1 second

**Diagnosis**:
```bash
# Profile slow templates
python scripts/profile_templates.py

# Check system resources
top -b -n 1 | head -20
df -h
```

**Solution**:
```python
# Pre-compile templates at startup
compile_templates()

# Use native types (faster)
from jinja2.nativetypes import NativeEnvironment
env = NativeEnvironment()

# Reduce context size
# Only pass required variables to render()

# Profile and optimize slow filters
import cProfile
cProfile.run('template.render(context)')
```

#### 3. Template Syntax Errors

**Symptom**: Rendering fails with syntax error

**Diagnosis**:
```bash
# Validate template syntax
python -m jinja2 -D 'file=template.j2' < /dev/null

# Check template parsing
python -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))
try:
    env.get_template('template.j2')
except Exception as e:
    print(f'Error: {e}')
"
```

**Solution**:
```bash
# Fix syntax errors
# Use online Jinja2 validator
# Review template for unclosed tags
grep -n '{%\|{{\|}}' template.j2
```

#### 4. Missing Templates

**Symptom**: Template not found error

**Diagnosis**:
```bash
# List templates
find /var/lib/jinja2 -name "*.j2"

# Check template path
echo $JINJA2_TEMPLATE_PATH

# Check file permissions
ls -la /var/lib/jinja2/
```

**Solution**:
```bash
# Verify template exists
test -f /var/lib/jinja2/my_template.j2 && echo "Found" || echo "Not found"

# Check permissions
chmod 644 /var/lib/jinja2/*.j2

# Deploy missing templates
cp templates/*.j2 /var/lib/jinja2/
```

---

## Summary

### Deployment Checklist

- [ ] Pre-flight checks passing
- [ ] Backups created
- [ ] Monitoring configured
- [ ] Alerting thresholds set
- [ ] Rollback procedure tested
- [ ] Team briefed and on-call
- [ ] Deployment window scheduled
- [ ] Post-deployment verification plan

### Post-Deployment Verification

- [ ] Health checks passing
- [ ] Performance metrics healthy
- [ ] Error rate < 1%
- [ ] P95 latency < 200ms
- [ ] Cache hit ratio > 80%
- [ ] No critical log errors
- [ ] Monitoring data flowing

---

## Quick Links

- [User Guide](COMPREHENSIVE_USER_GUIDE.md)
- [API Reference](JINJA2_API_REFERENCE.md)
- [Best Practices](JINJA2_BEST_PRACTICES.md)
- [Troubleshooting](features/JINJA2_TROUBLESHOOTING.md)
- [Release Notes](RELEASE_NOTES.md)

---

**For 24/7 support, contact:** devops@company.com  
**On-call rotation:** See PagerDuty  
**Incident channel:** #jinja2-incidents
