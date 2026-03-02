# Mode Editing Permissions Analysis

## Executive Summary

Currently, **9 out of 13 modes** (69%) have `edit` permissions in Kilo Code. This analysis identifies modes where editing capability contradicts their intended purpose, creating potential for unintended file modifications, security risks, and confused user experiences.

---

## Current State: Mode Permissions Matrix

| Mode | Current Groups | Has Edit? | Purpose Alignment |
|------|---------------|-----------|-------------------|
| **architect** | read, edit, command | ✅ Yes | ⚠️ **MISALIGNED** |
| **ask** | read, browser | ❌ No | ✅ Aligned |
| **code** | read, edit, command | ✅ Yes | ✅ Aligned |
| **compliance** | read, edit, browser | ✅ Yes | ⚠️ Review |
| **debug** | read, edit, command | ✅ Yes | ⚠️ Review |
| **document** | read, edit | ✅ Yes | ⚠️ Review |
| **explain** | read, browser | ❌ No | ✅ Aligned |
| **migration** | read, edit, command, browser | ✅ Yes | ✅ Aligned |
| **orchestrator** | read, edit, command | ✅ Yes | ✅ Aligned |
| **refactor** | read, edit, command | ✅ Yes | ✅ Aligned |
| **review** | read, edit | ✅ Yes | ⚠️ **MISALIGNED** |
| **security** | read, edit, command, browser | ✅ Yes | ⚠️ Review |
| **test** | read, edit, command | ✅ Yes | ✅ Aligned |

---

## Critical Issues Identified

### 🔴 Issue 1: Architect Mode Has Edit Permissions

**Current State:** `groups: [read, edit, command]`

**Problem:**
The Architect mode's role definition explicitly states:
> *"You never generate code before the design is confirmed."*

Yet it currently has full edit permissions, allowing it to modify files directly. This creates a contradiction between:
1. The persona (planning-only, design-first)
2. The permissions (can modify any file)

**Risk:** Users in Architect mode may accidentally trigger file modifications when they only wanted design recommendations. The persona encourages "gathering requirements" and "validating assumptions" before any code changes, but the permissions don't enforce this workflow.

**Recommendation:** Remove `edit` from Architect mode. Add `browser` for research capabilities.

---

### 🔴 Issue 2: Review Mode Has Edit Permissions

**Current State:** `groups: [read, edit]`

**Problem:**
Review mode is designed for **evaluation**, not modification:
> *"You end every review with a clear verdict: Ready to merge, Needs changes, or Needs discussion."*

A code reviewer's job is to identify issues and recommend fixes, not to silently apply them. Edit permissions enable:
- Unauthorized modifications during "review"
- Bypassing the normal code review workflow
- Loss of audit trail (who made what change and why)

**Risk:** Violates the separation of concerns principle. Reviewers should not be implementers in the same session.

**Recommendation:** Remove `edit` from Review mode. Keep as read-only with browser capability.

---

### 🟡 Issue 3: Compliance Mode Has Edit Permissions

**Current State:** `groups: [read, edit, browser]`

**Problem:**
Compliance is an **audit and advisory** function:
> *"You review code, configuration, and infrastructure with compliance requirements in mind, identifying gaps"*
> *"You always recommend seeking qualified legal or compliance counsel for formal audit purposes."*

The mode emphasizes "identifying gaps" and "recommending" changes, not implementing them. Compliance decisions often require:
- Legal review
- Security team approval
- Change management process

**Risk:** Direct edits could bypass organizational compliance workflows.

**Recommendation:** Remove `edit` from Compliance mode. Auditors review; others implement.

---

### 🟡 Issue 4: Debug Mode Has Edit Permissions

**Current State:** `groups: [read, edit, command]`

**Problem:**
Debug mode follows a strict methodology:
> *"You never jump straight to a fix before the root cause is confirmed."*
> *"Once root cause is confirmed you offer multiple fix options, describe each with its risks"*

The process is: investigate → hypothesize → confirm → propose fixes. Edit permissions allow skipping to implementation.

**Mitigation:** Debug mode genuinely needs edit for some scenarios (e.g., adding logging, temporary instrumentation). However, this could be handled through a workflow:
1. Debug mode identifies the issue (read-only)
2. User switches to Code mode to apply the fix

