---
name: "postmortem"
description: "Blameless incident postmortems with root cause analysis, action items, and learning capture"
version: "1.0"
languages: ["python"]
subagents: ["incident/postmortem", "orchestrator"]
---

# Postmortem Workflow (Verbose)

## Purpose
Conduct blameless incident postmortems to understand contributing factors, extract organizational learnings, and prevent recurrence through evidence-based improvements.

## When to Use This Workflow
- After any SEV1 or SEV2 incident
- After incidents that surprised team
- After repeated incidents (pattern indicates system issue)
- To investigate near-misses before they become outages
- To improve operational practices

## Prerequisites
- Incident resolved and documented
- Timeline of events captured
- Key participants available for discussion
- Blameless culture established (no punishment for mistakes)
- Process for tracking and closing action items

---

## Steps

### 1. Schedule Postmortem

**Goal:** Conduct analysis while context fresh, within 24 hours.

#### 1.1 Timing & Participants

```
Timing:
- SEV1: Postmortem within 24 hours
- SEV2: Postmortem within 48 hours
- SEV3+: Can schedule within 1 week
- Too late: >1 week causes memory decay, low attendance

Participants:
- Incident commander (owned response coordination)
- Technical leads (investigated and fixed issue)
- On-call engineer (first responder)
- Affected team members (responsible for system)
- Team manager (for resource allocation)
- Optional: Customer rep (understand customer impact)
- Optional: QA/testing lead (improve preventive testing)

NOT present:
- Anyone in blame-finding mindset
- People who didn't touch the incident
- Bystanders wasting time

Duration:
- Quick incident (< 10 minutes): 30-minute postmortem
- Moderate incident (10-60 minutes): 60-minute postmortem
- Long incident (> 1 hour): 90-minute postmortem
- Complex incident (multiple failures): 2-hour postmortem

Timezone:
- If global team: Schedule in overlapping hours
- If async needed: Record session + transcript
```

#### 1.2 Pre-Postmortem Preparation

```
Incident commander prepares:
- [ ] Document timeline of events
- [ ] Collect logs and metrics from incident period
- [ ] Identify configuration changes made
- [ ] Note all decisions made during incident
- [ ] Screenshot key dashboards at incident time
- [ ] List candidate root causes

Share pre-postmortem with team:
"Incident #12345: API Outage 2:05-2:25 PM
Timeline: [events]
Impact: 20 minutes downtime
Status: Service restored
Postmortem: Today 4pm in conference room"

Helps team:
- Refresh memory on incident
- Begin thinking about cause before meeting
- Come prepared with observations
```

---

### 2. Document Timeline

**Goal:** Create shared understanding of what happened and when.

#### 2.1 Timeline Construction

```
Method: Reconstruction with specificity

2:00 PM - Configuration change deployed
         - What: Changed timeout_ms = "5000" → 5000
         - Why: Optimization attempt (developer thought it would be faster)
         - Who: Engineer John (approved by lead Mary)
         - How: Normal deployment process (no canary, went 100% immediately)

2:05 PM - Error rate spiked to 100%
         - Alert fired automatically
         - On-call engineer Sarah paged

2:06 PM - Sarah confirmed: API returning 500 errors
         - All requests timing out
         - Database unreachable (seemed)

2:08 PM - Incident commander declared SEV1
         - Full team activated
         - Status page updated

2:10 PM - Database team investigated
         - Database responding normally
         - Confirmed not a database issue

2:15 PM - Application team traced logs
         - Timeout happening on every request
         - Traced to config change 5 minutes prior
         - Realized: timeout_ms should be string "5000ms", not integer 5000

2:20 PM - Rollback initiated
         - Reverted deployment to previous version
         - Took 5 minutes (validation + rolling restart)

2:25 PM - Error rate dropped to 0.05%
         - Service back to normal
         - All-clear sent

2:30 PM - Post-incident monitoring
         - Verified no cascading failures
         - Checked for customer complaints
         - Closed incident ticket
```

#### 1.2 Timeline Review

