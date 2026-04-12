---
name: "Secret Management"
description: "Secure handling of sensitive credentials and cryptographic keys"
agent: "security"
category: "security"
related_workflows:
  - security-hardening-checklist
  - compliance-audit-workflow
  - security-code-review
---

# Secret Management

Secure storage, rotation, and access control for sensitive credentials.

## Quick Steps

1. **Identify secrets** - API keys, passwords, certificates
2. **Remove from code** - Extract hardcoded secrets
3. **Implement vault** - HashiCorp Vault, AWS Secrets Manager
4. **Configure access** - Least privilege policies
5. **Enable rotation** - Automated credential refresh
6. **Audit usage** - Access logging and monitoring
7. **Test recovery** - Disaster recovery procedures

## Secret Types

- **API Keys** - Third-party service credentials
- **Database** - Connection strings and passwords
- **Certificates** - TLS/SSL certificates and keys
- **Encryption Keys** - Data encryption keys
- **SSH Keys** - Infrastructure access keys

## Critical Checks

- [ ] No secrets in source code (OWASP A07-2021)
- [ ] Secrets encrypted at rest (A02-2021)
- [ ] Access logged and monitored
- [ ] Rotation policy enforced
- [ ] Break-glass procedure tested

## Example Configuration

```yaml
# vault policy
path "secret/data/prod/*" {
  capabilities = ["read"]
  min_wrapping_ttl = "1h"
  max_wrapping_ttl = "24h"
}
```