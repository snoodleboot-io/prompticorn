---
name: security-code-review
description: "Manual and automated review of code for security vulnerabilities"
agent: "security"
category: "security"
related_workflows:
  - security-testing-workflow
  - dependency-scanning-workflow
  - vulnerability-scanning-workflow
---

# Security Code Review

Systematic review of source code to identify security vulnerabilities.

## Quick Steps

1. **Prepare review** - Gather code, docs, threat model
2. **Automated scan** - SAST tools analysis
3. **Manual review** - High-risk code paths
4. **Check security patterns** - Authentication, crypto, validation
5. **Document findings** - Severity and remediation
6. **Developer discussion** - Review findings together
7. **Verify fixes** - Re-review remediated code

## Focus Areas

- **Input Validation** - Injection prevention (A03-2021)
- **Authentication** - Secure implementation (A07-2021)
- **Cryptography** - Proper usage (A02-2021)
- **Access Control** - Authorization checks (A01-2021)
- **Error Handling** - Information leakage (A09-2021)

## Critical Checks

- [ ] SQL queries parameterized
- [ ] User input sanitized and validated
- [ ] Secrets not hardcoded
- [ ] CSRF protection implemented
- [ ] Security libraries up to date

## Example Issue

```python
# VULNERABLE: SQL Injection
query = f"SELECT * FROM users WHERE id = {user_id}"
# SECURE: Parameterized query
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```