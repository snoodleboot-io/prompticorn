# Product Requirements Document: Feature Enhancements Batch 1

**Document Version:** 1.0  
**Date:** 2026-03-02  
**Status:** Draft  
**Author:** AI Assistant  

---

## 1. Executive Summary

This PRD documents three feature enhancements for the PromptCLI/Kilo Code system:

1. **Enhanced PR Description Generation** - Enrich PR descriptions with comprehensive branch context
2. **Cross-Mode Role Awareness** - Enable modes to recognize when tasks require switching to another mode
3. **Legal Disclaimers for Security & Compliance** - Add liability disclaimers to security and compliance modes

These enhancements improve user experience, reduce context switching friction, and mitigate legal risk.

---

## 2. Feature 1: Enhanced PR Description Generation

### 2.1 Problem Statement

Currently, the orchestrator PR description prompt ([`orchestrator-pr-description.md`](promptcli/prompts/orchestrator-pr-description.md:8)) only instructs to "Read the git diff or commit log if not provided." This results in PR descriptions that:
- Miss context from branch naming conventions
- Don't leverage commit message patterns
- Cannot update existing PRs when new commits are added
- Lack categorization of changes based on commit history

### 2.2 User Stories

**US-1.1:** As a developer creating a PR, I want the system to extract context from my branch name (e.g., `feature/JIRA-123-add-login`) so that the PR description includes the ticket reference and change type.

**US-1.2:** As a developer with multiple commits, I want the PR description to summarize all commits on my branch compared to `main`, grouped by type (feat, fix, refactor), so reviewers understand the full scope.

**US-1.3:** As a developer updating an existing PR with new commits, I want the system to suggest an "Update" section that appends new changes to the existing description rather than regenerating it entirely.

**US-1.4:** As a reviewer, I want PR descriptions to include a "Commit Summary" section showing the evolution of the branch so I can trace the development history.

### 2.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| F1.1 | Extract and parse branch name to identify ticket IDs (JIRA, GitHub Issues, etc.) | Must |
| F1.2 | Parse conventional commits from `git log main..HEAD` and group by type | Must |
| F1.3 | Generate both "Initial PR" and "PR Update" formats based on context | Must |
| F1.4 | Include branch age (time since first commit) and number of files changed | Should |
| F1.5 | Detect breaking changes from commit messages (`BREAKING CHANGE:` footer) | Should |
| F1.6 | Suggest reviewers based on files changed and git blame history | Could |

#### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| N1.1 | Git command execution must not exceed 5 seconds |
| N1.2 | Branch parsing must support common patterns: `feature/`, `bugfix/`, `hotfix/`, `JIRA-###-description` |
| N1.3 | Works in detached HEAD state (fall back to commit messages only) |

### 2.4 Success Metrics

- PR descriptions include ticket references in 90%+ of cases where branch name contains them
- Commit summary section shows conventional commit grouping
- Users report reduced time writing PR descriptions

---

## 3. Feature 2: Cross-Mode Role Awareness

### 3.1 Problem Statement

Each mode in [`.kilocodemodes`](.kilocodemodes:1) operates in isolation. Users frequently:
- Ask the wrong mode for a task (e.g., asking Code mode for architecture advice)
- Don't know which mode to use for hybrid tasks
- Must manually switch modes when tasks evolve

### 3.2 User Stories

**US-2.1:** As a user in Code mode, when I ask "should I refactor this first?", I want the system to suggest switching to Refactor mode with an explanation of why.

**US-2.2:** As a user in any mode, when my request clearly belongs to another mode, I want the system to say "This is a security review question - switch to Security mode?" rather than answering incorrectly.

**US-2.3:** As a user in Architect mode, when I start asking implementation questions, I want the system to suggest switching to Code mode.

**US-2.4:** As a new user, I want the system to explain which mode to use for my task if I'm unsure.

### 3.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| F2.1 | Each mode's role definition must include a "whenToSwitch" section describing signals that indicate another mode is more appropriate | Must |
| F2.2 | Each mode must list 3-5 "relatedModes" with specific handoff triggers | Must |
| F2.3 | When a request clearly belongs to another mode, the system must suggest the switch with rationale | Must |
| F2.4 | Add a mode-selection helper that asks clarifying questions to route to the correct mode | Should |
| F2.5 | Track conversation context to detect mode drift and suggest switches proactively | Could |

#### Mode Handoff Matrix

