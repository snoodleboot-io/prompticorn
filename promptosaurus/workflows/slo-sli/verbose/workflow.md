---
name: slo-sli
description: "Comprehensive SLO/SLI framework for defining reliability targets, measuring performance, and managing error budgets"
version: "1.0"
languages: ["promql", "sql"]
subagents: ["observability/metrics", "orchestrator"]
---

# SLO/SLI Workflow (Verbose)

## Purpose
Establish and track service level objectives (SLOs) to define reliability targets, measure actual performance through SLI indicators, and manage error budgets to balance feature velocity with reliability.

## When to Use This Workflow
- Launching new service to production
- Improving reliability practices
- Negotiating service agreements with customers
- Setting incident response priorities
- Balancing development velocity with stability
- Tracking progress toward reliability goals

## Prerequisites
- Understanding of service capabilities
- Historical performance data
- Business requirements for reliability
- Team commitment to SLO accountability
- Observability infrastructure (metrics, logging)

---

## Steps

### 1. Define Business Targets (SLOs)

**Goal:** Align on reliability targets that matter for business.

#### 1.1 Availability SLO

```
Availability = Successful Requests / Total Requests

Examples by industry/type:

Internal Tools: 99.0% (7.2 hours downtime/month acceptable)
├─ Justification: Can be managed during business hours
├─ Users: 50 internal employees
├─ Impact: Productivity reduced, not revenue

SaaS Platform: 99.9% (43 minutes downtime/month)
├─ Justification: Standard for modern SaaS
├─ Users: 10K paying customers
├─ Impact: Customer churn if reliability poor

Financial System: 99.99% (4 minutes downtime/month)
├─ Justification: Money involved, regulatory requirements
├─ Users: 1000 traders
├─ Impact: Legal liability, fines

Critical Infrastructure: 99.999% (26 seconds downtime/month)
├─ Justification: Public safety depends on it
├─ Impact: Severe: Lives at risk

Selection process:
1. Ask business: What availability do customers expect?
2. Check competitors: Are they 99.9%?
3. Analyze cost: Each 9 = 10x more expensive
4. Commit: Make it a team goal
```

#### 1.2 Latency SLO

```
Latency = Request completion time (p50, p95, p99)

Design guidelines:

p50 (Median): Typical user experience
└─ API: <100ms
└─ Website: <1s
└─ Mobile app: <2s

p95 (95th percentile): "Bad day" users
└─ API: <200ms (2x median, accounts for tail latency)
└─ Website: <2s
└─ Mobile app: <4s

p99 (99th percentile): Worst 1% of users
└─ API: <500ms (allows for worst-case scenarios)
└─ Website: <5s
└─ Mobile app: <10s

Example SLO:
API Service Latency SLO:
├─ p50: < 50ms
├─ p95: < 200ms ← Usually tracked in SLO
└─ p99: < 500ms (informational, not SLO)
```

#### 1.3 Error Rate SLO

```
Error Rate = (Failed Requests / Total Requests) × 100%

Examples:

99% availability = 0.1% error rate allowed
├─ In 1 million requests: 1,000 failures acceptable

99.9% availability = 0.01% error rate allowed
├─ In 1 million requests: 100 failures acceptable

99.99% availability = 0.001% error rate allowed
├─ In 1 million requests: 10 failures acceptable

Selection:
```

#### 1.4 Service-Level SLOs Matrix

```
Service Reliability Targets

┌─────────────┬────────────────┬──────────┬─────────────┐
│ Service     │ Availability   │ Latency  │ Error Rate  │
├─────────────┼────────────────┼──────────┼─────────────┤
│ API Service │ 99.9%          │ <200ms   │ <0.1%       │
│ Database    │ 99.95%         │ <50ms    │ <0.05%      │
│ Auth        │ 99.95%         │ <100ms   │ <0.05%      │
│ Cache       │ 99.0%          │ <10ms    │ <1%         │
│ Queue       │ 99.9%          │ <1s      │ <0.1%       │
└─────────────┴────────────────┴──────────┴─────────────┘
```

---

### 2. Choose SLI Metrics

**Goal:** Select measurable indicators to track SLO compliance.

#### 2.1 SLI Categories

