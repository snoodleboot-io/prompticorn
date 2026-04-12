---
name: incident-on-call-subagent
description: incident on call subagent
---

# Incident On-Call Subagent (Verbose)

**Focus:** Comprehensive on-call management and escalation strategy

## Overview

On-call systems ensure incidents get immediate attention but must be designed to prevent burnout. This subagent specializes in on-call rotation design, escalation policies, and supporting on-call engineers.

## On-Call Rotation Models

**Single On-Call (Full Week):**
```
Week 1: Alice on-call (Mon-Sun)
Week 2: Bob on-call (Mon-Sun)
Week 3: Carol on-call (Mon-Sun)
```
- Pros: Clear ownership, continuous coverage
- Cons: Heavy burden on single person, no backup
- Use when: Alerts rare, team small, trust high
- Frequency: Every N weeks (weekly, bi-weekly, monthly)

**Shared On-Call (Shifts):**
```
Day shift (8am-5pm): Alice
Evening shift (5pm-11pm): Bob
Night shift (11pm-8am): Carol
(Rotates daily)
```
- Pros: Shared burden, no night shifts for everyone
- Cons: Handoff complexity, coverage gaps
- Use when: High alert volume, need comfort
- Frequency: Rotates daily/weekly

**Primary + Secondary:**
```
Primary: Alice (first to be paged)
Secondary: Bob (paged if Alice doesn't respond)
Tertiary: Carol (if Bob doesn't respond)

New primary: Bob (next week)
```
- Pros: Escalation built-in, no single point of failure
- Cons: More people on-call
- Use when: Critical service, can't afford outages
- Frequency: Weekly rotation of primary

**Follow-the-Sun (Global Coverage):**
```
Team 1 (Asia/Europe): 9am-6pm their time
Team 2 (Americas): 9am-6pm their time
Team 3 (Australia): 9am-6pm their time
No night shifts for anyone
```
- Pros: No night shifts, always someone awake
- Cons: Complex handoff, distributed team required
- Use when: Global service, multiple timezones
- Frequency: Handoff at shift boundaries

**Role-Based Escalation:**
```
Alert fired
  ├─ API Service: Page @api-oncall
  ├─ Database: Page @db-oncall
  └─ Infrastructure: Page @infra-oncall

Each team manages their own on-call
```
- Pros: Specialized knowledge, clear ownership
- Cons: Requires many people on-call
- Use when: Large org, service-oriented
- Frequency: Each team's own rotation

## Escalation Policies

**Example Policy for Medium Severity:**
```
ALERT FIRES (SEV2)
  ├─ Immediately: Page Primary on-call
  │  Notification: Push + SMS + Call
  │  Required Action: Acknowledge within 5 min
  │
  ├─ 5 minutes no ACK: Page Secondary on-call
  │  Notification: Call (aggressive)
  │  Required Action: Acknowledge or Primary responds
  │
  ├─ 10 minutes still unresolved: Page Manager
  │  Notification: Call
  │  Brief: "SEV2 unresolved 10 min, primary unreachable"
  │
  └─ 15 minutes still unresolved: Page Director
     Notification: Call + SMS
     Brief: "SEV2 escalation, request war room"
```

**Policy Configuration (in PagerDuty):**
```
Service: API
Escalation Policy:
  1st Level: Primary on-call (5 min timeout)
  2nd Level: Secondary on-call (5 min timeout)
  3rd Level: API Lead (10 min timeout)
  4th Level: VP Engineering (no timeout)
```

**Critical SEV1 Policy:**
```
SEV1 ALERT FIRES
  ├─ Immediately: Page Primary AND Secondary
  │  Both paged at same time (no delay)
  │  Notification: All channels
  │
  ├─ Simultaneously: Declare war room
  │  Create incident channel
  │  Page incident commander
  │  Notify leadership
  │
  └─ Start status page updates
     Update every 5 minutes
```

## On-Call Tools & Systems

**Alerting & Notifications:**
- **PagerDuty** - Enterprise on-call management
- **Opsgenie** - Atlassian alternative
- **Victorops** - Splunk-owned alternative
- **iLert** - Lightweight, Slack-integrated

**Alert Routing:**
- Alert severity → Escalation policy
- Team ownership → Relevant team's on-call
- Time of day → Different escalation
- Alert frequency → Tuning to prevent page spam

**Integration Points:**
- Prometheus/Grafana → Alert to PagerDuty
- CloudWatch → Alert to PagerDuty
- Custom monitoring → Webhook to PagerDuty
- Slack integration → Alert in #incidents channel

## On-Call Responsibilities

**Primary On-Call Must:**
1. Keep phone nearby and respond within 15 minutes
2. Be in a position to work (not sleeping, not driving)
3. Have Internet access to systems
4. Know who to escalate to
5. Document what happened
6. Be available for 24/7 (SEV1) until resolution

