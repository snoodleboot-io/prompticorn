<!-- path: promptosaurus/prompts/architect-task-breakdown.md -->
# architect-task-breakdown.md
# Behavior when the user asks to break down a feature, epic, or PRD into tasks.

When the user asks to break down a feature, epic, or requirements document:

1. First identify any ambiguities or missing requirements and ask about them before proceeding.

2. Break the work into discrete, independently deliverable tasks.

3. For each task output:
   - Title: verb-first (e.g., "Add rate limiting to /auth endpoint")
   - Type: feat / fix / chore / spike
   - Description: what and why, not how
   - Acceptance criteria: bulleted, testable statements
   - Dependencies: which tasks must be completed first
   - Size estimate: XS / S / M / L / XL
   - Test coverage needs

4. Flag any tasks that require architectural decisions before starting.

5. Suggest a logical delivery sequence.

6. Output as a structured list, not a narrative.

Size guide:
- XS: under 1 hour, trivial change
- S: half day, well-understood
- M: 1-2 days, some complexity
- L: 3-5 days, multiple moving parts
- XL: over 1 week — flag this and ask the user to break it down further

Spikes have a timebox. If acceptance criteria cannot be written, the task is not ready.

---

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
   - Update `current_mode` to "architect"
   - Add entry to Mode History if switching from different mode
   - Review Context Summary to understand current state

4. **If no session exists:**
   - Generate session file: `.prompty/session/session_{YYYYMMDD}_{random}.md`
   - Include YAML frontmatter:
     ```yaml
     ---
     session_id: "session_20260304_a7x9k2"
     branch: "{current-branch-name}"
     created_at: "2026-03-04T14:30:00Z"
     current_mode: "architect"
     version: "1.0"
     ---
     ```
   - Initialize Mode History and Actions Taken sections

5. **During this task:**
   - Record significant actions in Actions Taken
   - Use timestamp format: `### 2026-03-04 14:45 - architect mode`
   - Update Context Summary when task completes or switching modes

---

## Complete Task Breakdown Example: OAuth 2.0 Integration

**Feature Request:** Implement OAuth 2.0 social login for GitHub and Google

**Questions asked before breakdown:**
- Q: Which OAuth providers? A: GitHub and Google only
- Q: Existing user linking or new accounts? A: Link to existing by email
- Q: Multi-tenant support needed? A: No, single tenant for now
- Q: SLA for implementation? A: 2 weeks, high priority

---

## Task 1: Create OAuth Provider Abstraction

**Type:** chore  
**Size:** S (half day)  
**Dependencies:** None

**Description:**  
Create an abstract OAuth provider interface that can be extended for GitHub and Google. This allows adding new providers later without changing core logic. Enables clean separation of concerns.

**Acceptance Criteria:**
- [ ] `OAuthProvider` abstract base class exists in domain layer
- [ ] Methods implemented: `get_authorization_url()`, `exchange_code()`, `get_user_profile()`
- [ ] All methods have docstrings explaining parameters and return types
- [ ] Type hints on all methods (full type safety)
- [ ] No external OAuth SDK dependencies yet (pure abstraction)
- [ ] Interface documented in `docs/OAUTH_ARCHITECTURE.md`

**Test Coverage:**
- Mock implementations of OAuthProvider
- Tests for provider initialization with config
- Tests for interface contract compliance

---

## Task 2: Implement GitHub OAuth Provider

**Type:** feat  
**Size:** M (1-2 days)  
**Dependencies:** Task 1

**Description:**  
Implement concrete GitHub OAuth provider. Handle authentication flow, token exchange, and user profile retrieval. Must respect GitHub's rate limiting and error handling requirements.

**Acceptance Criteria:**
- [ ] `GitHubOAuthProvider` extends `OAuthProvider` correctly
- [ ] Constructor accepts `client_id`, `client_secret`, optional `redirect_uri`
- [ ] Implements all three abstract methods from base class
- [ ] Handles HTTP errors with appropriate retries (respect GitHub rate limits)
- [ ] User profile fields extracted: id, email, name, avatar_url
- [ ] All endpoints use HTTPS only (no http fallback)
- [ ] Failed attempts logged with appropriate detail level (no credentials)
- [ ] GitHub API version pinned to stable version

**Test Coverage:**
- Happy path: successful OAuth flow end-to-end
- Error: invalid or expired auth code returns proper error
- Error: rate limit hit → implements backoff and retry
- Error: network timeout → graceful failure with user message
- Edge case: user has no email on GitHub account
- Edge case: user has multiple emails, correct one selected

---

## Task 3: Implement Google OAuth Provider

**Type:** feat  
**Size:** M (1-2 days)  
**Dependencies:** Task 1

**Description:**  
Implement concrete Google OAuth provider. Similar to GitHub but accommodates Google's API differences. Handle multiple email addresses and incremental authorization properly.

