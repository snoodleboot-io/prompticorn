<!-- path: promptosaurus/.kilocode/rules-migration/workflow-verbose.md -->
# Migration Workflow - Verbose Version

**Metadata:**
- languages: [all]
- subagents: [migration/dependency-upgrade, migration/strategy]
- target_audience: Senior engineers, architects
- estimated_time: 4-16 hours
- complexity: high

## 1. Migration Types & Risk Classification

### Dependency Upgrade (Low-Medium Risk)
- **Scope:** Updating a single package/library version
- **Examples:** npm install react@19, pip install SQLAlchemy==2.1
- **Risk factors:** Breaking API changes, deprecations, new requirements
- **Timeline:** 2-4 hours for minor versions, 6-8 hours for major versions

### Database Schema Migration (High Risk)
- **Scope:** Changing data structure, columns, relationships
- **Examples:** Adding columns, renaming tables, changing relationships
- **Risk factors:** Data loss, downtime, backwards compatibility
- **Timeline:** 4-8 hours including verification and rollback prep
- **Critical:** Requires zero-downtime strategy for production

### Framework Migration (Very High Risk)
- **Scope:** Major architectural change (React class → hooks, Redux → Context)
- **Examples:** Angular.js → React, ORM upgrade, async model change
- **Risk factors:** Widespread code changes, behavioral shifts, new patterns
- **Timeline:** 2-5 days, phased approach required
- **Critical:** Extended testing period, potential for hidden bugs

### Architecture Refactor (High Risk)
- **Scope:** Restructuring how components interact (monolith → microservices)
- **Examples:** Adding caching layer, API client changes, state management
- **Risk factors:** Integration failures, data consistency, performance impacts
- **Timeline:** 3-7 days with integration testing
- **Critical:** Requires coordinated rollout plan

## 2. Pre-Migration Planning

### Step 2.1: Scope Definition
Define exactly what changes:
```
MIGRATION SCOPE CHECKLIST:
- [ ] Current state fully documented (versions, configurations, dependencies)
- [ ] Target state clearly defined (versions, APIs, patterns)
- [ ] Breaking changes identified and listed
- [ ] Deprecated features documented
- [ ] Impact assessment on each layer (API, DB, frontend, backend)
- [ ] Dependencies between changes mapped
```

### Step 2.2: Compatibility Assessment
Check constraints before starting:
```
COMPATIBILITY CHECKLIST:
- [ ] Node/Python/Go/Java version requirements met
- [ ] OS compatibility verified (Linux, macOS, Windows)
- [ ] Peer dependencies reviewed
- [ ] Package conflicts identified
- [ ] Security vulnerabilities checked (npm audit, pip-audit)
- [ ] License compatibility verified (if applicable)
- [ ] Enterprise restrictions checked (if applicable)
```

### Step 2.3: Rollback Strategy
Document how to undo changes:
```
ROLLBACK PROCEDURE TEMPLATE:
1. Identify rollback trigger point (automated tests fail, data corruption, etc.)
2. Database rollback (if applicable):
   - Manual SQL migrations down
   - Data backup restore procedure
   - Time estimate: ____ minutes
3. Code rollback:
   - git revert strategy vs git reset
   - Affected branches to revert
   - Time estimate: ____ minutes
4. Service verification:
   - Health checks to confirm rollback success
   - Data integrity verification
5. Communication plan: Who to notify, how to notify
6. Total rollback time estimate: ____ minutes
```

## 3. Test Plan Creation

### Step 3.1: Baseline Testing
Establish current behavior before changes:
```
BASELINE TEST PLAN:
1. Run full test suite on current code:
   - Unit test count: ____
   - Unit test coverage %: ____
   - Integration test count: ____
   - Integration test coverage %: ____

2. Document key metrics:
   - API response times (p50, p95, p99)
   - Database query times
   - Memory usage baseline
   - Error rates

3. Create manual test scenarios for critical paths:
   - User signup/login flow
   - Payment processing (if applicable)
   - Data export/import (if applicable)
   - Admin functionality (if applicable)
```

### Step 3.2: Migration Test Scenarios
Tests that MUST pass after migration:
```
REQUIRED TEST COVERAGE:
1. Compatibility tests:
   - Old API still works (if backwards compatible)
   - New API works as designed
   - Error handling unchanged

2. Edge case tests:
   - Empty/null values handled correctly
   - Boundary conditions (max, min values)
   - Concurrent operations (if relevant)
   - Error states match expectations

3. Performance tests:
   - Response times within 10% of baseline
   - Memory usage acceptable
   - No N+1 query problems (database migrations)
   - No memory leaks (resource cleanup verified)

4. Integration tests:
   - Services communicate correctly
   - Data flows correctly between layers
   - Third-party integrations still work
   - Event handling/queues (if applicable)

5. Regression tests:
   - Existing features still work
   - Existing bugs not reintroduced
   - Side effects minimal
```

