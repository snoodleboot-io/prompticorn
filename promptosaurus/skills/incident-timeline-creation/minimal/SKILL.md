---
name: incident-timeline-creation
type: skill
category: technical-skill
minimal: true
---
# Incident Timeline Creation (Minimal)

## Timeline Structure

```
2:00 PM - [EVENT] Database connection pool becomes exhausted
2:02 PM - [DECISION] Restart database service
2:03 PM - [METRIC CHANGE] Error rate spikes to 100%
2:05 PM - [ALERT] Automated alert fires
2:06 PM - [HUMAN ACTION] On-call engineer acknowledges
2:08 PM - [ESCALATION] Incident commander paged
2:15 PM - [ROOT CAUSE] Identified connection leak in query
2:20 PM - [REMEDIATION] Deploy fix
2:25 PM - [RESOLUTION] Service restored, error rate drops
```

## What to Include

- **Event:** What happened (alert fired, error spike, user report)
- **Decision:** What action taken (restart, rollback, scale up)
- **Metric:** What changed (CPU 30→90%, latency doubled)
- **Human Action:** Who did what (paged oncall, started mitigation)
- **Root Cause:** What was root cause
- **Resolution:** Service restored when

## Timeline Accuracy

Source of truth:
1. Server logs (timestamps are accurate)
2. Metrics dashboards (show exact time of change)
3. Chat history (Slack, Teams with timestamps)
4. Tickets (incident tracking system)

Don't rely on memory - reconstruct from logs!

## Key Timestamps

```
Detection Time: When problem detected (alert or user report)
Start Time: When problem actually began
Response Time: When team started responding
Mitigation Time: When fix began
Resolution Time: When service restored
```

## Example Full Timeline

```
2:00:00 - (ROOT CAUSE) Query change deployed
2:00:15 - Connection leak begins (slowly)
2:05:00 - First error (5 min into incident)
2:05:03 - Alert fires (detection lag: 3 sec)
2:05:30 - On-call pages (response lag: 27 sec)
2:06:00 - IC takes control (escalation lag: 30 sec)
2:08:00 - Root cause identified (diagnosis: 2 min)
2:12:00 - Fix deployed (remediation: 4 min)
2:14:00 - Service restored (total: 14 min)

User impact: 9 minutes (2:05 - 2:14)
```
