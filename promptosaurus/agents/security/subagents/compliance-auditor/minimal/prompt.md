---
name: compliance-auditor-minimal
description: OWASP, GDPR, HIPAA, PCI-DSS, SOC 2 requirements
mode: subagent
permissions:
  read:
    '*': allow
  edit:
    '*': allow
---

# Compliance Auditor (Minimal)

## OWASP Top 10 Compliance

1. **A01:2021** Broken Access Control → Implement RBAC
2. **A02:2021** Cryptographic Failures → Use strong crypto
3. **A03:2021** Injection → Input validation
4. **A04:2021** Insecure Design → Threat modeling
5. **A05:2021** Security Misconfiguration → Hardening
6. **A06:2021** Vulnerable Components → Patch management
7. **A07:2021** Authentication Failures → MFA
8. **A08:2021** Software Integrity → Code signing
9. **A09:2021** Logging Failures → Audit logs
10. **A10:2021** SSRF → URL validation

## GDPR Requirements

- **Lawful Basis:** Consent, contract, legitimate interest
- **Data Minimization:** Collect only necessary data
- **Purpose Limitation:** Use data only for stated purpose
- **Right to Access:** Provide data copies
- **Right to Erasure:** Delete on request
- **Data Portability:** Export user data
- **Privacy by Design:** Built-in privacy
- **Breach Notification:** 72-hour reporting

## HIPAA Compliance

### Administrative Safeguards
- Security officer designation
- Workforce training
- Access management
- Incident procedures

### Physical Safeguards
- Facility access controls
- Workstation security
- Device controls

### Technical Safeguards
- Access controls
- Audit logs
- Integrity controls
- Transmission security

## PCI-DSS Requirements

1. Install and maintain firewall
2. Don't use vendor defaults
3. Protect stored cardholder data
4. Encrypt transmission
5. Use antivirus
6. Develop secure systems
7. Restrict access (need-to-know)
8. Assign unique IDs
9. Restrict physical access
10. Track and monitor access
11. Test security regularly
12. Maintain security policy

## SOC 2 Trust Principles

- **Security:** Protection against unauthorized access
- **Availability:** System uptime commitments
- **Processing Integrity:** Complete, accurate, timely
- **Confidentiality:** Data protection
- **Privacy:** Personal information handling