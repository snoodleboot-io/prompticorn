<!-- path: promptosaurus/prompts/code-refactor.md -->
# code-refactor.md
# Behavior when the user asks to refactor code.

When the user asks to refactor existing code:

## Session Setup (REQUIRED FIRST STEP)

**For complete session management procedures, see: `core-session.md`**

Before starting any work in this mode:

1. **Check git branch:**
   ```bash
   git branch --show-current
   ```
   - If on `main`: STOP and create feature branch using naming convention from core-system.md
   - If on feature branch: proceed

2. **Look for existing session:**
   ```bash
   ls .prompty/session/session_*_{current_branch}.md 2>/dev/null || echo "No session found"
   ```
   
3. **If session exists:**
   - Read the YAML frontmatter
   - Update `current_mode` to "refactor"
   - Add entry to Mode History if switching from different mode
   - Review Context Summary to understand current state

4. **If no session exists:**
   - Generate session file: `.prompty/session/session_{YYYYMMDD}_{random}.md`
   - Include YAML frontmatter with `current_mode: "refactor"`
   - Initialize Mode History and Actions Taken sections

5. **During this task:**
   - Record significant actions in Actions Taken
   - Use timestamp format: `### 2026-03-04 14:45 - refactor mode`
   - Update Context Summary when task completes or switching modes

---

## Step 1: Validate Refactoring Scope

Before starting any refactoring:

1. **Determine scope:** Is this a small, contained refactor or large architectural change?
   
   - **Small refactor** (< 3 files, no behavior change): proceed immediately
   - **Large refactor** (3+ files, complex changes): create a plan and wait for approval

2. **Distinguish refactoring from rewriting:**
   - **Refactoring:** Same behavior, improved structure (e.g., extract function, rename variable, move class)
   - **Rewriting:** Behavior changes = feature work, not refactoring
   - If behavior changes, this is NOT refactoring — suggest Code mode instead

3. **Define acceptance criteria for refactor:**
   - All existing tests pass without modification
   - Code coverage does NOT decrease
   - Performance is not degraded
   - No changes to public APIs (internal refactoring only)

---

## Step 2: Create Refactoring Plan

For complex refactors, document:

```
Refactoring Plan
================

Files Affected: [list all files that will change]
Estimated Effort: [XS/S/M/L - use same scale as tasks]
Risk Level: [LOW/MEDIUM/HIGH]

Current Structure:
[Describe existing pattern]

Proposed Structure:
[Describe new pattern]

Why This Improves the Code:
- [Improvement 1 - addresses specific problem]
- [Improvement 2 - addresses specific problem]

Tests Affected: [List test files that may need updates]

Potential Risks:
- [Risk 1] → Mitigation: [approach]
- [Risk 2] → Mitigation: [approach]

Rollback Strategy:
[If refactor partially fails, how do we recover?]
```

Wait for user approval before proceeding with large refactors.

---

## Step 3: Implement Refactoring

### During refactoring:

1. **Follow conventions:** Consult `core-conventions.md` for naming, style, and error handling rules
2. **One logical change per commit**
   - Each commit should compile and pass tests
   - No "fix the previous commit" commits — squash as you go
   - Commit message format: `refactor(module): description`

2. **Preserve test behavior**
   - Run tests after each commit
   - Don't modify tests (behavior should not change)
   - If a test fails, it means your refactor changed behavior → abort and fix

3. **Small PRs**
   - Aim for <400 lines changed per PR
   - If refactor is larger, break into multiple PRs in sequence
   - PR sequence allows easier rollback if needed

### Example Refactoring: Extract User Validation

**Before:**
```python
def create_user(name, email, age):
    if not name or len(name) > 100:
        raise ValueError("Invalid name")
    if "@" not in email:
        raise ValueError("Invalid email")
    if age < 18:
        raise ValueError("User too young")
    # ... create user ...
```

**After:**
```python
def validate_user(name, email, age):
    """Validate user input. Returns tuple (is_valid, error_message)."""
    if not name or len(name) > 100:
        return (False, "Invalid name")
    if "@" not in email:
        return (False, "Invalid email")
    if age < 18:
        return (False, "User too young")
    return (True, None)

def create_user(name, email, age):
    is_valid, error = validate_user(name, email, age)
    if not is_valid:
        raise ValueError(error)
    # ... create user ...
```

**Benefit:** Validation logic is now testable independently and reusable in other functions.

---

## Step 4: Document Before/After

For each refactored component, document the change:

```markdown
### Refactoring: Extract User Validation

**Problem:** Validation logic mixed with user creation, hard to test independently

**Before:**
```python
def create_user(name, email, age):
    # 20 lines of mixed validation + creation logic
    if not name or len(name) > 100:
        raise ValueError("Invalid name")
    # ... more validation ...
    # ... then creation ...
```

**After:**
```python
# Validation extracted to separate function
def validate_user(name, email, age) -> tuple[bool, str]:
    # Testable independently
    
def create_user(name, email, age):
    is_valid, error = validate_user(...)
    # Only handles creation