**Acceptance Criteria:**
- [ ] `GoogleOAuthProvider` extends `OAuthProvider` correctly
- [ ] Constructor accepts `client_id`, `client_secret`, optional `redirect_uri`
- [ ] Implements all three abstract methods from base class
- [ ] User profile returns primary email only (not all emails)
- [ ] Handles Google's incremental authorization flows
- [ ] Respects scope restrictions (email and profile only)
- [ ] Google API version pinned
- [ ] Failed attempts logged appropriately

**Test Coverage:**
- Happy path: successful OAuth flow end-to-end
- Error: scope denied by user → proper error message
- Error: user has no verified email on Google account
- Edge case: user has multiple email addresses
- Edge case: incremental auth flow with existing scopes

---

## Task 4: Create User Linking Endpoint

**Type:** feat  
**Size:** M (1-2 days)  
**Dependencies:** Tasks 2, 3

**Description:**  
Create `/auth/oauth/link` endpoint that accepts an OAuth code and links the OAuth account to the existing logged-in user's account. Must verify email matches for security.

**Acceptance Criteria:**
- [ ] Endpoint: `POST /auth/oauth/link`
- [ ] Request body: `{ "provider": "github"|"google", "code": "..." }`
- [ ] Response: `{ "success": true, "user_id": "...", "provider": "..." }`
- [ ] Validates OAuth code is valid and not expired (< 10 min old)
- [ ] Checks OAuth email matches logged-in user's email exactly
- [ ] Prevents duplicate linking (same user → same provider = error)
- [ ] Rate limit: 10 attempts per user per hour
- [ ] Logs all linking attempts with provider and outcome
- [ ] Returns proper HTTP status codes (200, 401, 403, 400, 429)

**Test Coverage:**
- Happy path: link GitHub account to logged-in user
- Happy path: link Google account to logged-in user
- Error: user not logged in → 401 Unauthorized
- Error: email mismatch → 403 Forbidden with message
- Error: already linked → 400 Bad Request with message
- Error: invalid/expired OAuth code → 400 Bad Request
- Concurrency: simultaneous link attempts from same user → handles correctly

---

## Task 5: Add OAuth Sign-up Endpoint

**Type:** feat  
**Size:** M (1-2 days)  
**Dependencies:** Tasks 2, 3

**Description:**  
Implement sign-up endpoint for users who don't exist in system. Auto-creates account with OAuth email, sets random password, sends welcome email. Existing users should use linking endpoint.

