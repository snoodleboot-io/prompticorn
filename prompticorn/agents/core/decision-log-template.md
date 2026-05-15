<!-- path: prompticorn/prompts/agents/core/core-decision-log-template.md -->
# Core Decision Log Template

## Purpose

Decision logs record important decisions made during development. They provide context for why choices were made, what alternatives were considered, and what the trade-offs are.

Decision logs can be kept in:
1. **Session files** - For decisions within a single branch/work session
2. **Planning ADRs** - Architecture Decision Records in `planning/current/adrs/`
3. **Final docs** - Important decisions in `docs/decisions/` (finalized, stable)
Decision logs can be kept in:
1. **Session files** - For decisions within a single branch/work session
2. **Planning ADRs** - Architecture Decision Records in `planning/current/adrs/`
3. **Final docs** - Important decisions in `docs/decisions/` (finalized, stable)
Decision logs can be kept in:
1. **Session files** - For decisions within a single branch/work session
2. **Planning ADRs** - Architecture Decision Records in `planning/current/adrs/`
3. **Final docs** - Important decisions in `docs/decisions/` (finalized, stable)
Decision logs can be kept in:
1. **Session files** - For decisions within a single branch/work session
2. **Planning ADRs** - Architecture Decision Records in `planning/current/adrs/`
3. **Final docs** - Important decisions in `docs/decisions/` (finalized, stable)

---

## Basic Decision Log Entry

Use this format for recording decisions:

```markdown
## [YYYYMMDD] - [Decision Title]

**Date:** YYYY-MM-DD  
**Decision Maker:** [Name or Role]  
**Status:** [Proposed | Approved | Rejected | Implemented | Superceded]

### Context
What is the situation that prompted this decision?
Why are we making a decision now?
What are the forces at play (technical, business, constraints)?

### Problem
What specific problem are we trying to solve?
Why is it important to solve now?

### Options Considered

#### Option 1: [Name]
**Approach:** [Brief description]
**Pros:**
- [Advantage 1]
- [Advantage 2]
**Cons:**
- [Disadvantage 1]
- [Disadvantage 2]
**Effort:** [Low/Medium/High]
**Decision:** [Accepted / Rejected / Deferred]

#### Option 2: [Name]
**Approach:** [Brief description]
**Pros:**
- [Advantage 1]
**Cons:**
- [Disadvantage 1]
**Effort:** [Low/Medium/High]
**Decision:** [Accepted / Rejected / Deferred]

#### Option 3: [Name]
**Approach:** [Brief description]
**Pros:**
- [Advantage 1]
**Cons:**
- [Disadvantage 1]
**Effort:** [Low/Medium/High]
**Decision:** [Accepted / Rejected / Deferred]

### Decision
[Clear, unambiguous statement of what we decided to do]

### Rationale
Why did we choose this option over alternatives?
What factors were most important?

### Consequences

**Positive:**
- [Benefit 1]
- [Benefit 2]

**Negative / Trade-offs:**
- [Trade-off 1]
- [Trade-off 2]

**Neutral Observations:**
- [Observation 1]

### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| [Risk 1] | [H/M/L] | [H/M/L] | [How we'll mitigate] |
| [Risk 2] | [H/M/L] | [H/M/L] | [How we'll mitigate] |

### Implementation Plan

1. **Phase 1:** [What we'll do first]
   - Timeline: [When]
   - Owner: [Who]

2. **Phase 2:** [Next steps]
   - Timeline: [When]
   - Owner: [Who]

3. **Phase 3:** [Later steps]
   - Timeline: [When]
   - Owner: [Who]

### Success Criteria

- [ ] [Testable criterion 1]
- [ ] [Testable criterion 2]
- [ ] [Testable criterion 3]

### Related Decisions

- [Link to related decision 1]
- [Link to related decision 2]

### Reversibility

**Can this decision be reversed?** [Easy / Difficult / Irreversible]

**If we need to undo this:**
[What would happen? How much effort?]

### Approval

- **Approved by:** [Name]
- **Date:** YYYY-MM-DD
- **Review comments:** [Any notes from review]

---

## Complete Example: Decision to Use OAuth Instead of Email/Password

```markdown
## [20260304] - Implement OAuth 2.0 Instead of Custom Auth

