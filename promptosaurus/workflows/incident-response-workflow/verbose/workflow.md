---
name: "incident-response-workflow"
description: "Complete incident response including detection, triage, escalation, mitigation, and communication"
version: "1.0"
languages: ["python"]
subagents: ["incident/triage", "incident/runbook", "orchestrator"]
---

# Incident Response Workflow (Verbose)

## Purpose
Provide comprehensive incident response procedures to detect issues rapidly, assess impact, mobilize team response, mitigate problems quickly, and communicate transparently with stakeholders.

## When to Use This Workflow
- Production system experiencing outage or degradation
- User-facing service unavailable or slow
- Data integrity issues detected
- Security incident discovered
- Infrastructure failure

## Prerequisites
- On-call rotation in place
- Incident tracking system configured
- Runbooks for common issues
- Communication channels (Slack, PagerDuty)
- Team trained on incident response
- Monitoring/alerting configured

---

## Steps

### 1. Detect Incident

**Goal:** Identify problems as early as possible.

#### 1.1 Detection Methods

```
Automated Detection (Best - <1 minute delay):
├─ Monitoring alert fires
│  └─ API error rate > 1%
│  └─ Database latency p95 > 5s
│  └─ Service restart detected
├─ Health check fails
│  └─ Dependent service unreachable
│  └─ Data quality check fails
└─ Log anomaly detected
   └─ Spike in ERROR log level

User Report (Moderate - 5-15 minute delay):
├─ Support tickets arrive
├─ Users complain on social media
├─ Customer calls in
└─ Internal team reports issue

Team Discovery (Worst - 30+ minute delay):
├─ Engineer notices in dashboard
├─ Performance visibly degraded
└─ Too late - users already suffering
```

#### 1.2 Incident Start Time

Critical for SLA tracking:

```
Incident Timeline:

2:00 PM - Root cause begins (database connection leak starts)
2:03 PM - First error responses to users (3 min before detection)
2:05 PM - Alert fires, incident declared
2:06 PM - On-call engineer pages (lead time)
2:08 PM - Incident commander takes control (mobilization delay)
2:30 PM - Root cause identified
2:45 PM - Mitigation begins
3:00 PM - Service restored

Incident Duration:
- From user impact: 2:03 PM - 3:00 PM = 57 minutes
- From incident declaration: 2:05 PM - 3:00 PM = 55 minutes
- From mitigation start: 2:45 PM - 3:00 PM = 15 minutes
- Detection lag: 2 minutes (good!)
- Response lag: 3 minutes (acceptable)

SLA tracking: Usually "from detection" (2:05 PM)
Not "from user impact" (too hard to determine)
```

---

### 2. Initial Triage (First 5 Minutes)

**Goal:** Understand scope and severity to route appropriately.

#### 2.1 Severity Classification

```
SEV1 (Critical - Full Outage):
- Complete service unavailable
- All users affected
- Massive business impact
- Response: Page manager + on-call engineer immediately
- Target fix time: 15 minutes
- Example: API completely down, 0% success rate

SEV2 (High - Partial Outage):
- Service degraded or partially unavailable
- Many users affected (>10%)
- Significant business impact
- Response: Page on-call engineer
- Target fix time: 1 hour
- Example: Payment processing 10% of requests fail

SEV3 (Medium - Significant Issue):
- Some users experiencing issues
- Feature degradation
- Limited business impact
- Response: Create ticket, alert team
- Target fix time: 4 hours
- Example: Search results slightly inaccurate

SEV4 (Low - Minor Issue):
- Very few users affected
- Workaround available
- No business impact
- Response: Log and schedule
- Target fix time: 48 hours
- Example: Typo in error message
```

#### 2.2 Initial Assessment

```
Five questions (ask in first 5 minutes):

1. WHAT is affected?
   Answers: API down? Database? Specific feature? Region?
   Impact: Determines which team to page

2. HOW MANY users?
   Answers: 0.1% of traffic? 50%? 100%?
   Impact: Determines severity level

3. WHEN did it start?
   Answers: Just now? 10 minutes ago? Started at 2am?
   Impact: Helps identify root cause (recent deploy?)

4. CAN WE serve users somehow?
   Answers: Complete outage? Degraded? Partial functionality?
   Impact: Determines if mitigation available

5. WHAT changed recently?
   Answers: Deploy? Config change? Traffic spike? Bad data?
   Impact: Gives initial hypothesis for investigation

Sample triage:
Incident: "API returning 500 errors"
1. What: API Gateway → all requests failing
2. How many: 100% of traffic
3. When: 2:05 PM (5 minutes ago)
4. Can we serve: No, complete outage
5. Recent changes: Deploy 5 minutes ago
→ Verdict: SEV1, likely recent deploy caused it
→ Action: Page incident commander + senior engineer
```

