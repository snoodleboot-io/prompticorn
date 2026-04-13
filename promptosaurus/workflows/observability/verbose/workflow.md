---
name: "observability"
description: "Complete monitoring stack design covering metrics, logging, tracing, and alerting with dashboards and runbooks"
version: "1.0"
languages: ["python", "promql"]
subagents: ["observability/metrics", "observability/logging", "observability/tracing", "orchestrator"]
---

# Observability Workflow (Verbose)

## Purpose
Design and implement comprehensive observability infrastructure providing metrics, logs, and traces to understand system behavior, detect issues, and respond rapidly to incidents.

## When to Use This Workflow
- Building new monitoring system from scratch
- Expanding observability to new services
- Migrating from one monitoring tool to another
- Improving observability maturity (ad-hoc → comprehensive)
- Preparing for production launch
- Responding to monitoring gaps after incident

## Prerequisites
- List of services/systems to monitor
- SLO/SLA targets for each system
- Budget for monitoring tools and infrastructure
- Team expertise in metrics, logging, and tracing
- Incident response procedures in place

---

## Steps

### 1. Define Observability Goals

**Goal:** Align on what "good observability" means for your organization.

#### 1.1 Identify Systems & Dependencies

```
Service topology:
  API Gateway → Auth Service → User Database
            ↓
         Payment Service → Stripe API
            ↓
         Order Service → Order Database

Observability questions:
- What happens when Auth Service is slow?
- What happens when Payment Service fails?
- How do latencies cascade through services?
- Can we detect degradation before users complain?
```

#### 1.2 Define Health Indicators

```
System health checklist:

API Gateway:
✓ Request rate (requests/second)
✓ Latency (p50, p95, p99)
✓ Error rate (% of requests returning 5xx)
✓ Active connections
✓ Memory usage
✓ Disk I/O

Database:
✓ Query latency (p95)
✓ Query count
✓ Slow queries (>100ms)
✓ Connection pool usage
✓ Disk space
✓ Replication lag

Business Metrics:
✓ Active users (concurrent)
✓ Orders per minute
✓ Revenue per hour
✓ Conversion rate (checkout completed / cart created)
✓ Customer satisfaction
```

#### 1.3 Detection Targets

What problems must we detect automatically (not waiting for user complaints)?

```
Priority 1 (Must detect in <1 minute):
- Database down or responding slowly (>5s)
- API returning 5xx errors >1% of traffic
- Service restart/deployment (expected vs unexpected)

Priority 2 (Must detect in <5 minutes):
- Latency increase >50% (p95)
- Error rate increase (2% → 5%)
- Dependency service degradation
- Memory growth indicating leak

Priority 3 (Should detect in <1 hour):
- Slow queries degrading performance
- Disk space filling up
- TLS certificate expiring soon
- Traffic anomaly (unusual pattern)
```

#### 1.4 Target SLOs/SLAs

```
API Service Target SLO:
- Availability: 99.95% (maximum 22 minutes downtime/month)
- Latency: p95 < 200ms (95% of requests answer in <200ms)
- Error rate: <0.1% (99.9% of requests succeed)

Budget:
- Downtime allowed: 22 minutes/month
- Users willing to tolerate failures: 0.1%
- Incident response time: <5 minutes
```

---

### 2. Design Metrics Strategy

**Goal:** Choose metrics infrastructure and plan key metrics.

#### 2.1 Tool Selection

```
Metrics Tools Comparison:

Prometheus (Open Source)
- Pros: Free, powerful query language, works great at scale
- Cons: Requires operational expertise, limited retention
- Good for: Tech-forward teams, cloud-native apps

Grafana Cloud / Datadog
- Pros: Managed service, easy to use, built-in dashboards
- Cons: Expensive ($15-30/month per 1K metrics)
- Good for: Teams wanting turnkey solution

CloudWatch (AWS)
- Pros: Native AWS integration, minimal setup
- Cons: Limited PromQL, expensive custom metrics
- Good for: AWS-only teams

Choice for this example: Prometheus + Grafana (open source)
```

#### 2.2 Key Metrics Design

**RED Method (Request-driven services):**
```
1. Rate: Requests per second
   Metric: http_requests_total (counter)
   Label: service, method, path
   
   Query: rate(http_requests_total[5m])
   Alert: rate() > 1000/sec → possible DDoS or bug

2. Errors: Failed requests
   Metric: http_requests_total{status="5xx"} (counter)
   
   Query: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
   Alert: error_rate > 1% → need investigation

3. Duration (Latency): Request latency
   Metric: http_request_duration_seconds (histogram)
   Buckets: 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1
   
   Query: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   Alert: p95_latency > 500ms → performance issue
```

**USE Method (Resource-driven components):**
```
1. Utilization: Resource usage %
   Metric: container_memory_usage_bytes / container_spec_memory_limit_bytes
   Alert: >80% → risk of OOM

2. Saturation: Queue depth, connection pool usage
   Metric: db_connection_pool_available / db_connection_pool_size
   Alert: <10% available → connection exhaustion risk

3. Errors: Failed operations
   Metric: db_query_errors_total (counter)
   Alert: error_rate > 0.1% → database issues
```

