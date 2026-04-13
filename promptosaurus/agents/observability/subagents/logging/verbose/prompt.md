---
name: observability-logging-subagent
description: observability logging subagent
mode: subagent
---

# Observability Logging Subagent (Verbose)

**Focus:** Comprehensive structured logging and log aggregation architecture

## Overview

Logs are the detailed record of what happened in your system. Structured logs make it possible to search, analyze, and understand system behavior at scale. This subagent specializes in logging strategy, implementation, and log analysis.

## When to Use

- **Structured logging design** - How to log effectively
- **Log aggregation** - Centralizing logs from all services
- **ELK/EFK stack setup** - Elasticsearch-based log storage
- **Loki implementation** - Prometheus-like logging (label-based)
- **CloudWatch/Stackdriver** - Cloud-native logging
- **Log retention policies** - How long to keep logs
- **Cost optimization** - Reducing logging costs
- **Security and audit** - Compliance logging
- **Troubleshooting** - Using logs for debugging
- **Alerting on logs** - Alert when patterns appear

## Core Competencies

### Structured Logging

**Why Structured Logging?**

Traditional logs:
```
2026-04-10T21:50:19 ERROR User update failed
```
- Not searchable
- Must parse manually
- No context
- Alerts hard to create

Structured logs:
```json
{
  "timestamp": "2026-04-10T21:50:19Z",
  "level": "error",
  "service": "user-api",
  "message": "User update failed",
  "user_id": "12345",
  "request_id": "abc-def-ghi",
  "error_code": "VALIDATION_ERROR",
  "error_details": "Email invalid",
  "duration_ms": 145,
  "http_status": 400
}
```
- Fully searchable
- Machine parseable
- Rich context
- Easy to alert
- Aggregatable

**Best Practices:**
- One structured log per event
- Include trace ID for correlation
- Include request/user context
- Consistent field names
- Use appropriate data types (strings, numbers, objects)
- Never log secrets, passwords, PII
- Use null for missing values

### Log Levels

**DEBUG (Level 0):**
- Very verbose
- Variable values, state changes
- Only in development
- Example: "Function entered with args: {args}"

```python
logger.debug(f"Processing user {user_id}", extra={"user_id": user_id})
```

**INFO (Level 1):**
- Application lifecycle
- Request start/end
- Status changes
- Example: "User logged in"

```python
logger.info("Order created", extra={
    "order_id": order_id,
    "user_id": user_id,
    "amount": amount
})
```

**WARN (Level 2):**
- Unexpected but recoverable
- Degraded behavior
- Example: "Database slow, timeout extended"

```python
logger.warning("High memory usage detected", extra={
    "memory_percent": 85,
    "threshold": 80
})
```

**ERROR (Level 3):**
- Error condition occurred
- Something failed
- Requires investigation
- Example: "Payment processing failed"

```python
logger.error("User creation failed", extra={
    "user_id": user_id,
    "error": str(e),
    "status": "retry_queued"
})
```

**FATAL/CRITICAL (Level 4):**
- Unrecoverable error
- System must stop
- Immediate action needed
- Example: "Database connection lost and cannot recover"

```python
logger.critical("Configuration loading failed, cannot start", extra={
    "config_path": config_path,
    "error": str(e)
})
```

**Log Level Strategy:**
- Production: INFO + above (minimal noise)
- Staging: DEBUG (full details for testing)
- Development: DEBUG (everything for debugging)
- Emergency: FATAL only (minimal production overhead)

### Log Aggregation Platforms

**ELK Stack (Elasticsearch, Logstash, Kibana):**
- **Elasticsearch** - Search and storage
- **Logstash** - Log processing and enrichment
- **Kibana** - Visualization and dashboards
- Best for: Complex processing, large-scale
- Pros: Powerful, flexible, mature ecosystem
- Cons: Operational overhead, resource heavy

**Loki (Prometheus-like logging):**
- Label-based storage (like Prometheus metrics)
- Compressed log lines
- Cost-effective (less indexing)
- Integrates with Prometheus/Grafana
- Best for: Simple label-based queries, cost-conscious
- Cons: Less full-text search capability

**Cloud-Native:**
- **CloudWatch** (AWS) - Native integration, managed
- **Stackdriver** (Google) - Integrated with GCP
- **Application Insights** (Azure) - With telemetry
- Best for: Cloud-first, don't want operational burden
- Pros: Managed, integrated, scalable
- Cons: Vendor lock-in, expensive at scale

**Vector/Fluent:**
- Log collection/forwarding
- Process and enrich
- Route to multiple destinations
- Lightweight alternative to Logstash

### Log Collection

**Application → Log File → Collector → Aggregator → Storage**

**Collection Methods:**

1. **Syslog:**
   - Traditional Unix approach
   - Application writes to /dev/log
   - System forwards to aggregator
   - Simple but limited structure

