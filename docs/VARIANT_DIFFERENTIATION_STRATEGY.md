# Variant Differentiation Strategy

**Purpose:** Define clear differences between minimal and verbose variants  
**Date:** 2026-04-10

---

## Philosophy

**Minimal:** Concise, bullet-point style. For experienced developers who know the patterns.

**Verbose:** Detailed explanations, examples, edge cases. For learning or complex scenarios.

---

## Differentiation Guidelines

### Skills

**Minimal:**
- Concise bullet points
- Core instructions only
- Assumes reader knows context
- ~10-20 lines

**Verbose:**
- Detailed explanations
- Examples and code snippets
- Common pitfalls and edge cases
- Anti-patterns to avoid
- ~30-60 lines

**Example:**

#### Minimal - feature-planning
```markdown
## Instructions

Before implementing:
1. **Restate goal** - confirm understanding
2. **Read source files** - don't assume
3. **Identify files** to change
4. **Propose approach** with tradeoffs
5. **Flag assumptions**
6. **Wait for confirmation**
```

#### Verbose - feature-planning
```markdown
## Instructions

### Step 1: Restate the Goal

**Purpose:** Ensure alignment before writing code.

**How:**
- Summarize the feature in 1-2 sentences
- State the problem it solves
- Clarify expected behavior

**Example:**
> "We're adding a password reset feature because users can't recover locked accounts.
> When a user clicks 'Forgot Password', they should receive an email with a time-limited
> reset link."

### Step 2: Read Relevant Source Files

**Purpose:** Understand existing patterns before proposing changes.

**How:**
- Use `read` tool to examine related files
- Identify patterns (naming, error handling, tests)
- Note dependencies and integrations

**Common Mistake:** ❌ Assuming file structure without reading
**Correct Approach:** ✅ Read first, then propose

### Step 3: Identify All Files to Change

**Purpose:** Scope the work and catch integration points.

**How:**
- List all files that need modification
- Include tests, docs, config
- Note new files to create

**Example:**
```
Files to modify:
- src/auth/password_service.py (add reset logic)
- src/api/auth_routes.py (add /reset endpoint)
- tests/test_password_reset.py (new file)
- docs/API.md (document endpoint)
```

### Step 4: Propose Implementation Approach

**Purpose:** Get feedback on design before coding.

**Include:**
- High-level approach
- Alternative options considered
- Tradeoffs and risks
- Why you chose this approach

**Template:**
```
Approach: [Your chosen approach]

Alternatives considered:
1. [Alternative 1] - Pros: X, Cons: Y
2. [Alternative 2] - Pros: X, Cons: Y

Chosen because: [Reasoning]

Risks: [What could go wrong]
```

### Step 5: Flag Assumptions

**Purpose:** Surface uncertainties early.

**Examples of assumptions to flag:**
- "Assuming we use JWT tokens (not sessions)"
- "Assuming email service is already configured"
- "Assuming password reset links expire after 1 hour"

### Step 6: Wait for Confirmation

**Purpose:** Don't waste effort on wrong approach.

**What to do:**
- Present your plan
- Ask: "Does this approach sound right?"
- Wait for explicit approval
- Don't start coding until confirmed

**Why this matters:** Prevents rework when assumptions are wrong.
```

---

### Workflows

**Minimal:**
- Step titles only
- Brief 1-liner for each step
- ~15-25 lines

**Verbose:**
- Detailed step descriptions
- Rationale for each step
- Examples and templates
- What to avoid
- ~40-80 lines

**Example:**

#### Minimal - feature-workflow
```markdown
## Steps

### Step 1: Before writing code

- Restate goal
- Read source files
- Identify files to change
- Propose approach
- Flag assumptions
- Wait for confirmation

### Step 2: After confirmation

- Implement following conventions
- Match existing patterns
- Add inline comments
- Add TODO for review
- One file at a time

### Step 3: After implementation

- List follow-up work
- List tests needed
```

