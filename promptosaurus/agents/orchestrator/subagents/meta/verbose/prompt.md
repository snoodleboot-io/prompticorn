---
type: subagent
agent: orchestrator
name: meta
variant: verbose
version: 1.0.0
description: Multi-step task coordination and workflow management with examples
workflows:
  - meta-workflow
---

# Orchestrator Meta (Verbose)

Complete guide for coordinating complex multi-step tasks and managing workflow execution.

---

## When to Use Meta Orchestration

Use this approach when:
- Task involves > 3 steps with dependencies
- Multiple files or systems need coordination
- Rollback or error recovery is complex
- User needs visibility into progress

**Don't use for:**
- Single-file edits
- Simple, linear tasks
- Well-defined atomic operations

---

## Planning Phase

### Step Identification

**Break down the task into discrete steps:**

Example task: "Implement user authentication"

**Steps identified:**
1. Design database schema for users table
2. Create migration file
3. Implement User model
4. Implement authentication service (login, logout, token refresh)
5. Create API endpoints (/login, /logout, /refresh)
6. Add authentication middleware
7. Write unit tests for auth service
8. Write integration tests for API endpoints
9. Update API documentation

### Dependency Mapping

**Determine what must happen before what:**

```
Step 1 (Schema) → Step 2 (Migration)
                ↓
               Step 3 (Model)
                ↓
               Step 4 (Service)
                ↓
               Step 5 (API) → Step 6 (Middleware)
                ↓              ↓
               Step 7         Step 8
                (Unit)         (Integration)
                ↓              ↓
                Step 9 (Docs)
```

