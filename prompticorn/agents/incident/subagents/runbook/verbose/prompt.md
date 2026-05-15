---
name: incident-runbook-subagent
description: incident runbook subagent
mode: subagent
---

# Incident Runbook Subagent (Verbose)

**Focus:** Comprehensive runbook creation and operational procedures

## Overview

Runbooks are the playbooks for incident response. During an incident, people are stressed and cognitive function is impaired. Detailed, tested runbooks make recovery faster and more reliable.

## What Makes a Good Runbook

**Characteristics:**
- **Single Issue** - One runbook per problem
- **Clear** - Someone unfamiliar can follow it
- **Actionable** - Steps to take, not explanations
- **Testable** - Can be practiced before incidents
- **Linked** - To dashboards, logs, relevant docs
- **Decision Trees** - Clear escalation/go/no-go points
- **Time Estimates** - How long each step should take
- **Verified** - Recently tested and confirmed working

## Runbook Structure

**1. Summary (First 30 seconds)**
```
RUNBOOK: High Database Latency

Description:
When database response times exceed 500ms,
queries fail and API returns 504 errors.

Symptoms:
- API error rate spikes to 50%+
- Database query latency > 500ms
- Alert: "HighDatabaseLatency"

Severity: SEV2
Time to Resolution: 10-30 minutes
```

**2. Quick Checks (First 2 minutes)**
```
Before diving into diagnosis, verify:

□ Is the alert real?
  Command: curl -s https://api.example.com/health | grep database
  Expected: "status":"ok"
  
□ Is only one database or all?
  Command: mysql -h primary.db.example.com -e "SHOW PROCESSLIST" | wc -l
  Expected: < 100 processes
  
□ Did we just deploy?
  Check: https://deploy.example.com/history
  Recent deployment within last 5 minutes = likely cause
```

**3. Diagnosis (5-10 minutes)**
```
STEP 1: Check Database Connections
  Command: mysql -h primary.db.example.com -e "SHOW PROCESSLIST FULL\G"
  Look for:
    - Sleeping connections (kill old ones)
    - Long-running queries (> 60 seconds)
    - Lots of pending connections
    
  Action if found:
    - Sleeping: kill_id 123
    - Long query: kill_id 456
    - Too many: Investigate application connection pool

STEP 2: Check Database Load
  Command: ssh primary.db.example.com "top -bn1 | grep -E 'Cpu|Mem'"
  Look for:
    - CPU > 80% (overloaded)
    - Memory > 90% (swapping)
    - I/O wait > 50% (disk bound)
    
  Action if found:
    - High CPU: Slow query? Index missing?
    - High memory: Cache bloated?
    - High I/O: Disk full?

STEP 3: Check for Slow Queries
  Command: mysql -h primary.db.example.com -e \
    "SELECT TIME, ID, TIME_MS, SQL_TEXT FROM SLOW_LOG 
     ORDER BY TIME_MS DESC LIMIT 10"
  
  Action:
    - Is there a new slow query?
    - Did query recently change?
    - Does it need an index?
```

**4. Recovery Steps**
```
OPTION A: Kill Long-Running Query (Fast)
  ✓ Fastest recovery (seconds)
  ✓ Works when one query is hogging resources
  ✗ May lose that operation
  
  Command: mysql -h primary.db.example.com -e "KILL QUERY 123"
  Verify: Database latency returns to normal within 30 seconds
  Proceed to Step 5 (Verification)

OPTION B: Restart Connection Pool (Moderate)
  ✓ Cleans up hung connections
  ✓ Works for connection exhaustion
  ✗ Brief API errors during restart
  
  Command: ssh app.example.com "systemctl restart app-api"
  Wait: 60 seconds for restart
  Verify: Database latency improves
  Proceed to Step 5

OPTION C: Scale Database (Longer)
  ✓ Adds more capacity
  ✓ Handles load spikes
  ✗ Takes 5-10 minutes
  
  Step 1: ssh primary.db.example.com "add_replica.sh"
  Step 2: Monitor: watch "SHOW SLAVE STATUS"
  Step 3: Update app config to use replica for reads
  Verify: Load distributed, latency improves

OPTION D: Rollback Recent Deployment (If likely cause)
  ✓ Fixes query/config changes
  ✓ Fastest if deployment is root cause
  ✗ Loses any functionality from deployment
  
  Check: Did we deploy in last 5 minutes?
  If YES: Go to Deployment Rollback runbook
  If NO: Continue with other options
```

