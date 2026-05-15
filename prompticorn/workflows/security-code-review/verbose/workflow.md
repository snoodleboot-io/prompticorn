---
name: "security-code-review"
description: "Manual and automated review of code for security vulnerabilities"
agent: "security"
category: "security"
related_workflows:
  - security-testing-workflow
  - dependency-scanning-workflow
  - vulnerability-scanning-workflow
---

# Security Code Review - Comprehensive Guide

## Overview

Security code review is the systematic examination of source code to identify security flaws, vulnerabilities, and deviations from secure coding practices. This process combines automated scanning tools with manual review to ensure comprehensive coverage of potential security issues.

## Prerequisites

### Knowledge Requirements
- Understanding of secure coding principles
- Familiarity with OWASP Top 10
- Knowledge of common vulnerability patterns
- Language-specific security considerations
- Understanding of cryptography basics

### Tools and Resources
- **SAST Tools**: SonarQube, Fortify, Checkmarx, Semgrep
- **IDE Plugins**: SonarLint, SpotBugs, ESLint Security
- **Manual Review Tools**: GitHub Security, GitLab SAST
- **Reference Materials**: OWASP guides, CWE database

## Code Review Process

### Step 1: Preparation Phase

**1.1 Gather Context**
```python
def prepare_security_review(project):
    review_context = {
        "architecture": load_architecture_docs(),
        "threat_model": load_threat_model(),
        "data_flow": map_data_flows(),
        "security_requirements": get_security_requirements(),
        "previous_findings": load_historical_issues(),
        "dependencies": analyze_dependencies(),
        "frameworks": identify_frameworks(),
        "authentication_method": identify_auth_mechanism()
    }
    return review_context
```

**1.2 Define Review Scope**
```yaml
review_scope:
  included:
    - source_code: ["src/", "lib/", "api/"]
    - configurations: ["config/", "*.yml", "*.json"]
    - infrastructure: ["terraform/", "kubernetes/"]
    - scripts: ["scripts/", "deploy/"]
    - tests: ["test/", "spec/"]
  
  excluded:
    - third_party: ["vendor/", "node_modules/"]
    - generated: ["dist/", "build/"]
    - documentation: ["docs/"]
  
  priority_areas:
    - authentication: ["auth/", "login/"]
    - authorization: ["rbac/", "permissions/"]
    - data_handling: ["database/", "encryption/"]
    - external_interfaces: ["api/", "webhooks/"]
```

### Step 2: Automated Scanning

**2.1 SAST Configuration**
```json
// sonarqube-project.properties
{
  "sonar.projectKey": "security-review",
  "sonar.sources": "src",
  "sonar.tests": "test",
  "sonar.security.hotspots.maxIssues": "0",
  "sonar.security.vulnerabilities.maxIssues": "0",
  "sonar.javascript.security.eslint.enable": true,
  "sonar.python.security.bandit.enable": true,
  "sonar.java.security.spotbugs.enable": true
}
```

**2.2 Custom Security Rules with Semgrep**
```yaml
rules:
  - id: hardcoded-secret
    pattern-either:
      - pattern: $KEY = "..."
      - pattern: password = "..."
      - pattern: api_key = "..."
    message: "Hardcoded secret detected"
    languages: [python, javascript, java]
    severity: ERROR
    
  - id: sql-injection
    pattern-either:
      - pattern: |`
          $QUERY = "SELECT * FROM users WHERE id = " + $INPUT
      - pattern: |
          cursor.execute("..." + $INPUT)
    message: "Potential SQL injection"
    severity: ERROR
    
  - id: path-traversal
    pattern: |
      open($PATH + $USER_INPUT)
    message: "Potential path traversal vulnerability"
    severity: ERROR
