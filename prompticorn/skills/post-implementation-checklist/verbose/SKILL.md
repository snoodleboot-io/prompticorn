---
name: post-implementation-checklist
description: Comprehensive checklist for documenting follow-up work and testing needs after implementation
languages: [all]
subagents: [code/feature, code/refactor, architect/data-model]
tools_needed: []
---

## Post-Implementation Checklist

After completing any code implementation, use this checklist to ensure all follow-up work is documented and nothing is forgotten.

---

## 1. Technical Debt Assessment

### Code Quality Debt
- [ ] **Hardcoded values** - Any magic numbers or strings that should be constants/config?
- [ ] **TODOs left in code** - Document each TODO with ticket/issue number
- [ ] **Temporary workarounds** - Any "hack" comments that need proper fixes?
- [ ] **Copy-pasted code** - Sections that should be extracted to shared functions?
- [ ] **Overly complex functions** - Functions > 50 lines that need refactoring?

### Design Debt
- [ ] **Missing abstractions** - Patterns duplicated 3+ times that need extraction?
- [ ] **Tight coupling** - Components that know too much about each other?
- [ ] **Violated SOLID principles** - Classes with multiple responsibilities?
- [ ] **Missing interfaces** - Concrete dependencies that should use abstractions?

### Documentation Debt
- [ ] **Missing docstrings** - Public functions without documentation?
- [ ] **Outdated comments** - Comments that no longer match the code?
- [ ] **Missing README updates** - New features not reflected in docs?
- [ ] **API documentation** - Endpoints/functions needing OpenAPI/JSDoc updates?

### Performance Debt
- [ ] **N+1 queries** - Database calls inside loops?
- [ ] **Missing indexes** - Queries on unindexed columns?
- [ ] **Unbounded collections** - Loops/queries without pagination?
- [ ] **Synchronous blocking** - I/O operations blocking the main thread?

---

## 2. Missing Features & Edge Cases

### Feature Completeness
- [ ] **Happy path only?** - Error handling for all failure modes?
- [ ] **Validation missing?** - Input validation comprehensive?
- [ ] **Edge cases uncovered** - Empty inputs, nulls, zeros, boundary values?
- [ ] **Internationalization** - Hardcoded strings that need i18n?
- [ ] **Accessibility** - UI components meeting a11y standards?

### User Experience Gaps
- [ ] **Error messages** - Clear, actionable error messages for users?
- [ ] **Loading states** - Indicators for async operations?
- [ ] **Empty states** - Helpful messages when no data exists?
- [ ] **Success feedback** - Confirmation after successful operations?

### Security Gaps
- [ ] **Authentication** - All endpoints/routes protected?
- [ ] **Authorization** - Proper permission checks on sensitive operations?
- [ ] **Input sanitization** - SQL injection / XSS prevention?
- [ ] **Rate limiting** - Protection against abuse?
- [ ] **Secrets in logs** - No sensitive data logged?

---

## 3. Testing Requirements

### Unit Tests Needed
- [ ] **Core logic coverage** - All business logic functions tested?
- [ ] **Happy path tests** - Expected inputs → expected outputs?
- [ ] **Edge case tests** - Empty, null, zero, boundary values?
- [ ] **Error case tests** - Invalid inputs raise proper errors?
- [ ] **Mock boundaries** - External dependencies mocked correctly?

**Target Coverage:**
- Line coverage: 80%+
- Branch coverage: 70%+
- Function coverage: 90%+

### Integration Tests Needed
- [ ] **API endpoint tests** - All HTTP endpoints tested end-to-end?
- [ ] **Database interactions** - Queries tested with real DB?
- [ ] **External service mocks** - Third-party APIs properly mocked?
- [ ] **Multi-component flows** - User journeys tested?
- [ ] **State transitions** - Status changes validated?

### Mutation Tests Needed
- [ ] **Test quality verification** - Run mutation testing on critical code?
- [ ] **Mutation score target** - 80%+ mutation score achieved?

### Property-Based Tests (if applicable)
- [ ] **Input generation** - Use Hypothesis/fast-check for complex validation?
- [ ] **Invariant checks** - Properties that should always hold true?

### Performance Tests (if needed)
- [ ] **Load testing** - Performance under expected traffic?
- [ ] **Stress testing** - Breaking point identified?
- [ ] **Database query performance** - Slow queries optimized?

---

## 4. Related Changes Needed Elsewhere

### Database Schema
- [ ] **Migration scripts** - Up/down migrations created and tested?
- [ ] **Index creation** - Indexes for new query patterns?
- [ ] **Backward compatibility** - Old code still works during migration?
- [ ] **Rollback plan** - Migration reversible without data loss?

### Configuration
- [ ] **Environment variables** - New config added to .env.example?
- [ ] **Config validation** - Startup fails fast on missing config?
- [ ] **Documentation** - Config options documented in README?

### Dependencies
- [ ] **New packages added** - Documented and justified?
- [ ] **Version locks** - Dependencies pinned to specific versions?
- [ ] **Security audit** - Dependencies scanned for vulnerabilities?
- [ ] **License compatibility** - All licenses compatible with project?

### Infrastructure
- [ ] **Deployment changes** - CI/CD pipeline updated?
- [ ] **Environment differences** - Staging/prod configs updated?
- [ ] **Monitoring** - New metrics/alerts added?
- [ ] **Logging** - Structured logging for new components?

---

## 5. Cross-Cutting Concerns

