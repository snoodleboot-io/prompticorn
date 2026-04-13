# Actionable Reports Proposal

**Created:** 2026-04-12T12:56:00-05:00  
**Purpose:** Define how audit agents create actionable reports for implementation agents

---

## Overview

**Problem:** Audit agents (compliance, security, review, enforcement) should NOT modify code directly, but they need a way to communicate findings to implementation agents.

**Solution:** Structured actionable reports that audit agents can write and implementation agents can read.

---

## Report Directory Structure

```
.promptosaurus/
├── sessions/              # Session files (already exists)
└── reports/               # NEW: Actionable reports
    ├── compliance/
    │   ├── gdpr_violations_20260412.md
    │   └── soc2_findings_20260412.md
    ├── security/
    │   ├── vulnerabilities_20260412.md
    │   └── threat_model_20260412.md
    ├── enforcement/
    │   ├── style_violations_20260412.md
    │   └── pattern_violations_20260412.md
    └── review/
        ├── code_review_feature_auth_20260412.md
        └── performance_review_20260412.md
```

**Why `.promptosaurus/reports/`?**
- ✓ Co-located with sessions (same parent directory)
- ✓ Gitignored (like sessions) - reports are ephemeral
- ✓ Clear namespace separation by agent type
- ✓ Easy to clean up old reports
- ✗ Not committed to git (reports are point-in-time, not historical)

**Alternative: `docs/reports/` (committed to git)**
```
docs/
├── reports/               # Committed reports for historical tracking
│   ├── compliance/
│   ├── security/
│   ├── enforcement/
│   └── review/
```

**Why `docs/reports/`?**
- ✓ Historical tracking (see what issues existed over time)
- ✓ Can be referenced in PRs
- ✓ Can track resolution of findings
- ✗ Git noise (many report files)
- ✗ Requires cleanup of resolved reports

**Recommendation:** Use `.promptosaurus/reports/` for active/pending reports, move to `docs/reports/archive/` when resolved.

---

## Report File Format

### Standard Report Template

```yaml
---
report_type: security_audit
agent: security
subagent: vulnerability-assessment-specialist
created_at: 2026-04-12T14:30:00Z
branch: feat/auth-system
status: open  # open, in_progress, resolved, dismissed
severity: high  # critical, high, medium, low
---

# Security Vulnerability Report

## Summary

Found 3 SQL injection vulnerabilities in authentication endpoints.

## Findings

### Finding 1: SQL Injection in Login Endpoint

**Severity:** CRITICAL  
**File:** `src/auth/login.py`  
**Line:** 45-47  
**Category:** CWE-89 (SQL Injection)

**Issue:**
```python
# Current (vulnerable)
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)
```

**Recommendation:**
```python
# Fixed (parameterized query)
query = "SELECT * FROM users WHERE username = ?"
cursor.execute(query, (username,))
```

**Rationale:** User input is concatenated directly into SQL query, allowing SQL injection attacks.

**Priority:** MUST_FIX (security vulnerability)

---

### Finding 2: SQL Injection in Registration Endpoint

**Severity:** CRITICAL  
**File:** `src/auth/register.py`  
**Line:** 67-69  
**Category:** CWE-89 (SQL Injection)

**Issue:**
```python
# Current (vulnerable)
query = f"INSERT INTO users (username, email) VALUES ('{username}', '{email}')"
cursor.execute(query)
```

**Recommendation:**
```python
# Fixed (parameterized query)
query = "INSERT INTO users (username, email) VALUES (?, ?)"
cursor.execute(query, (username, email))
```

**Rationale:** User input is concatenated directly into SQL query.

**Priority:** MUST_FIX (security vulnerability)

---

### Finding 3: Missing Input Validation

**Severity:** HIGH  
**File:** `src/auth/login.py`  
**Line:** 40-42  
**Category:** CWE-20 (Improper Input Validation)

**Issue:**
No validation of username length or characters before database query.

**Recommendation:**
```python
# Add input validation
if not username or len(username) > 255:
    raise ValueError("Invalid username")
if not re.match(r'^[a-zA-Z0-9_-]+$', username):
    raise ValueError("Username contains invalid characters")