```

### Step 3: Manual Review Focus Areas

#### Authentication and Session Management

**3.1 Authentication Review Checklist**
```python
def review_authentication():
    checks = [
        {
            "check": "Password Storage",
            "verify": [
                "Uses bcrypt, scrypt, or Argon2",
                "Salt is unique per password",
                "Work factor is appropriate (>10 rounds)"
            ],
            "code_pattern": r"(bcrypt|scrypt|argon2|pbkdf2)",
            "owasp": "A02-2021"
        },
        {
            "check": "Session Management",
            "verify": [
                "Session ID regenerated on login",
                "Secure and HttpOnly flags set",
                "Appropriate timeout configured",
                "Sessions invalidated on logout"
            ],
            "code_pattern": r"(session\.regenerate|sessionid|set_cookie)",
            "owasp": "A07-2021"
        },
        {
            "check": "Multi-Factor Authentication",
            "verify": [
                "MFA available for sensitive operations",
                "TOTP/SMS/Hardware tokens supported",
                "Backup codes implemented"
            ],
            "code_pattern": r"(totp|mfa|two_factor|authenticator)",
            "owasp": "A07-2021"
        }
    ]
    return perform_checks(checks)
```

#### Authorization and Access Control

**3.2 Authorization Review**
```python
class AuthorizationReview:
    def check_access_control(self, code_base):
        issues = []
        
        # Check for missing authorization
        patterns = [
            r"@app\.route.*(?!@authorize)",  # Routes without auth decorator
            r"def (delete|update|create).*(?!check_permission)",  # CRUD without permission check
            r"SELECT.*FROM.*WHERE.*(?!user_id|owner)",  # Queries without user context
        ]
        
        for pattern in patterns:
            matches = search_codebase(pattern, code_base)
            for match in matches:
                issues.append({
                    "type": "Missing Authorization",
                    "location": match.location,
                    "severity": "High",
                    "owasp": "A01-2021"
                })
        
        # Check for IDOR vulnerabilities
        idor_patterns = [
            r"/api/users/([0-9]+)",  # Direct ID reference
            r"WHERE id = \$1(?!.*AND user_id)",  # No user context in query
        ]
        
        for pattern in idor_patterns:
            matches = search_codebase(pattern, code_base)
            for match in matches:
                issues.append({
                    "type": "Potential IDOR",
                    "location": match.location,
                    "severity": "High",
                    "owasp": "A01-2021"
                })
        
        return issues
```

#### Input Validation and Sanitization

**3.3 Input Validation Review**
```python
def review_input_validation(file_path):
    vulnerabilities = []
    
    # SQL Injection patterns
    sql_patterns = [
        (r'"SELECT.*\+.*\+', "SQL concatenation"),
        (r'f"SELECT.*{', "SQL f-string"),
        (r'\.format\(.*SELECT', "SQL format string"),
        (r'execute\([^?]*%[sd]', "SQL string interpolation")
    ]
    
    # XSS patterns
    xss_patterns = [
        (r'innerHTML\s*=\s*[^`]', "Direct innerHTML assignment"),
        (r'document\.write\(', "document.write usage"),
        (r'v-html=', "Vue.js v-html without sanitization"),
        (r'dangerouslySetInnerHTML', "React dangerous HTML")
    ]
    
    # Command Injection patterns
    cmd_patterns = [
        (r'os\.system\(.*\+', "Command concatenation"),
        (r'subprocess\.call\(.*shell=True', "Shell command execution"),
        (r'eval\(', "eval() usage"),
        (r'exec\(', "exec() usage")
    ]
    
    with open(file_path, 'r') as file:
        content = file.read()
        line_number = 0
        
        for line in content.split('\n'):
            line_number += 1
            
            # Check SQL injection
            for pattern, description in sql_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        "type": "SQL Injection",
                        "line": line_number,
                        "description": description,
                        "severity": "Critical",
                        "owasp": "A03-2021"
                    })
            
            # Check XSS
            for pattern, description in xss_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        "type": "Cross-Site Scripting",
                        "line": line_number,
                        "description": description,
                        "severity": "High",
                        "owasp": "A03-2021"
                    })
            
            # Check command injection
            for pattern, description in cmd_patterns:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        "type": "Command Injection",
                        "line": line_number,
                        "description": description,
                        "severity": "Critical",
                        "owasp": "A03-2021"
                    })
    
    return vulnerabilities
