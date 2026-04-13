---
name: strategy
description: Comprehensive strategy planning process
languages: [all]
subagents: [planning/strategy, architect/scaffold, code/feature, code/boilerplate]
steps:
  - Read target files and imports
  - Identify code smells
  - Define interface constraints
  - Propose refactoring approach
  - Flag decision points
  - Estimate scope and effort
  - Get confirmation
  - Check session management
  - Session creation/update
  - Record decisions
---

## Strategy Planning Workflow - Verbose

### Step 1: Read target files and imports

Before proposing any changes, read the complete file(s) being refactored and all files they import. This establishes the baseline for understanding existing patterns, dependencies, and constraints.

**What to look for:**
- Current code patterns and conventions
- Existing abstractions and their boundaries
- Dependencies between modules
- Test coverage for the code being refactored
- Public vs internal APIs

**Output:** Complete understanding of existing code structure and patterns.

### Step 2: Identify code smells

Identify the specific problems or "smells" you observe. These might include:
- Duplication (DRY violations)
- Long methods or classes (single responsibility violations)
- Complex conditionals
- Tight coupling
- Hard-coded values
- Missing abstractions

Pick from standard smell categories or name custom smells specific to this code.

**What to document:**
- Which specific code exhibits the smell
- Why it's problematic
- What impact it has on maintainability

**Output:** Clear list of identified problems and their locations.

### Step 3: Define interface constraints

Determine which parts of the observable interface (public API, contract) must be preserved. This prevents breaking changes and ensures the refactoring maintains backward compatibility.

**Interface elements to consider:**
- Public function/method signatures
- Return types and side effects
- Error handling contracts
- Database schema (if applicable)
- API endpoints and request/response shapes
- Event interfaces

**What to document:**
- Which interfaces cannot change
- Which can change (internal implementation)
- Migration path if breaking changes are unavoidable

**Output:** Clear definition of what must remain stable.

### Step 4: Propose refactoring approach

Describe your refactoring strategy with specific moves. Be concrete about what you will change and why.

**Include:**
- Overview of the proposed structure
- Specific refactoring moves (e.g., "extract method", "move class", "inline function")
- Which files will be affected
- Sequence of changes
- How you'll maintain backward compatibility

**Format:**
1. Problem summary (one sentence)
2. Proposed solution (one sentence)
3. Specific refactoring moves (numbered list)
4. Files to be modified/created/deleted
5. Rationale for this approach vs alternatives

**Output:** Detailed implementation plan the user can review before work begins.

### Step 5: Flag decision points

Identify moments in the refactoring where judgment calls are required. These are places where you cannot determine the right choice from the code alone and need user guidance.

**Examples of decision points:**
- "Should this new abstraction be in the same file or separate file?"
- "Is performance critical enough to justify caching here?"
- "Should we add new dependencies or build custom solution?"
- "Do we need to maintain backward compatibility for this API?"

**What to document:**
- Each decision point
- Your recommendation if applicable
- Trade-offs for each option
- Time cost of each choice

**Output:** List of decisions that need user approval to proceed.

### Step 6: Estimate scope and effort

Estimate the effort and complexity of the refactoring.

**Provide:**
- Number of files that will change
- Estimate of size (XS/S/M/L)
- Whether it can be done incrementally (smaller, testable pieces)
- Approximate lines of code affected
- Test coverage requirements

**Effort levels:**
- XS: < 1 hour, single file, low risk
- S: 2-4 hours, 2-3 files, well-understood change
- M: half day, 4-8 files, moderate complexity
- L: 1-2 days, multiple moving parts, significant refactoring

**Output:** Clear estimate the user can approve.

### Step 7: Get confirmation

Summarize the refactoring plan and wait for user approval before proceeding. This prevents wasted effort if the direction is wrong.

**Summary to present:**
1. Problems being solved
2. Proposed approach
3. Scope estimate
4. Decision points needing approval
5. Files that will change

**Output:** Explicit user approval to proceed, or feedback to adjust the plan.

### Step 8: Check session management

Before starting implementation, verify session management is properly configured. Sessions track work across mode switches and provide continuity.

**Check:**
- Session file exists for current branch
- Branch name in session matches current branch
- Session has Mode History section
- Current mode is updated in session
- Context Summary is accurate

**Output:** Valid session ready for implementation work.

### Step 9: Session creation/update

If no valid session exists, create one. If session exists, update it with the current work.

**Session file location:** `.promptosaurus/sessions/session_{YYYYMMDD}_{RANDOM}.md`

**YAML frontmatter:**
```yaml
---
session_id: "session_20260410_..."
branch: "feat/..."
created_at: "2026-04-10T..."
current_mode: "code"
version: "1.0"
---
```

**Sections to maintain:**
- Mode History (record mode switches)
- Actions Taken (log significant work)
- Context Summary (high-level status)

**Output:** Valid session file with refactoring context recorded.

### Step 10: Record decisions

Document all significant decisions made during planning in the session file. This helps future reviewers understand the reasoning.

**For each decision, record:**
- What was decided
- Why this option was chosen
- What alternatives were considered
- Impact on the refactoring

**Format in Actions Taken section:**
```
### {timestamp} - {mode} mode
- **Decision:** {What was decided}
- **Rationale:** {Why}
- **Alternatives:** {What else was considered}
- **Status:** Approved
```

**Output:** Documented decisions in session for accountability and learning.
