---
name: "Penetration Testing Guide"
description: "Ethical hacking methodology to identify exploitable vulnerabilities"
agent: "security"
category: "security"
related_workflows:
  - vulnerability-scanning-workflow
  - security-testing-workflow
  - threat-modeling-workflow
---

# Penetration Testing Guide

Simulated attacks to identify and exploit security weaknesses.

## Quick Steps

1. **Scoping** - Define targets and rules of engagement
2. **Reconnaissance** - Information gathering
3. **Enumeration** - Service and vulnerability discovery
4. **Exploitation** - Attempt to breach security
5. **Post-exploitation** - Lateral movement, privilege escalation
6. **Reporting** - Findings and recommendations
7. **Remediation verification** - Retest fixed issues

## Testing Types

- **Black Box** - No prior knowledge
- **Grey Box** - Limited knowledge
- **White Box** - Full knowledge
- **Red Team** - Advanced persistent threat simulation
- **Purple Team** - Collaborative testing

## Critical Checks

- [ ] Written authorization obtained
- [ ] OWASP Top 10 vectors tested
- [ ] Social engineering included (if authorized)
- [ ] Data exfiltration paths identified
- [ ] Executive report prepared

## Example Finding

```yaml
vulnerability: Remote Code Execution
cvss_score: 9.8
exploit_path: "Upload malicious file → Execute via LFI"
impact: "Full system compromise"
remediation: "Input validation, file type restrictions"
```