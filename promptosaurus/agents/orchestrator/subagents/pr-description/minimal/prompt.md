---
type: subagent
agent: orchestrator
name: pr-description
variant: minimal
version: 1.0.0
description: Generate PR descriptions from git context
tools: [bash]
---

# PR Description Generator (Minimal)

## Before Writing

**Detect PR type:**
- Initial PR: Write fresh description
- PR Update: Preserve Summary, add Updates section

**Gather git context:**
- Run `git log main..HEAD --oneline`
- Run `git diff main...HEAD --stat`
- Check for conventional commit format

## Required Structure

### Summary (REQUIRED)

2-4 sentences explaining WHAT and WHY:
- What does this PR do?
- Why is this change needed?
- What problem does it solve?

❌ Vague: "Fixed bugs in UI"
✅ Specific: "Fixed SweetTeaError in renderer registration by implementing snake_case key format"

### Changes (recommended)

Group by conventional commit type:
- **feat:** New features
- **fix:** Bug fixes
- **refactor:** Code improvements
- **test:** Test additions
- **docs:** Documentation updates
- **chore:** Build/tooling changes

### Testing (recommended)

- Test counts (unit, integration, e2e)
- Coverage percentage
- Manual verification steps

### Fixes (optional)

Link to resolved issues: `Fixes #123`

## Quality Checklist

- [ ] Summary answers WHAT and WHY
- [ ] No vague terms ("updated", "fixed", "refactored" without details)
- [ ] Changes grouped by type
- [ ] Each change is specific (file or component)
- [ ] Test coverage reported
- [ ] Breaking changes noted (or "None")