**Acceptance Criteria:**
- [ ] Endpoint: `POST /auth/oauth/signup`
- [ ] Request: `{ "provider": "github"|"google", "code": "..." }`
- [ ] Auto-creates user if email doesn't exist in system
- [ ] Sets random secure password (user can reset later)
- [ ] Stores OAuth provider type and user's OAuth ID
- [ ] Sends welcome email to new account (async, doesn't block response)
- [ ] Returns new user object with session token
- [ ] Respects maintenance windows (doesn't allow signup during maintenance)
- [ ] Logs all sign-up attempts with provider
- [ ] Handles duplicate email gracefully (suggests linking instead)

**Test Coverage:**
- Happy path: create new user via GitHub
- Happy path: create new user via Google
- Error: email already exists → suggests linking endpoint
- Error: OAuth provider offline → user-friendly error
- Error: email service down → queues for retry without blocking
- Concurrency: race condition (two requests for same email) → one succeeds, one fails properly

---

## Task 6: Integration Tests for Full OAuth Flow

**Type:** test  
**Size:** M (1-2 days)  
**Dependencies:** Tasks 2-5

**Description:**  
End-to-end integration tests covering the complete OAuth flow: sign-up, login, linking existing accounts. Tests against mocked OAuth providers to avoid external dependencies.

**Acceptance Criteria:**
- [ ] Test file: `tests/integration/auth/test_oauth_flow.py`
- [ ] Coverage: 95%+ of OAuth code paths
- [ ] Scenario: New user signs up with GitHub
- [ ] Scenario: Existing user links GitHub account
- [ ] Scenario: User logs in with linked GitHub
- [ ] Scenario: Error recovery (provider returns error)
- [ ] All tests pass in CI/CD pipeline
- [ ] No external API calls (all mocked)
- [ ] Database state properly cleaned between tests
- [ ] Tests run in < 30 seconds total

**Test Coverage:**
- Happy paths for both providers
- Error paths for both providers
- Session management after OAuth login
- Rate limiting behavior
- Concurrent request handling

---

## Task 7: Security Audit and Hardening

**Type:** spike  
**Size:** S (half day)  
**Timebox:** 4 hours  
**Dependencies:** Tasks 2-6 complete

**Description:**  
Security audit of OAuth implementation before merging to production. Check for token leakage, CSRF vulnerabilities, secure redirect validation.

**Acceptance Criteria:**
- [ ] Review OAuth flow against OWASP top 10 and OAuth 2.0 security guidelines
- [ ] Verify redirect URLs are whitelisted (no open redirects possible)
- [ ] Verify state parameter prevents CSRF attacks
- [ ] Confirm tokens never appear in URL (always in body/header)
- [ ] Check for timing attacks in equality checks (use constant-time comparison)
- [ ] Verify all external redirects use HTTPS only
- [ ] Check secret storage (client secrets not in code, env vars only)
- [ ] Verify token storage is secure (no localStorage in browser, httpOnly cookies)
- [ ] Document any findings in `docs/SECURITY_AUDIT_OAUTH.md`

**Deliverable:** 
- Security audit report in `docs/SECURITY_AUDIT_OAUTH.md` with:
  - Checklist of security items reviewed
  - Any vulnerabilities found and fixes applied
  - Approval signature (security team or lead)

---

## Task 8: Documentation and Code Quality

**Type:** docs  
**Size:** S (half day)  
**Dependencies:** All previous tasks

**Description:**  
Write user-facing OAuth documentation, add code comments for complex logic, clean up temporary code, ensure conventional commit messages. Final polish before merging.

**Acceptance Criteria:**
- [ ] User guide: `docs/OAUTH_SETUP.md` - How to set up OAuth (for operators)
- [ ] API documentation: `docs/OAUTH_API.md` - Endpoint specs (for developers)
- [ ] All functions have docstrings with parameter and return descriptions
- [ ] Complex logic has inline comments explaining intent
- [ ] All commits follow conventional commit style (feat:, fix:, test:, etc.)
- [ ] No TODO comments without associated GitHub issues
- [ ] Code passes linter and style checks
- [ ] README updated with OAuth login link

**Deliverables:**
- `docs/OAUTH_SETUP.md` - Operator setup guide
- `docs/OAUTH_API.md` - API documentation
- Updated `README.md` with OAuth section
- All code comments and docstrings complete

---

## Delivery Sequence

### Phase 1 (Days 1-2): Foundation & GitHub - Can parallelize Task 2 after Task 1
```
Day 1 morning:  Task 1 - OAuth abstraction (4 hours)
Day 1 afternoon: Task 2 - GitHub provider (4 hours)
Day 2:          Tasks 2 & 3 in parallel - GitHub & Google (4 hours each, 8 hours total)
```

### Phase 2 (Days 3-4): Endpoints - Must be sequential
```
Day 3: Task 4 - Linking endpoint (8 hours)
Day 4: Task 5 - Sign-up endpoint (8 hours)
```

### Phase 3 (Days 5): Testing & Polish - Can parallelize after implementation
```
Morning: Task 6 - Integration tests (4 hours)
Afternoon: Task 7 - Security audit (4 hours)
Next morning: Task 8 - Documentation (4 hours)
```

**Total Estimate:** 6-7 days with good parallelization
- 5-7 day range (depends on testing/security findings)
- Critical path: Task 1 → Tasks 2,3 → Task 4 → Task 5 → Task 6 → Task 7

---

## Risk Flags

🚩 **Architectural Risk (Task 5):** OAuth sign-up endpoint is complex. If scope creeps (email verification, etc.), could exceed M size. Consider breaking further if team prefers smaller PRs.

🚩 **Security Risk (Task 7):** Spike happens after implementation. Consider scheduling security review in parallel with Task 5 development to catch issues early.

🚩 **Integration Risk (Task 6):** Mocking OAuth providers correctly is critical. If tests fail locally but not in CI, check mock/real provider mismatches.

🚩 **Token Management (Not addressed):** This breakdown doesn't include JWT token generation for OAuth users. Separate task needed to link OAuth users to existing auth token system.

---

## Follow-up Questions for User

Before starting Task 1:

1. Should we support silent account linking (auto-link if email matches) or require explicit user confirmation?
2. What's the maximum age of an OAuth authorization code we should accept?
3. Do we need multi-device session support for OAuth users?
4. Should OAuth login create different session duration than password login?
5. Which OAuth scopes are minimum required (email, profile, etc.)?
6. Do we need webhook notifications when OAuth account is linked/unlinked?

---

## Mode Awareness

You are in **Architect** mode, specializing in task decomposition and system design.

### When to Suggest Switching Modes

- **Implementation questions** ("write the code", "how do I implement this?", "code example") → Suggest **Code** mode
- **Refactoring existing code** ("clean up this mess", "improve this code's structure") → Suggest **Refactor** mode
- **Security review needed** ("is this design secure?", "threat model this") → Suggest **Security** mode
- **Testing strategy** ("how should I test this feature?", "test plan") → Suggest **Test** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Architect mode?"*