### Step 3.3: Verification Checklist
Manual verification after automated tests pass:
```
MANUAL VERIFICATION:
- [ ] Smoke test critical paths in staging
- [ ] Check logs for errors/warnings
- [ ] Verify database integrity
- [ ] Check performance metrics vs baseline
- [ ] Verify third-party service connections
- [ ] Confirm UI/UX unchanged (if relevant)
- [ ] Check documentation accuracy
```

## 4. Data Migration Strategies

### For Database Schema Changes

**Strategy A: Zero-Downtime (Recommended for production)**
```
PHASE 1 (Before migration):
- Deploy code that reads/writes both old and new column
- Data starts populating new column alongside old
- Allow 24-48 hours for data sync

PHASE 2 (Migration window):
- Run migration script to backfill any missing data
- Add constraint to ensure new column has valid data
- Verify 100% data consistency

PHASE 3 (Post-migration):
- Deploy code that only reads/writes new column
- Keep old column temporarily (for 1 release)
- Monitor for issues

PHASE 4 (Cleanup):
- Remove old column in next release
- Update documentation
```

**Strategy B: Scheduled Downtime (For non-critical systems)**
```
1. Announce maintenance window
2. Take system offline
3. Run migration script
4. Verify data integrity
5. Deploy new code
6. Run validation tests
7. Bring system back online
8. Monitor for issues
```

**Strategy C: Parallel Run (For critical data changes)**
```
1. New system runs alongside old system
2. All reads go to old system initially
3. All writes go to both systems
4. Validate new system produces identical results
5. Switch reads to new system after validation period
6. Deprecate old system after confidence period
```

### Data Validation After Migration
```
VALIDATION QUERIES/SCRIPTS:
1. Count checks:
   - Old table count === new table count
   - No orphaned records

2. Sample verification:
   - Select random sample (500 rows)
   - Verify all columns populated correctly
   - Check data types correct

3. Constraint validation:
   - Foreign keys valid
   - Unique constraints satisfied
   - Null constraints respected

4. Business logic validation:
   - Calculations correct
   - Status transitions valid
   - Derived columns match formula
```

## 5. Incremental Execution Strategy

### Phase-Based Rollout (Prevents All-Or-Nothing Failure)

**Phase 1: Single Module (2-4 hours)**
- Migrate smallest, lowest-risk module first
- Establish pattern for remaining modules
- Run full test suite
- Get approval before next phase

**Phase 2: Related Modules (4-8 hours)**
- Migrate modules that depend on Phase 1
- Test integration between phases
- Verify backwards compatibility still works
- Document any new patterns discovered

**Phase 3: Core Services (8-16 hours)**
- Migrate main business logic
- Requires thorough integration testing
- Shadow traffic testing if applicable
- Extended monitoring period

**Phase 4: Cleanup (2-4 hours)**
- Remove old code/dependencies
- Update all references
- Final test run
- Documentation update

### Stopping Points Between Phases
After each phase, verify:
```
PHASE COMPLETION CHECKLIST:
- [ ] All tests passing (unit + integration)
- [ ] No new warnings/errors in logs
- [ ] Code review completed
- [ ] Performance metrics acceptable
- [ ] Documentation updated
- [ ] Decision point: Proceed to next phase or abort?
```

## 6. Testing Strategies for Migrations

### Unit Testing During Migration
```
UNIT TEST REQUIREMENTS:
- Test old pattern with new code (compatibility)
- Test new pattern in isolation
- Test error paths and edge cases
- Mock external dependencies completely
- Target: Maintain 80%+ coverage on changed code
```

### Integration Testing
```
INTEGRATION TEST REQUIREMENTS:
- Use real database or testcontainers
- Test multiple modules together
- Test at service boundaries
- Test data consistency across changes
- Test backwards compatibility scenarios
```

### Mutation Testing (Verify Test Quality)
```
MUTATION TESTING:
- After unit tests pass, run mutation testing
- Inject artificial bugs into migrated code
- Tests should catch the mutations
- Target: 80%+ mutation score on critical paths
```

### Load Testing (For Performance-Critical Code)
```
LOAD TEST CHECKLIST:
- [ ] Establish baseline performance (pre-migration)
- [ ] Run same load test post-migration
- [ ] Compare results (should be < 10% difference)
- [ ] Identify bottlenecks if performance degraded
- [ ] Verify no memory leaks under sustained load
```

