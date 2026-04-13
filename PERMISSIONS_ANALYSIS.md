# Agent & Subagent Permissions Analysis

**Generated:** 2026-04-12T12:38:53-05:00

---

## Executive Summary

**Total Agents:** 107 (25 top-level + 82 subagents)

**Mode Distribution:**
- `mode: primary` — 17 agents (user-selectable entry points)
- `mode: all` — 8 agents (user-selectable + delegable)
- `mode: subagent` — 82 agents (only callable by parent agents)

**Permission Issues Found:**
- 8 agents need permission review
- 11 total issues identified

---

## Top-Level Agents (25)

### Permission Matrix

| Agent | Mode | Read | Edit | Bash | Status |
|-------|------|------|------|------|--------|
| `architect` | `primary` | ✓ all | restricted | ✗ | ⚠ REVIEW |
| `ask` | `primary` | ✓ all | restricted | ✓ | ✓ OK |
| `backend` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `code` | `all` | ✓ all | ✓ all | ✓ | ✓ OK |
| `compliance` | `primary` | ✓ all | ✓ all | ✓ | ⚠ REVIEW |
| `data` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `debug` | `all` | ✓ all | ✓ all | ✓ | ⚠ REVIEW |
| `devops` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `document` | `all` | ✓ all | ✓ all | ✓ | ⚠ REVIEW |
| `enforcement` | `primary` | ✓ all | restricted | ✓ | ⚠ REVIEW |
| `explain` | `all` | ✓ all | restricted | ✓ | ⚠ REVIEW |
| `frontend` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `incident` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `migration` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `mlai` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `observability` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `orchestrator` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `performance` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `planning` | `primary` | ✓ all | restricted | ✓ | ✓ OK |
| `product` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `qa-tester` | `primary` | ✓ all | ✓ all | ✓ | ✓ OK |
| `refactor` | `all` | ✓ all | ✓ all | ✓ | ✓ OK |
| `review` | `all` | ✓ all | restricted | ✓ | ⚠ REVIEW |
| `security` | `all` | ✓ all | ✓ all | ✓ | ⚠ REVIEW |
| `test` | `all` | ✓ all | ✓ all | ✓ | ✓ OK |

---

## Detailed Permission Analysis

### `architect` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'(docs/.*\\.md$|\\.promptosaurus/sessions/.*\\.md$)': 'allow', '*': 'deny'}
```

**Issues:**
- ⚠️  Should edit docs and sessions, deny code

**Recommended:**
```yaml
edit: {'(docs/.*\.md$|\.promptosaurus/sessions/.*\.md$)': 'allow', '*': 'deny'}
```

---

### `compliance` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
bash: allow
edit: {'*': 'allow'}
```

**Issues:**
- ⚠️  Should be read-only (audit role)
- ⚠️  Bash should be restricted for audit/review roles

**Recommended:**
```yaml
edit: {'\.promptosaurus/sessions/.*\.md$': 'allow', '*': 'deny'}
bash: deny or limit to specific commands
```

---

### `debug` (all)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Issues:**
- ⚠️  Debug should be read-only (diagnosis, not fixes)

**Recommended:**
```yaml
edit: {'*': 'deny'}
```

---

### `document` (all)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
bash: allow
edit: {'*': 'allow'}
```

**Issues:**
- ⚠️  Should only edit markdown files

**Recommended:**
```yaml
edit: {'*\.md$': 'allow', '*': 'deny'}
```

---

### `enforcement` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
bash: allow
edit: {'(docs/.*\\.md$|\\.promptosaurus/sessions/.*\\.md$)': 'allow', '*': 'deny'}
```

**Issues:**
- ⚠️  Should be read-only (audit role)
- ⚠️  Bash should be restricted for audit/review roles

**Recommended:**
```yaml
edit: {'\.promptosaurus/sessions/.*\.md$': 'allow', '*': 'deny'}
bash: deny or limit to specific commands
```

---

### `explain` (all)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
bash: allow
edit: {'\\.promptosaurus/sessions/.*\\.md$': 'allow', '*': 'deny'}
```

**Issues:**
- ⚠️  Bash should be restricted for audit/review roles

**Recommended:**
```yaml
bash: deny or limit to specific commands
```

---

### `review` (all)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
bash: allow
edit: {'\\.promptosaurus/sessions/.*\\.md$': 'allow', '*': 'deny'}
```

**Issues:**
- ⚠️  Should be read-only (review, not modify)
- ⚠️  Bash should be restricted for audit/review roles

**Recommended:**
```yaml
edit: {'*': 'deny'} or omit edit permission
bash: deny or limit to specific commands
```

---

### `security` (all)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Issues:**
- ⚠️  Should be read-only for security audits

**Recommended:**
```yaml
edit: {'\.promptosaurus/sessions/.*\.md$': 'allow', '*': 'deny'}
```

---

### `ask` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'\\.promptosaurus/sessions/.*\\.md$': 'allow', '*': 'deny'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `backend` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `code` (all)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `data` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `devops` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `frontend` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `incident` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `migration` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `mlai` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `observability` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `orchestrator` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `performance` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `planning` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'(docs/.*\\.md$|\\.promptosaurus/sessions/.*\\.md$)': 'allow', '*': 'deny'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `product` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `qa-tester` (primary)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `refactor` (all)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

### `test` (all)

**Current Permissions:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Status:** ✓ Permissions appropriate for role

---

## Subagents Summary (82)

Subagents inherit most permissions from their parent agents.
Key subagent categories:

- **architect/*** — 3 subagents
- **ask/*** — 3 subagents
- **backend/*** — 4 subagents
- **code/*** — 6 subagents
- **compliance/*** — 3 subagents
- **data/*** — 5 subagents
- **debug/*** — 3 subagents
- **devops/*** — 5 subagents
- **document/*** — 1 subagents
- **explain/*** — 1 subagents
- **frontend/*** — 4 subagents
- **incident/*** — 4 subagents
- **migration/*** — 1 subagents
- **mlai/*** — 8 subagents
- **observability/*** — 5 subagents
- **orchestrator/*** — 4 subagents
- **performance/*** — 4 subagents
- **product/*** — 3 subagents
- **qa-tester/*** — 4 subagents
- **refactor/*** — 1 subagents
- **review/*** — 3 subagents
- **security/*** — 6 subagents
- **test/*** — 1 subagents

**Note:** All subagents have `mode: subagent` and are only invokable by their parent agent or via `@` mentions.