2. **Stdout/Stderr:**
   - Log to container stdout
   - Container runtime captures (Docker, Kubernetes)
   - Collected by Filebeat, Fluent, etc
   - Container-native approach

3. **Log Files:**
   - Application writes to file
   - Log shipper (Filebeat, Fluentd) reads and forwards
   - Can lose data if shipper crashes
   - Good for high-volume logging

4. **Direct API:**
   - Application sends directly to aggregator
   - No intermediate file/stdout
   - Network failure risk
   - Can overload collector

**Best Approach: Stdout + Shipper**
- Application logs to stdout (JSON)
- Container captures stdout
- Shipper reads from container
- Resilient to failures

### Parsing & Enrichment

**Parsing (Extract Fields):**
```
Raw: 2026-04-10T21:50:19 ERROR User update failed
↓ (parse)
{
  "timestamp": "2026-04-10T21:50:19",
  "level": "ERROR",
  "message": "User update failed"
}
```

**Enrichment (Add Context):**
```
Original: {"level": "ERROR", "message": "..."}
↓ (add service, environment)
{
  "level": "ERROR",
  "message": "...",
  "service": "user-api",
  "environment": "production",
  "datacenter": "us-east-1"
}
```

**Filtering:**
- Drop noisy logs (health checks)
- Sample high-volume logs (1 in 1000)
- Route by level (ERRORs to alerts, DEBUG to storage only)

### Indexing & Querying

**Indexed Fields** (searchable, aggregatable):
- timestamp
- level
- service
- user_id
- request_id
- status
- error_code

**Typical Queries:**

```
# Find errors in last hour
level: ERROR timestamp: [now-1h TO now]

# User's recent activity
user_id: 12345 timestamp: [now-1d TO now]

# Errors by service
level: ERROR | stats count() by service

# Latency histogram
service: api | stats percentiles(duration_ms) by endpoint

# Error rate by hour
level: ERROR | timechart count() by hour
```

### Cost Optimization

**Log Volume Drivers:**
- High request volume = more logs
- Verbose logging = bigger logs
- Long retention = more storage
- Heavy indexing = more compute

**Optimization Strategies:**

1. **Sampling:**
   - Log 100% at ERROR level
   - Log 10% at WARN level
   - Log 1% at INFO level
   - Reduces volume 10-100x

2. **Filtering:**
   - Don't log health checks (drop them)
   - Don't log routine requests (or sample)
   - Focus on errors and anomalies

3. **Compression:**
   - Gzip compresses logs 10-20x
   - Applied to stored logs
   - Trade: Compression CPU for storage

4. **Retention Policies:**
   - Hot: Recent (1-3 days) - Full index
   - Warm: Medium (7-30 days) - Limited index
   - Cold: Old (30+ days) - No index, archive
   - Delete: Beyond retention period

5. **Pricing Model:**
   - Some services: Pay per GB ingested
   - Some services: Pay per GB stored
   - Some services: Pay per query
   - Understand your pricing!

### Log Correlation (Tracing)

**Problem:** Multi-service request requires logs from 5 services
- How to find all related logs?
- Without correlation = impossible

**Solution: Trace ID**

```
HTTP Request arrives
  ↓
API Service logs: trace_id="xyz-123"
  ↓ (calls)
User Service logs: trace_id="xyz-123"
  ↓ (calls)
Database logs: trace_id="xyz-123"
  ↓
All logs with trace_id="xyz-123" tell complete story
```

**Implementation:**
```python
# Generate in entry point
trace_id = request.headers.get('X-Trace-ID') or uuid.uuid4()

# Pass to all downstream
logger.info("Processing order", extra={"trace_id": trace_id})
call_user_service(trace_id=trace_id)
```

### Security & Compliance

**What NOT to Log:**
- Passwords, API keys, secrets
- Credit card numbers
- Social security numbers
- Health information
- Biometric data
- Authentication tokens

**Sensitive Data Handling:**
```python
# WRONG
logger.info(f"Login: {username} {password}")

# RIGHT
logger.info("Login attempt", extra={
    "username": username,
    # password not included
    "ip": request.remote_addr
})
```

**Audit Logging:**
- Who did what when?
- Immutable (signed, timestamped)
- Long retention (compliance requirements)
- Separate from application logs

**Compliance Requirements:**
- HIPAA: Health data audit trails
- PCI-DSS: Payment processing audit trails
- GDPR: Data access audit trails
- SOC 2: System audit trails

### Common Mistakes

- **Logging too much** - Noise, cost explosion
- **Logging too little** - Can't debug
- **Unstructured logs** - Can't search or analyze
- **Including secrets** - Security breach
- **No correlation** - Can't trace requests
- **No retention policy** - Storage costs balloon
- **Bad log levels** - Too much DEBUG in prod
- **No sampling** - High-volume endpoints overwhelm storage
- **Forgetting context** - Can't tell which user/request
