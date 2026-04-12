---
name: "Dependency Scanning"
description: "Identify and manage vulnerabilities in third-party dependencies"
agent: "security"
category: "security"
related_workflows:
  - vulnerability-scanning-workflow
  - security-code-review
  - compliance-audit-workflow
---

# Dependency Scanning

Detect and remediate vulnerabilities in third-party libraries and components.

## Quick Steps

1. **Inventory dependencies** - Direct and transitive
2. **Scan for vulnerabilities** - CVE database matching
3. **Assess impact** - Exploitability in your context
4. **Prioritize updates** - Critical and high severity first
5. **Test updates** - Compatibility verification
6. **Deploy patches** - Staged rollout
7. **Monitor continuously** - Automated scanning

## Scanning Tools

- **npm/yarn audit** - JavaScript dependencies
- **pip-audit** - Python packages
- **OWASP Dependency-Check** - Multi-language
- **Snyk** - Commercial SCA tool
- **GitHub Dependabot** - Automated PRs

## Critical Checks

- [ ] All dependencies documented (OWASP A06-2021)
- [ ] License compliance verified
- [ ] Critical CVEs patched within 24 hours
- [ ] Transitive dependencies scanned
- [ ] Update strategy documented

## Example Output

```bash
┌───────────────┬──────────────────────────────┐
│ Severity      │ Vulnerable Package           │
├───────────────┼──────────────────────────────┤
│ Critical      │ log4j@2.14.1 (CVE-2021-44228)│
│ High          │ spring-core@5.2.1            │
└───────────────┴──────────────────────────────┘
```