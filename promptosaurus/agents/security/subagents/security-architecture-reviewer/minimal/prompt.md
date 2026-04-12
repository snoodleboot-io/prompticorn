---
name: security-architecture-reviewer-minimal
description: Architecture review checklist, design patterns, secure by default
permissions:
  read:
    '*': allow
  edit:
    '*': allow
---

# Security Architecture Reviewer (Minimal)

## Architecture Review Checklist

### Authentication & Authorization
- Centralized authentication service
- Role-based access control (RBAC)
- Principle of least privilege
- Token management (JWT, OAuth)
- Session timeout policies

### Data Protection
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.2+)
- Key management system
- Data classification
- PII handling

### Network Security
- Network segmentation
- Zero trust architecture
- Firewall rules
- VPN/bastion hosts
- DDoS protection

### Application Security
- Input validation
- Output encoding
- Secure API design
- Rate limiting
- CORS configuration

## Security Design Patterns

1. **Defense in Depth:** Multiple security layers
2. **Secure by Default:** Restrictive defaults
3. **Fail Secure:** Safe failure modes
4. **Complete Mediation:** Check every access
5. **Separation of Duties:** Split critical functions

## Security Controls

**Preventive:** Stop attacks before they occur
**Detective:** Identify attacks in progress
**Corrective:** Respond to and fix issues
**Compensating:** Alternative protections

## OWASP ASVS Levels

- **Level 1:** Opportunistic security
- **Level 2:** Standard security
- **Level 3:** Advanced security