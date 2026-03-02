# Product Requirements Document: Session Context Persistence

**Document Version:** 1.0  
**Date:** 2026-03-02  
**Status:** Draft  
**Author:** AI Assistant  

---

## 1. Executive Summary

This PRD defines the Session Context Persistence feature for the PromptCLI/Kilo Code system. Currently, mode switches result in complete loss of context—users must repeatedly explain their goals, re-reference files, and re-establish context. This feature introduces persistent session files that maintain continuity across mode switches, branch changes, and IDE restarts.

**Key Benefits:**
- **Context Continuity:** Maintain task state, decisions, and progress across mode switches
- **Branch-Aware Sessions:** Sessions are tied to feature branches, enabling natural workflow alignment
- **Automatic Management:** Sessions are created, updated, and retrieved transparently without user intervention
- **Audit Trail:** Complete history of mode transitions and actions for debugging and review

**Success Metrics:**
- 90%+ reduction in repeated context explanations during mode switches
- Zero user effort to manage session lifecycle (automatic creation/updates)
- Session files provide actionable context when revisiting branches after days/weeks

---

## 2. Problem Statement

### 2.1 Current Pain Points

1. **Context Loss on Mode Switch:** When switching from architect to code mode, all design decisions, constraints, and context must be re-explained
2. **No Session Boundaries:** AI cannot distinguish between unrelated tasks on the same branch
3. **Branch Context Confusion:** Work done on feature branches lacks association with the branch itself
4. **No Historical Recall:** Returning to a branch after time away requires rebuilding context from git history

### 2.2 Use Cases

**UC-1: Multi-Mode Feature Development**
User starts in architect mode to design a new API, switches to code mode for implementation, then to test mode for verification. Each mode switch currently loses previous context.

**UC-2: Interrupted Workflows**
User is halfway through implementing a feature when they need to switch to a hotfix on another branch. Returning to the feature branch should restore their previous session context.

**UC-3: Long-Running Sessions**
User works on a complex feature spanning multiple days. Session history provides continuity and decision trail.

---

## 3. User Stories

### 3.1 Session Lifecycle

**US-1.1:** As a developer starting work on a feature branch, I want a session to be automatically created so that my work context is captured without manual effort.

**US-1.2:** As a developer returning to a feature branch after working elsewhere, I want my previous session context to be automatically restored so I don't need to reconstruct my mental model.

**US-1.3:** As a developer on the main branch, I want the system to either create a new feature branch for me or ask for a branch name so that session context is properly isolated.

**US-1.4:** As a developer working on multiple features, I want to see all active sessions so I can choose which one to resume.

### 3.2 Mode Integration

**US-2.1:** As a developer switching from Architect to Code mode, I want the new mode to receive a summary of design decisions so implementation aligns with the architecture.

**US-2.2:** As a developer in any mode, I want the system to know which mode I'm in and what I've already done so I don't need to repeat context.

**US-2.3:** As a developer completing a task, I want the session to record what was accomplished so the next mode can build on it.

### 3.3 Context Recovery

**US-3.1:** As a developer returning to work after a break, I want to see what I was last working on, what decisions were made, and what remains incomplete.

**US-3.2:** As a developer debugging an issue, I want to see the history of mode switches and actions that led to the current state.

---

## 4. Functional Requirements

### 4.1 Session Storage

| ID | Requirement | Priority |
|----|-------------|----------|
| F1.1 | Session files stored in `.prompty/session/` directory | Must |
| F1.2 | Session files named `session_{id}.md` with unique identifier | Must |
| F1.3 | Session directory created automatically if it doesn't exist | Must |
| F1.4 | Session files use Markdown with YAML frontmatter format | Must |
| F1.5 | Old session files archived after 30 days of inactivity | Could |

### 4.2 Branch Association

| ID | Requirement | Priority |
|----|-------------|----------|
| F2.1 | Session files include `branch_name` field in frontmatter | Must |
| F2.2 | Multiple sessions allowed per branch (no uniqueness constraint) | Must |
| F2.3 | When on main branch, system detects and prompts for feature branch creation | Must |
| F2.4 | If branch detection fails, system prompts user for branch name | Must |
| F2.5 | Session lookup by branch name returns most recently active session | Should |
| F2.6 | Branch name extraction from git commands with fallback chain | Must |

### 4.3 Session Identification

| ID | Requirement | Priority |
|----|-------------|----------|
| F3.1 | AI context tracks currently active session ID | Must |
| F3.2 | `current_session` pointer file stored at `.prompty/session/.current` | Must |
| F3.3 | Pointer file contains only the active session filename | Must |
| F3.4 | Session ID is a URL-safe string (UUID or timestamp-based) | Must |
| F3.5 | Session lookup falls back to branch-based search if pointer missing | Should |

### 4.4 File Format