**Date:** 2026-03-04  
**Decision Maker:** Engineering Lead  
**Status:** Approved

### Context

Our application currently requires users to create accounts with email/password.
User research shows sign-up friction is a major barrier to adoption.
We want to reduce friction and improve user experience.
We need to decide: should we add OAuth support (GitHub, Google, etc.)?

### Problem

Current sign-up process requires:
1. Email entry
2. Password creation (with complexity requirements)
3. Email verification
4. Account creation

This takes 5-10 minutes and has 40% drop-off rate.

We want to reduce drop-off and support faster sign-up for developers.

### Options Considered

#### Option 1: OAuth 2.0 (GitHub + Google)
**Approach:** Implement OAuth for GitHub and Google. Users can sign up with one click.
**Pros:**
- Fastest sign-up (one click)
- Lowest friction
- Industry standard, well-understood
- No password management needed
- GitHub/Google handle security
- Familiar to developers

**Cons:**
- Dependency on GitHub/Google availability
- User can't use app if OAuth provider is down
- Requires OAuth implementation (some work)
- Users need GitHub/Google account
- Binding to third-party user data

**Effort:** Medium (2 weeks)
**Decision:** ACCEPTED - This is our primary solution

#### Option 2: Email/Password + Optional OAuth
**Approach:** Keep email/password system AND add OAuth as optional alternative.
**Pros:**
- Users have choice
- Email/password is fallback
- No dependency on third parties
- Maximum flexibility

**Cons:**
- More complex to maintain (two auth systems)
- Users still need to choose during signup
- Doesn't fully solve friction problem
- More code = more bugs

**Effort:** High (4 weeks)
**Decision:** REJECTED - Adds too much complexity

#### Option 3: Magic Links (Email Only)
**Approach:** No password. User clicks email link to login each time.
**Pros:**
- No password to remember
- Simple to implement
- Works for everyone with email
- No third-party dependency

**Cons:**
- Still requires email entry
- Email delivery not instant
- Doesn't solve core friction
- More email infrastructure needed

**Effort:** Medium (2 weeks)
**Decision:** DEFERRED - Could be future addition

### Decision

Implement OAuth 2.0 with GitHub and Google as sign-up options.
Keep email/password as fallback for users without GitHub/Google accounts.
Timeline: 2 weeks.

### Rationale

OAuth solves the core problem (sign-up friction) with minimal new complexity.
It's the industry standard for developer-focused apps.
GitHub is essential for our target audience.
Google login supports non-developer users.
Fallback to email/password provides safety net.

### Consequences

**Positive:**
- Sign-up time reduced from 10 minutes to 2 minutes
- User drop-off likely decreases by 30-40%
- Aligns with user expectations
- Reduces our password management burden
- Better user experience for our target audience

**Negative:**
- Dependency on GitHub/Google uptime
- If GitHub is down, new GitHub-signup users can't sign up
- Need to manage OAuth secrets securely
- Additional complexity in auth layer
- Need to handle account linking (same email across providers)

**Neutral:**
- Email/password still needed as fallback
- Different UX flow than competitors
- Users need to understand OAuth concept (though they probably do)

### Risks and Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| GitHub down → can't signup | Low | High | Fallback to email/password; monitor GitHub status |
| Phishing via fake OAuth screens | Medium | High | Security audit; clear UI indicators; HTTPS only |
| User account linking bugs | Medium | Medium | Comprehensive testing; manual verification step |
| OAuth config errors | Medium | Medium | Deployment checklist; automated configuration tests |

### Implementation Plan

1. **Phase 1 - Foundation (Week 1):**
   - Create OAuth provider abstraction
   - Implement GitHub OAuth provider
   - Implement Google OAuth provider
   - Owner: Backend team
   - Timeline: Days 1-3

