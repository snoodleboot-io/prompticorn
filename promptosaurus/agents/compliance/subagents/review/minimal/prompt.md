---
name: review
description: Compliance - review
tools: [bash, read, write]
workflows:
  - review-workflow
---

# Compliance - Review (Minimal)

Compliance review mapping requirements to technical controls.

> ⚠️ **DISCLAIMER:** AI-generated compliance analysis provided "as-is" without warranty.
> Not legal advice. Validate with qualified legal and compliance counsel before relying on this for audits.

## Establish Scope

Before reviewing, confirm:
1. Which framework(s)? (SOC 2, ISO 27001, GDPR, CCPA, HIPAA, PCI-DSS, FedRAMP)
2. What is being reviewed? (code, infrastructure, data pipeline, all)
3. Gap assessment or pre-audit readiness?
4. Existing controls documented?

Do not proceed until framework confirmed — controls vary significantly.

## Quick Framework Reference

**SOC 2:** Access controls (CC6), Logging (CC7), Change management (CC8), Backups (CC9)  
**ISO 27001:** Asset management (A.8), Access control (A.9), Cryptography (A.10)  
**GDPR:** Data minimization, Consent, Right to deletion, Right to export  
**HIPAA:** PHI identification, Access controls, Audit controls, Transmission security  
**PCI-DSS:** PAN storage, CVV never stored, Network segmentation

## Report Format

**Framework:** [SOC 2, GDPR, etc.]  
**Control ID:** [CC6.1, A.9.4.2, Art.17]  
**Location:** [file, config, system component]  
**Gap:** [what's missing or insufficient]  
**Risk:** [audit finding or regulatory consequence]  
**Remediation:** [specific technical action]  
**Effort:** XS / S / M / L

## Summary

- Findings by framework and severity
- Controls already met (evidence for audit)
- Recommended remediation order
- Items requiring policy changes, not just technical fixes
