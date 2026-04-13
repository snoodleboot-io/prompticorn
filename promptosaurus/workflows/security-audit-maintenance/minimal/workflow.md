---
name: security-audit-maintenance
type: workflow
category: workflow-patterns
minimal: true
---
# Security Audit Workflow

**Version:** 1.0

### Monthly Security Audit (2 hours)

```bash
cd /home/john_aven/Documents/software/promptosaurus

# 1. Dependency vulnerabilities
pip-audit --desc > security-report-deps.txt

# 2. Code security scan
bandit -r promptosaurus/ -f json > security-report-code.json

# 3. Type checking (catches some unsafe patterns)
pyright --outputjson | jq .

# 4. Secrets scan
detect-secrets scan --baseline .secrets.baseline
```