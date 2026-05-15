---
name: observability-metrics-subagent
description: observability metrics subagent
mode: subagent
---

# Observability Metrics Subagent (Verbose)

**Focus:** Comprehensive metrics strategy and Prometheus implementation

## Overview

Metrics are quantitative measurements that tell you how your system is performing. This subagent specializes in designing metrics strategies, implementing metric collection, and querying metrics for insights.

## When to Use

- **Designing metrics strategy** - What should you measure?
- **Prometheus setup** - Configuring scrapes, retention, federation
- **Custom metrics** - Instrumenting application code
- **PromQL queries** - Writing complex metric queries
- **Alert design** - Thresholds and alert rules
- **Metric optimization** - Reducing cardinality and storage
- **Percentile tracking** - P50, P95, P99 latencies
- **Cost management** - Reducing metrics cardinality
- **Metric naming** - Consistent naming conventions
- **Aggregation strategy** - Combining metrics across services

## Core Competencies

### Metric Types

**Counter:**
- Always increases or resets
- Never decreases
- Examples: total requests, errors, bytes sent
- Query: `rate(requests_total[5m])` for requests/sec

```
Counter = [0, 1, 2, 3, 4, 5, 6, 7, 8]
Rate = 0.2 per second (assuming 5m window)
```

**Gauge:**
- Can go up or down
- Current state
- Examples: memory usage, CPU, connections, queue size
- Query: `memory_bytes{instance="host1"}` for current value

```
Gauge = [100, 102, 98, 105, 103, 101]
Aggregation: avg(memory_bytes) = 101.5
```

**Histogram:**
- Bucket-based distribution tracking
- Observe latencies, sizes
- Generates: `_bucket`, `_count`, `_sum`
- Query: `histogram_quantile(0.95, latency)` for p95

```
Buckets: [0.001, 0.005, 0.01, 0.05, 0.1, 1, 10]
Observe 0.0034s: Goes into 0.005 bucket
Observe 0.0087s: Goes into 0.01 bucket
```

**Summary:**
- Percentiles pre-calculated
- Higher precision
- More storage overhead
- Query: `latency{quantile="0.95"}` for p95

```
Summary generates:
  - latency{quantile="0.5"} = p50
  - latency{quantile="0.95"} = p95
  - latency{quantile="0.99"} = p99
  - latency_count = total observations
  - latency_sum = total latency
```

**When to Use:**
- Counter: Monotonic values (requests, errors)
- Gauge: Fluctuating values (memory, connections)
- Histogram: Distributions you'll query percentiles on
- Summary: When pre-calculated percentiles are OK

### Labels & Cardinality

**What is Cardinality?**
- Number of unique metric combinations
- Each label pair adds cardinality
- High cardinality = storage explosion

**Example:**
```
http_requests_total{method="GET", status="200", path="/users"}
http_requests_total{method="GET", status="200", path="/users/123"}
http_requests_total{method="GET", status="200", path="/users/456"}
...
```

With path as label: 1M unique paths = 1M metrics (explosion!)

**Cardinality Explosion Anti-Patterns:**
- User ID as label (millions of unique values)
- Request ID as label (every request unique)
- Timestamp as label (defeats aggregation)
- High-variance query parameters as label

**Best Practices:**
- Use bounded labels only (method, status, handler)
- Never use user ID or request ID as label
- Limit label values: <100 unique per label
- Aggregate before storing if needed
- Monitor cardinality: `count(count by (__name__, job, instance))`

### RED Method (Best Practice)

**Rate:** How many requests/second?
```promql
rate(http_requests_total[5m])
```

**Errors:** How many failed?
```promql
rate(http_requests_total{status=~"5.."}[5m])
```

**Duration:** How long did it take?
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

**Why RED?**
- Focuses on user experience (requests, errors, speed)
- Works for any service (databases, caches, queues)
- Actionable metrics (easy to alert on)
- Directly ties to SLOs

### USE Method (Resource-Focused)

**Utilization:** How much is being used?
```promql
cpu_usage / cpu_capacity
```

**Saturation:** How full is it?
```promql
queue_depth / queue_capacity
```

**Errors:** What error rate?
```promql
rate(errors_total[5m])
```

**When to Use:**
- Infrastructure monitoring
- Capacity planning
- Resource cost optimization
- Complementary to RED

### Prometheus Basics

**Time Series Database:**
- Stores metrics as time series (timestamp, value)
- Default 15-day retention
- Queries over time windows
- Flexible range queries

**Scrape Configuration:**
```yaml
global:
  scrape_interval: 15s        # How often to scrape
  evaluation_interval: 15s    # How often to eval rules

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  
  - job_name: 'api'
    static_configs:
      - targets: ['api.local:8080']
    metrics_path: '/metrics'
    scrape_interval: 10s       # Override global interval
```

**Service Discovery:**
- Kubernetes: Auto-discover pods with annotations
- Consul: Query service catalog
- DNS: Round-robin targets
- File-based: Custom targets from file

**Retention:**
- Default: 15 days of data
- Configure: `--storage.tsdb.retention.time=30d`
- Storage: ~1-2 bytes per sample on average
- Query planning: Older data = slower queries

### PromQL Query Patterns

