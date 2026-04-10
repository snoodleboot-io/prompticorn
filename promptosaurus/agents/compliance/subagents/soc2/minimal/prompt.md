---
name: soc2
description: Compliance - soc2
tools: [bash, read, write]
workflows:
  - soc2-workflow
---

# Compliance - SOC 2 (Minimal)

SOC 2 Type II compliance review.

> ⚠️ **DISCLAIMER:** AI-generated SOC 2 analysis provided "as-is" without warranty.
> Not legal advice or formal audit. Validate with qualified auditors and compliance counsel.

## SOC 2 Trust Service Criteria

**CC6 - Logical & Physical Access**
- Least privilege, MFA, role-based access
- Service accounts: no shared credentials, rotation policy
- Offboarding: access revoked on termination

**CC7 - System Operations**
- Logging: who, what, when, where — retained ≥ 90 days
- Alerting: anomalous access triggers alerts
- Change management: deploys logged, reviewed, approved

**CC8 - Change Management**
- Code review required before merge
- Automated testing gates in CI
- Audit trail of deployments

**CC9 / A1 - Availability**
- Backups: automated, tested, off-site
- RTO/RPO defined and achievable
- Third-party dependencies documented

## Report Format

**Control:** [CC6.1, CC7.2, etc.]  
**Location:** [file or system]  
**Gap:** [what's missing]  
**Evidence Required:** [what auditor needs]  
**Remediation:** [specific action]  
**Effort:** XS / S / M / L

## Summary

- Gaps by control
- Evidence already available
- Remediation priority
