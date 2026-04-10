<!-- path: promptosaurus/.kilocode/rules-migration/workflow-minimal.md -->
# Migration Workflow - Minimal Version

**Metadata:**
- languages: [all]
- subagents: [migration/dependency-upgrade, migration/strategy]
- estimated_time: 2-8 hours
- complexity: medium

## Migration Checklist (Quick Reference)

### 1. Plan & Scope (30 min)
- [ ] Identify what's changing (framework, database, architecture, dependency)
- [ ] List all affected files/modules
- [ ] Check for incompatibilities with current constraints
- [ ] Create rollback procedure

### 2. Create Test Plan (15 min)
- [ ] Document current behavior baseline
- [ ] Write tests that must pass after migration
- [ ] Identify edge cases to verify
- [ ] Plan verification steps

### 3. Execute Migration (2-6 hours)
- [ ] Do incremental changes (one module at a time)
- [ ] Update tests alongside code
- [ ] Maintain backwards compatibility if feasible
- [ ] Run tests after each phase

### 4. Verify & Validate (1 hour)
- [ ] All tests passing (unit + integration)
- [ ] No orphaned code from old pattern
- [ ] Performance baseline met
- [ ] Staging environment validation

### 5. Document & Communicate (30 min)
- [ ] Update relevant docs
- [ ] Record decision in ADR
- [ ] Notify team of changes
- [ ] Update CHANGELOG

## Common Migration Types

**Dependency Upgrade:** Framework, library, or package version
**Database Migration:** Schema changes, new ORM, query pattern updates
**Architecture:** State management, API pattern, caching layer changes
**Refactor:** Code pattern updates while preserving behavior

## Abort Criteria

Stop and rollback if:
- Critical test failures unresolved
- Performance degradation > 10%
- Data inconsistency detected
- Breaking changes to public API

---

**Total Steps: 5 | Estimated Lines: 28 | Complexity: Quick checklist**
