---
name: "task-breakdown-workflow"
description: "Comprehensive task breakdown with estimation techniques, dependency mapping, and work breakdown structures"
version: "1.0"
languages: ["agile", "project-management"]
subagents: ["architect", "orchestrator", "code"]
---

# Task Breakdown Workflow (Verbose)

## Purpose
Transform high-level features, epics, or requirements into well-defined, independently deliverable tasks. This workflow ensures work is properly scoped, estimated, and sequenced for efficient execution.

## When to Use This Workflow
- Breaking down a feature into implementable tasks
- Planning a sprint or milestone
- Estimating project timeline
- Onboarding new team member to a feature
- Creating development roadmap

## Prerequisites
- Feature requirements or user story
- Understanding of system architecture
- Access to stakeholders for clarification
- Knowledge of team velocity

---

## Steps

### 1. Clarify Requirements

**Goal:** Ensure complete understanding before breaking down work.

#### 1.1 Read Requirements Thoroughly
Understand what is being asked:

**Example requirement:**
```
Feature: User Profile Management

As a user, I want to manage my profile information
so that I can keep my account details up to date.

Includes:
- Edit name, email, phone number
- Upload profile picture
- Change password
- View activity history
```

#### 1.2 Identify Ambiguities
Flag anything unclear or missing:

**Questions to ask:**
```
Ambiguity 1: "Edit email" - Can users change email freely or need verification?
→ Ask: Do we send a verification email to the new address?

Ambiguity 2: "Upload profile picture" - What formats? Size limits?
→ Ask: What file formats (JPEG, PNG, GIF)? Max file size?

Ambiguity 3: "View activity history" - How much history? What actions?
→ Ask: Last 30 days? Last 100 actions? What events count?

Ambiguity 4: No mention of validation
→ Ask: Email format validation? Phone number format?

Ambiguity 5: No mention of permissions
→ Ask: Can users edit other users' profiles? Admin-only fields?
```

#### 1.3 Confirm Scope Boundaries
Define what IS and IS NOT included:

**In Scope:**
- Edit name, email, phone
- Upload profile picture (JPEG, PNG only, max 5MB)
- Change password (requires current password)
- View last 30 days of activity

**Out of Scope:**
- Delete account (separate feature)
- Two-factor authentication (separate feature)
- OAuth profile sync (future enhancement)
- Bulk user management (admin feature)

#### 1.4 Define Success Criteria
What does "done" look like?

**Feature-level acceptance criteria:**
```
- [ ] User can edit name, email, phone and see changes immediately
- [ ] Email change requires verification link
- [ ] Profile picture uploads successfully and displays on profile
- [ ] Password change requires current password for security
- [ ] Activity history shows last 30 days of login, profile edit events
- [ ] All changes logged for audit trail
- [ ] Mobile responsive
- [ ] All UI tests passing
```

---

### 2. Break Work into Tasks

**Goal:** Decompose feature into discrete, independently deliverable tasks.

#### 2.1 Apply Work Breakdown Structure (WBS)
Break feature into layers:

**Level 1: Feature**
```
User Profile Management
```

**Level 2: Components**
```
├── Profile Data Editing
├── Profile Picture Upload
├── Password Change
└── Activity History
```

**Level 3: Tasks**
```
Profile Data Editing:
  ├── Backend: Create update profile endpoint
  ├── Backend: Add email validation
  ├── Backend: Implement email verification flow
  ├── Frontend: Build profile edit form
  └── Frontend: Handle email verification UI

Profile Picture Upload:
  ├── Backend: Create image upload endpoint
  ├── Backend: Implement image validation (format, size)
  ├── Backend: Store image in S3
  ├── Frontend: Build image upload UI
  └── Frontend: Show image preview

Password Change:
  ├── Backend: Create password change endpoint
  ├── Backend: Validate current password
  ├── Backend: Hash and store new password
  └── Frontend: Build password change form

Activity History:
  ├── Backend: Create activity logging system
  ├── Backend: Create activity retrieval endpoint
  └── Frontend: Build activity history view
```

#### 2.2 Ensure Tasks Are Independently Testable
Each task should be verifiable on its own:

**Good task (testable independently):**
```
Task: Create update profile endpoint
Test: Send PUT /api/profile with new name
Expected: 200 response, name updated in database
```

