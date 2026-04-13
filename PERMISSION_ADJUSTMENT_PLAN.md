# Agent Permission Adjustment Plan

**Created:** 2026-04-12T12:52:00-05:00  
**Branch:** feat/mode-field-implementation  
**Based on:** PERMISSIONS_ANALYSIS.md

---

## Overview

**Agents requiring permission changes:** 8  
**Total issues to fix:** 11

**Principle:** Apply least-privilege principle while maintaining agent functionality.

---

## Phase 1: Top-Level Agent Permission Adjustments

### 1.1 `architect` Agent ✓ MINOR FIX

**Current Issue:**
- Edit permissions use escaped backslashes in regex (cosmetic issue)

**Current:**
```yaml
edit: {'(docs/.*\\.md$|\\.promptosaurus/sessions/.*\\.md$)': 'allow', '*': 'deny'}
```

**Recommended:**
```yaml
edit: {'(docs/.*\.md$|\.promptosaurus/sessions/.*\.md$)': 'allow', '*': 'deny'}
```

**Action:** Update regex escaping (no functional change)  
**Risk:** LOW - cosmetic fix  
**Files:** `promptosaurus/agents/architect/prompt.md`

---

### 1.2 `compliance` Agent ⚠️ MAJOR CHANGE

**Current Issue:**
- Full edit permissions (should be read-only audit role)
- Full bash permissions (should be restricted)

**Current:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Recommended:**
```yaml
read: {'*': 'allow'}
edit: {'\.promptosaurus/sessions/.*\.md$': 'allow', '*': 'deny'}
bash: deny
```

**Rationale:** Compliance is an audit/review role - should NOT modify code directly. Can only document findings in sessions.

**Action:** 
1. Restrict edit to sessions only
2. Remove bash access (or limit to `grep`, `find`, `cat` if needed)

**Risk:** MEDIUM - may break existing workflows  
**Files:** `promptosaurus/agents/compliance/prompt.md`

**Decision needed:** Should compliance have LIMITED bash (read-only commands like `grep`, `find`) or NO bash?

---

### 1.3 `debug` Agent ⚠️ MAJOR CHANGE

**Current Issue:**
- Full edit permissions (debug should diagnose, not fix)

**Current:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Recommended:**
```yaml
read: {'*': 'allow'}
edit: {'\.promptosaurus/sessions/.*\.md$': 'allow', '*': 'deny'}
bash: allow
```

**Rationale:** Debug agent diagnoses problems and documents findings. Fixes should be delegated to `code` agent.

**Action:** Restrict edit to sessions only  
**Risk:** MEDIUM - may break existing workflows where debug directly patches code  
**Files:** `promptosaurus/agents/debug/prompt.md`

**Decision needed:** Should debug be able to create temporary test files for reproduction? If yes, allow `(test/.*|tmp/.*|\.promptosaurus/.*)`.

---

### 1.4 `document` Agent ⚠️ MODERATE CHANGE

**Current Issue:**
- Can edit all files (should only edit markdown)

**Current:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Recommended:**
```yaml
read: {'*': 'allow'}
edit: {'.*\.md$': 'allow', '*': 'deny'}
bash: allow
```

**Rationale:** Documentation agent should only create/edit markdown files, not code.

**Action:** Restrict edit to `.md` files only  
**Risk:** LOW - documentation should only touch markdown anyway  
**Files:** `promptosaurus/agents/document/prompt.md`

---

### 1.5 `enforcement` Agent ⚠️ MAJOR CHANGE

**Current Issue:**
- Can edit docs (should be read-only audit)
- Full bash permissions (should be restricted)

**Current:**
```yaml
read: {'*': 'allow'}
edit: {'(docs/.*\\.md$|\\.promptosaurus/sessions/.*\\.md$)': 'allow', '*': 'deny'}
bash: allow
```

**Recommended:**
```yaml
read: {'*': 'allow'}
edit: {'\.promptosaurus/sessions/.*\.md$': 'allow', '*': 'deny'}
bash: deny
```

**Rationale:** Enforcement is an audit role - reads code, documents violations. Should NOT edit docs or have bash access.

**Action:** 
1. Remove docs edit permission
2. Remove bash (or limit to read-only commands)

**Risk:** MEDIUM - enforcement may need bash for code scanning  
**Files:** `promptosaurus/agents/enforcement/prompt.md`

**Decision needed:** Should enforcement have LIMITED bash for code scanning (`grep`, `rg`, `find`, `cat`) or NO bash?

---

### 1.6 `explain` Agent ⚠️ MINOR CHANGE

**Current Issue:**
- Full bash permissions (explain is read-only educational role)

**Current:**
```yaml
read: {'*': 'allow'}
edit: {'\\.promptosaurus/sessions/.*\\.md$': 'allow', '*': 'deny'}
bash: allow
```

