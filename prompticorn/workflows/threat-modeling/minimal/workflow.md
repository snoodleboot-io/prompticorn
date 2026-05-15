---
name: "threat-modeling"
description: "Systematic identification and analysis of security threats"
agent: "security"
category: "security"
related_workflows:
  - security-testing-workflow
  - vulnerability-scanning-workflow
  - penetration-testing-guide
---

# Threat Modeling

Identify and assess potential security threats before they become vulnerabilities.

## Quick Steps

1. **Define scope** - System boundaries and assets
2. **Create architecture diagrams** - Data flow diagrams (DFD)
3. **Identify threats** - Apply STRIDE methodology
4. **Document threats** - Risk matrix and threat catalog
5. **Prioritize risks** - DREAD scoring or CVSS
6. **Define mitigations** - Security controls and countermeasures
7. **Validate model** - Review with stakeholders

## STRIDE Framework

- **S**poofing - Authentication threats
- **T**ampering - Data integrity threats
- **R**epudiation - Non-repudiation threats
- **I**nformation Disclosure - Confidentiality threats
- **D**enial of Service - Availability threats
- **E**levation of Privilege - Authorization threats

## Critical Checks

- [ ] All entry points identified (OWASP Top 10: A07-2021)
- [ ] Trust boundaries documented
- [ ] Data flows mapped with sensitivity levels
- [ ] Attack vectors enumerated
- [ ] Risk ratings assigned using consistent methodology

## Example Output

```yaml
threat_id: THR-001
category: Spoofing
asset: User Authentication
risk_level: High
mitigation: Implement MFA
```