```

**Priority:** SHOULD_FIX (defense in depth)

---

## Summary Statistics

- **Total Findings:** 3
- **Critical:** 2
- **High:** 1
- **Medium:** 0
- **Low:** 0

## Recommended Actions

1. **Immediate:** Fix Finding 1 and 2 (SQL injection vulnerabilities)
2. **Short-term:** Add input validation (Finding 3)
3. **Follow-up:** Security review after fixes applied

## Verification Steps

After fixes are applied:
1. Re-run security scan on affected files
2. Verify parameterized queries are used
3. Test with SQL injection payloads
4. Update report status to 'resolved'

---

## Metadata for Orchestrator

**Actionable Items:**
```yaml
- file: src/auth/login.py
  line: 45
  action: replace
  priority: must_fix
  
- file: src/auth/register.py
  line: 67
  action: replace
  priority: must_fix
  
- file: src/auth/login.py
  line: 40
  action: add_validation
  priority: should_fix
```

**Estimated Effort:** 30 minutes  
**Risk Level:** Low (well-defined fixes)  
**Tests Required:** Yes (security tests)
```

---

## Permission Model Update

### Audit Agents Get Report Write Access

**Old Model (Sessions Only):**
```yaml
# compliance, security, review, enforcement
permissions:
  read: {'*': 'allow'}
  edit: {'\.promptosaurus/sessions/.*\.md$': 'allow', '*': 'deny'}
  bash: deny
```

**New Model (Sessions + Reports):**
```yaml
# compliance, security, review, enforcement
permissions:
  read: {'*': 'allow'}
  edit: 
    '(\.promptosaurus/sessions/.*\.md$|\.promptosaurus/reports/{agent_type}/.*\.md$)': 'allow'
    '*': 'deny'
  bash: deny  # or limited read-only commands
```

**Dynamic agent_type replacement:**
- `security` agent can write to `.promptosaurus/reports/security/`
- `compliance` agent can write to `.promptosaurus/reports/compliance/`
- `enforcement` agent can write to `.promptosaurus/reports/enforcement/`
- `review` agent can write to `.promptosaurus/reports/review/`

---

## Workflow Examples

### Example 1: Security Audit → Code Fix

**Step 1: User invokes security audit**
```bash
User: "Run security audit on auth module"
```

**Step 2: Security agent scans and creates report**
```
Security agent:
- Reads src/auth/*.py
- Finds 3 SQL injection vulnerabilities
- Creates .promptosaurus/reports/security/vulnerabilities_20260412.md
- Returns summary to user
```

**Step 3: User requests fixes**
```bash
User: "Fix the security vulnerabilities"
```

**Step 4: Orchestrator delegates to code agent**
```
Orchestrator:
- Reads .promptosaurus/reports/security/vulnerabilities_20260412.md
- Extracts actionable items
- Delegates to code agent with context
```

**Step 5: Code agent implements fixes**
```
Code agent:
- Reads report
- Applies fixes from recommendations
- Updates files
- Runs tests
- Updates report status to 'resolved'
```

**Step 6: Security agent verifies**
```bash
User: "Verify security fixes"
```

```
Security agent:
- Re-scans fixed files
- Verifies vulnerabilities are resolved
- Updates report status to 'verified'
- Archives report to docs/reports/archive/
```

---

### Example 2: Enforcement Audit → Orchestrated Fixes

**Step 1: Enforcement scan**
```bash
User: "Check code against style conventions"
```

**Step 2: Enforcement creates report**
```
Enforcement agent:
- Reads core-conventions-python.md
- Scans all .py files
- Finds 47 style violations
- Creates .promptosaurus/reports/enforcement/style_violations_20260412.md
```

**Step 3: User reviews and approves**
```bash
User: "Show me the top 10 violations"
Enforcement: [Shows critical violations]

User: "Fix all MUST_FIX violations"
```

**Step 4: Orchestrator batch-processes**
```
Orchestrator:
- Reads report
- Groups violations by file
- Creates fix plan
- Delegates to code agent in batches
```

**Step 5: Code agent applies fixes**
```
Code agent:
- Processes violations file-by-file
- Applies automated fixes where possible
- Flags manual fixes for user
- Updates report with progress
```

---

### Example 3: Code Review → Discussion

**Step 1: Review agent reviews PR**
```bash
User: "Review the authentication PR"
```

**Step 2: Review creates report**
```
Review agent:
- Reads PR diff
- Analyzes code quality, patterns, edge cases
- Creates .promptosaurus/reports/review/code_review_auth_20260412.md
- Flags 3 blockers, 5 suggestions
```