**Request Success SLI:**
```
SLI = (requests with status 2xx or 3xx) / total requests

Measurement:
SELECT 
  SUM(CASE WHEN status IN (200,201,204,301,302,304) THEN 1 ELSE 0 END) as successful,
  COUNT(*) as total,
  ROUND(100.0 * SUM(CASE WHEN status IN (...)) / COUNT(*), 2) as success_rate
FROM requests
WHERE timestamp > NOW() - INTERVAL 5 MINUTE;

Target: success_rate >= 99.9%
Alert: success_rate < 99.8% (trending toward SLO breach)
```

**Latency SLI:**
```
SLI = requests completing within latency threshold / total

Measurement (Prometheus):
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
) <= 0.2  # 200ms threshold

Target: p95_latency <= 200ms
Alert: p95_latency > 150ms (trending toward breach)
```

**Completeness SLI:**
```
SLI = records successfully processed / records expected

Example (data pipeline):
SELECT 
  COUNT(CASE WHEN status = 'success' THEN 1 END) as processed,
  COUNT(CASE WHEN status = 'expected' THEN 1 END) as expected,
  100.0 * COUNT(CASE WHEN status = 'success' THEN 1 END) / 
    COUNT(CASE WHEN status = 'expected' THEN 1 END) as completion_rate
FROM processed_records
WHERE date = CURRENT_DATE;

Target: completion_rate >= 99.9%
Alert: completion_rate < 99.8%
```

**Freshness SLI:**
```
SLI = (data available within max age) / (total data)

Example:
SELECT 
  COUNT(CASE WHEN age_minutes <= 60 THEN 1 END) as fresh,
  COUNT(*) as total,
  100.0 * COUNT(CASE WHEN age_minutes <= 60 THEN 1 END) / COUNT(*) as freshness
FROM data_warehouse
WHERE CURRENT_TIMESTAMP - last_updated >= INTERVAL 60 MINUTE;

Target: freshness >= 99.5%
Alert: freshness < 98%
```

---

### 3. Set Error Budgets

**Goal:** Track "allowed failures" and use as resource allocation.

#### 3.1 Error Budget Calculation

```
SLO: 99.9% availability
Month: 30 days = 2,592,000 seconds

Downtime allowed:
(100 - 99.9) / 100 × 2,592,000 = 2,592 seconds = 43.2 minutes

Error budget allocation:
├─ 10 minutes: Deploy and config changes (expected)
├─ 15 minutes: Experiments, chaos engineering (learning)
├─ 10 minutes: Cleanup, maintenance (technical debt)
├─ 8 minutes: Contingency for unexpected issues

Every decision "costs" error budget:
- Deploy new feature: Costs 2% error budget risk
- Chaos engineering test: Costs 3% error budget risk  
- Big refactor: Costs 5% error budget risk

Team tracks: Are we spending budget faster than allowed?
```

#### 3.2 Error Budget Dashboards

```
Monthly Error Budget Status:

SLO: 99.9% availability
Monthly budget: 43 minutes downtime allowed
Elapsed: 10 days (33% of month)
Consumed: 8 minutes (19% of budget)
Remaining: 35 minutes (81% of budget)

Burn rate (actual vs allowed):
Allowed burn: 43min / 30days = 1.4 min/day
Actual burn: 8min / 10days = 0.8 min/day
Status: ✓ Healthy (under-consuming)

Can we deploy today?
- Risk budget for deploy: 5 min
- Remaining: 35 min
- Safe? YES, still 30 min after deploy

Alert rules:
├─ Burn rate > 2x allowed: Yellow warning
├─ Burn rate > 5x allowed: Red alert (stop deployments)
├─ >50% budget consumed: Weekly review with team
```

---

### 4. Implement SLI Measurements

**Goal:** Instrument code and infrastructure to measure SLI.

#### 4.1 Application-Level SLI Measurement

```python
# Python Flask example
from prometheus_client import Counter, Histogram

# Count successful vs failed requests
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['service', 'method', 'endpoint', 'status']
)

# Track latency
http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['service', 'method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

@app.route('/api/orders', methods=['POST'])
def create_order():
    start_time = time.time()
    
    try:
        order = process_order(request.json)
        
        # Record success
        http_requests_total.labels(
            service='order-service',
            method='POST',
            endpoint='/api/orders',
            status='200'
        ).inc()
        
        # Record latency
        duration = time.time() - start_time
        http_request_duration.labels(
            service='order-service',
            method='POST',
            endpoint='/api/orders'
        ).observe(duration)
        
        return jsonify(order), 200
        
    except Exception as e:
        # Record failure
        http_requests_total.labels(
            service='order-service',
            method='POST',
            endpoint='/api/orders',
            status='500'
        ).inc()
        
        raise
```