```

#### Cryptography and Secrets Management

**3.4 Cryptography Review**
```python
def review_cryptography():
    crypto_issues = []
    
    # Weak algorithms
    weak_crypto = {
        "MD5": "Use SHA-256 or better",
        "SHA1": "Use SHA-256 or better",
        "DES": "Use AES-256",
        "RC4": "Use AES-256-GCM",
        "ECB": "Use CBC or GCM mode",
        "Random()": "Use cryptographically secure random"
    }
    
    # Check for weak crypto usage
    for algo, recommendation in weak_crypto.items():
        usage = find_usage(algo)
        if usage:
            crypto_issues.append({
                "type": "Weak Cryptography",
                "algorithm": algo,
                "recommendation": recommendation,
                "locations": usage,
                "severity": "High",
                "owasp": "A02-2021"
            })
    
    # Check for hardcoded secrets
    secret_patterns = [
        r'["\']\w{40}["\']',  # SHA-1 like
        r'["\'][A-Za-z0-9+/]{40,}={0,2}["\']',  # Base64
        r'(api[_-]?key|secret|token|password)\s*=\s*["\'][^"\'
]{8,}["\']',
        r'BEGIN (RSA|DSA|EC) PRIVATE KEY'
    ]
    
    for pattern in secret_patterns:
        matches = search_pattern(pattern)
        if matches:
            crypto_issues.append({
                "type": "Hardcoded Secret",
                "pattern": pattern,
                "matches": len(matches),
                "severity": "Critical",
                "owasp": "A07-2021"
            })
    
    return crypto_issues
```

### Step 4: Business Logic Review

**4.1 Business Logic Security**
```python
class BusinessLogicReview:
    def review_business_logic(self, application_flow):
        issues = []
        
        # Race condition checks
        race_condition_areas = [
            "voucher_redemption",
            "account_transfer",
            "inventory_update",
            "payment_processing"
        ]
        
        for area in race_condition_areas:
            if not has_atomic_operations(area):
                issues.append({
                    "type": "Race Condition",
                    "area": area,
                    "impact": "Financial loss, data corruption",
                    "severity": "High"
                })
        
        # Price manipulation checks
        if allows_client_side_pricing():
            issues.append({
                "type": "Price Manipulation",
                "description": "Client can modify prices",
                "severity": "Critical"
            })
        
        # Workflow bypass checks
        workflows = [
            "registration_flow",
            "payment_flow",
            "approval_flow"
        ]
        
        for workflow in workflows:
            if can_skip_steps(workflow):
                issues.append({
                    "type": "Workflow Bypass",
                    "workflow": workflow,
                    "severity": "High"
                })
        
        return issues
```

### Step 5: Third-Party Dependencies

**5.1 Dependency Security Review**
```python
import json
import requests

def review_dependencies():
    vulnerabilities = []
    
    # JavaScript/Node.js
    if os.path.exists('package.json'):
        result = os.popen('npm audit --json').read()
        audit_data = json.loads(result)
        vulnerabilities.extend(parse_npm_audit(audit_data))
    
    # Python
    if os.path.exists('requirements.txt'):
        result = os.popen('safety check --json').read()
        safety_data = json.loads(result)
        vulnerabilities.extend(parse_safety_check(safety_data))
    
    # Java
    if os.path.exists('pom.xml'):
        result = os.popen('mvn dependency-check:check').read()
        vulnerabilities.extend(parse_dependency_check(result))
    
    # Check for outdated dependencies
    outdated = check_outdated_dependencies()
    for dep in outdated:
        if dep.age_months > 12:
            vulnerabilities.append({
                "type": "Outdated Dependency",
                "package": dep.name,
                "current": dep.current_version,
                "latest": dep.latest_version,
                "severity": "Medium"
            })
    
    return vulnerabilities
```

## Security Code Review Checklist

### Comprehensive Review Checklist

```markdown
## Security Code Review Checklist

### Authentication & Session Management
- [ ] Passwords hashed with strong algorithm (bcrypt/scrypt/Argon2)
- [ ] Session IDs regenerated after login
- [ ] Secure/HttpOnly flags on cookies
- [ ] Account lockout mechanism implemented
- [ ] MFA available for sensitive operations
- [ ] Password reset tokens expire
- [ ] No credentials in source code

### Authorization & Access Control
- [ ] All endpoints have authorization checks
- [ ] No IDOR vulnerabilities
- [ ] Principle of least privilege applied
- [ ] Role-based access control implemented
- [ ] No privilege escalation paths
- [ ] API rate limiting in place

### Input Validation & Output Encoding
- [ ] All inputs validated (whitelist approach)
- [ ] SQL queries use parameterization
- [ ] XSS prevention (output encoding)
- [ ] Path traversal prevention
- [ ] Command injection prevention
- [ ] XXE prevention in XML parsing
- [ ] SSRF prevention in URL handling

