# security-review.md
# Behavior when the user asks for a security review of code or infrastructure.
#
# Scope: code and structural security issues only.
# Out of scope: compliance frameworks, policy, certifications — use Compliance mode for those.

## Before Reviewing

Read the code. Do not produce findings from assumptions.
Ask what the code does if it is not clear — context changes severity dramatically.

If given a diff or PR: also read the surrounding code the diff touches,
not just the changed lines.

## Review Categories — Work Through All of These

### 1. INJECTION
- SQL injection: string interpolation in queries, ORM raw() escape hatches
- Command injection: shell exec with user-controlled input
- Path traversal: file operations with unvalidated paths
- Template injection: user input rendered in server-side templates
- LDAP / XPath / NoSQL injection

### 2. AUTHENTICATION & SESSION
- Hardcoded credentials or secrets anywhere in code or config
- Secrets committed to version control (check .env files, comments, test fixtures)
- Weak or missing authentication on sensitive endpoints
- Session tokens: entropy, expiry, invalidation on logout
- JWT: algorithm confusion (none/HS256/RS256), missing expiry, missing signature validation

### 3. AUTHORIZATION
- Missing authorization checks (assumes authentication = authorization)
- Insecure direct object reference: can user A access user B's resource by changing an ID?
- Privilege escalation paths: can a low-privilege action trigger a high-privilege one?
- Mass assignment: are all user-supplied fields explicitly allowlisted?

### 4. CRYPTOGRAPHY
- Weak algorithms: MD5, SHA1, DES, RC4, ECB mode
- Hardcoded IV or salt
- Insufficient key length
- Using encryption where signing is needed (or vice versa)
- Random number generation using non-cryptographic sources

### 5. DATA EXPOSURE
- Sensitive fields (passwords, tokens, PII) logged or returned in API responses
- Stack traces or internal error details exposed to clients
- Overly permissive CORS configuration
- Sensitive data in URLs (query params, path segments) that appear in logs

### 6. INPUT VALIDATION
- Missing length limits on user input
- Type coercion surprises (especially in dynamic languages)
- Regex denial of service (ReDoS): catastrophic backtracking patterns
- File upload: missing type validation, missing size limits, executable content

### 7. DEPENDENCY & SUPPLY CHAIN
- Known vulnerable dependency versions (flag for CVE lookup — do not assume safe)
- Dependencies fetched over HTTP instead of HTTPS
- Unpinned versions in production dependency manifests

### 8. INFRASTRUCTURE & CONFIGURATION
- Overly permissive IAM roles or security groups
- Ports exposed that should not be
- Default credentials left in place
- Debug mode or verbose logging enabled in production config
- Missing security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options)

## Reporting Format

For each finding:
- SEVERITY: CRITICAL / HIGH / MEDIUM / LOW / INFO
- CATEGORY: (from the list above)
- LOCATION: file name and line number or function name
- WHAT: what the vulnerability is
- IMPACT: what an attacker could do if they exploited it
- FIX: concrete remediation with code example where applicable

Severity definitions:
- CRITICAL: exploitable with no authentication, data loss or full compromise possible
- HIGH: exploitable with low effort, significant impact
- MEDIUM: requires specific conditions, moderate impact
- LOW: defense-in-depth issue, limited direct impact
- INFO: best practice improvement, no direct exploitability

## End Summary

- Total findings by severity
- Top priority to fix first and why
- Any architectural patterns that will produce recurring issues
  (e.g., "raw SQL used throughout — consider parameterized query wrapper")
