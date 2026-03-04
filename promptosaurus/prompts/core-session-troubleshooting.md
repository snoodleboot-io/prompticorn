<!-- path: promptosaurus/prompts/core-session-troubleshooting.md -->
# Session Troubleshooting Guide

## Overview

This guide helps diagnose and fix issues with session files and session management.

---

## Issue 1: Session File Not Found

**Symptoms:**
- No files in `.prompty/session/` directory
- Getting "session not found" errors
- Session management not working

**Diagnosis:**
```bash
# Check if directory exists
ls -la .prompty/session/

# List all session files
ls -la .prompty/session/session_*.md

# Check if directory is gitignored
cat .gitignore | grep session
```

**Solutions:**

### Solution A: Directory Doesn't Exist
```bash
# Create directory
mkdir -p .prompty/session/

# Create first session
# (Follow session file format from core-session.md)
```

### Solution B: Session Deleted Accidentally
```bash
# Check git log to see if it was committed (shouldn't be)
git log --all -- .prompty/session/

# Recreate new session
# (Sessions are safe to delete - they're gitignored)
```

---

## Issue 2: Multiple Sessions for Same Branch

**Symptoms:**
- Different session files for the same branch
- Confused about which is current
- Lost work because context spread across files

**Diagnosis:**
```bash
# List all sessions and their branch names
for file in .prompty/session/session_*.md; do
  echo "=== $file ==="
  head -5 "$file"
done

# Or use grep to find matching branches
grep -l "branch: \"feat/PROJ-123-auth\"" .prompty/session/session_*.md
```

**Solution:**

1. **Identify which session is current:**
   ```bash
   # Check dates - most recent is likely current
   ls -lt .prompty/session/session_*.md | head -3
   ```

2. **Merge information if needed:**
   - Read both session files
   - Copy any important Actions Taken to the more recent one
   - Delete the older session

3. **Delete duplicates:**
   ```bash
   # Keep the most recent, delete others
   rm .prompty/session/session_older_date_*.md
   ```

4. **Update the surviving session:**
   - Make sure `current_mode` is set correctly
   - Update `created_at` if needed
   - Run a mode switch to record where you are

---

## Issue 3: Session Branch Doesn't Match Current Branch

**Symptoms:**
- Session file has different branch name than current branch
- Context doesn't make sense for current work
- Warnings about branch mismatch

**Diagnosis:**
```bash
# Check current branch
git branch --show-current
# Output: feat/PROJ-123-auth

# Check session branch field
grep "^branch:" .prompty/session/session_*.md
# Output: branch: "feat/PROJ-124-other"
# ❌ MISMATCH!
```

**Solutions:**

### Solution A: Create New Session for Current Branch
```bash
# Current branch is feat/PROJ-123-auth
# But session is for feat/PROJ-124-other
# → Create new session for current branch

# Keep old session as backup (won't hurt)
# Create new session for feat/PROJ-123-auth
```

### Solution B: Switch to the Correct Branch
```bash
# If session is for feat/PROJ-124-other but you want to work there:
git checkout feat/PROJ-124-other

# Now session will match
# Verify:
git branch --show-current  # Should match session branch
```

### Solution C: Fix Session Branch Field
```bash
# If session is wrong for some reason, edit it:
# (Careful - YAML is sensitive to formatting)

# Current:
#   branch: "feat/PROJ-124-wrong"
# 
# Should be:
#   branch: "feat/PROJ-123-correct"

# Then verify it matches current branch
```

---

## Issue 4: YAML Frontmatter is Broken

**Symptoms:**
- Error parsing session file
- Frontmatter doesn't load
- Session recognized as corrupted

**Diagnosis:**
```bash
# Check YAML syntax
head -10 .prompty/session/session_*.md

# Should look like:
# ---
# session_id: "session_20260304_k7m9x1"
# branch: "feat/PROJ-123-..."
# created_at: "2026-03-04T14:30:00Z"
# current_mode: "code"
# version: "1.0"
# ---
```

**Common Issues:**

### Missing or Extra Dashes
❌ Wrong:
```
--
session_id: ...
--
```

✓ Correct:
```
---
session_id: ...
---
```

### Indentation Issues
❌ Wrong:
```yaml
---
  session_id: "..." (extra spaces)
---
```

✓ Correct:
```yaml
---
session_id: "..."
---
```

### Quote Issues
❌ Wrong:
```yaml
session_id: session_20260304_k7m9x1 (no quotes)
branch: 'feat/PROJ-123 (mismatched quotes)
```

✓ Correct:
```yaml
session_id: "session_20260304_k7m9x1"
branch: "feat/PROJ-123-auth"
```

**Solution:**

1. **Fix the YAML carefully:**
   ```bash
   # Open in editor and fix formatting
   vim .prompty/session/session_20260304_k7m9x1.md
   
   # Verify syntax after editing
   head -10 .prompty/session/session_*.md
   ```

2. **If too broken, create new session:**
   ```bash
   # Copy content to new session
   # Keep old one as backup (it might still have context)
   # Create fresh session with correct YAML
   ```

---

## Issue 5: Session Context is Unclear

**Symptoms:**
- Session exists but doesn't explain current state
- Context Summary is vague or incomplete
- Don't understand what work has been done

