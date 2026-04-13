---
name: slo-sli
description: "Define and track service level objectives and indicators"
version: "1.0"
languages: ["promql", "sql"]
subagents: ["observability/metrics", "orchestrator"]
---

# SLO/SLI Workflow (Minimal)

## Purpose
Establish and track service level objectives (SLOs) and indicators (SLIs) to define reliability targets and measure performance against them.

## Steps

### 1. Define Business Targets (SLOs)
- What availability does business need? (99.9%, 99.99%)
- What latency is acceptable? (p95 latency < 200ms)
- What error rate is tolerable? (<0.1%)
- What completeness? (100% of data processed)
- Break down by service/feature

### 2. Choose SLI Metrics
- Availability SLI: (successful_requests / total_requests)
- Latency SLI: p95 request latency
- Completeness SLI: Records processed / records expected
- Freshness SLI: Data age vs maximum acceptable age

### 3. Set Error Budgets
- Calculate allowed failures from SLO
- Example: 99.9% availability = 43 minutes downtime/month
- Treat error budget as project resource
- "Spend" budget on: deploys, experiments, cleanup

### 4. Implement SLI Measurements
- Instrument code to measure SLI
- Use metrics or logs to track SLI
- Aggregate to service/team level
- Compare actual SLI vs target SLO

### 5. Create Alerts
- Alert when SLO at risk (e.g., 50% budget consumed in 1 week)
- Alert when SLO violated (burn rate too high)
- Track error budget consumption over time

### 6. Review & Adjust
- Weekly: Are we tracking error budget correctly?
- Monthly: Did we meet SLO? Why/why not?
- Quarterly: Do SLO targets still make sense?
- Adjust SLO based on business needs and capability

### 7. Communicate SLO Status
- Weekly report: SLI vs SLO, error budget remaining
- Dashboards: Public SLO status for users
- Incidents: "This incident will consume 2 days of error budget"
