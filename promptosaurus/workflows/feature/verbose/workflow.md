---
name: "feature"
description: Comprehensive step-by-step feature implementation process
steps:
- Before writing code
- After confirmation  
- After implementation
---

## Steps

### Step 1: Before Writing Code

**Purpose:** Understand requirements and plan approach before coding.

**Actions:**

1. **Restate the goal** in your own words
   - Confirms understanding
   - Surfaces misalignment early
   - Example: "We're adding X feature to solve Y problem"

2. **Read relevant source files**
   - Don't assume - always read first
   - Understand existing patterns
   - Note dependencies and integrations
   - Use `read` and `glob` tools

3. **Identify all files** to change
   - Source files to modify
   - New files to create
   - Tests to add/update
   - Docs to update
   - Config changes

4. **Propose implementation approach**
   - High-level design
   - Alternatives considered with pros/cons
   - Tradeoffs noted
   - Why this approach over alternatives

5. **Flag assumptions** you're making
   - Technology choices
   - API contracts
   - Data formats
   - Integration points

6. **Wait for confirmation**
   - Present your plan clearly
   - Ask: "Does this approach sound right?"
   - Don't proceed until explicitly approved
   - Prevents wasted effort on wrong approach

**Output:** Plan document with approach, file list, and assumptions

---

### Step 2: After Confirmation

**Purpose:** Implement using established patterns and conventions.

**Actions:**

1. **Follow core conventions** exactly
   - Match existing code style
   - Use same error handling patterns
   - Follow naming conventions
   - Check `core-conventions.md` when uncertain

2. **Match patterns** in the same layer
   - Read similar files first
   - Copy established patterns
   - Don't invent new patterns without asking
   - Maintain consistency

3. **Add inline comments** for non-obvious logic
   - Explain WHY, not WHAT
   - Flag magic numbers with explanation
   - Note invariants that must be maintained
   - Document assumptions in code

4. **Add TODO comments** for judgment calls
   - Mark decisions needing review
   - Flag quick fixes to revisit later
   - Note potential improvements
   - Format: `// TODO: [what and why]`

5. **Implement one file at a time**
   - Complete one file before next
   - Easier to review incrementally
   - Reduces merge conflicts
   - Maintains focus

**Output:** Implemented code following all conventions

---

### Step 3: After Implementation

**Purpose:** Document follow-up work and testing needs.

**Actions:**

1. **List follow-up work created**
   - Tech debt introduced
   - Missing features or edge cases
   - Related changes needed elsewhere
   - Performance optimizations deferred

2. **List tests that should be written**
   - Unit tests required
   - Integration tests needed
   - Edge cases to cover
   - Performance tests if applicable

**Output:** Follow-up task list and comprehensive test plan

---

## Complete Flow Summary

**Plan** → **Confirm** → **Implement** → **Follow-up**

This workflow ensures:
- ✅ Alignment before coding
- ✅ Consistent implementation
- ✅ Documented follow-up
- ✅ No surprises