| ID | Requirement | Priority |
|----|-------------|----------|
| F4.1 | YAML frontmatter contains all metadata fields | Must |
| F4.2 | `session_id` field: unique identifier | Must |
| F4.3 | `branch_name` field: associated git branch | Must |
| F4.4 | `start_time` field: ISO 8601 timestamp of session creation | Must |
| F4.5 | `last_updated` field: ISO 8601 timestamp of last activity | Must |
| F4.6 | `mode_history` field: array of mode transitions with timestamps | Must |
| F4.7 | `current_mode` field: slug of active mode | Must |
| F4.8 | `context_summary` field: text summary of current work | Must |
| F4.9 | `actions_taken` field: array of completed actions | Must |
| F4.10 | Body section contains detailed context, decisions, notes | Should |

### 4.5 Mode Integration

| ID | Requirement | Priority |
|----|-------------|----------|
| F5.1 | All modes check for session file on startup | Must |
| F5.2 | If no session exists for current branch, create new session automatically | Must |
| F5.3 | Session context read and provided to mode at startup | Must |
| F5.4 | Session file updated when switching modes | Must |
| F5.5 | Session file updated when completing significant actions | Must |
| F5.6 | Mode prompt includes session context awareness instructions | Must |
| F5.7 | Session provides continuity across mode switches | Must |

---

## 5. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| N1.1 | Session file operations must complete within 100ms |
| N1.2 | Session files must be human-readable and editable |
| N1.3 | Session format must be versioned for future migrations |
| N1.4 | Git branch detection must work in detached HEAD state with graceful fallback |
| N1.5 | Session system must not block mode startup on file I/O errors |
| N1.6 | Maximum session file size: 1MB (with rotation/archival for large sessions) |
| N1.7 | Session files must be excluded from git via `.gitignore` |

---

## 6. Session File Format Specification

### 6.1 File Location

```
.prompty/
├── session/
│   ├── session_abc123def.md
│   ├── session_xyz789ghi.md
│   └── .current  # Pointer to active session
└── configurations.yaml
```

### 6.2 File Structure

```markdown
---
session_id: sess_20260302_001
branch_name: feature/session-persistence
start_time: "2026-03-02T15:30:00Z"
last_updated: "2026-03-02T16:45:22Z"
current_mode: architect
mode_history:
  - mode: architect
    entered_at: "2026-03-02T15:30:00Z"
    summary: "Designing session persistence feature"
  - mode: code
    entered_at: "2026-03-02T16:15:00Z"
    summary: "Implementing session manager module"
  - mode: architect
    entered_at: "2026-03-02T16:45:22Z"
    summary: "Reviewing implementation approach"
context_summary: |
  Designing session context persistence for PromptCLI.
  Key decisions: store in .prompty/session/, YAML frontmatter,
  branch-based association, automatic lifecycle management.
actions_taken:
  - timestamp: "2026-03-02T15:35:00Z"
    mode: architect
    action: "Created PRD for session persistence"
    files_affected:
      - docs/prd/session-context-persistence.md
  - timestamp: "2026-03-02T16:00:00Z"
    mode: architect
    action: "Created ARD with data models"
    files_affected:
      - docs/ard/session-context-persistence.md
---

# Session: Session Context Persistence Design

## Current Focus
Creating comprehensive design documents for session context persistence feature.

## Key Decisions
1. Store session files in `.prompty/session/` directory
2. Use YAML frontmatter for metadata, Markdown body for details
3. Branch association allows multiple sessions per branch
4. Automatic session lifecycle (create/update without user action)

## Open Questions
- Should we implement session archival/rotation for large files?
- How to handle merge conflicts in session context?

## Notes
- Consider encryption for sensitive context
- Future: session sharing between team members
```

### 6.3 YAML Frontmatter Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | string | Yes | Unique session identifier |
| `branch_name` | string | Yes | Associated git branch |
| `start_time` | ISO 8601 datetime | Yes | Session creation timestamp |
| `last_updated` | ISO 8601 datetime | Yes | Last activity timestamp |
| `current_mode` | string | Yes | Active mode slug |
| `mode_history` | array | Yes | Mode transition history |
| `context_summary` | string | Yes | Current work summary |
| `actions_taken` | array | Yes | Completed actions log |
| `version` | string | No | Session format version |

### 6.4 Mode History Entry Schema

| Field | Type | Description |
|-------|------|-------------|
| `mode` | string | Mode slug |
| `entered_at` | ISO 8601 datetime | When mode was entered |
| `exited_at` | ISO 8601 datetime | When mode was exited (null if current) |
| `summary` | string | What was done in this mode |

### 6.5 Action Entry Schema

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 datetime | When action was completed |
| `mode` | string | Mode that performed the action |
| `action` | string | Description of what was done |
| `files_affected` | array | List of files modified/created |