**Recommended:**
```yaml
read: {'*': 'allow'}
edit: {'\\.promptosaurus/sessions/.*\\.md$': 'allow', '*': 'deny'}
bash: deny
```

**Rationale:** Explain agent reads code and explains it. Doesn't need bash for this role.

**Action:** Remove bash access  
**Risk:** LOW - explain is purely educational/explanatory  
**Files:** `promptosaurus/agents/explain/prompt.md`

---

### 1.7 `review` Agent ⚠️ MAJOR CHANGE

**Current Issue:**
- Can edit sessions (review should be read-only)
- Full bash permissions (should be restricted)

**Current:**
```yaml
read: {'*': 'allow'}
edit: {'\\.promptosaurus/sessions/.*\\.md$': 'allow', '*': 'deny'}
bash: allow
```

**Recommended:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'deny'}
bash: deny
```

**Rationale:** Review agent reads code and provides feedback - should NOT modify anything, including sessions. Outputs reviews to user directly.

**Action:** 
1. Remove all edit permissions
2. Remove bash access

**Risk:** HIGH - major workflow change, review comments must go to user, not files  
**Files:** `promptosaurus/agents/review/prompt.md`

**Decision needed:** If review creates review reports, should it be able to write to `docs/reviews/` directory? If yes, use `{'docs/reviews/.*\.md$': 'allow', '*': 'deny'}`.

---

### 1.8 `security` Agent ⚠️ MAJOR CHANGE

**Current Issue:**
- Full edit permissions (security is audit role)

**Current:**
```yaml
read: {'*': 'allow'}
edit: {'*': 'allow'}
bash: allow
```

**Recommended:**
```yaml
read: {'*': 'allow'}
edit: {'\.promptosaurus/sessions/.*\.md$': 'allow', '*': 'deny'}
bash: allow
```

**Rationale:** Security agent audits code for vulnerabilities. Should document findings in sessions, not modify code directly. Fixes delegated to `code` agent.

**Action:** Restrict edit to sessions only  
**Risk:** MEDIUM - security may need to create security reports  
**Files:** `promptosaurus/agents/security/prompt.md`

**Decision needed:** Should security be able to write to `docs/security/` for reports? If yes, use `{'(docs/security/.*\.md$|\.promptosaurus/sessions/.*\.md$)': 'allow', '*': 'deny'}`.

---

## Phase 2: Subagent Permission Review

**Approach:** Compare each subagent's permissions to parent agent.

### 2.1 Inheritance Check

For each parent agent with subagents:

1. **Read parent permissions** from `promptosaurus/agents/{parent}/prompt.md`
2. **Read subagent permissions** from `promptosaurus/agents/{parent}/subagents/{subagent}/minimal/prompt.md`
3. **Compare:** Subagent should have ≤ permissions of parent
4. **Flag violations:** Subagent should NOT have more permissions than parent

### 2.2 Expected Subagent Patterns

**Pattern A: Same as Parent (most common)**
- Subagent does specialized work within parent's domain
- Example: `code/feature` subagent has same permissions as `code` parent

**Pattern B: More Restrictive than Parent**
- Subagent has narrower scope than parent
- Example: `architect/data-model` might only edit `docs/data-models/` instead of all docs

**Pattern C: Session-Only (rare)**
- Subagent only documents analysis
- Example: Some review subagents might only write to sessions

### 2.3 Subagent Review Checklist

For each of 82 subagents:

```
[ ] Check parent permissions
[ ] Check subagent permissions
[ ] Verify subagent ≤ parent (no escalation)
[ ] Verify permissions match subagent purpose
[ ] Flag if subagent has MORE permissions than parent
[ ] Flag if subagent has LESS permissions but should be same
```

### 2.4 High-Priority Subagent Reviews

**Parents with restricted permissions (check subagents carefully):**

1. **architect** (edit restricted) → 3 subagents
   - `data-model` - should match parent
   - `scaffold` - might need code edit for scaffolding?
   - `task-breakdown` - should match parent

2. **compliance** (will be restricted) → 3 subagents
   - `gdpr` - should match parent (read-only)
   - `review` - should match parent (read-only)
   - `soc2` - should match parent (read-only)

3. **debug** (will be restricted) → 3 subagents
   - `log-analysis` - should match parent (sessions only)
   - `root-cause` - should match parent (sessions only)
   - `rubber-duck` - should match parent (sessions only)

4. **document** (will be restricted) → 1 subagent
   - `strategy-for-applications` - should match parent (markdown only)

5. **enforcement** (will be restricted) → 0 subagents (no children)

6. **explain** (will be restricted) → 1 subagent
   - `strategy` - should match parent (read-only)

7. **review** (will be restricted) → 3 subagents
   - `accessibility` - should match parent (read-only)
   - `code` - should match parent (read-only)
   - `performance` - should match parent (read-only)

8. **security** (will be restricted) → 6 subagents
   - `compliance-auditor` - should match parent (sessions only)
   - `review` - should match parent (sessions only)
   - `security-architecture-reviewer` - should match parent
   - `threat-model` - should match parent
   - `threat-modeling-expert` - should match parent
   - `vulnerability-assessment-specialist` - should match parent

---

## Phase 3: Decision Points

Before proceeding, need decisions on:

### 3.1 Bash Permissions for Audit Roles

**Agents affected:** compliance, enforcement, explain, review

**Options:**

**Option A: NO BASH** (strictest)
- Pro: Least privilege, forces use of read tools
- Con: May need bash for code scanning (grep, find, etc.)

**Option B: LIMITED BASH** (read-only commands)
- Allow: `grep`, `rg` (ripgrep), `find`, `cat`, `head`, `tail`, `wc`, `ls`
- Deny: All write commands, git commands, package managers
- Pro: Practical for scanning/analysis
- Con: Harder to implement permission granularity

**Option C: FULL BASH** (current - least restrictive)
- Pro: Maximum flexibility
- Con: Violates least-privilege principle

**Recommendation:** Option B (limited bash) with allow-list

**Implementation:** Would require bash permission enhancement to support command-level filtering (currently only allow/deny)

---

### 3.2 Report Writing Permissions

**Agents affected:** security, review, compliance, enforcement

**Question:** Should audit agents be able to write reports to `docs/` directories?

**Options:**

**Option A: Sessions Only** (strictest)
- Reports written to `.promptosaurus/sessions/`
- Pro: Clear separation, reports not committed
- Con: Reports may get lost, harder to track

**Option B: Dedicated Report Directories**
- Allow writing to `docs/reviews/`, `docs/security/`, `docs/compliance/`
- Pro: Reports are trackable, can be committed
- Con: More complex permissions

**Recommendation:** Option B - create dedicated report directories per domain

---

### 3.3 Debug Temporary File Creation

**Agent affected:** debug

**Question:** Should debug be able to create temp files for reproduction?

**Options:**

**Option A: NO** (strictest)
- Debug only reads and documents
- Pro: Cleanest separation
- Con: Can't create test cases for reproduction

**Option B: YES** (allow temp/test directories)
- Allow: `(test/.*|tmp/.*|\.promptosaurus/.*)`
- Pro: Debug can create reproduction scripts
- Con: More permissions than pure diagnosis

**Recommendation:** Option A initially, revisit if needed

---

### 3.4 Architect Scaffold Permissions

**Agent affected:** architect/scaffold subagent

**Question:** Should `scaffold` subagent be able to create code files?

**Context:** Scaffolding typically creates starter code structures.

**Options:**

**Option A: Inherit Parent** (docs/sessions only)
- Scaffold outputs plan only, delegates to `code` agent
- Pro: Clean separation of design vs implementation
- Con: Extra delegation step

**Option B: Allow Code Creation**
- Scaffold can create initial file structures
- Pro: More efficient, direct scaffolding
- Con: Blurs architect/code boundary

**Recommendation:** Option A - scaffold designs structure, code agent creates files

---

## Phase 4: Implementation Steps

### Step 1: Create Permission Presets (30 min)

Create reusable permission patterns:

```yaml
# File: promptosaurus/agents/_permission_presets.yaml