## 7. Common Pitfalls & Mitigation

### Pitfall 1: Incomplete Dependency Updates
**Problem:** Update package but miss transitive dependency conflicts
**Symptom:** Subtle bugs, version conflicts, unexpected behavior
**Mitigation:** 
- Run `npm ls` or `pip show` to see full dependency tree
- Use lock files (package-lock.json, poetry.lock)
- Test with clean install from lock file

### Pitfall 2: Orphaned Code
**Problem:** Old code paths remain after migration
**Symptom:** Maintenance confusion, technical debt, dead code
**Mitigation:**
- Use IDE refactoring tools to track all usages
- Remove old code immediately, don't comment it out
- Use git history if you need to retrieve it later

### Pitfall 3: Breaking Change Introduction
**Problem:** New code breaks existing users/integrations
**Symptom:** Integration failures, error reports from users
**Mitigation:**
- Maintain backwards compatibility during transition
- Deprecate old API gradually (warn before removal)
- Maintain old API surface for at least 1-2 releases

### Pitfall 4: Data Loss or Corruption
**Problem:** Migration doesn't handle all edge cases correctly
**Symptom:** Missing data, incorrect values, inconsistent state
**Mitigation:**
- Backup database before starting
- Run migration on copy first (staging/test environment)
- Validate every row after migration
- Keep old data structure temporarily

### Pitfall 5: Insufficient Testing
**Problem:** Migrations introduce hidden bugs
**Symptom:** Issues appear days/weeks after deployment
**Mitigation:**
- Write tests BEFORE migration starts
- Test edge cases, not just happy path
- Use mutation testing to verify test quality
- Extended monitoring period post-migration

### Pitfall 6: Uncoordinated Rollout
**Problem:** Multiple teams make conflicting changes
**Symptom:** Merge conflicts, integration failures, deployments fail
**Mitigation:**
- Establish clear timeline and communication
- Designate migration owner/coordinator
- Hold daily standups during migration period
- Lock affected files/modules during migration

### Pitfall 7: Documentation Lag
**Problem:** Docs don't reflect actual implementation
**Symptom:** New developers confused, decisions unclear
**Mitigation:**
- Update docs alongside code changes
- Create ADR to document migration decision
- Add comments explaining why old code existed

## 8. Monitoring During & After Migration

### During Migration
```
MONITORING CHECKLIST:
- [ ] Error rate normal (no spike)
- [ ] Response times acceptable
- [ ] Memory usage stable
- [ ] CPU usage normal
- [ ] Database connections healthy
- [ ] Third-party API calls working
- [ ] No unexpected warnings in logs
```

### Post-Migration (48-72 hours)
```
POST-MIGRATION VALIDATION:
- [ ] No increase in error rate
- [ ] No performance degradation
- [ ] No memory leaks detected
- [ ] All integration points working
- [ ] User reports of issues addressed
- [ ] Database consistency verified
- [ ] All tests still passing
```

## 9. Communication & Documentation

### Pre-Migration Communication
- Notify affected teams
- Share timeline and impact assessment
- Explain migration approach and rationale
- Set expectations for downtime (if any)

### Documentation Update
- Update README with new versions/requirements
- Add ADR (Architecture Decision Record) explaining why
- Update installation/setup guide
- Update API documentation (if relevant)
- Add migration guide for developers

### Post-Migration Communication
- Share what changed and why
- Document any new patterns/best practices
- List deprecated features with timeline for removal
- Update CHANGELOG with breaking changes clearly marked

## 10. Complete Migration Template

```markdown
# Migration: [Name]

## Scope
[What is changing]

## Timeline
- [ ] Phase 1: [Module 1] - [Date]
- [ ] Phase 2: [Module 2] - [Date]
- [ ] Phase 3: [Cleanup] - [Date]

## Rollback Procedure
[See section 2.3]

## Test Coverage
- Before: [X% coverage]
- After: [Y% coverage]
- Tests to add: [List]

## Risks
1. [Risk 1] - Likelihood: [High/Med/Low] - Impact: [High/Med/Low]
2. [Risk 2]

## Verification Plan
- [ ] All tests passing
- [ ] Performance baseline met
- [ ] Data consistency verified
- [ ] Integration tests pass
- [ ] Manual smoke tests pass

## Documentation Changes
- [ ] README updated
- [ ] API docs updated
- [ ] CHANGELOG updated
- [ ] ADR created

## Approval
- [ ] Code review
- [ ] Security review
- [ ] Performance review
- [ ] Team sign-off
```

---

**Total Sections: 10 | Estimated Lines: 240 | Complexity: Comprehensive guide**