#### 2.3 Create Incident Record

```
Incident Ticket Format:

Title: API Service Outage - 100% traffic failing
Severity: SEV1
Created: 2026-04-10 14:05:00 UTC
Start Time: 2026-04-10 14:05:00 UTC
Estimated User Impact: 100,000 users
Affected Services: API Gateway

Initial Symptoms:
- API returning HTTP 500 errors for all requests
- Error rate: 100%
- Started: 5 minutes ago (2:05 PM)
- Recent change: Deployed config change 5 minutes before

Actions Taken:
- [ ] Incident commander assigned
- [ ] On-call team paged
- [ ] Slack #incidents channel created
- [ ] Customer communication sent
- [ ] Root cause identified
- [ ] Mitigation begun
- [ ] Service restored
- [ ] All-clear sent
```

---

### 3. Establish Incident Command

**Goal:** Organize response with clear roles and responsibilities.

#### 3.1 Incident Commander

```
Role: Incident Commander

Responsibilities:
- Declare incident open/resolved
- Make strategic decisions (rollback? scale up? wait?)
- Coordinate across teams
- Track timeline
- Escalate if needed
- Close incident when done

Authority:
- Can page anyone
- Can request resources
- Can approve rollbacks
- Can pause deployments

Does NOT:
- Dig into technical details (that's engineers' job)
- Make individual fix decisions (that's tech lead's job)
- Communicate directly to customers (that's comms' job)

Example decision:
"We've been investigating 30 minutes with no resolution.
Time to escalate. Call database team manager and architect."
```

#### 3.2 Communications Lead

```
Role: Communications Lead

Responsibilities:
- Update #incidents Slack channel (every 15 minutes)
- Send customer notifications
- Coordinate with support team
- Track timeline
- Prepare post-incident report

Timeline of updates:

2:05 PM - Incident declared
"🚨 INCIDENT: API Service Outage
Severity: SEV1
Impact: 100% of API requests failing
Status: INVESTIGATING"

2:10 PM - Initial findings
"Update: Deploy 5 minutes before incident.
Rolling back config change now."

2:15 PM - Mitigation underway
"Update: Config rollback in progress.
Monitoring service recovery."

2:25 PM - Resolution
"✅ RESOLVED: Service restored at 2:25 PM.
Duration: 20 minutes
Cause: Config change bug
Post-incident analysis tomorrow 10am."
```

#### 3.3 Technical Leads

```
Role: Technical Leads

Responsibilities:
- Investigate root cause
- Propose mitigations
- Implement fixes
- Monitor recovery
- Suggest prevention measures

Distribution of effort:
- Lead engineer: Overall coordination, high-level diagnosis
- Database expert: If database suspected
- Network engineer: If network suspected
- Application engineer: If app code suspected

Don't all dive into technical investigation - it's inefficient.
Focus on systematic elimination of possibilities.
```

---

### 4. Investigate Root Cause

**Goal:** Identify what caused the problem rapidly.

#### 4.1 Systematic Investigation

```
Decision tree (using process of elimination):

Is API accepting connections?
├─ No → Network/firewall issue
│   └─ Check load balancer logs
│   └─ Check API server status
│   └─ Restart API service
│
├─ Yes → Is API processing requests?
    ├─ No → API hung/deadlock
    │   └─ Check process status
    │   └─ Check for deadlock in logs
    │   └─ Kill and restart
    │
    └─ Yes → Is API reaching dependencies?
        ├─ No → Dependency down
        │   └─ Check which dependency
        │   └─ Is database responding?
        │   └─ Is cache responding?
        │   └─ Failover to replica/secondary
        │
        └─ Yes → Application bug
            └─ Check recent code changes
            └─ Review logs for error pattern
            └─ Rollback recent deploy
```

#### 4.2 Rapid Debugging Techniques

```
Log analysis:
grep "2026-04-10 14:0[5-9]" api.log | tail -100
→ Look for ERROR pattern right at incident time

Metrics correlation:
- Plot CPU, memory, latency together
- What changed right at 2:05 PM?
- CPU spike? Memory leak? Connection pool exhaustion?

Recent changes:
git log --since="1 hour" --oneline
→ What deployed in last hour?

Hypothesis testing:
"It's the recent deploy"
→ Test: Rollback and see if issue goes away
"It's the database"
→ Test: Verify database connectivity and latency
"It's the cache"
→ Test: Clear cache and monitor
```