#### Verbose - feature-workflow
```markdown
## Steps

### Step 1: Before Writing Code

**Purpose:** Understand requirements and plan approach.

**Actions:**
1. **Restate the goal** in your own words
   - Confirms understanding
   - Surfaces misalignment early

2. **Read relevant source files**
   - Don't assume - always read first
   - Understand existing patterns
   - Note dependencies

3. **Identify all files** to change
   - Source files
   - Tests
   - Docs
   - Config

4. **Propose implementation approach**
   - High-level design
   - Alternatives considered
   - Tradeoffs noted

5. **Flag assumptions**
   - List what you're uncertain about
   - Ask for clarification

6. **Wait for confirmation**
   - Don't proceed until approved
   - Prevents wasted effort

**Output:** Plan document with approach, files, and assumptions

### Step 2: After Confirmation

**Purpose:** Implement using established patterns.

**Actions:**
1. **Follow core conventions** exactly
   - Match existing code style
   - Use same error handling
   - Follow naming patterns

2. **Match patterns** in the same layer
   - Read similar files first
   - Copy patterns, don't invent new ones

3. **Add inline comments** for non-obvious logic
   - Explain WHY, not WHAT
   - Flag magic numbers
   - Note invariants

4. **Add TODO comments** for judgment calls
   - Mark decisions needing review
   - Flag quick fixes to revisit

5. **Implement one file at a time**
   - Complete one file before next
   - Easier to review
   - Reduces merge conflicts

**Output:** Implemented code following conventions

### Step 3: After Implementation

**Purpose:** Document follow-up and testing needs.

**Actions:**
1. **List follow-up work**
   - Tech debt created
   - Missing features
   - Related changes needed

2. **List tests needed**
   - Unit tests required
   - Integration tests
   - Edge cases to cover

**Output:** Follow-up task list and test plan
```

---

## Content Structure

### Skills Structure

```markdown
---
name: skill-name
description: One-line purpose
tools_needed: [tool1, tool2]
---

## Instructions

[MINIMAL: Bullet points only]
[VERBOSE: Step-by-step with explanations, examples, templates]

## Common Mistakes (verbose only)

- ❌ Anti-pattern
- ✅ Correct approach

## Examples (verbose only)

[Code snippets or templates]
```

### Workflow Structure

```markdown
---
name: workflow-name
description: One-line purpose
steps:
  - Step 1
  - Step 2
---

## Steps

### Step 1: [Name]

[MINIMAL: 1-liner]
[VERBOSE: Purpose, Actions, Output, Examples]

### Step 2: [Name]

[MINIMAL: 1-liner]
[VERBOSE: Purpose, Actions, Output, Examples]
```

---

## Priority Order

### Phase 1: Core Skills/Workflows (High Priority) - ✅ COMPLETE
1. ✅ **feature-planning** skill - DONE (19 lines minimal, 130+ lines verbose)
2. ✅ **feature-workflow** workflow - DONE (28 lines minimal, 120+ lines verbose)
3. ✅ **test-aaa-structure** skill - DONE (25 lines minimal, 200+ lines verbose)
4. ✅ **data-model-workflow** workflow - DONE (53 lines minimal, 301 lines verbose)

### Phase 2: Specialized Skills (Medium Priority) - 🔨 NEXT
5. **incremental-implementation** skill
6. **test-coverage-categories** skill
7. **mermaid-erd-creation** skill

### Phase 3: Advanced Workflows (Lower Priority)
8. Remaining workflows as needed
9. **Note:** strategy-workflow and review-workflow have duplicate variants that need cleanup

---

## Implementation Plan

### Step 1: Create Templates
- Create minimal skill template
- Create verbose skill template
- Create minimal workflow template
- Create verbose workflow template

### Step 2: Update Top 4 (High Priority)
- feature-planning skill (minimal + verbose)
- feature-workflow workflow (minimal + verbose)
- test-aaa-structure skill (minimal + verbose)
- data-model-workflow workflow (minimal + verbose)

### Step 3: Validate Output
- Test builders with new content
- Verify minimal is concise (10-25 lines)
- Verify verbose is detailed (40-80 lines)
- Check all 5 tools render correctly

### Step 4: Update Remaining Content
- Update remaining skills
- Update remaining workflows
- Add examples where helpful

---

## Success Criteria

**Minimal variant:**
- ✅ Concise (10-25 lines for skills, 15-30 for workflows)
- ✅ Bullet-point style
- ✅ Core instructions only
- ✅ Assumes experienced reader

**Verbose variant:**
- ✅ Detailed (30-80 lines for skills, 40-100 for workflows)
- ✅ Explanations and examples
- ✅ Common mistakes section
- ✅ Templates where applicable
- ✅ Teaches the "why"

**Both variants:**
- ✅ Same information, different depth
- ✅ Standalone (can use either)
- ✅ Clear and actionable