### Cryptography
- [ ] No weak algorithms (MD5, SHA1, DES)
- [ ] Proper key management
- [ ] No hardcoded secrets
- [ ] TLS 1.2+ enforced
- [ ] Certificate validation implemented
- [ ] Random number generation is secure

### Error Handling & Logging
- [ ] No stack traces in production
- [ ] Generic error messages to users
- [ ] Security events logged
- [ ] No sensitive data in logs
- [ ] Log injection prevention

### Data Protection
- [ ] PII data encrypted at rest
- [ ] Sensitive data encrypted in transit
- [ ] Data retention policies implemented
- [ ] Secure data disposal
- [ ] No sensitive data in URLs

### Third-Party Components
- [ ] Dependencies up to date
- [ ] Known vulnerabilities patched
- [ ] License compliance verified
- [ ] Minimal dependency footprint
- [ ] Supply chain security considered
```

## Reporting and Remediation

### Finding Report Template

```markdown
## Security Finding Report

### Finding ID: SEC-2024-001

**Title:** SQL Injection in User Search Function

**Severity:** Critical (CVSS 9.1)

**OWASP Category:** A03-2021 (Injection)

**CWE:** CWE-89 (SQL Injection)

### Description
The user search function in `/api/users/search` is vulnerable to SQL injection due to direct string concatenation of user input into the SQL query.

### Affected Code
```python
# File: api/users.py, Line 45
def search_users(query):
    sql = f"SELECT * FROM users WHERE name LIKE '%{query}%'"
    return db.execute(sql)
```

### Proof of Concept
```bash
curl "https://api.example.com/users/search?q=' OR '1'='1"
# Returns all users in database
```

### Impact
- Database compromise
- Data exfiltration
- Potential RCE via SQL functions
- Compliance violations (GDPR, PCI-DSS)

### Remediation

**Immediate Fix:**
```python
def search_users(query):
    sql = "SELECT * FROM users WHERE name LIKE ?"
    return db.execute(sql, (f"%{query}%",))
```

**Long-term Recommendations:**
1. Implement ORM (SQLAlchemy, Django ORM)
2. Use prepared statements for all queries
3. Input validation layer
4. Database user with minimal privileges
5. Web Application Firewall (WAF)

### References
- https://owasp.org/www-project-top-ten/2021/A03_2021-Injection/
- https://cwe.mitre.org/data/definitions/89.html
```

## Best Practices

### Review Process Best Practices
- ✓ Use threat model to guide review
- ✓ Combine automated and manual review
- ✓ Focus on high-risk areas first
- ✓ Review in small increments
- ✓ Collaborate with developers
- ✓ Document all findings
- ✓ Verify fixes with re-review

### Common Anti-Patterns to Identify
- ✗ Security through obscurity
- ✗ Client-side security controls
- ✗ Blacklist validation (use whitelist)
- ✗ Rolling custom crypto
- ✗ Trusting user input
- ✗ Insufficient logging

## Integration with Development

### CI/CD Integration

```yaml
# GitHub Actions security workflow

on:
  pull_request:
    branches: [main, develop]

jobs:
  security-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run SAST
        uses: github/super-linter@v4
        env:
          DEFAULT_BRANCH: main
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: SonarQube Scan
        uses: sonarsource/sonarqube-scan-action@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
      
      - name: Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: auto
      
      - name: Dependency Check
        run: |
          npm audit
          safety check
      
      - name: Security Gate
        run: |
          if [ "$CRITICAL_FINDINGS" -gt 0 ]; then
            echo "Critical security issues found"
            exit 1
          fi
```

## Metrics and KPIs

### Security Review Metrics
- Vulnerabilities found per KLOC
- Time to review per KLOC
- False positive rate
- Fix rate within SLA
- Repeat vulnerability rate
- Coverage of security controls

## References

- OWASP Code Review Guide
- OWASP Top 10 2021
- CWE Top 25
- SANS Secure Coding Guidelines
- NIST SP 800-64: Security Considerations in SDLC

## Conclusion

Security code review is an essential practice that must be integrated throughout the software development lifecycle. By combining automated tools with manual expertise and following systematic review processes, organizations can significantly reduce their vulnerability exposure and build more secure applications.