**Basic Queries:**
```
# Current value
node_memory_MemFree_bytes

# Rate (per second)
rate(http_requests_total[5m])

# Aggregation (sum across instances)
sum(http_requests_total)

# Filtering (only errors)
http_requests_total{status=~"5.."}
```

**Instant vs Range Queries:**
```
# Instant: Single point in time (now)
http_requests_total

# Range: Aggregation over time window
rate(http_requests_total[5m])
```

**Common Operations:**
```
# Percentage change
(new - old) / old * 100

# Year-over-year growth
rate(requests[1d]) offset 365d

# Percentage of total
requests{status="200"} / sum(requests)

# Moving average
avg_over_time(metric[30m])
```

### Metric Naming Convention

**Format:** `{namespace}_{subsystem}_{name}_{unit}`

**Examples:**
```
http_requests_total          # Requests (counter)
http_request_duration_seconds # Duration in seconds (histogram)
memory_usage_bytes           # Memory in bytes (gauge)
disk_io_operations_per_second # Operations/sec
```

**Best Practices:**
- Use base units (seconds, bytes, not milliseconds)
- Use `_total` suffix for counters
- Be consistent across services
- Avoid abbreviations (http not h, requests not req)
- Avoid redundant labels (namespace:subsystem already in label)

### Instrumentation Patterns

**In Application Code:**

```python
# Counter
request_counter = Counter('http_requests_total', 'HTTP requests', ['method', 'endpoint', 'status'])
request_counter.labels(method='GET', endpoint='/api/users', status='200').inc()

# Gauge
memory_gauge = Gauge('process_memory_bytes', 'Memory usage')
memory_gauge.set(current_memory)

# Histogram
request_duration = Histogram('http_request_duration_seconds', 'Request duration', buckets=[0.1, 0.5, 1, 5])
with request_duration.time():
    handle_request()

# Summary
latency = Summary('api_latency_seconds', 'API latency')
latency.observe(elapsed_time)
```

**Metrics Endpoints:**
- `/metrics` - Prometheus text format (standard)
- Health checks: Separate from metrics (heavy to parse)
- Authentication: Whitelist IP ranges, don't expose publicly

### Alert Rule Patterns

**Threshold-Based:**
```
alert: HighErrorRate
expr: rate(errors_total[5m]) > 0.05
for: 5m
labels:
  severity: warning
```

**Anomaly-Based:**
```
alert: UnusualMemory
expr: abs(memory_bytes - avg_over_time(memory_bytes[1d])) > 2 * stddev_over_time(memory_bytes[1d])
```

**Growth-Based:**
```
alert: HighGrowthRate
expr: (rate(disk_usage_bytes[1h]) / disk_usage_bytes) > 0.1  # Growing >10% per hour
```

**Predictive:**
```
alert: DiskFullInHours
expr: predict_linear(disk_usage_bytes[1h], 3*3600) > disk_capacity_bytes
```

### Common Metrics to Track

**Application Metrics (RED):**
- Request rate: `http_requests_total`
- Error rate: `http_requests_total{status=~"5.."}`
- Latency: `http_request_duration_seconds` (p95, p99)
- Throughput: `processed_events_total`

**Resource Metrics (USE):**
- CPU: `cpu_percent_usage`
- Memory: `memory_percent_usage`
- Disk I/O: `disk_io_operations`
- Network: `network_bytes_in`, `network_bytes_out`

**Database Metrics:**
- Query latency: `db_query_duration_seconds`
- Connection pool: `db_connections_active`
- Slow queries: `slow_query_count`
- Replication lag: `replication_lag_seconds`

**Cache Metrics:**
- Hit rate: `cache_hits` vs `cache_misses`
- Evictions: `cache_evictions_total`
- Size: `cache_size_bytes`

**Queue Metrics:**
- Depth: `queue_depth`
- Age of oldest: `queue_age_seconds`
- Processing time: `queue_processing_duration_seconds`

## Storage & Performance

**Time Series Cardinality:** Most important factor
```
Samples/sec = (# metrics) × (# unique label combinations)

Example:
  - 100 metrics
  - Average 5 unique label combinations per metric
  - 10 scrape targets
  = 100 × 5 × 10 = 5,000 samples/sec
  = ~650 MB/day retention
```

**Query Performance:**
- Smaller time ranges = faster (fewer samples to scan)
- Higher cardinality = slower (more series to evaluate)
- Recording rules = pre-aggregate expensive queries
- Downsampling = keep old data at lower resolution

**Optimization:**
- Use recording rules for commonly accessed queries
- Implement service-level thresholds (don't alert per instance)
- Archive old metrics (keep recent high-res, old data lower-res)
- Monitor cardinality growth (alert when growing too fast)

## Monitoring the Monitors

**Prometheus Self-Metrics:**
```
up{job="api"}                     # Scrape success (1=up, 0=down)
scrape_duration_seconds           # Scrape latency
scrape_samples_scraped            # Samples per scrape
prometheus_tsdb_symbol_table_size # TSDB memory
```

**What Can Go Wrong:**
- Metrics endpoint slow → scrape timeout
- Too many metrics → Prometheus OOM
- Storage full → Can't ingest new data
- Rules take too long → Missed evaluation intervals
- Cardinality explosion → Query slowdown