**Step 3: User discusses findings**
```bash
User: "Why is Finding 2 a blocker?"
Review: [Explains rationale]

User: "I disagree, mark as dismissed"
Review: [Updates report status for Finding 2]
```

**Step 4: User requests fixes for accepted items**
```bash
User: "Fix Finding 1 and Finding 3"
```

**Step 5: Code agent implements**
```
Code agent:
- Reads report
- Implements fixes for Finding 1, 3
- Updates report
```

---

## Report Lifecycle

```
[Created] → [Open] → [In Progress] → [Resolved] → [Verified] → [Archived]
             ↓
         [Dismissed] → [Archived]
```

**States:**
- **Created:** Report just generated
- **Open:** Findings documented, awaiting action
- **In Progress:** Code agent is implementing fixes
- **Resolved:** Fixes applied, awaiting verification
- **Verified:** Audit agent confirmed fixes
- **Dismissed:** User or agent marked as not applicable
- **Archived:** Moved to `docs/reports/archive/` for historical reference

---

## Benefits of This Approach

### 1. Clean Separation of Concerns
- ✓ Audit agents don't touch code
- ✓ Code agents don't do audits
- ✓ Reports are the communication layer

### 2. Traceability
- ✓ Every finding is documented
- ✓ Fixes are linked to findings
- ✓ Historical record of what was found

### 3. Automation-Friendly
- ✓ Structured format allows automated processing
- ✓ Orchestrator can batch-process reports
- ✓ Status tracking enables workflow automation

### 4. User Control
- ✓ User can review findings before fixes
- ✓ User can dismiss false positives
- ✓ User can prioritize which findings to fix

### 5. Audit Trail
- ✓ Reports show what was found when
- ✓ Archived reports show resolution history
- ✓ Compliance-friendly documentation

---

## Implementation Plan

### Phase 1: Create Report Infrastructure

1. Create `.promptosaurus/reports/` directory structure
2. Create report template files
3. Update `.gitignore` to include `reports/` (or not, depending on choice)

### Phase 2: Update Audit Agent Permissions

Update 4 agents:
- `compliance` → can write to `.promptosaurus/reports/compliance/`
- `security` → can write to `.promptosaurus/reports/security/`
- `enforcement` → can write to `.promptosaurus/reports/enforcement/`
- `review` → can write to `.promptosaurus/reports/review/`

### Phase 3: Update Agent System Prompts

Add instructions for report creation:
- When to create reports
- Report format/structure
- Status management
- Actionable item formatting

### Phase 4: Update Orchestrator

Teach orchestrator to:
- Discover reports in `.promptosaurus/reports/`
- Parse actionable items
- Delegate fixes to appropriate agents
- Track report status

### Phase 5: Create Utilities

Helper scripts:
- List all open reports
- Archive resolved reports
- Generate summary of findings
- Cleanup old reports

---

## Directory Structure Final Recommendation

```
.promptosaurus/
├── sessions/                    # Gitignored - temporary session state
├── reports/                     # Gitignored - active actionable reports
│   ├── compliance/
│   ├── security/
│   ├── enforcement/
│   └── review/
└── .gitignore                   # Ignore sessions and reports

docs/
├── reports/                     # Committed - resolved reports archive
│   └── archive/
│       ├── 2026-04/
│       │   ├── security_vulnerabilities_20260412.md
│       │   └── style_violations_20260412.md
│       └── 2026-03/
└── ...
```

**Workflow:**
1. Audit agent creates report in `.promptosaurus/reports/{type}/`
2. Code agent implements fixes
3. Audit agent verifies
4. Report moved to `docs/reports/archive/{YYYY-MM}/` for historical tracking
5. Committed with PR showing what was found and fixed

---

## Decision Matrix

| Aspect | Option A: Ephemeral | Option B: Committed | Recommendation |
|--------|-------------------|-------------------|----------------|
| **Location** | `.promptosaurus/reports/` | `docs/reports/` | Both (ephemeral + archive) |
| **Gitignored** | Yes | No | Yes for active, No for archive |
| **Cleanup** | Manual/automated | Manual (git history) | Auto-archive after 30 days |
| **Traceability** | Low | High | Archive resolved reports |
| **Clutter** | None | Medium | Archive by month |

**Final Recommendation:**
- Active reports: `.promptosaurus/reports/` (gitignored)
- Resolved reports: `docs/reports/archive/YYYY-MM/` (committed)
- Best of both worlds: clean working directory + historical tracking
