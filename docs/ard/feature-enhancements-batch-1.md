# Architecture Requirements Document: Feature Enhancements Batch 1

**Document Version:** 1.0  
**Date:** 2026-03-02  
**Status:** Draft  
**Author:** AI Assistant  

---

## 1. Executive Summary

This ARD provides technical architecture and implementation guidance for three feature enhancements:

1. **Enhanced PR Description Generation** - Git integration for rich branch context
2. **Cross-Mode Role Awareness** - Mode metadata and handoff detection
3. **Legal Disclaimers** - Static content updates to existing prompts

---

## 2. Feature 1: Enhanced PR Description Generation

### 2.1 Current State

The PR description feature is implemented in:
- Prompt: [`orchestrator-pr-description.md`](promptcli/prompts/orchestrator-pr-description.md:1)
- Called by: `orchestrator` mode via [`orchestrator-meta.md`](promptcli/prompts/orchestrator-meta.md:57)

Current implementation reads git diff only:
```markdown
- Read the git diff or commit log if not provided — run git diff or git log directly
```

### 2.2 Proposed Architecture

#### 2.2.1 Git Context Gathering Module

Create a new utility module `promptcli/git_context.py`:

```python
from pydantic import BaseModel

class GitContextGatherer:
    """Gather comprehensive git context for PR generation."""
    
    def branch_context(self) -> BranchContext:
        """Extract branch name, ticket IDs, and metadata."""
        
    def commit_summary(self, base: str = "main") -> CommitSummary:
        """Parse conventional commits from base..HEAD."""
        
    def detect_pr_update(self, existing_pr_body: str | None) -> bool:
        """Determine if this is an initial PR or an update."""
        
    def format_for_prompt(self) -> str:
        """Format git context as structured text for LLM prompt."""
```

#### 2.2.2 Data Models

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class BranchContext(BaseModel):
    name: str
    ticket_ids: list[str]  # Extracted JIRA-123, #456, etc.
    type: Literal["feature", "bugfix", "hotfix", "chore", "unknown"]
    age_days: float
    commit_count: int

class ConventionalCommit(BaseModel):
    sha: str
    type: Literal["feat", "fix", "refactor", "test", "docs", "chore", "other"]
    scope: str | None
    description: str
    breaking: bool
    body: str | None

class CommitSummary(BaseModel):
    commits: list[ConventionalCommit]
    by_type: dict[str, list[ConventionalCommit]]
    breaking_changes: list[ConventionalCommit]
    files_changed: list[str]
```

#### 2.2.3 Git Command Strategy

| Information | Git Command | Fallback |
|-------------|-------------|----------|
| Branch name | `git branch --show-current` | `git rev-parse --abbrev-ref HEAD` |
| Commits vs main | `git log main..HEAD --format="%H|%s|%b"` | Use `origin/main` if local main stale |
| Files changed | `git diff --name-only main..HEAD` | Empty list on failure |
| Branch age | `git log HEAD --reverse --format="%ci" -1` | N/A |
| Existing PR | Read from `.github/pull_request_template.md` or env | None |

**Error Handling:**
- All git commands wrapped in try/except with 5s timeout
- On failure, fall back to simple `git diff` behavior
- Log warnings but don't fail the PR generation

#### 2.2.4 Prompt Template Updates

Update [`orchestrator-pr-description.md`](promptcli/prompts/orchestrator-pr-description.md:1) to include:

```markdown
## Git Context Gathering