**5. Escalation Criteria**
```
WHEN TO ESCALATE:
□ After 5 minutes: No improvement with Step 1-2
  → Page DBA on-call
  → Message: "Database latency > 500ms, tried standard steps"
  
□ After 10 minutes: Still not resolved
  → Escalate to Database team lead
  → Page infrastructure on-call
  
□ After 15 minutes: Complete database failure
  → This becomes SEV1
  → Page VP of Engineering
  → Declare incident over
  
CONTACT INFO:
  DBA on-call: @alice (Slack: #db-on-call)
  Infra team: @bob (Phone: 555-0100)
  VP Eng: @carol (Email: carol@example.com)
```

**6. Post-Recovery Verification**
```
After recovery, verify:

□ API error rate returned to < 0.5%
  Dashboard: https://grafana.example.com/d/api-errors

□ Database latency < 100ms p99
  Dashboard: https://grafana.example.com/d/db-latency

□ All services healthy
  Command: curl https://api.example.com/health/deep
  Expected: All green

□ No cascading issues
  Check: https://monitoring.example.com/alerts
  Expected: All alerts cleared

If verification fails:
  → Do NOT close the incident
  → Return to Step 3 (Diagnosis)
  → Consider escalating
```

**7. Post-Incident Documentation**
```
AFTER incident is resolved:

□ Update incident ticket with resolution
  - What was the root cause?
  - What steps worked?
  - What didn't work?
  
□ File any bugs or follow-ups
  - Query optimization needed?
  - Index missing?
  - Config needs change?
  
□ Schedule postmortem (if SEV1/SEV2)
  - Time: Within 24 hours
  - Why did this happen?
  - How do we prevent recurrence?
  
□ Update this runbook if procedures changed
  - Did we learn a better approach?
  - Are there gaps in the procedures?
```

## Decision Tree Example

```
Database Latency Alert Fires
        │
        ├─→ Is it real? (curl health check)
        │   NO → Dismiss alert, investigate why false positive
        │   YES → Continue
        │
        ├─→ Database completely down?
        │   YES → SEV1, page everyone, use failover procedures
        │   NO → Continue
        │
        ├─→ Database CPU > 90%?
        │   YES → Check for long-running queries, kill them
        │   NO → Continue
        │
        ├─→ Database connections > 200?
        │   YES → Restart application connection pool
        │   NO → Continue
        │
        ├─→ Recent deployment (< 5 min)?
        │   YES → Consider rollback
        │   NO → Continue
        │
        └─→ Problem persists > 5 min?
            YES → Escalate to DBA on-call
            NO → Problem resolving, proceed to verification
```

## Testing Your Runbooks

**Before Incidents Happen:**
- Run through during staging/test environment
- Practice during on-call rotation (not in production)
- Update based on what you learn
- Add timestamps to test: "Last tested: 2026-04-10"

**During Postmortems:**
- Was the runbook easy to follow?
- Did procedures work as written?
- What was missing?
- Update the runbook accordingly

**Metrics:**
- Time to follow runbook
- How many steps were skipped?
- Did responder need help?
- Areas of confusion

## Runbook Anti-Patterns

- **Too long** - People won't read it during crisis
- **Too vague** - "Fix the database" without steps
- **Outdated** - Dashboard links changed, commands don't work
- **Blaming** - "You'll need to talk to Bob because he's the only one who knows"
- **Theoretical** - Never tested in practice
- **No escalation** - No guidance on when to get help
- **Assumes knowledge** - "Just SSH and restart"

## Example Runbooks

**Email Alerts Not Sending:**
- Check mail queue size
- Check mail service status
- Restart mail service if hung
- Check firewall rules
- Escalate to infra if still broken

**API Returning 500 Errors:**
- Check error logs
- Check database connectivity
- Check cache connectivity
- Restart API service
- Check recent deployments
- Rollback if deployment-related

**Memory Leak Suspected:**
- Check memory growth over time
- Identify which process is leaking
- Restart affected service
- File ticket to investigate
- Monitor for recurrence

## Integration with Alerts

**Every alert needs:**
- Link to relevant runbook
- Clear description of what it means
- Links to dashboards
- Relevant metrics

**Example alert:**
```
Alert: HighDatabaseLatency
Description: Database query latency > 500ms for 5 minutes
Runbook: https://wiki.example.com/runbooks/high-db-latency
Dashboard: https://grafana/d/db-latency
Severity: SEV2
```

During incident, first action: Find and follow the runbook.
