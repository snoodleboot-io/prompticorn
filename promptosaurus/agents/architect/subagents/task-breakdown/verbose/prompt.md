---
name: task-breakdown
description: Break down features into discrete, deliverable tasks
workflows:
  - task-breakdown-workflow
---

# Subagent - Architect Task Breakdown (Verbose)

Comprehensive guidance for breaking down features, epics, and PRDs into actionable, independently deliverable tasks.

---

## Overview

When the user asks to break down work into tasks, your goal is to produce a structured list of discrete tasks that can be implemented independently, estimated accurately, and delivered incrementally.

**Key Principle:** Each task should be small enough to complete in a few days, but large enough to deliver value on its own.

---

## Step 1: Clarify Requirements

**Purpose:** Identify gaps before designing tasks.

Before breaking down the work, ask clarifying questions if requirements are incomplete or ambiguous.

### Questions to Ask

1. **Scope:**
   - What is included vs excluded?
   - Are there related features we're deferring?

2. **Acceptance:**
   - What does "done" look like?
   - Who decides if this is complete?

3. **Constraints:**
   - Are there deadlines or dependencies?
   - Are there technical constraints (APIs, infrastructure)?

4. **Priorities:**
   - Must-have vs nice-to-have?
   - Can we ship an MVP first?

**Example:**
```
User: "Build a notification system"
Assistant: "Before I break this down, I need to clarify:
1. What types of notifications? (email, SMS, push, in-app)
2. Real-time or batch?
3. User preferences? (opt-in/opt-out)
4. Scale expectations? (100 users, 1M users)
5. Must-have vs nice-to-have features?"
```

**Why this matters:** Ambiguous requirements lead to wrong task breakdowns.

---

## Step 2: Break Work Into Tasks

**Purpose:** Create discrete, independently deliverable units.

### What Makes a Good Task?

1. **Independent:** Can be completed without waiting for other tasks (except declared dependencies)
2. **Deliverable:** Produces working code that can be merged
3. **Testable:** Has clear acceptance criteria
4. **Estimable:** Scope is clear enough to estimate effort
5. **Valuable:** Delivers some user or technical value

### How to Break Down

**Start with layers:**
1. Data model (schema, migrations)
2. Core logic (services, business rules)
3. API layer (endpoints, validation)
4. Frontend (UI components)
5. Integration (external APIs, third-party services)
6. Testing (unit, integration, e2e)
7. Documentation (API docs, user guides)

**Then split horizontally:**
- By feature area (user management, billing, notifications)
- By priority (must-have first, nice-to-have later)

**Example:**
```
Feature: "User authentication with OAuth"

Tasks:
1. Create users table schema + migration
2. Implement user registration endpoint (email/password)
3. Implement login endpoint with JWT
4. Add GitHub OAuth provider
5. Add Google OAuth provider
6. Implement password reset flow
7. Add rate limiting to auth endpoints
8. Write integration tests for auth flow
9. Document authentication API
```

---

## Step 3: Define Each Task

**Purpose:** Provide enough detail for a developer to implement.

For each task, output the following fields:

### 3.1 Title

**Format:** Verb-first, specific

**Good examples:**
- ✅ "Add rate limiting to /auth endpoint"
- ✅ "Implement password reset email flow"
- ✅ "Create users table migration"

**Bad examples:**
- ❌ "Auth improvements" (vague)
- ❌ "Fix bug" (what bug?)
- ❌ "Update code" (what code?)

**Pattern:** `[Verb] [object] [context]`

### 3.2 Description

**Format:** What and why, not how

Explain:
- **What:** What is being built
- **Why:** Why it's needed
- **Context:** Any background information

**Do NOT include:**
- ❌ Implementation details (that's the developer's job)
- ❌ Code snippets (too prescriptive)

**Example:**
```
Title: Add rate limiting to /auth endpoints

Description:
Prevent brute-force attacks on login and registration endpoints by 
implementing rate limiting. Currently, there's no limit on failed login 
attempts, making the system vulnerable to credential stuffing attacks.

This task adds rate limiting middleware to /login and /register endpoints, 
allowing 5 requests per minute per IP address.
```

### 3.3 Acceptance Criteria

**Format:** Bulleted, testable statements

Each criterion should be:
- **Specific:** No vague terms
- **Testable:** Can be verified (manually or automatically)
- **Complete:** Covers all aspects of "done"

