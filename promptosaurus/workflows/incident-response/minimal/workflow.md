---
name: incident-response
description: "Triage, escalate, and communicate during incidents"
version: "1.0"
languages: ["python"]
subagents: ["incident/triage", "incident/runbook", "orchestrator"]
---

# Incident Response Workflow (Minimal)

## Purpose
Quickly detect, assess, and respond to incidents to minimize customer impact and restore service.

## Steps

### 1. Detect Incident
- Alert fires (automated detection)
- User reports issue (support tickets, social media)
- Team member notices problem (monitoring dashboard)
- Establish incident start time (when did problem begin?)

### 2. Initial Triage (First 5 Minutes)
- What is affected? (API down? Slow? Partial?)
- How many users impacted?  (1 user? 10%? 100%?)
- Severity assessment: SEV1 (critical), SEV2 (high), SEV3 (medium), SEV4 (low)
- Page on-call engineer
- Create incident in tracking system
- Post initial update to #incidents Slack channel

### 3. Establish Incident Command
- Declare incident commander (single person in charge)
- Declare communications lead (updates stakeholders)
- Declare technical lead(s) (investigating root cause)
- Define escalation: Who to page if not resolved?

### 4. Investigate Root Cause
- Look at recent deployments (was something just shipped?)
- Check system metrics (CPU/memory/disk issues?)
- Review logs for error patterns
- Test hypotheses systematically

### 5. Implement Mitigation
- Immediate fix: Get service back online first
- Degraded mode: Can we serve users partially?
- Workaround: Route traffic elsewhere?
- Rollback: Revert last deployment if it's the cause?

### 6. Verify Resolution
- Can users access service again?
- Are error rates normal?
- Are metrics back to baseline?
- Double-check: Was fix complete or partial?

### 7. Close Incident & Communicate
- Declare incident resolved when service restored
- Send final communication (what happened, how long, what we're doing)
- Schedule postmortem for same day
- Begin recovery: monitor for recurrence

### 8. Postmortem (24 Hours Later)
- Document what happened (timeline)
- Root cause analysis (why did it happen?)
- Action items to prevent recurrence
- Share learnings with team