#### 2.3 Cardinality Management

**Good cardinality (bounded):**
```
Labels with fixed values:
- service: [api, auth, payment, order] (4 values)
- method: [GET, POST, PUT, DELETE] (4 values)
- region: [us-east, us-west, eu-west] (3 values)

Result: 4 * 4 * 3 = 48 metric combinations
Cost: Manageable
```

**Bad cardinality (unbounded):**
```
Customer ID as label:
- customer_id: [1, 2, 3, ..., 1000000] (1M values)

Result: Causes cardinality explosion
Cost: Prometheus OOM, query slowdown
Fix: Remove customer_id label, or aggregate into buckets
```

#### 2.4 Retention & Aggregation

```
Raw metrics: 15-second precision, 14 days retention
- Storage: ~100GB/day
- Cost: Database: $0.50/day

Hourly aggregates: 1-hour precision, 1 year retention
- Storage: ~1GB/day
- Cost: Database: $0.05/day

Archive (nightly): Daily summaries for compliance/audit
- Storage: Minimal
- Cost: Object storage: $0.01/day

Total cost: ~$0.56/day for 1 year of history
```

---

### 3. Plan Logging Infrastructure

**Goal:** Design log aggregation and retention strategy.

#### 3.1 Structured Logging

```json
// BAD (unstructured)
"2026-04-10 14:30:45 User 123 created order 456 for $99.99"

// GOOD (structured with context)
{
  "@timestamp": "2026-04-10T14:30:45.123Z",
  "level": "INFO",
  "service": "order-service",
  "trace_id": "abc123def456",
  "user_id": "123",
  "order_id": "456",
  "amount": 99.99,
  "currency": "USD",
  "message": "Order created successfully",
  "duration_ms": 145,
  "database": "orders_db",
  "region": "us-east-1"
}
```

#### 3.2 Log Levels & Sampling

```
INFO: Normal operations (order created, user logged in)
- Sampling: All in production
- Retention: 30 days
- Volume: ~1GB/day

WARN: Unusual but handled (retry attempt, timeout recovered)
- Sampling: All events
- Retention: 90 days
- Volume: ~100MB/day

ERROR: Issues needing attention (API failed, query error)
- Sampling: All events
- Retention: 1 year
- Alerts: Yes

DEBUG: Development only (variable values, function entry/exit)
- Sampling: In non-prod only
- Retention: 7 days
- Volume: ~5GB/day

Cost estimate:
- INFO + WARN + ERROR: ~1.1GB/day × $0.30/GB = $0.33/day
- All with DEBUG: ~6GB/day × $0.30/GB = $1.80/day
```

#### 3.3 Log Correlation

```
Single request flow:

Client → API Gateway → Auth Service → Order Service → Database
trace_id: "abc123def456" (same across all services)

Service logs:
API Gateway: "Received POST /orders trace_id=abc123def456"
Auth Service: "Validating token trace_id=abc123def456"
Order Service: "Creating order trace_id=abc123def456"
Database: "INSERT order trace_id=abc123def456"

Benefits:
- Can follow single request across all services
- Understand request latency breakdown
- Diagnose where delay occurred
```

---

### 4. Design Distributed Tracing

**Goal:** Understand end-to-end request flow and latencies.

#### 4.1 Tracing Architecture

```
Request Path with Traces:

User Request
  ↓ (create root span: "POST /orders")
API Gateway
  ├─ span: "validate-auth" (10ms)
  ├─ span: "route-request" (2ms)
  └─ calls Order Service
      ↓ (child span: "create-order")
      Order Service
        ├─ span: "validate-input" (5ms)
        ├─ span: "calculate-price" (20ms)
        └─ calls Database
            ↓ (child span: "insert-order")
            Database
              └─ span: "INSERT" (30ms)

Total latency: 67ms
Breakdown visible in trace visualization
```

#### 4.2 Sampling Strategy

```
Always sample (100%):
- Failed requests (errors, status 5xx)
- High-latency requests (p99, >5 second)
- Special requests (admin operations, large transactions)

Adaptive sampling:
- Peak traffic: Sample 0.1% (1 in 1000 requests)
- Off-peak: Sample 10% (1 in 10 requests)
- Incident/debugging: Sample 100%

Cost estimate:
- 100K requests/second
- 1% sample rate: 1K traces/sec
- Cost: ~$50/month for 2.6B traces
```

---

### 5. Set Up Alerting Rules

**Goal:** Detect problems and notify team automatically.

#### 5.1 Alert Rule Categories

```
Threshold-Based:
- API latency p95 > 500ms
- Error rate > 1%
- CPU > 80%

Anomaly-Based:
- Request rate 3x higher than normal
- Error rate doubled from baseline
- Disk fill rate suggests full in 24 hours

Composition:
- AND: Both conditions true (specific issues)
- OR: Either condition true (broadly relevant)
```