---

## 7. Mode Integration Requirements

### 7.1 Session Awareness in All Modes

Each mode's prompt must be updated to include:

1. **Session Check Instruction:** Check for existing session on startup
2. **Context Reading:** Read session context if it exists
3. **Session Creation:** Create new session if none exists for current branch
4. **Context Updating:** Update session on mode switch and action completion
5. **Context Providing:** Include session context in responses

### 7.2 Mode-Specific Context Handling

| Mode | Context Provided | Context Captured |
|------|------------------|------------------|
| `architect` | Previous design decisions, constraints | Design decisions, task breakdowns |
| `code` | Architecture decisions, implementation notes | Code changes, implementation details |
| `test` | Code changes, test requirements | Test coverage, test results |
| `refactor` | Code smells, refactoring targets | Refactoring changes, improvements |
| `debug` | Error context, previous debugging steps | Root cause findings, fixes applied |
| `document` | Documentation needs, target audience | Documentation created, updates made |
| `review` | Code to review, review criteria | Review findings, recommendations |
| `security` | Security concerns, audit scope | Vulnerabilities found, mitigations |
| All others | Generic session context | Generic action logging |

### 7.3 Session-Aware Prompt Template

Each mode's system prompt should include:

```markdown
## Session Context Awareness

1. **On Startup:**
   - Check `.prompty/session/.current` for active session pointer
   - If no active session exists for current branch, create new session file
   - Read session context and incorporate into your understanding

2. **During Operation:**
   - Maintain awareness of session context in your responses
   - Reference previous decisions and actions when relevant
   - Update context_summary when focus or understanding changes

3. **On Mode Switch:**
   - Update mode_history with exit timestamp and summary
   - Ensure context_summary reflects current state

4. **On Action Completion:**
   - Log significant actions to actions_taken array
   - Include files affected by the action
   - Update last_updated timestamp

5. **Context Persistence:**
   - Session provides continuity—use it to avoid repeating information
   - Reference session history when user asks "what were we doing?"
   - Build on previous context rather than starting fresh
```

---

## 8. User Interaction Flows

### 8.1 New Session Creation Flow

```
User starts mode on feature branch
    ↓
System checks for existing session on branch
    ↓
No session found
    ↓
System creates new session file
    ↓
System updates .current pointer
    ↓
Mode starts with empty session context
```

### 8.2 Existing Session Restoration Flow

```
User starts mode on feature branch
    ↓
System checks for existing session on branch
    ↓
Session found
    ↓
System reads session context
    ↓
System updates mode_history
    ↓
Mode starts with full context loaded
```

### 8.3 Main Branch Handling Flow

```
User starts mode on main branch
    ↓
System detects main branch
    ↓
Option A: Auto-create feature branch (if configured)
        ↓
        System runs `git checkout -b feature/auto-{timestamp}`
        ↓
        Create session on new branch
    ↓
Option B: Prompt user for branch name
        ↓
        User provides branch name
        ↓
        System runs `git checkout -b {branch_name}`
        ↓
        Create session on new branch
```

### 8.4 Mode Switch Flow

```
User requests mode switch
    ↓
Current mode updates session:
   - Set exit timestamp in mode_history
   - Update context_summary
   - Log any pending actions
    ↓
System writes updated session file
    ↓
New mode starts:
   - Reads session context
   - Adds new entry to mode_history
   - Continues with full context
```

---

## 9. Success Metrics & KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Session Creation Rate | 100% | % of mode starts that have associated session |
| Context Retrieval Success | 95%+ | % of session lookups that find valid context |
| User Context Repetition | <10% | % of interactions where user repeats previous context |
| Session File Integrity | 99%+ | % of session files with valid YAML frontmatter |
| Mode Switch Continuity | 90%+ | % of mode switches where context is properly transferred |

---

## 10. Future Enhancements

| Priority | Enhancement | Description |
|----------|-------------|-------------|
| P1 | Session CLI Commands | List, switch, archive sessions via CLI |
| P2 | Session Diff/Merge | Compare sessions, merge context from multiple sessions |
| P3 | Session Templates | Pre-defined session templates for common workflows |
| P4 | Team Session Sharing | Share session context with team members |
| P5 | AI-Powered Summarization | Auto-generate context_summary from conversation |
| P6 | Session Analytics | Insights into mode usage, session duration, patterns |

---

## 11. Open Questions

1. **Session Archival:** Should we implement automatic archival of old sessions or leave that to the user?
2. **Multi-Branch Sessions:** Should sessions be transferable between branches (e.g., when a feature branch is merged)?
3. **Session Conflicts:** How should we handle concurrent session modifications?
4. **Session Privacy:** Should session files be encrypted or contain privacy controls?
5. **Migration Strategy:** How do we migrate session format versions when schema changes?