| Current Mode | Signal to Switch | Target Mode |
|--------------|------------------|-------------|
| Code | "Should I redesign this?" / Architecture questions | Architect |
| Code | "Is this secure?" / Security concerns | Security |
| Code | "How do I test this?" | Test |
| Architect | "How do I implement this?" / Code examples requested | Code |
| Security | "Does this meet SOC 2?" / Compliance frameworks | Compliance |
| Compliance | "Is this vulnerable?" / Exploitability questions | Security |
| Test | "This is hard to test" / Design issues | Refactor |
| Debug | Root cause found, fix needed | Code |
| Review | "Should I rewrite this?" | Refactor |
| Ask | "Do this for me" / Implementation request | Code |

### 3.4 Success Metrics

- Users correctly routed to appropriate mode in 80%+ of edge cases
- Reduced "you should use X mode instead" responses from users
- Increased multi-mode workflows (sequential mode usage)

---

## 4. Feature 3: Legal Disclaimers for Security & Compliance

### 4.1 Problem Statement

Security ([`security-review.md`](promptcli/prompts/security-review.md:1)) and Compliance ([`compliance-review.md`](promptcli/prompts/compliance-review.md:1)) modes provide professional-grade analysis but lack disclaimers about:
- The AI nature of the analysis
- No warranty or liability
- Not a substitute for professional audit/legal review
- User responsibility for final decisions

### 4.2 User Stories

**US-3.1:** As a security engineer using the tool, I want clear disclaimers so my organization understands this is an assistive tool, not a certified security audit.

**US-3.2:** As a compliance officer, I want explicit statements that findings should be validated by qualified legal/compliance counsel before relying on them for audits.

**US-3.3:** As a developer, I want to understand the limitations of AI-generated security advice so I don't assume false confidence.

### 4.3 Requirements

#### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| F3.1 | Add disclaimer header to [`security-review.md`](promptcli/prompts/security-review.md:1) output | Must |
| F3.2 | Add disclaimer header to [`compliance-review.md`](promptcli/prompts/compliance-review.md:1) output | Must |
| F3.3 | Include disclaimer in mode definition in [`.kilocodemodes`](.kilocodemodes:188) | Should |
| F3.4 | Disclaimers must be concise but cover: AI-generated nature, no warranty, not professional advice, user responsibility | Must |

#### Disclaimer Content Requirements

The disclaimer must include:
1. **Tool Nature:** "This analysis is generated by an AI assistant..."
2. **No Warranty:** "...provided 'as-is' without warranty of any kind..."
3. **Not Professional Advice:** "...not a substitute for professional security audit/legal review..."
4. **User Responsibility:** "...you are solely responsible for verifying findings..."

### 4.4 Success Metrics

- Disclaimers present in 100% of Security and Compliance mode outputs
- Legal risk assessment shows reduced exposure
- Users report understanding the tool's limitations

---

## 5. Out of Scope

The following are explicitly out of scope for this batch:

1. **GitHub/GitLab API Integration** - Local git only; remote platform APIs not included
2. **Automatic Mode Switching** - Suggestions only; user must confirm mode changes
3. **Persistent Conversation State** - No memory of previous mode switches across sessions
4. **Custom Disclaimer Wording** - Standard disclaimer text; no user customization

---

## 6. Dependencies

| Dependency | Impact |
|------------|--------|
| Git executable | Required for Feature 1 |
| Existing mode structure | Feature 2 modifies [`.kilocodemodes`](.kilocodemodes:1) and prompt files |
| Prompt template system | Feature 3 updates existing markdown files |

---

## 7. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Git command failures | Medium | Medium | Graceful fallback to basic diff |
| Mode handoff suggestions become annoying | Medium | Low | Make suggestions optional via config |
| Disclaimer too verbose | Low | Low | Keep to 2-3 sentences max |
| Performance degradation from git ops | Low | Medium | Cache git results, 5s timeout |

---

## 8. Open Questions

1. Should mode handoff suggestions include a clickable/actionable switch command?
2. Should the PR description feature cache git results between invocations?
3. Is there a specific legal team review required for the disclaimer text?

---

## 9. Appendix

### 9.1 Related Documents

- [`.kilocodemodes`](.kilocodemodes:1) - Mode definitions
- [`orchestrator-pr-description.md`](promptcli/prompts/orchestrator-pr-description.md:1) - Current PR prompt
- [`security-review.md`](promptcli/prompts/security-review.md:1) - Security mode prompt
- [`compliance-review.md`](promptcli/prompts/compliance-review.md:1) - Compliance mode prompt

### 9.2 Glossary

| Term | Definition |
|------|------------|
| Mode | A specialized AI persona (Code, Security, Architect, etc.) |
| Conventional Commit | Structured commit message format (`type(scope): description`) |
| PR | Pull Request |
| JIRA | Issue tracking system by Atlassian |