presets:
  full_access:
    read: {'*': 'allow'}
    edit: {'*': 'allow'}
    bash: allow

  read_only:
    read: {'*': 'allow'}
    edit: {'*': 'deny'}
    bash: deny

  audit_role:
    read: {'*': 'allow'}
    edit: {'\.promptosaurus/sessions/.*\.md$': 'allow', '*': 'deny'}
    bash: deny  # or limited commands if supported

  documentation_role:
    read: {'*': 'allow'}
    edit: {'.*\.md$': 'allow', '*': 'deny'}
    bash: allow

  architect_role:
    read: {'*': 'allow'}
    edit: {'(docs/.*\.md$|\.promptosaurus/sessions/.*\.md$)': 'allow', '*': 'deny'}
    bash: deny

  security_audit_with_reports:
    read: {'*': 'allow'}
    edit: {'(docs/security/.*\.md$|\.promptosaurus/sessions/.*\.md$)': 'allow', '*': 'deny'}
    bash: allow
```

### Step 2: Update Top-Level Agents (2 hours)

For each agent requiring changes:

1. Open `promptosaurus/agents/{agent}/prompt.md`
2. Update `permissions:` section in YAML frontmatter
3. Add comment explaining permission rationale
4. Save file

**Files to modify:**
- `promptosaurus/agents/architect/prompt.md` ✓ minor
- `promptosaurus/agents/compliance/prompt.md` ⚠️ major
- `promptosaurus/agents/debug/prompt.md` ⚠️ major
- `promptosaurus/agents/document/prompt.md` ⚠️ moderate
- `promptosaurus/agents/enforcement/prompt.md` ⚠️ major
- `promptosaurus/agents/explain/prompt.md` ⚠️ minor
- `promptosaurus/agents/review/prompt.md` ⚠️ major
- `promptosaurus/agents/security/prompt.md` ⚠️ major

### Step 3: Review Subagent Permissions (3 hours)

For each of 82 subagents:

1. Run permission comparison script (create if needed)
2. Flag subagents with mismatched permissions
3. Update subagent permissions to match parent (or be more restrictive)
4. Document rationale for any exceptions

**Script needed:**
```bash
#!/bin/bash
# compare_subagent_permissions.sh
for parent in promptosaurus/agents/*/; do
  if [ -d "$parent/subagents" ]; then
    parent_name=$(basename "$parent")
    for subagent in "$parent/subagents"/*/minimal/prompt.md; do
      subagent_name=$(basename $(dirname $(dirname "$subagent")))
      echo "Checking: $parent_name/$subagent_name"
      # Compare permissions logic here
    done
  fi
