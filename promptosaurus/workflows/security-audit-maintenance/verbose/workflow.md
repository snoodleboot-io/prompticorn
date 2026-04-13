---
name: security-audit-maintenance
type: workflow
category: workflow-patterns
minimal: false
---
# Security Audit Workflow

**Version:** 1.0  
**Cadence:** Monthly (First Wednesday)  
**Owner:** Security Team / Engineering  
**Status:** Active

---

## Quick Reference

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

---

## Areas to Check

### 1. Dependencies (10 min)
**Command:** `pip-audit --desc`

**What to look for:**
- CVEs with CVSS score > 5.0 (medium or higher)
- Critical vulnerabilities (CVSS 9+) = immediate action
- Check affected version ranges
- Verify project version is affected

**Action:**
- P0 (Critical): Update immediately, commit, deploy
- P1 (High): Update in next release cycle
- P2 (Medium): Include in monthly dependency update
- P3 (Low): Document and defer

### 2. Code Security (15 min)
**Command:** `bandit -r promptosaurus/ -f json`

**What to look for:**
- Hardcoded secrets (API keys, passwords)
- Unsafe SQL construction
- Insecure deserialization
- Insecure random generation
- Use of eval/exec

**Action:**
- Hardcoded secrets: Remove immediately, use env vars
- SQL injection risks: Use parameterized queries
- Unsafe deserialization: Use safe parsers
- Other issues: Fix per severity

### 3. Type Safety (10 min)
**Command:** `pyright --outputjson`

**What to look for:**
- Any `# type: ignore` comments (should be rare)
- `Any` types (should be explicit narrowing)
- Type coercion without validation
- Unchecked external input

**Action:**
- Remove all unnecessary `# type: ignore`
- Replace `Any` with specific types
- Add input validation where needed

### 4. Secrets Detection (5 min)
**Command:** `detect-secrets scan --baseline .secrets.baseline`

**What to look for:**
- API keys in code
- Passwords in comments
- Private keys
- Auth tokens

**Action:**
- Move to .env (never commit)
- Use env vars in code
- Rotate exposed keys immediately
- Update baseline after fixing

---

## Monthly Audit Report Template

```markdown
# Security Audit Report
**Date:** YYYY-MM-DD
**Auditor:** [Name]

## Summary
- Critical vulnerabilities: X
- High vulnerabilities: X
- Medium vulnerabilities: X
- Code issues found: X
- Status: ✅ PASS / ⚠️ ACTION NEEDED

## Findings

### Dependency Vulnerabilities
[List any CVEs found]

### Code Security Issues
[List any bandit findings]

### Type Safety Issues
[List any type errors]

### Secrets Detected
[List any secrets found]

## Actions Taken
- [Action 1]
- [Action 2]

## Recommendations
- [Recommendation 1]
- [Recommendation 2]

## Next Audit
[Date of next audit]
```

---

## Decision Tree

**Critical vulnerability found?**
- YES: Update immediately, test, deploy same day
- NO: Continue to next check

**Hardcoded secret found?**
- YES: Remove, rotate secret, commit fix immediately
- NO: Continue to code security checks

**Type safety issues found?**
- HIGH count: Schedule focused cleanup session
- LOW count: Fix as part of next PR

**Multiple high-risk findings?**
- YES: Schedule security review with team
- NO: Document and track in issues

---

## Incident Response (Critical Vuln Found)

1. **Assess impact (5 min)**
   - Is project version affected?
   - Can it be exploited in current usage?
   - What's the CVSS score?

2. **Patch immediately (15 min)**
   - Update dependency
   - Run full test suite
   - Verify fix

3. **Deploy (10 min)**
   - Commit with security flag
   - Push to main
   - Monitor CI/CD

4. **Document (5 min)**
   - Create security advisory entry
   - Log in audit report
   - Notify stakeholders if severe

---

## Tools Configuration

### .secrets.baseline
(If not exist, create with `detect-secrets scan --baseline`)
Tracks known secrets that are OK (test credentials, etc)

### .bandit
Configure in pyproject.toml:
```toml
[tool.bandit]
exclude_dirs = ["tests", ".venv"]
skips = []  # Don't skip security checks
```

### pyright
Use strict mode (configured in project)