2. **Phase 2 - Integration (Week 1-2):**
   - Create signup endpoint with OAuth
   - Create login endpoint with OAuth
   - Implement account linking
   - Owner: Full-stack team
   - Timeline: Days 4-7

3. **Phase 3 - Testing & Deploy (Week 2):**
   - Integration tests
   - Security audit
   - Deploy to staging
   - User acceptance testing
   - Deploy to production
   - Owner: QA + Engineering Lead
   - Timeline: Days 8-14

### Success Criteria

- [ ] OAuth sign-up works for GitHub and Google
- [ ] Account linking works correctly
- [ ] Email/password fallback still works
- [ ] All tests passing (unit + integration)
- [ ] Security audit passed
- [ ] Documentation complete
- [ ] Sign-up time < 2 minutes
- [ ] Zero account linking bugs in staging

### Related Decisions

- [JWT Implementation Decision](./jwt-implementation.md) - How we manage tokens for OAuth users
- [Email Notification Decision](./email-service.md) - How OAuth users get welcome emails

### Reversibility

**Can this decision be reversed?** Difficult

**If we need to undo this:**
- OAuth is tightly integrated with auth layer
- Users created via OAuth have OAuth credentials stored
- Reverting would require migration of OAuth users to email/password
- Takes significant effort but technically possible
- Once users exist via OAuth, removing OAuth is disruptive to them

### Approval

- **Approved by:** Engineering Lead (Alice)
- **Date:** 2026-03-04
- **Review comments:** "This is the right call. OAuth is standard practice. Implementation plan looks solid. Let's do security audit in parallel with development to catch issues early."

---

## Decision Log Storage

### In Session File

For session-specific decisions:
```markdown
## Session Overview
[...]

## Decisions Made This Session

### 2026-03-04 14:00 - Decided to extract validation logic
**Rationale:** Validation is used in 3 places, should be DRY  
**Alternative:** Leave as-is and duplicate code  
**Chosen:** Extract to separate function for reuse  
**Status:** Approved

### 2026-03-04 16:30 - Decided to use dependency injection
**Rationale:** Easier to test, follows SOLID principles  
**Alternative:** Direct instantiation within class  
**Chosen:** Dependency injection via constructor  
**Status:** Approved
```

### In Planning Directory

For development planning decisions:
- Active work: `planning/current/adrs/ADR-NNN-title.md`
- Completed work: `planning/complete/adrs/ADR-NNN-title.md`
- Future exploration: `planning/backlog/adrs/DRAFT_ADR-NNN-title.md`

### In Docs Directory (Finalized Only)

For stable, user-facing architectural decisions:
- Finalized decisions: `docs/decisions/ADR-NNN-title.md`
- Format: Same as template above
- Review: Required from team leads
- Update: When decision status changes

---

## When to Log a Decision

Log a decision if:
- ✓ It will affect multiple systems or files
- ✓ It involves trade-offs or alternatives were considered
- ✓ It impacts long-term maintainability
- ✓ It's not obvious why this approach was chosen
- ✓ It could be revisited later
- ✓ Multiple people need to understand the reasoning

Don't log if:
- ✗ It's a simple implementation detail (variable naming)
- ✗ It follows a clear standard (use core-conventions.md pattern)
- ✗ It's a minor tactical choice
- ✗ Everyone agrees instantly with no discussion

---

## Review Checklist for Decision Logs

Before approving a decision log entry:

- [ ] Context is clear (why are we deciding this now?)
- [ ] Problem is well-defined (what are we solving?)
- [ ] Options are fairly presented (no strawmanning)
- [ ] Pros/cons are realistic (not exaggerated)
- [ ] Decision is unambiguous (clear what we chose)
- [ ] Rationale is explained (why this option?)
- [ ] Consequences are documented (what happens now?)
- [ ] Risks are identified (what could go wrong?)
- [ ] Reversibility is clear (can we undo this?)
- [ ] Success criteria are testable (how do we know if it worked?)