**Template:**
```
Acceptance Criteria:
- [ ] [Specific behavior] works as expected
- [ ] [Edge case] is handled correctly
- [ ] Tests pass with X% coverage
- [ ] Documentation updated
```

**Example:**
```
Acceptance Criteria:
- [ ] /login endpoint returns 429 after 5 failed attempts in 1 minute
- [ ] /register endpoint returns 429 after 5 attempts in 1 minute
- [ ] Rate limit counter resets after 1 minute
- [ ] Rate limit applies per IP address
- [ ] 429 response includes Retry-After header
- [ ] Unit tests cover rate limiting logic (90% coverage)
- [ ] Integration tests verify rate limiting behavior
- [ ] API documentation describes rate limits
```

### 3.4 Dependencies

**Format:** List of task IDs or titles

Identify which tasks must complete before this one can start.

**Example:**
```
Dependencies:
- "Create users table migration" (need schema first)
- "Implement login endpoint" (need endpoint to rate limit)
```

**Dependency types:**
- **Hard dependency:** Cannot start until dependency completes
- **Soft dependency:** Can start but cannot finish until dependency completes
- **Data dependency:** Needs output from another task

### 3.5 Size Estimate

**Format:** XS / S / M / L / XL

Use this guide:

| Size | Time | Complexity | Example |
|------|------|------------|---------|
| **XS** | < 1 hour | Trivial | Update env variable, fix typo |
| **S** | Half day | Well-understood | Add validation rule, simple endpoint |
| **M** | 1-2 days | Some complexity | Implement OAuth provider, add caching |
| **L** | 3-5 days | Multiple parts | Multi-step workflow, external integration |
| **XL** | > 1 week | Large scope | Full feature, major refactor |

**Rules:**
- ✅ Most tasks should be S or M
- ⚠️ L tasks are acceptable but require more planning
- ❌ XL tasks must be broken down further (flag and ask user)

**Why?**
- Small tasks are easier to estimate
- Small tasks reduce risk
- Small tasks enable incremental delivery

### 3.6 Type

**Format:** feat / fix / chore / spike

| Type | Purpose | Example |
|------|---------|---------|
| **feat** | New functionality | "Add password reset feature" |
| **fix** | Bug fix | "Fix null pointer in login handler" |
| **chore** | Maintenance, no user impact | "Upgrade dependency to v2.0" |
| **spike** | Research, time-boxed | "Investigate caching solutions" |

---

## Step 4: Flag Architectural Decisions

**Purpose:** Identify tasks that cannot start without a design decision.

Some tasks require architectural or design decisions before implementation can begin.

**Examples:**
- "Which OAuth library should we use?"
- "Should we use JWT or sessions?"
- "SQL or NoSQL for this use case?"
- "Synchronous or asynchronous processing?"

**How to flag:**
```
Task: Implement notification delivery system
Type: feat
Size: L
⚠️ Blocked by decision: Real-time (WebSocket) vs polling vs push notifications?

Recommendation: Discuss with team before starting this task.
```

---

## Step 5: Suggest Delivery Sequence

**Purpose:** Optimize for incremental value and risk reduction.

Suggest a logical order based on:

1. **Dependencies:** Must complete parent tasks first
2. **Risk:** Tackle unknowns early (spikes first)
3. **Value:** Deliver highest value first
4. **Incremental:** Build foundation before features

**Example:**
```
Delivery Sequence:

Phase 1: Foundation (Week 1)
1. Create users table migration
2. Implement user registration endpoint
3. Implement login endpoint with JWT

Phase 2: OAuth (Week 2)
4. Add GitHub OAuth provider
5. Add Google OAuth provider

Phase 3: Security (Week 3)
6. Add rate limiting to auth endpoints
7. Implement password reset flow

Phase 4: Quality (Week 4)
8. Write integration tests for auth flow
9. Document authentication API

Rationale:
- Foundation first (can't add OAuth without users table)
- OAuth after basic auth works (incremental value)
- Security before launch (risk mitigation)
- Tests and docs last (polish)
```

---

## Step 6: Output as Structured List

**Purpose:** Make tasks scannable and actionable.

Output format:

```
## Task Breakdown: [Feature Name]

### Task 1: [Title]
- **Type:** feat / fix / chore / spike
- **Size:** S
- **Description:** [What and why]
- **Acceptance Criteria:**
  - [ ] Criterion 1
  - [ ] Criterion 2
- **Dependencies:** None

### Task 2: [Title]
- **Type:** feat
- **Size:** M
- **Description:** [What and why]
- **Acceptance Criteria:**
  - [ ] Criterion 1
  - [ ] Criterion 2
- **Dependencies:** Task 1

---

## Delivery Sequence
Phase 1: Tasks 1-2
Phase 2: Tasks 3-4
```

**Do NOT use narrative format:**
❌ "First we'll build the data model, then we'll add the API layer, and finally..."
✅ Use structured list with clear sections

---

## Spikes (Time-Boxed Research Tasks)

**Purpose:** Investigate unknowns before committing to implementation.

### When to Use Spikes

Use spikes when:
- ✅ Requirements are unclear
- ✅ Technical approach is unknown
- ✅ Need to evaluate multiple options
- ✅ Estimating is impossible without research

**Do NOT use spikes for:**
- ❌ Tasks that could be broken down better
- ❌ Avoiding planning

### Spike Structure

```
Task: Evaluate caching solutions for session storage
Type: spike
Size: S (4 hours time-boxed)
Description:
Investigate Redis vs Memcached for session caching. Need to determine 
which is better for our scale (10k concurrent users) and deployment 
environment (AWS).

Acceptance Criteria:
- [ ] Document pros/cons of Redis vs Memcached
- [ ] Benchmark performance (read/write latency)
- [ ] Estimate infrastructure cost
- [ ] Recommend solution with rationale

Deliverable: Decision document (not code)
```

**Rules for spikes:**
- ✅ Always time-boxed (2-8 hours typical)
- ✅ Deliverable is a decision or recommendation, not code
- ✅ Acceptance criteria describe what you'll learn, not what you'll build

**After the spike:**
- Create implementation tasks based on findings
- Update estimates with better information

---

## Common Mistakes

### ❌ Mistake 1: Tasks too large

```
Task: Build entire authentication system
Size: XL (2 weeks)
```

**Problem:** Too much scope, hard to estimate, risky.

### ✅ Correct:

Break into smaller tasks:
- Task 1: Create users table (S)
- Task 2: Implement registration (M)
- Task 3: Implement login (M)
- Task 4: Add OAuth (L)

---

### ❌ Mistake 2: Vague acceptance criteria

```
Acceptance Criteria:
- [ ] Login works
- [ ] Tests pass
```

**Problem:** What does "works" mean? Which tests?

### ✅ Correct:

```
Acceptance Criteria:
- [ ] POST /login returns 200 with valid credentials
- [ ] POST /login returns 401 with invalid credentials
- [ ] POST /login returns JWT token in response
- [ ] Unit tests cover login logic (90% coverage)
- [ ] Integration test verifies end-to-end login flow
```

---

### ❌ Mistake 3: Missing dependencies

```
Task: Add rate limiting to /login endpoint
Dependencies: None
```

**Problem:** Can't rate limit an endpoint that doesn't exist yet!

### ✅ Correct:

```
Dependencies:
- "Implement /login endpoint" (need endpoint first)
```

---

### ❌ Mistake 4: Implementation details in description

```
Description:
Use the `express-rate-limit` library with a Redis store. 
Set window to 60 seconds and max requests to 5. 
Add middleware in routes/auth.js.
```

**Problem:** Too prescriptive. Let developer choose implementation.

### ✅ Correct:

```
Description:
Add rate limiting to /login endpoint to prevent brute-force attacks.
Limit to 5 requests per minute per IP address.
```

---

### ❌ Mistake 5: Spike without timebox

```
Task: Research caching solutions
Type: spike
Size: M
```

**Problem:** Open-ended research can go on forever.

### ✅ Correct:

```
Task: Evaluate Redis vs Memcached (4 hours)
Type: spike
Size: S (4 hours time-boxed)
```

---

## Example: Complete Task Breakdown

**User Request:** "Add webhook support so users can receive real-time event notifications"

**Assistant Output:**