```
Ask each participant:
"Is your timeline accurate? Any events I'm missing?"

Check for gaps:
- "Who noticed the problem first?" (was there detection lag?)
- "Who made the call to rollback?" (was there decision delay?)
- "Was anyone waiting for someone else?" (were there blockers?)

Final timeline with delays identified:
2:00 PM - Config deployed
(5 min detection lag due to alert batch window)
2:05 PM - Alert fires ← Detection lag: 5 minutes
2:06 PM - On-call pages
(2 min response lag - Sarah was in meeting)
2:08 PM - Incident commander arrives ← Response lag: 2 minutes
(7 min diagnosis lag - took time to eliminate database)
2:15 PM - Root cause identified ← Diagnosis lag: 7 minutes
(5 min remediation lag - rolling restart takes time)
2:20 PM - Rollback started
(5 min rollback lag - validation + deployment)
2:25 PM - Service restored ← Total: 25 minutes

Without these delays:
- Detection lag: -5 min = 2:00 PM incident start
- Response lag: -2 min = 2:01 PM incident commander
- Diagnosis lag: -3 min (if had better monitoring) = 2:12 PM found it
- Remediation lag: -2 min (if had faster deploy) = 2:18 PM fixed
- Total: Could have been 18 minutes instead of 25
```

---

### 3. Root Cause Analysis (5 Whys)

**Goal:** Understand not just the immediate cause, but the underlying system failures.

#### 3.1 Five Whys Technique

```
Level 1: What happened?
"API requests started timing out and failing"

Why 1: Why did requests time out?
"Configuration changed timeout from 5 seconds to 5 milliseconds"

Why 2: Why was timeout changed to 5 milliseconds?
"Developer tried to optimize but made a mistake in format
(used integer 5000 instead of string '5000ms')"

Why 3: Why didn't we catch the mistake before deploy?
"No validation of configuration format - code accepted either format
No testing for configuration changes
Config deployed to 100% at once instead of canary"

Why 4: Why is there no configuration validation?
"Wasn't considered important - "config files are simple"
No code review for config changes
No schema validation framework in place"

Why 5: Why wasn't this prevented earlier?
"Lack of configuration governance
No monitoring of configuration changes
No runbook for config debugging"

Root cause: Lack of configuration governance and validation framework
Contributing factors:
- No config validation on deploy
- No schema enforcement
- No canary deployments
- Limited monitoring of config changes
- No runbook for config troubleshooting
```

#### 3.2 Avoid False Roots

```
Common mistakes in RCA:

FALSE ROOT: "Developer made a typo"
- Blames individual, not system
- Doesn't prevent recurrence (can't prevent typos)
- Creates defensive culture

TRUE ROOT: "Configuration format not validated"
- Addresses system failure
- Prevents recurrence (add validation)
- Points to improvement

FALSE ROOT: "Alert was slow"
- Blames monitoring
- But 5-minute delay wasn't the main issue

TRUE ROOT: "Config went to 100% immediately"
- Canary deployment would have caught in first 5%
- Prevented full outage

Guidance: Always ask "How do we prevent this class of error?"
Answer that question = real root cause
```

---

### 4. Identify Contributing Factors

**Goal:** Recognize all system failures that enabled the incident.

#### 4.1 Contributing Factor Analysis

```
Configuration Format Validation Missing:
- Severity: HIGH (easy to implement, high impact)
- Prevention: Add JSON schema validation
- Cost: 2 hours of engineering
- Benefit: Catches config errors before deploy

Canary Deployment Not Used:
- Severity: HIGH (best practice, not followed)
- Prevention: Enforce canary for all config changes
- Cost: Deployment process change
- Benefit: 5% of users exposed vs. 100%

No Monitoring of Config Changes:
- Severity: MEDIUM (nice to have)
- Prevention: Alert when config changes at deploy time
- Cost: 1 hour logging integration
- Benefit: Faster debugging

Configuration Rollback Not Automated:
- Severity: MEDIUM (made recovery slower)
- Prevention: Automated rollback for failed deployments
- Cost: Deployment system enhancement
- Benefit: 1-minute recovery instead of 5 minutes

Lack of Configuration Runbook:
- Severity: LOW (how-to guide for debugging)
- Prevention: Create and test runbook
- Cost: 1 hour documentation
- Benefit: Faster diagnosis next time
```

