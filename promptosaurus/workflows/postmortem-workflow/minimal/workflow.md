---
name: "postmortem-workflow"
description: "Conduct blameless incident postmortems and extract learnings"
version: "1.0"
languages: ["python"]
subagents: ["incident/postmortem", "orchestrator"]
---

# Postmortem Workflow (Minimal)

## Purpose
Conduct blameless postmortems to understand how incidents happen, extract learnings, and prevent recurrence.

## Steps

### 1. Schedule Postmortem
- Schedule within 24 hours while memory fresh
- Invite: incident commander, technical leads, affected teams, oncall manager
- Duration: 60 minutes for most incidents (30 min for minor)
- Record: Enable transcript/recording for async sharing

### 2. Document Timeline
- When did problem start? (user first reported vs actual start time)
- What actions were taken? (deployments, restarts, rollbacks)
- When was issue detected? (alert lag?)
- When was issue resolved? (service restored)
- What was customer impact duration?

### 3. Root Cause Analysis (5 Whys)
- What happened? (API returned 500 errors)
- Why? (Database became unavailable)
- Why? (Disk ran out of space)
- Why? (Log files weren't rotated)
- Why? (Log rotation job was misconfigured)
- Root cause: Misconfigured log rotation

### 4. Identify Contributing Factors
- Lack of monitoring (didn't detect disk filling)
- No alerting (nobody knew disk at 90%)
- Insufficient runbook (no procedure to debug disk issues)
- Configuration not tested (misconfiguration went unnoticed)

### 5. Generate Action Items
- Immediate (today): Monitor disk space in real-time
- Short-term (this week): Fix log rotation configuration
- Medium-term (this month): Implement disk space alerts
- Long-term (quarterly): Improve log management system

### 6. Assign Owners & Due Dates
- Each action item has owner and deadline
- Track action item completion in future
- Close item when completed and verified

### 7. Share Learnings
- Document postmortem in wiki/knowledge base
- Share key insights in team retrospective
- Present to leadership if major incident
- Use learnings to improve processes