#### 5.2 Alert Routing

```
Alert: API Error Rate > 1%
├─ Severity: CRITICAL
├─ Service: api-service
├─ Route to: #api-oncall (Slack)
│          pagerduty/api-oncall (page engineer)
│          ops@company.com (email)
└─ Runbook: docs/runbooks/api-error-rate.md

Alert: Disk Space > 80%
├─ Severity: WARNING
├─ Service: database
├─ Route to: #infrastructure (Slack)
│          ops@company.com (email)
└─ Runbook: docs/runbooks/disk-space-low.md
```

#### 5.3 Alert Fatigue Prevention

```
Problem: Too many alerts
- Team ignores all alerts
- Real issues missed in noise
- On-call burnout

Solution: Smarter alerting
- Increment alert based on correlation
  One host having high CPU = noise
  All hosts having high CPU = real issue
  
- Use deduplication/grouping
  Same alert condition = group into one
  
- Adjust thresholds
  Error rate threshold too sensitive?
  Increase from 0.5% to 1%
  
- Use multiple conditions
  CPU > 80% AND memory > 80% AND request_queue_growing
  → More specific, less false positives
```

---

### 6. Build Dashboards

**Goal:** Provide visualization for rapid troubleshooting.

#### 6.1 Service Overview Dashboard

```
API Service Health (at a glance)

Request Metrics:
├─ Rate: 1,234 req/sec ↑ (10% from average)
├─ Latency (p95): 145ms → (baseline 100ms)
├─ Error Rate: 0.08% ← (within SLO <0.1%)

Resource Usage:
├─ CPU: 65% average
├─ Memory: 78% (warning: >80% is alert)
├─ Disk: 45%

Dependencies:
├─ Database: ✓ Healthy (p95 latency: 30ms)
├─ Auth Service: ✓ Healthy
├─ Payment Service: ⚠ Slow (p95 latency: 450ms, usually 200ms)
└─ Cache: ✓ Healthy (hit rate: 92%)

Alerts:
⚠ Payment Service Latency High (2m ago)
  Action: Investigating with on-call engineer
```

#### 6.2 Performance Investigation Dashboard

```
When API latency is high (p95 > 500ms):

Where's the latency?
├─ Client → Server: 50ms (network)
├─ Server processing: 300ms ← SLOW!
│  ├─ Auth validation: 100ms
│  ├─ Business logic: 80ms
│  └─ Database query: 120ms ← SLOWEST!
└─ Server → Client: 50ms (network)

Database query analysis:
├─ Query: SELECT * FROM orders WHERE customer_id = ?
├─ Execution time: 120ms (usually 20ms)
├─ Scanned rows: 500K (table is 5M rows)
├─ Missing index? customers.customer_id not indexed
└─ Recommendation: Add index to customer_id column
```

---

### 7. Establish Runbooks

**Goal:** Enable team to debug and fix issues rapidly.

#### 7.1 Runbook Structure

```
Title: API Latency High (p95 > 500ms)

Severity: CRITICAL
Audience: On-call API engineer
Expected resolution time: <15 minutes

Symptoms:
- Alert: p95 latency > 500ms
- User reports: "requests are slow"
- Dashboard: Latency spike on timeline

Diagnosis (decision tree):
1. Check database latency
   - Is DB responding normally? (p95 < 50ms)
   - Yes → Database not the issue, continue
   - No → Skip to database troubleshooting

2. Check external dependency latency
   - Is Payment Service responding? (<200ms p95)
   - Yes → Dependency not the issue
   - No → Page Payment Service on-call

3. Check request rate
   - Is traffic unusually high? (compare to baseline)
   - Yes → Scale up instances or rate-limit
   - No → Application issue, continue

Remediation:
- Step A: Add database index if identified
- Step B: Scale up API instances (add 5 replicas)
- Step C: Enable request caching for 5 minutes
- Step D: If nothing works → rollback last deployment

Verification:
- [ ] p95 latency back to <200ms
- [ ] Error rate unchanged (no degradation)
- [ ] No user complaints reported
```

---

## Common Pitfalls

- **Monitoring but not acting:** Alerts go off, team ignores → issues escalate
- **Too many alerts:** Alert fatigue leads to missed critical issues
- **Poor dashboard UX:** Team can't quickly understand system health
- **Metrics without context:** High CPU% but don't know why (batch job? leak?)
- **Incomplete traces:** Can't see cross-service latency breakdown
- **Logs without structure:** Searching logs is impossible at scale

## Success Criteria

- ✓ All critical systems have metrics, logs, and traces
- ✓ Team detects issues <1 minute after they occur
- ✓ Can investigate and remediate issue in <15 minutes
- ✓ Dashboards show system health at a glance
- ✓ Runbooks enable team to self-serve (no expert needed)
- ✓ Alert accuracy >95% (false positive rate <5%)
- ✓ Observability cost is <5% of infrastructure cost
- ✓ Team confident in system reliability
