---
name: incident-response-security
description: "Structured approach to handling security incidents and breaches"
agent: "security"
category: "security"
related_workflows:
  - vulnerability-scanning-workflow
  - compliance-audit-workflow
  - threat-modeling-workflow
---

# Incident Response Security

Rapid and effective response to security incidents and breaches.

## Quick Steps

1. **Detection** - Identify potential incident
2. **Triage** - Assess severity and scope
3. **Containment** - Limit damage and spread
4. **Investigation** - Root cause analysis
5. **Eradication** - Remove threat completely
6. **Recovery** - Restore normal operations
7. **Lessons learned** - Post-incident review

## Incident Severity

- **Critical** - Active breach, data exfiltration
- **High** - System compromise, ransomware
- **Medium** - Malware detection, suspicious activity
- **Low** - Policy violations, false positives

## Critical Checks

- [ ] Incident response team notified within 15 minutes
- [ ] Evidence preserved (chain of custody)
- [ ] Communication plan activated
- [ ] Regulatory notifications sent (GDPR 72-hour rule)
- [ ] Root cause identified and patched

## Example Timeline

```
T+0min: Alert received - suspicious database queries
T+5min: Triage complete - SQL injection confirmed
T+15min: Database isolated, web server taken offline
T+30min: Forensic image captured
T+2hr: Patch deployed, systems restored
```