Before generating the PR description:
1. Run `git branch --show-current` to get branch name
2. Run `git log main..HEAD --oneline` to get commit history
3. Parse branch name for ticket references (JIRA-###, ####)
4. Categorize commits by conventional commit type
5. Check if a PR description already exists (update vs. create)

## Output Formats

### Initial PR Format
Include sections:
- Summary (with ticket references if found)
- Changes (grouped by conventional commit type: feat, fix, refactor, etc.)
- Breaking Changes (if any commits have BREAKING CHANGE footer)
- Testing
- Ticket References

### Update PR Format
If updating an existing PR:
- Preserve the original Summary
- Add "## Updates Since Last Review" section
- List new commits only
- Note any breaking changes introduced
```

#### 2.2.5 Branch Name Parsing

Regex patterns for ticket extraction:
```python
patterns = {
    "jira": r"[A-Z]{2,}-\d+",  # JIRA-123, PROJ-456
    "github": r"#\d+",         # #123
    "linear": r"[A-Z]+-\d+",   # Same as JIRA
}

type_patterns = {
    "feature": r"^(feature|feat)/",
    "bugfix": r"^(bugfix|bug|fix)/",
    "hotfix": r"^hotfix/",
    "chore": r"^(chore|docs|refactor)/",
}
```

### 2.3 Files to Modify

| File | Change Type | Description |
|------|-------------|-------------|
| `promptcli/prompts/orchestrator-pr-description.md` | Modify | Add git context instructions |
| `promptcli/git_context.py` | Create | New git gathering utilities |
| `promptcli/builders/kilo.py` | Modify | Integrate git context into output |

### 2.4 Testing Strategy

1. **Unit Tests:** Mock git commands, test parsing logic
2. **Integration Tests:** Run against real git repos with known branch names
3. **Edge Cases:**
   - Detached HEAD state
   - No commits ahead of main
   - Unconventional commit messages
   - Very long branch names
   - Special characters in commit messages

---

## 3. Feature 2: Cross-Mode Role Awareness

### 3.1 Current State

Modes defined in [`.kilocodemodes`](.kilocodemodes:1) have:
- `slug`, `name`, `description`
- `roleDefinition` - detailed persona
- `whenToUse` - usage guidance
- `groups` - permission groups

No cross-mode awareness exists.

### 3.2 Proposed Architecture

#### 3.2.1 Mode Handoff Detection in Prompts

Add to each mode's prompt file (e.g., [`code-feature.md`](promptcli/prompts/code-feature.md:1)):

```markdown
## Mode Awareness

You are currently in Code mode. You specialize in implementation and feature development.

### When to Suggest Another Mode

If the user asks:
- Architecture or design questions → Suggest Architect mode
- Security concerns or vulnerability checks → Suggest Security mode
- Testing strategy questions → Suggest Test mode
- "Should I refactor this?" → Suggest Refactor mode

### How to Suggest a Switch

Say:
"This sounds like a [MODE_NAME] question. [Brief rationale]. 
Would you like to switch to [MODE_NAME] mode? 
Say 'switch to [slug]' or ask me to continue in Code mode."

Never answer questions outside your specialization without flagging the limitation.
```

#### 3.2.3 Handoff Matrix (Complete)

| From Mode | Trigger Pattern | To Mode | Rationale |
|-----------|-----------------|---------|-----------|
| Code | "architecture", "design", "structure" | Architect | System design expertise |
| Code | "secure", "vulnerability", "exploit", "OWASP" | Security | Security engineering specialization |
| Code | "test", "coverage", "TDD" | Test | Testing best practices |
| Code | "refactor", "clean up", "simplify" | Refactor | Code quality specialization |
| Architect | "implement", "write code", "example" | Code | Implementation expertise |
| Architect | "is this secure" | Security | Security review required |
| Security | "compliance", "SOC 2", "GDPR", "audit" | Compliance | Regulatory expertise |
| Security | "how do I fix" | Code | Implementation guidance |
| Compliance | "vulnerability", "exploit" | Security | Security technical analysis |
| Test | "hard to test", "refactor for testability" | Refactor | Improve testability |
| Debug | Root cause found, "how do I fix" | Code | Implement fix |
| Review | "should I rewrite", "needs redesign" | Refactor | Code restructuring |
| Ask | "do this for me", "implement" | Code | Hands-on coding |
| Ask | "create a design for" | Architect | System design |
| Migration | "update the code" | Code | Post-migration implementation |

### 3.3 Files to Modify

| File | Change Type | Description |
|------|-------------|-------------|
| `promptcli/prompts/*.md` (all) | Modify | Add "Mode Awareness" section to each mode prompt |

### 3.4 Implementation Order

1. Add "Mode Awareness" section to core mode prompts (code, security, architect, test, debug, refactor)
2. Roll out to remaining mode prompts

---

## 4. Feature 3: Legal Disclaimers

### 4.1 Current State

No disclaimers exist in:
- [`security-review.md`](promptcli/prompts/security-review.md:1)
- [`compliance-review.md`](promptcli/prompts/compliance-review.md:1)
- [`.kilocodemodes`](.kilocodemodes:188) Security/Compliance definitions

### 4.2 Proposed Changes

#### 4.2.1 Security Review Disclaimer

Add to top of [`security-review.md`](promptcli/prompts/security-review.md:1):

```markdown
# security-review.md
# Behavior when the user asks for a security review of code or infrastructure.

> ⚠️ **DISCLAIMER:** This security analysis is generated by an AI assistant and 
> is provided "as-is" without warranty of any kind. It is not a substitute for 
> a professional security audit or penetration test. Findings should be validated 
> by qualified security professionals. You are solely responsible for verifying 
> recommendations and ensuring your code meets your organization's security 
> requirements.

## Before Reviewing
# ... rest of file unchanged
```

#### 4.2.2 Compliance Review Disclaimer

Add to top of [`compliance-review.md`](promptcli/prompts/compliance-review.md:1):

```markdown
# compliance-review.md
# Behavior when the user asks for a compliance review of code, infrastructure, 
# or data handling.

> ⚠️ **DISCLAIMER:** This compliance analysis is generated by an AI assistant 
> and is provided "as-is" without warranty of any kind. It is not legal advice 
> and does not constitute a formal compliance assessment. Controls and findings 
> should be validated by qualified legal and compliance counsel before relying 
> on them for audits or regulatory submissions. You are solely responsible for 
> ensuring your systems meet applicable regulatory requirements.

## Step 1 — Establish Scope
# ... rest of file unchanged
```

#### 4.2.3 Mode Definition Updates

Update [`.kilocodemodes`](.kilocodemodes:188) Security mode:

```yaml
- slug: security
  name: 🔐 Security
  description: Security reviews for code and infrastructure. 
    ⚠️ AI-generated analysis - not a substitute for professional security audit.
  roleDefinition: |
    You are a senior application security engineer...
    
    IMPORTANT LIMITATION: You are an AI assistant providing guidance only. 
    Always recommend validation by qualified security professionals for 
    production systems.
```

Update [`.kilocodemodes`](.kilocodemodes:210) Compliance mode:

```yaml
- slug: compliance
  name: 📋 Compliance
  description: SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS compliance reviews.
    ⚠️ AI-generated analysis - not legal advice or formal assessment.
  roleDefinition: |
    You are a senior compliance engineer and technical auditor...
    
    IMPORTANT LIMITATION: You are an AI assistant providing guidance only. 
    Always recommend seeking qualified legal or compliance counsel for formal 
    audit purposes and regulatory interpretation.
```

### 4.3 Files to Modify

| File | Change Type | Description |
|------|-------------|-------------|
| `promptcli/prompts/security-review.md` | Modify | Add disclaimer header |
| `promptcli/prompts/compliance-review.md` | Modify | Add disclaimer header |
| `.kilocodemodes` | Modify | Add disclaimer to Security/Compliance descriptions |

---

## 5. Implementation Phases

### Phase 1: Legal Disclaimers (Low Risk)
- **Effort:** 1-2 hours
- **Files:** 3 markdown files
- **Risk:** Minimal - text-only changes
- **Order:** Start here for quick win

### Phase 2: Cross-Mode Awareness (Medium Risk)
- **Effort:** 4-6 hours
- **Files:** [`.kilocodemodes`](.kilocodemodes:1), [`registry.py`](promptcli/registry.py:1), 12+ prompt files
- **Risk:** Mode handoffs could be annoying if too aggressive
- **Order:** Implement after disclaimers
- **Strategy:** Pilot with 3 core modes (Code, Security, Architect), then expand

### Phase 3: Enhanced PR Descriptions (Higher Risk)
- **Effort:** 8-12 hours
- **Files:** New module + prompt updates
- **Risk:** Git command failures, performance issues
- **Order:** Implement last
- **Strategy:** Extensive testing required

---

## 6. Performance Considerations

| Feature | Impact | Mitigation |
|---------|--------|------------|
| Git commands | +2-5s latency | 5s timeout, caching, async execution |
| Mode metadata parsing | Minimal | Parse once at startup, cache in Registry |
| Disclaimer text | +~200 tokens per response | Negligible |

---

## 7. Security Considerations

| Feature | Risk | Mitigation |
|---------|------|------------|
| Git context gathering | Command injection via branch names | Sanitize all git inputs, use `--` separators |
| PR description generation | Secrets in commit messages | Filter patterns matching secrets before LLM |
| Mode handoff suggestions | Social engineering via crafted prompts | Suggestions only, user must confirm switch |

---

## 8. Appendix

### 8.1 Git Context Output Format

Example of formatted git context for LLM prompt:

```markdown
## Branch Context

- **Branch:** feature/JIRA-456-add-oauth
- **Type:** feature
- **Ticket References:** JIRA-456
- **Commits ahead of main:** 7
- **Branch age:** 3 days

## Commit Summary

### Features (2)
- `a1b2c3d` feat(auth): add OAuth2 login flow
- `e4f5g6h` feat(auth): implement token refresh

### Fixes (1)
- `i7j8k9l` fix(auth): handle expired tokens gracefully

### Refactors (1)
- `m0n1o2p` refactor(auth): extract auth utilities

### Breaking Changes
⚠️ **BREAKING CHANGE:** OAuth configuration now requires `client_secret` 
in `config/oauth.yml` (previously optional)

## Files Changed (12)
- src/auth/oauth.py (new)
- src/auth/token.py (new)
- tests/auth/test_oauth.py (new)
- config/oauth.yml.example (modified)
- ...
```

### 8.2 Related Documents

- [PRD: Feature Enhancements Batch 1](docs/prd/feature-enhancements-batch-1.md)
- [`.kilocodemodes`](.kilocodemodes:1)
- [`promptcli/registry.py`](promptcli/registry.py:1)
- [Git Context ADR (to be created)](docs/adr/)