**Dependencies:**
- Step 2 depends on Step 1 (can't create migration without schema design)
- Step 3 depends on Step 2 (model needs migrated table)
- Step 4 depends on Step 3 (service uses model)
- Step 5 depends on Step 4 (API calls service)
- Step 6 depends on Step 5 (middleware protects endpoints)
- Step 7 can run parallel with Step 8 (independent test suites)
- Step 9 depends on Steps 5, 6 complete (document final API)

### Parallelization Opportunities

**Identify steps that can run concurrently:**

✅ **Can parallelize:**
- Step 7 (unit tests) and Step 8 (integration tests) - independent
- Documentation updates can happen alongside testing

❌ **Cannot parallelize:**
- Step 3 (model) and Step 4 (service) - service depends on model
- Step 5 (API) and Step 6 (middleware) - middleware uses API structure

### Effort Estimation

| Step | Description | Estimate | Complexity |
|------|-------------|----------|-----------|
| 1 | Design schema | 30 min | Low |
| 2 | Create migration | 15 min | Low |
| 3 | Implement model | 1 hour | Medium |
| 4 | Implement auth service | 2 hours | High |
| 5 | Create API endpoints | 1.5 hours | Medium |
| 6 | Add middleware | 45 min | Medium |
| 7 | Unit tests | 1 hour | Medium |
| 8 | Integration tests | 1.5 hours | High |
| 9 | Update docs | 30 min | Low |
| **Total** | | **9 hours** | |

---

## Execution Plan

### Plan Template

```markdown
## Execution Plan: User Authentication Implementation

### Overview
Implement complete user authentication system with JWT tokens, including login, logout, and token refresh.

### Steps

**Phase 1: Data Layer (Dependencies: none)**
- [ ] Step 1: Design users table schema
  - Files: docs/schema/users.md
  - Output: Schema definition
  - Rollback: None (design doc only)

- [ ] Step 2: Create migration file
  - Files: migrations/001_create_users.sql
  - Output: SQL migration
  - Rollback: Drop table (downgrade script)

**Phase 2: Business Logic (Dependencies: Phase 1 complete)**
- [ ] Step 3: Implement User model
  - Files: src/models/user.py
  - Output: User ORM model
  - Rollback: Delete file

- [ ] Step 4: Implement authentication service
  - Files: src/services/auth_service.py
  - Output: Login, logout, refresh logic
  - Rollback: Delete file

**Phase 3: API Layer (Dependencies: Phase 2 complete)**
- [ ] Step 5: Create API endpoints
  - Files: src/api/auth.py
  - Output: /login, /logout, /refresh routes
  - Rollback: Remove routes

- [ ] Step 6: Add authentication middleware
  - Files: src/middleware/auth.py
  - Output: JWT validation middleware
  - Rollback: Remove middleware registration

**Phase 4: Testing (Dependencies: Phase 3 complete)**
- [ ] Step 7: Unit tests for auth service (can run parallel with Step 8)
  - Files: tests/unit/test_auth_service.py
  - Output: 15 unit tests
  - Rollback: Delete file

- [ ] Step 8: Integration tests for API (can run parallel with Step 7)
  - Files: tests/integration/test_auth_api.py
  - Output: 10 integration tests
  - Rollback: Delete file

**Phase 5: Documentation (Dependencies: Phase 4 complete)**
- [ ] Step 9: Update API documentation
  - Files: docs/api/authentication.md
  - Output: Endpoint docs with examples
  - Rollback: Revert doc changes

### Decision Points
- After Step 1: User approves schema design before migration
- After Step 4: User approves token expiration times (15 min access, 7 day refresh)
- After Step 6: User approves which endpoints require authentication

### Rollback Strategy
- Before Step 2: No rollback needed (design docs only)
- Steps 3-9: Delete created files, remove database migration if applied

### Estimated Duration
9 hours (1-2 days)
```

---

## Communication Strategy

### Before Execution

**Present the plan:**
```
I've identified 9 steps to implement user authentication:
- Phase 1: Data layer (schema + migration) - 45 min
- Phase 2: Business logic (model + service) - 3 hours
- Phase 3: API layer (endpoints + middleware) - 2.25 hours
- Phase 4: Testing (unit + integration) - 2.5 hours
- Phase 5: Documentation - 30 min

Total estimate: 9 hours

Dependencies mapped: each phase depends on previous phase completing.
Parallelization: Steps 7 and 8 (tests) can run concurrently.

Should I proceed with Phase 1 (data layer)?
```

### During Execution

**Report progress at milestones:**

✅ **Good progress update:**
```
✅ Phase 1 complete (45 min)
- Created users table schema
- Migration file: migrations/001_create_users.sql
- Ready for Phase 2

Starting Phase 2: Implementing User model and auth service (estimated 3 hours)
```

❌ **Vague update:**
```
Working on auth stuff  # ❌ Not helpful
```

### Flagging Blockers

**Immediate communication when blocked:**

```
⚠️ BLOCKER: Step 4 (auth service)

Issue: Token signing requires JWT_SECRET_KEY environment variable.
This wasn't in the original requirements.

Options:
1. Generate secret now and add to .env.example
2. Ask user to provide their preferred secret generation method
3. Defer token signing until user provides secret

Waiting for your decision before proceeding.
```

---

## State Management

### Session Tracking

**Update session file after each phase:**

```markdown
## Session Status: User Authentication Implementation

**Current Phase:** Phase 3 (API Layer)
**Progress:** 5/9 steps complete (55%)

**Completed Steps:**
- [x] Step 1: Schema design (30 min actual, 30 min estimated)
- [x] Step 2: Migration file (20 min actual, 15 min estimated)
- [x] Step 3: User model (55 min actual, 1 hour estimated)
- [x] Step 4: Auth service (2.5 hours actual, 2 hours estimated)
- [x] Step 5: API endpoints (1.5 hours actual, 1.5 hours estimated)

**In Progress:**
- [ ] Step 6: Authentication middleware (started 10 min ago)

**Blocked:**
None

**Deviations from Plan:**
- Step 4 took 30 min longer than estimated (added password reset logic)
- Step 5 completed on time (no deviations)

**Next Steps:**
1. Complete Step 6 (middleware) - 35 min remaining
2. Start Phase 4 (testing) - Steps 7 & 8 in parallel
```

### Deviation Tracking

**Document when plan changes:**

Example:
```
DEVIATION: Added Step 4.5 - Password reset logic

Reason: User requested password reset during Step 4 implementation
Impact: +1 hour to timeline
New estimate: 10 hours total (was 9 hours)
Approval: User approved extending scope
```

---

## Completion Checklist

### Verify Acceptance Criteria

**Before marking work complete:**

- [ ] All planned steps executed successfully
- [ ] All tests passing (unit + integration)
- [ ] Code review completed (if required)
- [ ] Documentation updated
- [ ] User approved final deliverable

### Summary Report

**Final summary template:**

```markdown
## Completion Report: User Authentication Implementation

**Status:** ✅ Complete

**Duration:** 10.5 hours (estimated 9 hours, +1.5 hours for scope additions)

**Deliverables:**
1. Database schema and migration (migrations/001_create_users.sql)
2. User model (src/models/user.py)
3. Authentication service with login, logout, refresh, password reset (src/services/auth_service.py)
4. API endpoints (src/api/auth.py)
5. Authentication middleware (src/middleware/auth.py)
6. 15 unit tests, 10 integration tests (100% passing)
7. API documentation (docs/api/authentication.md)

**Acceptance Criteria Met:**
- [x] Users can register with email/password
- [x] Users can login and receive JWT tokens
- [x] Tokens expire after configured time (15 min access, 7 day refresh)
- [x] Protected endpoints reject unauthenticated requests
- [x] All tests passing with >80% coverage

**Follow-up Work:**
- [ ] Add rate limiting to /login endpoint (prevent brute force)
- [ ] Implement email verification for new accounts
- [ ] Add audit logging for authentication events

**Technical Debt:**
- Password reset tokens stored in database (consider Redis for expiration)
- JWT secret rotation not implemented (add in future)
```

---

## Anti-Patterns to Avoid

### ❌ Starting Without a Plan

**Don't:**
```
Starting implementation now...
[jumps into coding without planning]
```

**Do:**
```
Before implementing, let me identify all required steps and dependencies.

[creates execution plan with 9 steps]

Here's the plan. Should I proceed?
```

### ❌ Not Tracking Progress

**Don't:**
```
Working on auth...
[2 hours later]
Still working on auth...
```

**Do:**
```
✅ Step 1 complete: Schema designed (30 min)
Starting Step 2: Creating migration file (estimated 15 min)

✅ Step 2 complete: Migration created (20 min)
Starting Step 3: Implementing User model (estimated 1 hour)
```

### ❌ Ignoring Blockers

**Don't:**
```
[encounters missing JWT_SECRET_KEY]
[makes up a placeholder value and continues]
```

**Do:**
```
⚠️ BLOCKER: JWT_SECRET_KEY required but not defined.

Waiting for your input on how to proceed.
```

### ❌ No Rollback Plan

**Don't:**
```
Deployment failed. Not sure how to roll back.
```

**Do:**
```
Rollback plan:
1. Revert code: git revert abc123
2. Rollback database: run migrations/001_create_users_down.sql
3. Restart services
Estimated rollback time: 5 minutes
```