### Observability
- [ ] **Metrics** - Key metrics instrumented (latency, error rate, throughput)?
- [ ] **Logs** - Structured logs with correlation IDs?
- [ ] **Traces** - Distributed tracing spans added?
- [ ] **Alerts** - Threshold-based alerts configured?

### Error Handling
- [ ] **Error boundaries** - Errors caught at appropriate levels?
- [ ] **Retry logic** - Transient failures retried with backoff?
- [ ] **Circuit breakers** - Failing dependencies don't cascade?
- [ ] **Graceful degradation** - System functional when dependencies fail?

### Data Consistency
- [ ] **Transactions** - ACID properties maintained where needed?
- [ ] **Race conditions** - Concurrent operations handled correctly?
- [ ] **Eventual consistency** - Async operations converge to correct state?
- [ ] **Idempotency** - Retry-safe operations?

---

## 6. Communication & Documentation

### Team Communication
- [ ] **Changes announced** - Team notified of breaking changes?
- [ ] **Knowledge sharing** - Complex decisions documented (ADR)?
- [ ] **Runbook updated** - Operations team has deployment guide?

### External Documentation
- [ ] **API documentation** - OpenAPI spec / public API docs updated?
- [ ] **User documentation** - End-user guides updated?
- [ ] **Changelog** - Entry added with version and date?

---

## 7. Pre-Merge Verification

### Code Review Readiness
- [ ] **Self-review done** - Reviewed own diff for obvious issues?
- [ ] **Commits cleaned** - Logical, well-described commits?
- [ ] **No debug code** - console.log / print statements removed?
- [ ] **Linter passing** - All lint rules satisfied?
- [ ] **Type checker passing** - No type errors?

### CI/CD Status
- [ ] **All tests passing** - Unit, integration, e2e tests green?
- [ ] **Build succeeds** - Production build successful?
- [ ] **Coverage threshold met** - Coverage above project minimum?
- [ ] **Security scan passing** - No new vulnerabilities?

### Manual Testing
- [ ] **Tested locally** - Feature works in local environment?
- [ ] **Tested in staging** - Feature works in staging environment?
- [ ] **Smoke tests** - Critical paths verified manually?

---

## 8. Post-Merge Follow-Up

### Monitoring
- [ ] **Deployment verified** - Feature deployed successfully?
- [ ] **Error rates normal** - No spike in errors after deploy?
- [ ] **Performance acceptable** - No latency regression?
- [ ] **Logs reviewed** - No unexpected warnings/errors?

### Follow-Up Tickets
- [ ] **Tech debt tickets created** - All identified debt has tickets?
- [ ] **Missing feature tickets** - Known gaps documented as issues?
- [ ] **Test gap tickets** - Missing tests tracked for future work?

---

## Output Format

After implementation, produce a summary like this:

```markdown
## Post-Implementation Summary

### Follow-Up Work Created
**Technical Debt:**
- PROJ-456: Refactor user validation logic (duplicated 3x)
- PROJ-457: Extract email sending to background job
- PROJ-458: Add proper error handling to payment flow

**Missing Features:**
- PROJ-459: Add pagination to user list endpoint
- PROJ-460: Implement email verification flow
- PROJ-461: Add rate limiting to authentication

**Documentation:**
- PROJ-462: Update API documentation for new endpoints
- PROJ-463: Add architecture decision record for payment provider choice

### Tests Needed
**Unit Tests:**
- [ ] test_user_validation_with_invalid_email
- [ ] test_user_validation_with_special_characters
- [ ] test_payment_processing_retries_on_failure

**Integration Tests:**
- [ ] test_user_registration_end_to_end
- [ ] test_payment_flow_with_webhook
- [ ] test_email_verification_complete_flow

**Coverage Status:**
- Current: 78% (below 80% target)
- Missing: Error handling paths in payment module

### Related Changes
**Database:**
- Migration #047 created for users.email_verified column
- Index needed on users.email for lookup performance

**Configuration:**
- Added PAYMENT_PROVIDER_API_KEY to .env.example
- Updated staging/prod configs with new keys

**Dependencies:**
- Added `stripe==5.2.0` for payment processing
- Added `celery==5.3.0` for background jobs
```

---

## Common Mistakes to Avoid

### Mistake 1: "I'll remember to fix this later"
**Problem:** You won't. Create a ticket immediately.

**Fix:** Document all tech debt as tickets before merging.

---

### Mistake 2: Skipping test documentation
**Problem:** Tests don't get written, coverage drops over time.

**Fix:** Explicitly list every test case that should exist.

---

### Mistake 3: Vague follow-up items
**Bad:** "Improve error handling"
**Good:** "Add retry logic with exponential backoff to email service (PROJ-789)"

**Fix:** Make follow-up items specific and actionable.

---

### Mistake 4: Ignoring cross-cutting concerns
**Problem:** New feature works but breaks monitoring, logs nothing, has no alerts.

**Fix:** Check observability, error handling, security for every change.

---

### Mistake 5: Forgetting about operations
**Problem:** Feature deploys, breaks in prod, ops team has no runbook.

**Fix:** Update deployment docs and runbooks before merging.

---

## When to Use This Checklist

**ALWAYS use after:**
- Implementing new features
- Making significant changes to existing features
- Refactoring code
- Updating data models or schemas
- Adding new dependencies

**Timing:**
- Review checklist BEFORE creating pull request
- Include summary in PR description
- Reference created tickets in PR comments
