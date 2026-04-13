---
name: security-hardening-checklist
description: "Comprehensive checklist for hardening systems against attacks"
agent: "security"
category: "security"
related_workflows:
  - vulnerability-scanning-workflow
  - compliance-audit-workflow
  - security-testing-workflow
---

# Security Hardening Checklist

Systematic hardening of systems, applications, and infrastructure.

## Quick Steps

1. **Baseline assessment** - Current security posture
2. **Apply OS hardening** - CIS benchmarks
3. **Configure network security** - Firewalls, segmentation
4. **Harden applications** - Secure defaults
5. **Implement monitoring** - Logging and alerting
6. **Document changes** - Configuration management
7. **Verify hardening** - Security validation

## Hardening Categories

- **OS Level** - Patches, services, permissions
- **Network** - Firewall rules, VLANs, ACLs
- **Application** - Security headers, TLS, session config
- **Database** - Encryption, access controls, auditing
- **Cloud** - IAM, security groups, encryption

## Critical Checks

- [ ] Default credentials changed (OWASP A07-2021)
- [ ] Unnecessary services disabled
- [ ] Security patches current (A06-2021)
- [ ] TLS 1.2+ enforced (A02-2021)
- [ ] Least privilege implemented

## Example Hardening

```bash
# Disable unnecessary services
systemctl disable telnet.service
systemctl disable ftp.service
# Set secure kernel parameters
echo "net.ipv4.tcp_syncookies = 1" >> /etc/sysctl.conf
```