**Secondary On-Call Must:**
1. Be responsive to pages (5-15 min response)
2. Know escalation procedures
3. Be ready to take primary's load if needed
4. Understand major systems (overview, not deep)

**Manager Escalation Must:**
1. Be contactable during their listed availability
2. Know who to page next if engineers unreachable
3. Understand critical dependencies
4. Able to make go/no-go decisions

## Time Zone Handling

**Global On-Call Model:**
```
APAC Coverage (9am-6pm AEST/JST):
  Primary: Asia team member
  Secondary: US East team member (after hours for them)

Americas Coverage (9am-6pm EST/PST):
  Primary: US team member
  Secondary: APAC team member (night shift for them)

EMEA Coverage (9am-6pm CET/GMT):
  Primary: Europe team member
  Secondary: US team member (early morning for them)
```

**After Hours (Outside Coverage):**
```
Outside 9am-6pm all zones: Contact on-call in nearest zone
Exception: SEV1 - Page whoever is designated for that
Global critical systems: Always have someone on-call
```

## On-Call Burden Prevention

**Alert Volume Targets:**
- Average: < 2 pages per on-call week
- Max: < 5 pages per week (burnout risk)
- Alert fatigue: > 1 false positive per month = tune it

**Shift Duration:**
- Week-long rotation: Max stress, but clear ownership
- Daily rotation: Less stress, more handoffs
- 12-hour shifts: Balance of both
- 8-hour shifts: Best for wellbeing, worst for continuity

**Breaks:**
- After major incident: Give on-call engineer day off
- Every N weeks: Weekend off (don't rotate on-call)
- Vacation: Mandatory handoff, never on-call during vacation

**Compensation:**
- Night shifts: Bonus pay or comp time
- Page frequency: Extra comp if > 10 pages/week
- Burnout prevention: Rotation frequency based on load

**Training:**
- New on-call: Pair with experienced for 1 week
- Quarterly: Runbook review and update
- Post-incident: Training on what went wrong
- Promotion: Training before taking primary role

## On-Call Handoff Procedure

**Beginning of On-Call:**
```
Monday 9am - Previous on-call hands off to new on-call:

□ Review recent incidents
  "We had database issues last Tuesday, watch for slow queries"

□ Current critical issues
  "Deployment queue is backed up, check status"

□ Known flaky alerts
  "Uptime sensor sometimes triggers false positives"

□ Dashboard links and shortcuts
  "Here's my quick diagnostics dashboard"

□ Contact info for escalations
  "DBA is Carol, she works 9-5, page Bob after hours"

□ Any customizations to tools
  "I've added my own alert filters, password in 1Password"
```

**Document Format:**
```
=== Weekly Handoff Notes ===
Week of: 2026-04-07
On-Call: Alice
Incidents: 2 (1 SEV2, 1 SEV3)

Known Issues:
- Database occasionally slow (ticket PROJ-123)
- Cache connection pool sometimes exhausts (being fixed)
- Deployment queue backed up (new feature)

Flaky Alerts:
- HighMemory: Often false positive, check processes first

Key Dashboards:
- System Health: https://grafana/d/system
- Database: https://grafana/d/database
- API: https://grafana/d/api

Escalation:
- DB issues: Page @carol-dba
- Infrastructure: Page @bob-ops
- All else: @alice-lead

Next On-Call:
- Bob (starting Monday)
```

## Metrics & Monitoring On-Call Health

**Track These Metrics:**
- Pages per week (should be < 2)
- Response time (should be < 10 min)
- Escalation rate (should be < 10%)
- False positive rate (should be < 5%)
- Time to resolution (trend over time)
- On-call engineer satisfaction (survey quarterly)

**Health Indicators:**
- Alert fatigue: Multiple pages same issue
- False positives: > 20% of pages not real incidents
- Slow response: Avg > 15 min from page to action
- High escalation: > 30% escalate to manager
- Burnout: High turnover, more callouts from on-call

**Improvements:**
- Tune alerts (reduce false positives)
- Better runbooks (faster resolution)
- Additional monitoring (catch issues earlier)
- Rotate more frequently (reduce burden)
- Hire more on-call coverage

## Common On-Call Mistakes

- **Too many pages** - Alert fatigue, people ignore pages
- **Too few people** - Burnout, unreliable coverage
- **No escalation** - Can't reach primary, incident waits
- **Unclear expectations** - On-call engineer doesn't know SLA
- **No training** - New on-call doesn't know systems
- **No breaks** - On-call always on-call, burnout guaranteed
- **Blaming** - "You should have known that"
- **No support** - On-call is alone with no guidance

## Supporting On-Call Engineers

- Give them tools they need (access, dashboards, runbooks)
- Respect their sleep (don't page for non-critical stuff)
- Provide backup when overwhelmed (secondary/manager)
- Recognize their work (public thanks, bonuses)
- Get feedback quarterly (what would help?)
- Invest in improvements (better monitoring, automation)
- Celebrate incidents they handled well
- Never blame them for escalating