**Recommendation:** Consider removing `edit`, but this requires workflow changes. Lower priority.

---

### 🟡 Issue 5: Document Mode Edit Permissions

**Current State:** `groups: [read, edit]`

**Problem:**
Document mode generates:
- READMEs
- API documentation
- Changelogs
- Comments

These are generally safe edits, but consider:
- Should documentation changes go through the same review as code?
- Does auto-generated documentation need human review first?

**Recommendation:** Keep `edit` but consider adding a warning or confirmation for certain file types.

---

### 🟡 Issue 6: Security Mode Has Edit Permissions

**Current State:** `groups: [read, edit, command, browser]`

**Problem:**
Security mode:
> *"recommend the simplest fix that closes the attack vector without over-engineering"*

Security fixes should often be:
- Peer-reviewed by security team
- Tested in staging first
- Documented for audit trails

**Risk:** Direct edits to fix security issues without proper review could introduce new vulnerabilities.

**Recommendation:** Consider removing `edit`. Security findings should be tickets, not immediate patches.

---

## Recommended Changes

### Immediate Changes (High Priority)

| Mode | Action | New Groups | Rationale |
|------|--------|------------|-----------|
| **architect** | Remove `edit`, add `browser` | read, browser, command | Design-first mode should not modify files. Browser enables research for better designs. |
| **review** | Remove `edit` | read, browser | Reviewers evaluate; they don't modify. Browser enables checking external references. |

### Considered Changes (Medium Priority)

| Mode | Action | New Groups | Rationale |
|------|--------|------------|-----------|
| **compliance** | Remove `edit` | read, browser | Compliance is audit/advisory, not implementation. |
| **security** | Remove `edit` | read, command, browser | Security fixes need review pipeline. |

### Keep As-Is (Low Priority)

| Mode | Current Groups | Rationale |
|------|---------------|-----------|
| **code** | read, edit, command | Primary implementation mode - needs edit. |
| **refactor** | read, edit, command | Modifies existing code - needs edit. |
| **test** | read, edit, command | Writes test files - needs edit. |
| **migration** | read, edit, command, browser | Transforms code - needs edit. |
| **orchestrator** | read, edit, command | Writes config files - needs edit. |
| **document** | read, edit | Generates docs - needs edit. |
| **debug** | read, edit, command | May need instrumentation - keep edit. |
| **ask** | read, browser | Already correct - Q&A mode. |
| **explain** | read, browser | Already correct - explanation mode. |

---

## Implementation Plan

### Phase 1: Critical Fixes

Update [`promptcli/registry.py`](promptcli/registry.py:268) `kilo_modes` dictionary:

```python
"architect": {
    # ... other fields ...
    "groups": ["read", "browser", "command"],  # Removed: edit
},
"review": {
    # ... other fields ...
    "groups": ["read", "browser"],  # Removed: edit
},
```

### Phase 2: Workflow Documentation

Create documentation explaining:
1. **Architect → Code workflow**: Design in Architect, implement in Code
2. **Review → Code workflow**: Review findings, implement fixes in Code
3. **Compliance → Orchestrator workflow**: Findings become tickets/infrastructure changes

### Phase 3: UX Enhancements (Future)

Consider adding UI features:
- Mode switch suggestions: "Your design is ready. Switch to Code mode to implement?"
- Permission warnings: "This mode cannot edit files. Switch modes to make changes."

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| User confusion when Architect can't edit | Medium | Low | Clear mode descriptions; workflow documentation |
| Review mode users expecting to apply fixes | Medium | Low | Tool output explains the review→code workflow |
| Breaking existing user workflows | Low | Medium | Announce changes in changelog; provide migration guide |
| Compliance/Security teams needing edit | Low | Low | They can switch to Code mode for approved changes |

---

## Conclusion

The current permission model grants editing capabilities too broadly. By removing `edit` from **architect** and **review** modes, we align permissions with the intended purpose of each mode:

- **Architect**: Design and planning (read, research, run commands)
- **Review**: Evaluation and feedback (read, research)
- **Code**: Implementation (read, edit, run commands)

This creates clearer boundaries, reduces accidental modifications, and enforces better separation of concerns in the development workflow.