---

### 5. Implement Mitigation

**Goal:** Restore service to users as fast as possible.

#### 5.1 Mitigation Options

```
Fast mitigations (try first - 5-15 min):
1. Rollback recent deploy (if suspected cause)
2. Restart service (clear hung connections, memory)
3. Clear cache (if cache poisoned)
4. Failover to replica (if primary failed)
5. Route traffic away (if server broken)

Degraded mode mitigations (when full restore not possible):
1. Return cached responses (serve stale data)
2. Reduced functionality (disable non-critical features)
3. Rate limiting (serve customers fairly)
4. Queue requests (serve slowly, not fail)

Long-term fix (after service restored):
1. Patch root cause
2. Add monitoring/alerting
3. Improve tests to catch issue
4. Update runbooks

Example:
Incident: Database connection pool exhausted
Fast mitigation: Restart API service (clears stale connections)
→ 80% of connections drop, new requests get fresh connections
→ Service restored, users notice 30-second pause only
Duration: 5 minutes

Without mitigation:
→ Waiting for DBA to analyze why pool exhausted
→ 45 minutes of outage
```

---

### 6. Verify Resolution

**Goal:** Confirm service actually restored before declaring incident closed.

#### 6.1 Resolution Checklist

```
Before declaring "resolved":

[ ] Can users access service?
    - Manual test from different region
    - Check uptime monitoring dashboard
    - Review customer feedback

[ ] Are error rates normal?
    - Error rate < 0.1% (was 100% before)
    - No more 500 errors in logs
    - Exceptions dropping toward baseline

[ ] Are metrics normal?
    - CPU returned to normal
    - Memory stable (no growth)
    - Latency p95 < 200ms (baseline)
    - Database connections < 300

[ ] Did we fix it or just applied band-aid?
    - If restarted API: Will it crash again? (YES → band-aid)
    - If rolled back deploy: Does new code have bug? (YES → incomplete fix)
    - If added capacity: Will that capacity prevent recurrence? (YES → real fix)

Decision:
- All green + real fix → Declare resolved
- Some red + band-aid → Declare "band-aid in place" + plan real fix
```

---

### 7. Close Incident & Communicate

#### 7.1 Final Communications

```
To users:
"We experienced an API outage from 2:05 PM to 2:25 PM UTC (20 minutes).
Service is now fully restored. We apologize for the disruption.
Root cause: Configuration error in recent deploy.
We're taking immediate action to prevent recurrence.
More details in our status page."

To internal team:
"Incident closed. Duration: 20 minutes.
Root cause: Deploy bug.
Mitigation: Config rollback.
Postmortem: Tomorrow 10am.
Action items will be assigned."

To leadership:
"SEV1 incident 2:05-2:25 PM (20 min).
Impact: 100% of API traffic.
Cause: Configuration error.
Fix: Rollback.
Prevention: Enhanced testing before deploy."
```

#### 7.2 Schedule Postmortem

```
Key details for postmortem:

Timeline:
- 2:05 PM - Alert fires
- 2:05 PM - Incident declared
- 2:06 PM - On-call engineer pages
- 2:08 PM - Incident commander takes control
- 2:15 PM - Root cause identified
- 2:25 PM - Service restored
- 2:30 PM - All-clear sent

Root cause:
Configuration change introduced bug:
  OLD: timeout_ms = "5000"
  NEW: timeout_ms = 5000  ← Missing quotes, treated as seconds not milliseconds
  Result: 5-second timeout instead of 5ms → timeout on every request

Contributing factors:
- No configuration validation in deployment
- No canary deployment (went to 100% at once)
- No monitoring of configuration changes

Prevention measures:
- Add schema validation to configuration
- Implement canary deployments (5% → 50% → 100%)
- Alert on config change
- Require change approval before deploy
```

---

## Common Pitfalls

- **Rushing to fix without understanding cause:** Band-aid instead of solution
- **Wrong person in command:** No clear decision authority
- **No communication:** Users left wondering what happened
- **Blame hunting:** "Who deployed that bug?" instead of "How do we prevent this?"
- **Not following decision tree:** Debugging randomly vs. systematically
- **Ignoring prevention:** Repeats same incident

## Success Criteria

- ✓ Service restored in <15 minutes for SEV1
- ✓ Root cause identified within incident
- ✓ Clear incident commander taking control
- ✓ User communication transparent and timely
- ✓ No blame assigned (blameless postmortem culture)
- ✓ Prevention measures implemented to prevent recurrence
- ✓ Team confident in incident response playbook