done
```

### Step 4: Regenerate Agent Files (15 min)

```bash
# Clear caches
uv cache clean
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null

# Regenerate
echo -e "\n\n\n\n\n\n\n\n\n\n" | uv run promptosaurus init

# Verify mode fields are preserved
for file in .kilo/agents/*.md; do
  grep "^mode:" "$file"
done
```

### Step 5: Testing & Validation (1 hour)

1. Build test cases for each agent
2. Verify restricted agents cannot edit outside permissions
3. Verify full-access agents still work
4. Document any breaking changes

### Step 6: Update Documentation (30 min)

1. Update `PERMISSIONS_ANALYSIS.md` with new status
2. Create `PERMISSIONS_CHANGELOG.md` documenting changes
3. Update agent README files if they exist

---

## Phase 5: Rollout Strategy

### Option 1: All at Once (Fast, risky)
- Apply all changes in single commit
- Risk: Multiple agents break simultaneously
- Good for: Development environment with quick recovery

### Option 2: Staged Rollout (Slower, safer)
- **Stage 1:** Minor changes (architect, explain) - 2 agents
- **Stage 2:** Moderate changes (document) - 1 agent
- **Stage 3:** Major audit role changes (compliance, enforcement, review, security) - 4 agents
- **Stage 4:** Debug changes - 1 agent
- **Stage 5:** Subagent alignment - 82 subagents
- Good for: Production environment, need validation between stages

**Recommendation:** Option 2 (staged rollout) with testing between stages

---

## Phase 6: Success Criteria

**Definition of Done:**

- [ ] All 8 agents have updated permissions
- [ ] All 82 subagents reviewed and aligned with parents
- [ ] No subagent has MORE permissions than parent
- [ ] Permissions match agent roles (audit = read-only, etc.)
- [ ] `PERMISSIONS_ANALYSIS.md` updated with new status
- [ ] All generated files in `.kilo/agents/` have correct permissions
- [ ] Test suite passes (if exists)
- [ ] Breaking changes documented
- [ ] Rollback plan documented

---

## Rollback Plan

If changes cause issues:

```bash
# Rollback source files
git checkout HEAD -- promptosaurus/agents/*/prompt.md
git checkout HEAD -- promptosaurus/agents/*/subagents/*/minimal/prompt.md

# Regenerate
uv cache clean
find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null
echo -e "\n\n\n\n\n\n\n\n\n\n" | uv run promptosaurus init

# Verify rollback
git diff .kilo/agents/
```

---

## Estimated Timeline

**Total time:** ~7.5 hours

- Phase 1: Decision making - 30 min
- Phase 2: Permission preset creation - 30 min
- Phase 3: Top-level agent updates - 2 hours
- Phase 4: Subagent review - 3 hours
- Phase 5: Regeneration - 15 min
- Phase 6: Testing - 1 hour
- Phase 7: Documentation - 30 min

**Plus buffer for issues:** +2 hours  
**Total with buffer:** ~9.5 hours

---

## Next Steps

**Before proceeding, need decisions on:**

1. ✅ or ❌ Apply staged rollout vs all-at-once?
2. ✅ or ❌ Bash permissions for audit roles: NO / LIMITED / FULL?
3. ✅ or ❌ Allow audit agents to write reports to `docs/` directories?
4. ✅ or ❌ Allow debug to create temp files?
5. ✅ or ❌ Allow scaffold subagent to create code files?

**Recommendation:** Get user sign-off on decisions before starting implementation.