**Diagnosis:**
```bash
# Read the entire session file carefully
cat .prompty/session/session_*.md

# Check specific sections:
# 1. Context Summary (what work is in progress?)
# 2. Mode History (what modes have we been in?)
# 3. Actions Taken (what specifically was done?)
```

**Solutions:**

### Solution A: Read Sections Carefully
1. Read **Mode History** - see the sequence of work
2. Read **Actions Taken** - see specific files and decisions
3. Read **Context Summary** - high-level view of current state

### Solution B: Check Related Files
```bash
# Actions Taken reference files that were created/modified
# Open those files to understand what happened

# Example from session:
# "File: src/auth/jwt_validator.py - Created"
# → Open that file to see what was built

cat src/auth/jwt_validator.py
```

### Solution C: Review Commit History
```bash
# Sessions reference work but commits have details
# Look at commits on this branch

git log --oneline  # Recent commits
git show <commit>  # Details of specific commit
```

### Solution D: Ask for Clarification
- If context is still unclear, ask the user
- Better to clarify than proceed with wrong understanding
- Update session with clarifications

---

## Issue 6: Session is Too Old (Stale)

**Symptoms:**
- Session was created > 1 week ago
- Branch has many new commits
- Context may be outdated

**Diagnosis:**
```bash
# Check session age
ls -l .prompty/session/session_*.md

# Check how old the branch is
git log -1 --format="%ai" main..HEAD

# Compare dates
```

**Solutions:**

### Solution A: Review and Update Context
1. Read current session
2. Review git log since session was created
3. Update Context Summary with latest status
4. Update Mode History with recent mode switches

### Solution B: Create New Session
```bash
# If too much has changed, create fresh session
# and archive the old one

# Archive old session
mkdir -p .prompty/session/archive/
mv .prompty/session/session_old_date_*.md .prompty/session/archive/

# Create new session with current state
# (Copy relevant info from old session if needed)
```

### Solution C: Keep Historical Record
```bash
# Archive old sessions after ~30 days
# This keeps history but avoids confusion

mkdir -p .prompty/session/archive/
mv .prompty/session/session_*.md .prompty/session/archive/

# Keeps context but signals this is old work
# Create new session for current work
```

---

## Issue 7: Mode History is Missing or Incomplete

**Symptoms:**
- No Mode History section in session
- Only one mode even though you switched modes
- Can't see progression of work

**Diagnosis:**
```bash
# Check if Mode History section exists
grep -A 10 "## Mode History" .prompty/session/session_*.md

# If missing or only one entry, it needs updating
```

**Solution:**

1. **Add Mode History section if missing:**
   ```markdown
   ## Mode History

   | Mode | Entered | Exited | Summary |
   |------|---------|--------|---------|
   | architect | 09:00 | 11:15 | Designed auth system |
   | code | 11:15 | 16:45 | Implemented models |
   | review | 17:00 | - | Code review in progress |
   ```

2. **Update when switching modes:**
   ```markdown
   # Before switching, update the current mode row:
   | code | 11:15 | 16:45 | Implemented 3 models, 92% test coverage |
   
   # Then add new mode row:
   | review | 17:00 | - | Code review in progress |
   ```

---

## Issue 8: Actions Taken is Vague or Missing Details

**Symptoms:**
- Actions Taken section is empty or sparse
- Can't see what specifically was done
- No timestamps on entries

**Solution:**

1. **Add detailed entries:**
   ```markdown
   ### 2026-03-04 14:45 - code mode
   - **Task:** PROJ-123-1 - Implement JWT validation
   - **File:** `src/auth/jwt_validator.py` - Created, 150 LOC
   - **Status:** Complete, tests passing
   ```

2. **Include:**
   - Timestamps (ISO8601 format)
   - What was done (specific, not vague)
   - Files created/modified
   - Status (complete, in progress, blocked)

---

## Quick Checklist: Session Health

```
Session Health Check:
- [ ] Session file exists for current branch
- [ ] YAML frontmatter is valid (can be parsed)
- [ ] Branch field matches current branch
- [ ] Mode History section exists and has entries
- [ ] Actions Taken section exists with timestamps
- [ ] Context Summary is clear and current
- [ ] File is < 500 lines (otherwise archive and create new)
- [ ] Created date is < 1 week old (otherwise review)
```

If ANY check fails, refer to the relevant issue section above.

---

## Preventing Problems

### 1. Create Session Immediately
```bash
# When starting work on new branch:
git checkout -b feat/PROJ-123-...
# Create session before doing anything else
```

### 2. Update After Significant Work
```bash
# After completing a task:
# Update Actions Taken and Context Summary
# Don't wait until end of day
```

### 3. Review Before Mode Switch
```bash
# Before switching modes:
# Update Mode History with exit time and summary
# Read Context Summary for next mode
```

### 4. Archive Old Sessions
```bash
# After ~1 week on a branch:
# Archive old session if creating new one
mkdir -p .prompty/session/archive/
mv old_session.md .prompty/session/archive/
```

---

## When to Contact Support

If you encounter issues not covered here:
- Session file is corrupted beyond repair
- Git branch is in inconsistent state
- Multiple tools created conflicting sessions
- Lost important session context

→ **Create new session and note what happened as meta-comment**

All session files are safe to delete/recreate - they're not committed to git.