```
## Task Breakdown: Webhook Support

### Task 1: Create webhooks table migration
- **Type:** feat
- **Size:** S
- **Description:** Create database schema for storing webhook configurations. Each user can register multiple webhook URLs with event filters.
- **Acceptance Criteria:**
  - [ ] Table has fields: id, user_id, url, events, secret, created_at
  - [ ] Migration up/down scripts created
  - [ ] Migration tested locally
- **Dependencies:** None

### Task 2: Implement webhook registration endpoint
- **Type:** feat
- **Size:** M
- **Description:** Add POST /webhooks endpoint to allow users to register webhook URLs. Validate URL format and generate signing secret.
- **Acceptance Criteria:**
  - [ ] POST /webhooks creates webhook record
  - [ ] Validates URL format (https:// only)
  - [ ] Generates and returns webhook secret
  - [ ] Returns 400 for invalid URLs
  - [ ] Unit tests cover validation logic
- **Dependencies:** Task 1 (need schema first)

### Task 3: Implement event dispatcher
- **Type:** feat
- **Size:** L
- **Description:** Create service to dispatch events to registered webhooks. Match event types to webhook subscriptions and send HTTP POST with HMAC signature.
- **Acceptance Criteria:**
  - [ ] Dispatches events to matching webhooks
  - [ ] Signs payload with HMAC-SHA256
  - [ ] Handles HTTP failures gracefully
  - [ ] Retries failed deliveries (max 3 attempts)
  - [ ] Unit tests cover dispatch logic (85% coverage)
- **Dependencies:** Task 2 (need webhooks to dispatch to)

### Task 4: Add webhook delivery logging
- **Type:** feat
- **Size:** M
- **Description:** Log all webhook delivery attempts for debugging and user visibility. Store request/response, status, and retry count.
- **Acceptance Criteria:**
  - [ ] Creates delivery_logs table
  - [ ] Logs every delivery attempt
  - [ ] GET /webhooks/:id/deliveries endpoint returns logs
  - [ ] Logs include: timestamp, status, response_code, error
  - [ ] Integration tests verify logging
- **Dependencies:** Task 3 (need dispatcher first)

### Task 5: Implement webhook verification endpoint
- **Type:** feat
- **Size:** S
- **Description:** Add GET /webhooks/:id/verify endpoint to send test payload. Helps users verify their webhook receiver works.
- **Acceptance Criteria:**
  - [ ] Sends test payload to webhook URL
  - [ ] Returns success/failure status
  - [ ] Does not retry on failure (one-shot test)
  - [ ] Unit tests cover verification logic
- **Dependencies:** Task 3 (uses dispatcher)

### Task 6: Add rate limiting to webhook endpoints
- **Type:** feat
- **Size:** S
- **Description:** Prevent abuse by rate limiting webhook registration and verification endpoints.
- **Acceptance Criteria:**
  - [ ] POST /webhooks limited to 10/hour per user
  - [ ] GET /webhooks/:id/verify limited to 5/hour per user
  - [ ] Returns 429 with Retry-After header
  - [ ] Integration tests verify rate limits
- **Dependencies:** Task 2, Task 5

### Task 7: Document webhook API
- **Type:** chore
- **Size:** S
- **Description:** Add webhook documentation to API reference. Include registration, event types, signature verification, and retry policy.
- **Acceptance Criteria:**
  - [ ] Document POST /webhooks endpoint
  - [ ] Document event payload format
  - [ ] Document HMAC signature verification
  - [ ] Include example code (curl, Python)
  - [ ] Document retry and delivery policy
- **Dependencies:** All tasks (need complete picture)

---

## Delivery Sequence

**Phase 1: Foundation (Week 1)**
- Task 1: Database schema
- Task 2: Registration endpoint

**Phase 2: Core Logic (Week 2)**
- Task 3: Event dispatcher
- Task 4: Delivery logging

**Phase 3: UX & Security (Week 3)**
- Task 5: Verification endpoint
- Task 6: Rate limiting

**Phase 4: Polish (Week 4)**
- Task 7: Documentation

**Rationale:**
- Foundation first (can't dispatch without registration)
- Core logic next (dispatcher is critical path)
- UX/security after core works (incremental value)
- Documentation last (need complete feature)

**Total Estimate:** 3-4 weeks for 7 tasks
```

---

## Summary

**Process:**
1. Clarify requirements (ask questions)
2. Break into discrete tasks
3. Define each task (title, description, criteria, dependencies, size, type)
4. Flag architectural decisions
5. Suggest delivery sequence
6. Output as structured list

**Task Quality:**
- Independent, deliverable, testable, estimable, valuable
- S or M size preferred (< 2 days)
- Clear acceptance criteria
- Explicit dependencies

**Key Rule:** Small tasks, clear criteria, logical sequence.