---

### 5. Generate Action Items

**Goal:** Create specific, measurable improvements.

#### 5.1 Action Item Template

```
Action Item #1: Add configuration schema validation

Description:
Before deploying any configuration change, validate against JSON schema
that enforces timeout_ms must be a string, not integer.
Catches format errors before deployment.

Acceptance Criteria:
- [ ] JSON schema defined for all configs
- [ ] Validation runs in CI/CD pipeline
- [ ] Deployment fails if schema validation fails
- [ ] Tested with invalid config (deployment blocked)

Owner: DevOps Engineer (Sarah)
Due: 2 weeks

Priority: HIGH (quick win, high impact)
Status: PLANNED

---

Action Item #2: Implement canary deployments for config

Description:
All configuration changes should follow canary pattern:
5% of servers → 50% → 100%
with monitoring between stages.

Acceptance Criteria:
- [ ] Canary deployment process documented
- [ ] Canary deployment tool configured
- [ ] All team members trained
- [ ] Config changes require canary approval

Owner: Infrastructure Team
Due: 4 weeks

Priority: HIGH
Status: PLANNED

---

Action Item #3: Add configuration change monitoring

Description:
Alert when configuration changes during deployment,
log all changes to audit trail for debugging.

Acceptance Criteria:
- [ ] Alert configured for config changes
- [ ] Audit log captures who/when/what changed
- [ ] Searchable in log system
- [ ] Team alerted on anomalies

Owner: Monitoring Team
Due: 2 weeks

Priority: MEDIUM
Status: PLANNED
```

---

### 6. Assign Owners & Due Dates

#### 6.1 Action Item Tracking

```
Postmortem Outcomes Summary:

Action Items (5 total):
1. Config schema validation - Sarah (DevOps) - 2 weeks - HIGH
2. Canary deployment process - Infrastructure team - 4 weeks - HIGH
3. Config change monitoring - Monitoring team - 2 weeks - MEDIUM
4. Configuration runbook - Documentation - 3 days - LOW
5. Team training on config debugging - QA - 1 week - LOW

Total effort: ~40 hours engineering
Time to full prevention: 4 weeks (canary is critical path)
Time to partial prevention: 2 weeks (validation + runbook)

Follow-up:
- Weekly: Track action item progress
- 4 weeks: Verify all items completed
- 8 weeks: Verify effectiveness (measure: zero config incidents)
```

---

### 7. Share Learnings

**Goal:** Distribute knowledge to prevent similar incidents.

#### 7.1 Documentation & Communication

```
Create blameless postmortem document:

Title: Postmortem - API Timeout Incident April 10, 2026
Date: April 11, 2026
Duration: 20 minutes (2:05-2:25 PM UTC)
Severity: SEV1

Timeline: [documented above]
Root Cause: Configuration validation missing
Contributing Factors: [5 factors analyzed]
Action Items: [5 items with owners and due dates]

Key Learning:
"Configuration changes bypass code review safeguards.
We need to treat config as code with same validation."

Takeaway:
"Even 'simple' things like config files need governance.
Automate validation rather than relying on humans."

Share with:
1. Engineering team (Slack announcement)
2. Product team (how it happened, what we're fixing)
3. Customers (transparency + trust)
4. New team members (training material)
5. All-hands (company-wide learning)
```

---

## Common Pitfalls

- **Blame hunting:** "Who deployed the bad config?"
- **Shallow RCA:** Stop at "developer made a mistake"
- **No follow-through:** Action items assigned but never done
- **Unrealistic timeline:** 4 weeks to fix something that needed fixing now
- **No blameless culture:** Defensive responses prevent honest discussion

## Success Criteria

- ✓ Timeline documented and agreed by all
- ✓ Root cause identified (system failure, not individual)
- ✓ Contributing factors analysis complete
- ✓ 3-5 action items assigned with owners
- ✓ Timeline realistic and achievable
- ✓ Team feels heard and learns something
- ✓ Action items 80% complete within target dates
- ✓ Similar incidents decrease by 90% next quarter