#### 4.2 Query SLI in Prometheus

```promql
# Current hour availability (success rate)
sum(rate(http_requests_total{status=~"2.."}[1h])) 
/
sum(rate(http_requests_total[1h]))

# P95 latency
histogram_quantile(0.95, 
  rate(http_request_duration_seconds_bucket[5m])
)

# SLO status
(
  (
    sum(rate(http_requests_total{status=~"2.."}[30d]))
    /
    sum(rate(http_requests_total[30d]))
  ) >= 0.999
)
```

---

### 5. Create Alerts

**Goal:** Alert when SLO at risk of being breached.

#### 5.1 Alert Rules

```yaml
groups:
  - name: slo
    rules:
      - alert: SLOAvailabilityAtRisk
        expr: |
          (sum(rate(http_requests_total{status=~"2.."}[5m])) 
           / sum(rate(http_requests_total[5m]))) < 0.999
        for: 5m
        annotations:
          summary: "Availability dropping below SLO"
          description: "Current availability: {{ $value | humanize }}%"
      
      - alert: SLOLatencyAtRisk
        expr: |
          histogram_quantile(0.95, 
            rate(http_request_duration_seconds_bucket[5m])
          ) > 0.25  # 250ms, SLO is 200ms
        for: 10m
        annotations:
          summary: "Latency trending toward SLO breach"
          description: "Current p95: {{ $value }}s"
      
      - alert: ErrorBudgetBurnHigh
        expr: |
          (1 - availability_current_month) / (1 - slo_target) > 2
        annotations:
          summary: "Error budget burning 2x faster than allowed"
          description: "Consume budget in {{ $value }} days"
```

---

### 6. Review & Adjust

**Goal:** Periodically validate SLO targets and adjust if needed.

#### 6.1 Weekly Review

```
Weekly SLO Scorecard:

API Service (Target: 99.9%):
├─ Actual: 99.92% ✓ PASS
├─ Incidents: 1 (5-minute outage)
├─ Trend: Stable
└─ Status: Exceeding SLO

Database (Target: 99.95%):
├─ Actual: 99.91% ✗ MISS
├─ Incidents: 1 (15-minute latency spike)
├─ Trend: Declining (was 99.96% last week)
└─ Status: BELOW SLO, needs investigation
   Action: Debug slow queries, upgrade hardware

Auth Service (Target: 99.95%):
├─ Actual: 99.97% ✓ PASS
├─ Incidents: 0
├─ Trend: Improving (was 99.94% last week)
└─ Status: Exceeding SLO

Summary:
- 2/3 services meeting SLO
- Overall reliability improving
- Action: Focus on Database optimization
```

#### 6.2 Quarterly SLO Review

```
Questions to ask:

1. Were SLO targets realistic?
   - If we're consistently missing: SLO too ambitious
   - If we're consistently exceeding: SLO too conservative

2. Did SLO targets reflect business needs?
   - Did customers complain about latency/availability?
   - Did SLO violations cause customer churn?

3. What incidents taught us?
   - Root causes identified?
   - Mitigations preventing recurrence?

4. Do SLO targets still make sense?
   - Business needs changed? (feature criticality)
   - System evolved? (now more scalable)
   - Team capacity changed? (more engineers)

Adjustments:
- Too loose: Tighten SLO targets next quarter
- Too tight: Relax SLO targets, invest in reliability
- Just right: Keep same targets, continue execution
```

---

## Common Pitfalls

- **SLO too loose:** Team doesn't treat reliability seriously
- **SLO too tight:** Team overworks, no time for improvements
- **SLI != SLO:** Measuring wrong thing (e.g., uptime vs success rate)
- **No error budget:** Team can't innovate, overly conservative
- **Poor SLI instrumentation:** Metrics don't reflect user experience
- **SLO theater:** Set SLO but don't actually measure or enforce

## Success Criteria

- ✓ SLO targets documented and agreed by business
- ✓ SLI measurements in place and accurate
- ✓ SLO compliance tracked in dashboards
- ✓ Team understands error budget and uses it
- ✓ Alert fires before SLO breached (lead time)
- ✓ SLO reviewed quarterly and adjusted as needed
- ✓ SLO breaches trigger post-mortems and improvements
- ✓ SLO communicated to customers/stakeholders