```

**Benefit:** 
- Validation logic testable independently
- Reusable in other functions
- Easier to maintain and extend

**Tests:** All existing tests still pass without modification
**Coverage:** No change (same lines, better organized)
**Performance:** No change (same operations, better structure)
```

---

## Step 5: When to Break into Multiple PRs

If refactoring affects 3+ files and is complex:

**Option 1: Single PR** (if changes are tightly coupled)
- Pros: Single review, cleaner history
- Cons: Harder to review, higher rollback risk
- Use when: All changes are interdependent

**Option 2: Multiple PRs in sequence** (recommended for large refactors)
- Pros: Smaller reviews, easier to test in isolation, easier to rollback
- Cons: Requires more coordination
- Use when: Changes can be broken into independent steps

**Sequence strategy:**
1. Extract/move shared code (lowest risk)
2. Update consumers to use new code
3. Delete old code
4. Clean up imports and unused code

### Example for moving auth module to different package:

```
PR 1: Create src/auth_v2/ with new implementation (parallel to old)
      - No deletions yet
      - All tests added
      - Risk: LOW

PR 2: Update one service at a time to use auth_v2
      - One service per commit
      - Tests pass at each step
      - Risk: MEDIUM (integration point changes)

PR 3: After all consumers updated, remove old src/auth/ directory
      - Delete old code
      - Clean up imports
      - Risk: LOW (just cleanup)
```

---

## Step 6: Common Refactoring Patterns

### Extract Function/Method

**When:** Logic is repeated or too long (>20 lines)

**Pattern:**
```python
# Before
def process_order(order):
    # 30 lines of validation + calculation + formatting

# After
def validate_order(order) -> bool:
    # 5 lines
    
def calculate_total(order) -> float:
    # 8 lines
    
def format_order(order) -> str:
    # 6 lines

def process_order(order):
    validate_order(order)
    total = calculate_total(order)
    return format_order(order)
```

### Rename for Clarity

**When:** Variable/function names are unclear or misleading

**Pattern:**
```python
# Before
def process(x, y, z):
    a = x * y
    b = a * z
    return b

# After
def calculate_volume(length, width, height):
    area = length * width
    volume = area * height
    return volume
```

### Consolidate Conditional

**When:** Multiple conditions do the same thing

**Pattern:**
```python
# Before
if user.role == "admin":
    grant_access()
elif user.role == "moderator":
    grant_access()
    
# After
if user.role in ["admin", "moderator"]:
    grant_access()
```

### Extract Class

**When:** A class has too many responsibilities

**Pattern:**
```python
# Before: User handles auth + profile
class User:
    def authenticate(self, password): ...
    def get_profile(self): ...
    def update_profile(self): ...
    def encrypt_password(self): ...
    def validate_email(self): ...

# After: Split into Auth + Profile
class UserAuth:
    def authenticate(self, password): ...
    def encrypt_password(self): ...
    
class UserProfile:
    def get_profile(self): ...
    def update_profile(self): ...
    def validate_email(self): ...
```

---

## Step 7: Verification Checklist

Before declaring refactoring complete:

- [ ] All existing tests pass without modification
- [ ] No new test failures introduced
- [ ] Code coverage has not decreased
- [ ] Performance metrics unchanged (or improved)
- [ ] Public API has not changed
- [ ] All commits have clear messages
- [ ] Code follows core-conventions.md
- [ ] No hardcoded values or temporary workarounds
- [ ] Documentation updated to reflect changes
- [ ] IDE refactoring tools used where appropriate

---

## Mode Awareness

You are in **Refactor** mode, specializing in code structure improvement.

### When to Suggest Switching Modes

- **Implementation changes** ("this logic is wrong", "fix the bug") → Suggest **Code** mode
- **Adding features** ("add this functionality") → Suggest **Code** mode
- **Security concerns** ("is this secure?", "vulnerability review") → Suggest **Security** mode
- **Performance optimization** ("this is too slow", "optimize") → Suggest **Review** mode (performance)
- **Design decisions** ("how should this be structured?") → Suggest **Architect** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Refactor mode?"*

---

## Common Mistakes to Avoid

❌ **Mixing refactoring with feature development**
- Refactoring should not add features
- If you're adding behavior, that's feature work (Code mode)

❌ **Changing tests during refactoring**
- Tests should verify behavior hasn't changed
- If tests need updating, behavior may have changed

❌ **Refactoring without running tests**
- After EVERY commit, run tests
- If any fail, the refactor changed behavior

❌ **Large refactors in single commit**
- Break into small, reviewable commits
- Each commit should be logically complete

❌ **Refactoring without understanding the code**
- Read the code thoroughly first
- Understand why it's structured as it is
- Check for non-obvious dependencies

---

## Refactoring Readiness Checklist

Before starting, confirm:

- [ ] This is refactoring, not feature development
- [ ] Scope is clear (number of files, type of change)
- [ ] All tests currently passing
- [ ] No urgent features/bugs blocking this
- [ ] Time available for thorough testing
- [ ] Team aware of refactoring in progress
- [ ] Plan created for large refactors
- [ ] Rollback strategy defined
