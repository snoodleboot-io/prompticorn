---
name: observability-alerting-subagent
description: observability alerting subagent
---

# Observability Alerting Subagent (Verbose)

**Focus:** Comprehensive alert design and alert fatigue management

## Overview

Alerts are how you're notified when something goes wrong. Poor alerts lead to alert fatigue (ignoring real problems). Good alerts catch real issues with minimal false positives.

## Core Principles

**Good Alerts Are:**
- Actionable (something to do, not just information)
- Accurate (true positives, not false alarms)
- Timely (early enough to fix before impact)
- Relevant (only critical issues)
- Understandable (clear what's wrong and why)

**Bad Alerts Are:**
- Unactionable (what do you do about it?)
- Noisy (false positives, ignored)
- Too late (damage already done)
- Too sensitive (every fluctuation)
- Confusing (unclear what broke)

## Alert Design Patterns

### Threshold-Based Alerts

**Fixed Threshold:**
```
Alert if: CPU > 80%

Pros: Simple, intuitive
Cons: Doesn't adapt to load changes
```

```promql
ALERT HighCPU
  IF node_cpu_percent > 80
  FOR 5m
  ANNOTATIONS:
    summary: "High CPU on {{ $labels.instance }}"
    description: "CPU is {{ $value }}%"
```

**Percentage-Based Threshold:**
```
Alert if: Memory > 90% of capacity

Better than absolute threshold
Adapts to different server sizes
```

```promql
ALERT HighMemory
  IF (node_memory_used / node_memory_total) > 0.9
```

**Per-Instance Baseline:**
```
Alert if: CPU deviates > 20% from that instance's normal
Uses historical data for instance
Adapts to actual usage patterns
```

### Anomaly-Based Alerts

**Standard Deviation:**
```promql
ALERT UnusualMemory
  IF abs(memory - avg_over_time(memory[1d])) > 2 * stddev_over_time(memory[1d])
  FOR 10m
```
- Alert when deviates 2σ from mean
- Reduces false positives
- Catches subtle changes

**Prophet/Seasonal Decomposition:**
```
Trend: Overall direction
Seasonal: Predictable cycle (daily, weekly)
Residual: Unexpected deviation

Alert on: Large residual
```

**Isolation Forest/DBSCAN:**
```
ML-based anomaly detection
Good for: Complex patterns
Con: Harder to explain to users
```

### Composite Alerts

**AND Condition (both must be true):**
```promql
ALERT ServiceDown
  IF (up{job="api"} == 0) AND (up{job="database"} == 0)
```
- Only alert if both are down (likely cascade failure)
- Reduces noise from transient failures

**OR Condition (any is true):**
```promql
ALERT AnyServiceDown
  IF (up{job="api"} == 0) OR (up{job="database"} == 0)
```

**Rate + Threshold Combination:**
```promql
ALERT HighErrorRate
  IF (rate(errors[5m]) > 0.05) AND (rate(requests[5m]) > 10)
  FOR 5m
```
- Alert on high error rate BUT only if traffic above threshold
- Ignores errors when traffic is low

### Severity Levels

**INFO (No Paging):**
- Informational only
- No immediate action needed
- Example: "Backup completed successfully"
- Routing: Log only, dashboard only

**WARNING (Paging, Can Wait):**
- Problem detected but not urgent
- Can be resolved next business day
- Example: "Disk 70% full"
- Routing: Team email, Slack, monitoring system

**CRITICAL (Page Now):**
- Immediate action required
- Users affected or will be soon
- Example: "Service down", "Error rate > 10%"
- Routing: Page on-call engineer via PagerDuty

**CATASTROPHIC (All Hands):**
- System down or data loss risk
- Highest priority
- Example: "Database down", "Data corruption detected"
- Routing: Page multiple engineers, war room

### Alert Tuning

**Problem: Alert Fatigue**
```
Too many alerts → Team ignores all
Only alert on issues that require action
```

**Tuning Approach:**

1. **Set Initial Threshold** (conservative)
2. **Monitor False Positives** (how often false?)
3. **Adjust Threshold** (raise if too many FP)
4. **Verify True Positives** (still catch real issues?)
5. **Evaluate Delay** (fast enough to respond?)
6. **Finalize**

**Example Tuning:**

Day 1: Alert on Error Rate > 5%
- Gets 100 alerts/day (too many)
- Raise threshold

Day 2: Alert on Error Rate > 10%
- Gets 20 alerts/day (better)
- Check: Missing any real issues?
- No issues missed

Day 3: Alert on Error Rate > 10% for 5 minutes
- Gets 8 alerts/day (good)
- Fewer transient spikes
- Fast enough to respond

**Anti-Patterns to Avoid:**
- Alert on every tiny change (noise)
- Alert on metrics without understanding (what does it mean?)
- Alert on symptoms, not causes
- No severity level (everything is critical)
- Alerts with no runbook (what do you do?)

### Runbooks

**Every Alert Needs a Runbook:**
```
ALERT HighErrorRate
  ANNOTATIONS:
    summary: "High error rate detected"
    runbook: "https://wiki.example.com/high-error-rate"
```

**Runbook Content:**
```markdown
# High Error Rate

## Definition
Alert triggers when error rate > 10% for 5 minutes

## Immediate Actions
1. Page on-call engineer
2. Check recent deployments (last 30 min)
3. Check database status
4. Check external service dependencies

## Investigation Steps
1. Query recent errors: `SELECT * FROM errors WHERE timestamp > now - 30m`
2. Check error patterns: `SELECT type, count(*) FROM errors GROUP BY type`
3. Check deployment timing
4. Check metrics for related issues

## Common Causes
- New deployment introduced bug
- Database slow (check CPU, connections)
- External service down
- Cache miss storm (Thundering herd)

## Resolution
- If recent deployment: Rollback
- If database: Scale up or optimize queries
- If external service: Wait or switch provider

## Escalation
- No response in 15 min: Page manager
- Still not resolved in 30 min: Page director
```

### Alert Routing & Escalation

**Routing Rules:**
```
INFO → Slack channel only
WARNING → Email + Slack
CRITICAL → PagerDuty + Slack + Email

Database alerts → DBA team
API alerts → Backend team
Frontend alerts → Frontend team
```

**PagerDuty Integration:**
```
Alert → PagerDuty escalation policy
  → Primary: Page engineer on-call
  → No response in 30min: Page manager
  → No response in 30min: Page director
```

**Time-Based Routing:**
```
Business hours (9-5):
  → Team Slack + Email

After hours (5pm-9am):
  → Page on-call engineer only

Weekends:
  → Critical only → Page on-call
  → Warning → Slack, no page
```

### Alert Suppression & Silence

**Suppress During Known Issues:**
```
Maintenance window: Silence all alerts from 2-3pm
Suppress: app_*.* for duration: 1 hour
Reason: "Database maintenance"
```

**Suppress Flaky Alerts:**
```
Known flaky metric: sometimes produces false positives
Suppress: transient_metric_name
Add runbook: "Investigate flakiness JIRA-123"
```

**Suppress Expected Alerts:**
```
Known degradation during backups
Suppress: backup_* alerts during backup
Enable only alerts that indicate real problems
```

### Alert Metrics

**Measure Alert Quality:**

```
True Positive Rate = (Real issues caught) / (Total issues)
False Positive Rate = (False alarms) / (Total alerts)
Sensitivity = True Positive Rate
Specificity = 1 - False Positive Rate

Goal: High sensitivity (catch real issues), low FP rate
```

**Alert Response Time:**
```
Time from alert fired to engineer notified: < 5 min
Time from notification to page received: < 1 min
Total: < 6 min from issue to engineer action
```

**Alert Relevance:**
```
How many alerts lead to action?
How many are ignored?
Ratio should be > 80% actionable
If < 50% actionable: Tune alerts
```

### Integration with Incident Management

**Alert → PagerDuty → Incident → Postmortem**

```
1. Alert fires (Prometheus)
2. Notification sent (PagerDuty)
3. Engineer receives page (phone call, SMS)
4. Engineer acknowledges (incident started)
5. Engineer investigates
6. Issue resolved
7. Incident closed
8. Postmortem scheduled
9. Learn and improve
```

### Common Alert Examples

**Service Down:**
```promql
ALERT ServiceDown
  IF up{job="api"} == 0
  FOR 1m
  LABELS:
    severity: critical
  ANNOTATIONS:
    summary: "{{ $labels.job }} is down"
    runbook: "https://wiki/service-down"
```

**High Error Rate:**
```promql
ALERT HighErrorRate
  IF rate(http_errors_total[5m]) / rate(http_requests_total[5m]) > 0.1
  FOR 5m
  LABELS:
    severity: critical
  ANNOTATIONS:
    summary: "High error rate: {{ $value | humanizePercentage }}"
```

**Disk Nearly Full:**
```promql
ALERT DiskNearlyFull
  IF (node_filesystem_avail / node_filesystem_size) < 0.1
  FOR 10m
  LABELS:
    severity: warning
  ANNOTATIONS:
    summary: "Disk {{ $labels.device }} is {{ humanizePercentage $value }} full"
```

**Slow Query Rate:**
```promql
ALERT SlowQueryRate
  IF rate(db_slow_queries_total[5m]) > 10
  FOR 5m
  LABELS:
    severity: warning
  ANNOTATIONS:
    summary: "{{ $value }} slow queries per second"
```

### Testing Alerts

**Test With Synthetic Data:**
```
Deploy test app that generates metrics
Configure alerts to point to test metrics
Verify alert fires as expected
```

**Test Without Impacting Production:**
```
Use different metric prefix (test_*)
Use different alert names
Test in staging environment first
```

**Validation Checklist:**
- [ ] Alert fires within expected time
- [ ] Alert stops firing when issue resolved
- [ ] Runbook is accurate and helpful
- [ ] Notification routing is correct
- [ ] Severity level is appropriate
- [ ] Alert message is clear and actionable