**Bad task (can't test without other tasks):**
```
Task: Implement profile editing
(Too vague - what specifically? Can't test until frontend exists)
```

#### 2.3 Size Tasks Appropriately
Target 0.5-3 days per task:

**Too large (>3 days):**
```
Task: Implement profile management
→ Split into: Edit profile + Upload picture + Change password
```

**Too small (<2 hours):**
```
Task: Add validation to email field
→ Combine with: Create update profile endpoint
```

**Just right (0.5-3 days):**
```
Task: Create image upload endpoint with validation
- 4 hours: S3 integration
- 2 hours: Image validation
- 2 hours: Tests
Total: 1 day
```

#### 2.4 Apply INVEST Criteria
Ensure tasks are well-formed:

**I - Independent:** Can be worked on without waiting for other tasks
**N - Negotiable:** Details can be discussed, not set in stone
**V - Valuable:** Delivers user or technical value
**E - Estimable:** Can be estimated with reasonable accuracy
**S - Small:** Fits within 0.5-3 days
**T - Testable:** Has clear acceptance criteria

**Example:**
```
Task: Create update profile endpoint
✓ Independent: Can implement without frontend
✓ Negotiable: Exact fields can be adjusted
✓ Valuable: Enables profile editing feature
✓ Estimable: Similar to other CRUD endpoints (1 day)
✓ Small: 1 day
✓ Testable: API test can verify behavior
```

---

### 3. Define Each Task

**Goal:** Write clear, actionable task descriptions.

#### 3.1 Task Template
Use consistent structure:

```markdown
## Task: [Verb] [Object] [Context]

**Type:** feat / fix / chore / spike / docs / test
**Size:** XS / S / M / L / XL
**Dependencies:** [List of task IDs]
**Assignee:** [Name or TBD]

### Description
[What needs to be done and why - 2-3 sentences]

### Acceptance Criteria
- [ ] [Specific, testable criterion 1]
- [ ] [Specific, testable criterion 2]
- [ ] [Specific, testable criterion 3]

### Technical Notes
[Any implementation details, edge cases, or constraints]

### Definition of Done
- [ ] Code written and self-reviewed
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed and approved
- [ ] Deployed to staging
```

#### 3.2 Example: Well-Defined Task

```markdown
## Task 1: Create Update Profile Endpoint

**Type:** feat
**Size:** M (1-2 days)
**Dependencies:** None
**Assignee:** Backend Team

### Description
Create a REST API endpoint that allows authenticated users to update 
their profile information (name, email, phone). Email changes require 
verification to prevent account hijacking.

### Acceptance Criteria
- [ ] PUT /api/profile endpoint accepts name, email, phone fields
- [ ] Endpoint requires authentication (JWT token)
- [ ] Users can only update their own profile
- [ ] Email change triggers verification email
- [ ] Email not updated until user clicks verification link
- [ ] Phone number validated for format (E.164)
- [ ] Returns 200 with updated profile on success
- [ ] Returns 400 for validation errors
- [ ] Returns 401 if not authenticated
- [ ] Returns 403 if trying to edit another user's profile
- [ ] All changes logged in audit table

### Technical Notes
- Use existing EmailService for verification emails
- Verification token expires in 24 hours
- Store pending email in separate field until verified
- Phone validation regex: ^\+[1-9]\d{1,14}$

### Definition of Done
- [ ] Code written following core-conventions-python.md
- [ ] Unit tests: 8 test cases (happy path + edge cases)
- [ ] Integration test: End-to-end profile update flow
- [ ] API documentation updated (OpenAPI spec)
- [ ] Code reviewed by senior engineer
- [ ] Deployed to staging and tested manually
```

#### 3.3 Task Sizing Guide

**XS (< 0.5 days, 1-4 hours):**
- Add validation to existing endpoint
- Fix typo in UI
- Update documentation
- Minor refactor

**S (0.5-1 day):**
- Create simple CRUD endpoint
- Build basic UI form
- Add unit tests for module
- Simple bug fix

**M (1-2 days):**
- Create endpoint with complex logic
- Build UI with validation and error handling
- Add integration tests
- Medium complexity bug fix

**L (2-3 days):**
- Create feature with backend + frontend
- Complex refactor across multiple files
- Performance optimization requiring profiling

**XL (>3 days - AVOID):**
- Anything larger should be split into smaller tasks
- If unavoidable, mark as "epic" and break down further

#### 3.4 Task Types

**feat:** New feature or enhancement
```
Example: Add user profile editing
```

**fix:** Bug fix
```
Example: Fix email validation rejecting valid addresses
```

**chore:** Maintenance, refactoring, dependency updates
```
Example: Upgrade FastAPI from 0.95 to 0.100
```

**spike:** Research or proof-of-concept (timeboxed)
```
Example: Investigate Redis vs Memcached for session storage (4 hours)
```

**docs:** Documentation only
```
Example: Write API integration guide
```

**test:** Add missing tests
```
Example: Add integration tests for profile endpoints
```

---

### 4. Identify Architectural Decisions

**Goal:** Flag tasks requiring design choices before implementation.

#### 4.1 Recognize Decision Points
Identify where technical choices must be made:

**Example decision points:**
```
Task: Store profile pictures
Decision needed: Where to store images?
Options: 
  A) S3 (scalable, CDN-ready, costs money)
  B) Database (simple, no external dependency, slow for large files)
  C) Local filesystem (free, not scalable)
Recommendation: S3 (best for production, aligns with NFRs)
```

#### 4.2 Mark Tasks Requiring Approval
Some decisions need stakeholder input:

**Example:**
```
Task: Implement email verification flow
Decision needed: How long should verification links be valid?
Options:
  A) 24 hours (secure but may expire before user checks email)
  B) 7 days (user-friendly but less secure)
  C) 1 hour (very secure but poor UX)
Stakeholder: Product Manager
Recommendation: 24 hours (industry standard)
```

#### 4.3 Identify High-Risk Tasks
Flag tasks with uncertainty or technical risk:

**Risk indicators:**
- First time using a technology
- Integration with external system (unknown behavior)
- Performance-critical code
- Security-sensitive operations
- Complex algorithm

**Example:**
```
Task: Integrate with Okta SSO
Risk: High (never used Okta API before)
Mitigation: Create 4-hour spike task to prototype integration first
```

#### 4.4 Create Spike Tasks for Unknowns
When outcome is uncertain, create timeboxed research task:

**Spike task template:**
```markdown
## Spike: Investigate Image Storage Options

**Type:** spike
**Timebox:** 4 hours
**Assignee:** Backend Lead

### Goal
Determine best approach for storing user profile pictures (S3, database, or filesystem).

### Questions to Answer
- What is cost of S3 for 10K users?
- What is performance difference vs database storage?
- How complex is S3 integration?
- What are security considerations for each approach?

### Deliverable
- 1-page doc comparing options with recommendation
- Prototype code showing S3 upload (if recommended)

### Success Criteria
- [ ] All questions answered with data
- [ ] Clear recommendation with rationale
- [ ] Team has enough info to make decision
```

---

### 5. Sequence Tasks

**Goal:** Order tasks by dependencies and identify parallelization opportunities.

#### 5.1 Identify Dependencies
Map what must happen before what:

**Dependency types:**

**Hard dependency (blocking):**
```
Task A: Create database schema
Task B: Create API endpoint using that schema
→ B depends on A (can't start B until A is done)
```

**Soft dependency (preferred order):**
```
Task A: Create API endpoint
Task B: Build UI consuming that endpoint
→ B prefers A done, but can be mocked
```

**No dependency (parallel):**
```
Task A: Create update profile endpoint
Task B: Create upload image endpoint
→ Can work in parallel
```

#### 5.2 Create Dependency Graph

**Example:**
```
Profile Editing Feature:

Start
  ├─> Task 1: Database schema (1 day)
  │       ├─> Task 2: Update profile endpoint (1 day)
  │       │       ├─> Task 5: Profile edit UI (1 day)
  │       │       └─> Task 6: Email verification UI (0.5 day)
  │       └─> Task 3: Upload image endpoint (1 day)
  │               └─> Task 7: Image upload UI (1 day)
  └─> Task 4: Activity logging system (1 day)
          └─> Task 8: Activity history UI (0.5 day)

Critical path: 1 → 2 → 5 (3 days)
```

#### 5.3 Suggest Delivery Sequence
Order tasks for logical progression:

**Sequence 1: By dependency (recommended)**
```
Week 1:
  Day 1: Task 1 (schema)
  Day 2-3: Task 2 (update endpoint) + Task 4 (activity logging) [parallel]
  Day 4: Task 3 (upload endpoint)

Week 2:
  Day 1-2: Task 5 (edit UI) + Task 7 (upload UI) [parallel]
  Day 3: Task 6 (verification UI) + Task 8 (activity UI) [parallel]
```

**Sequence 2: By value (MVP first)**
```
MVP (minimum viable):
  Task 1 → Task 2 → Task 5 (basic profile editing)

Enhancements:
  Task 3 → Task 7 (image upload)
  Task 4 → Task 8 (activity history)
  Task 6 (email verification)
```

#### 5.4 Identify Parallelization Opportunities
Find tasks that can run concurrently:

**Parallelizable:**
```
Backend developer 1: Task 2 (update endpoint)
Backend developer 2: Task 4 (activity logging)
Frontend developer: Task 5 (edit UI, can mock API)
```

**Cannot parallelize (blocking):**
```
Task 1 (schema) must finish before Task 2, 3, 4 start
```

---

### 6. Output Structured Task List

**Goal:** Present tasks in clear, actionable format.

#### 6.1 Task List Format

**Option A: Numbered List**
```markdown
## Profile Management Feature - Task Breakdown

**Total estimated effort:** 8 days
**Critical path:** 3 days (with 2 developers)

### Tasks

1. **[M] Create user profile database schema**
   - Type: feat
   - Size: M (1 day)
   - Dependencies: None
   - Acceptance Criteria:
     - [ ] users table has name, email, phone fields
     - [ ] email_verifications table created
     - [ ] activity_log table created
     - [ ] Migration file created

2. **[M] Create update profile endpoint**
   - Type: feat
   - Size: M (1 day)
   - Dependencies: Task 1
   - Acceptance Criteria:
     - [ ] PUT /api/profile endpoint accepts name, email, phone
     - [ ] Email change triggers verification
     - [ ] All changes logged
     - [ ] 8 unit tests passing

[... continue for all tasks ...]
```

**Option B: Table Format**
```markdown
| ID | Task | Type | Size | Dependencies | Owner | Status |
|----|------|------|------|--------------|-------|--------|
| 1 | Create database schema | feat | M | - | Backend | Todo |
| 2 | Update profile endpoint | feat | M | 1 | Backend | Todo |
| 3 | Upload image endpoint | feat | M | 1 | Backend | Todo |
| 4 | Activity logging system | feat | M | 1 | Backend | Todo |
| 5 | Profile edit UI | feat | M | 2 | Frontend | Todo |
| 6 | Email verification UI | feat | S | 2 | Frontend | Todo |
| 7 | Image upload UI | feat | M | 3 | Frontend | Todo |
| 8 | Activity history UI | feat | S | 4 | Frontend | Todo |
```

#### 6.2 Highlight Critical Path
Show which tasks block others:

```markdown
## Critical Path (blocks entire feature):
Task 1 (schema) → Task 2 (update endpoint) → Task 5 (edit UI)
Estimated: 3 days

## Can be done in parallel (after Task 1):
- Task 3 (upload endpoint) + Task 4 (activity logging)
- Task 7 (upload UI) + Task 8 (activity UI)
```

#### 6.3 Note Assumptions and Unknowns

```markdown
## Assumptions
- Email verification uses existing EmailService
- S3 bucket for images already exists
- Users can only edit their own profile (not admin editing)
- Profile picture max size 5MB

## Unknowns / Open Questions
- [DECISION NEEDED] Email verification link expiry time? (Recommend: 24 hours)
- [DECISION NEEDED] What happens to old profile pictures when new one uploaded? (Recommend: delete old)
- [RISK] Okta SSO integration complexity unknown (spike task created)
```

#### 6.4 Summary Statistics

```markdown
## Summary

**Total tasks:** 8
**Total effort:** 8 developer-days
**Timeline (with 2 devs):** 4 calendar days
**Risks:** 1 (Okta integration)
**Decisions needed:** 2 (verification expiry, old image handling)

**Breakdown by type:**
- feat: 7 tasks
- spike: 1 task

**Breakdown by size:**
- S: 2 tasks
- M: 6 tasks
- L: 0 tasks

**Breakdown by owner:**
- Backend: 4 tasks (4 days)
- Frontend: 4 tasks (3 days)
```

---

## Task Breakdown Techniques

### Technique 1: User Story Splitting
Split large user stories into smaller ones:

**Large story:**
```
As a user, I want to manage my profile
```

**Split into:**
```
1. As a user, I want to edit my name and email
2. As a user, I want to upload a profile picture
3. As a user, I want to change my password
4. As a user, I want to view my activity history
```

### Technique 2: Layer Splitting
Split by architectural layer:

**Feature: Profile editing**
```
Database layer: Create schema
API layer: Create endpoint
Business logic: Validate inputs
Frontend: Build UI
```

### Technique 3: Component Splitting
Split by component or module:

**Feature: E-commerce checkout**
```
Cart component
Shipping component
Payment component
Order confirmation component
```

### Technique 4: Complexity Splitting
Split complex tasks into simpler ones:

**Complex task:**
```
Implement payment processing (XL - 5 days)
```

**Split into:**
```
1. Integrate Stripe SDK (M - 1 day)
2. Create payment processing endpoint (M - 1 day)
3. Add error handling and retries (S - 0.5 day)
4. Build payment form UI (M - 1 day)
5. Add payment success/failure flows (S - 0.5 day)
6. Write integration tests (M - 1 day)
Total: 5 days (same effort, but better tracking)
```

---

## Estimation Techniques

### Planning Poker
Team estimates tasks together using Fibonacci sequence (1, 2, 3, 5, 8, 13):

**Process:**
1. Product owner describes task
2. Each developer picks estimate (in secret)
3. All reveal simultaneously
4. Discuss high and low estimates
5. Re-vote until consensus

### T-Shirt Sizing
Estimate relative size instead of hours:

- **XS:** Trivial change
- **S:** Simple task
- **M:** Moderate complexity
- **L:** Complex task
- **XL:** Very complex (should be split)

### Reference Class Forecasting
Compare to similar past tasks:

```
Task: Create user registration endpoint
Reference: We built login endpoint last sprint (took 1 day)
Estimate: Registration is similar complexity → 1 day
```

### Three-Point Estimation
Estimate best, worst, and likely cases:

```
Task: Integrate third-party API
Best case: 4 hours (API works perfectly)
Likely case: 1 day (some API quirks)
Worst case: 2 days (API has issues, need workarounds)

Formula: (Best + 4×Likely + Worst) / 6
Estimate: (4 + 4×8 + 16) / 6 = 8.7 hours ≈ 1 day
```

---

## Complete Example: Breaking Down "User Authentication"

**Feature:** User Authentication

**Clarified requirements:**
- Email/password registration
- Email verification required before login
- Secure password hashing (bcrypt)
- JWT tokens for session management
- Password reset via email
- Rate limiting on login attempts

**Task breakdown:**

```markdown
## User Authentication - Task Breakdown

### Phase 1: Core Authentication (Days 1-3)

1. **[M] Create user database schema**
   - users table (id, email, password_hash, verified, created_at)
   - verification_tokens table
   - password_reset_tokens table
   - Migration: 0.5 days
   - Size: M (0.5 days)

2. **[M] Implement password hashing utilities**
   - Bcrypt hashing function
   - Password validation function
   - 8 unit tests
   - Size: S (0.5 days)
   - Depends: None

3. **[M] Create registration endpoint**
   - POST /api/auth/register
   - Validate email format
   - Hash password
   - Send verification email
   - Size: M (1 day)
   - Depends: 1, 2

4. **[M] Create email verification endpoint**
   - GET /api/auth/verify/:token
   - Mark user as verified
   - Return success page
   - Size: S (0.5 days)
   - Depends: 1, 3

5. **[M] Create login endpoint**
   - POST /api/auth/login
   - Verify email + password
   - Check user verified
   - Return JWT token
   - Size: M (1 day)
   - Depends: 1, 2

### Phase 2: Password Reset (Days 4-5)

6. **[M] Create password reset request endpoint**
   - POST /api/auth/reset-password
   - Generate reset token
   - Send reset email
   - Size: M (0.5 days)
   - Depends: 1

7. **[M] Create password reset confirmation endpoint**
   - POST /api/auth/reset-password/confirm
   - Validate reset token
   - Update password
   - Size: M (0.5 days)
   - Depends: 1, 2, 6

### Phase 3: Security (Day 6)

8. **[S] Add rate limiting**
   - Max 5 login attempts per minute per IP
   - Use Redis for counter
   - Return 429 when exceeded
   - Size: S (0.5 days)
   - Depends: 5

9. **[M] Add security logging**
   - Log all auth attempts
   - Log failed logins
   - Log password changes
   - Size: S (0.5 days)
   - Depends: None

### Phase 4: Testing (Day 7)

10. **[M] Write integration tests**
    - Complete registration flow
    - Login flow
    - Password reset flow
    - Rate limiting behavior
    - Size: M (1 day)
    - Depends: All above

**Total: 7 days (1 developer) or 4 days (2 developers in parallel)**

**Critical path:** 1 → 3 → 4 → 5 (3 days)
```

**Assumptions:**
- Email service already exists
- JWT library already in use
- Redis available for rate limiting

**Risks:**
- Email deliverability (may go to spam) - mitigate with SPF/DKIM setup

**Decisions needed:**
- JWT expiration time? (Recommend: 24 hours)
- Verification email expiry? (Recommend: 24 hours)
- Password complexity requirements? (Recommend: 12 chars min)
