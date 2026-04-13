---
name: "schema-migration"
description: "Safely evolve database schema without downtime"
version: "1.0"
languages: ["sql"]
subagents: ["data/pipeline", "orchestrator"]
---

# Schema Migration Workflow (Minimal)

## Purpose
Safely evolve database schemas with zero downtime, backward compatibility, and rollback capability.

## Steps

### 1. Plan the Change
- Document current schema and constraints
- Design new schema changes (add/remove/modify columns)
- Identify affected tables, indexes, views, procedures
- Assess impact: Which queries/applications need updates?
- Estimate data volume and migration time

### 2. Ensure Backward Compatibility
- Make changes additive: Add new columns before removing old ones
- Keep old column during dual-write period (2-4 weeks)
- Don't change column types without careful migration
- Maintain indexes on frequently queried columns

### 3. Pre-Migration Validation
- Backup current database
- Validate migration script on staging environment
- Test rollback procedure
- Performance test on production-like data
- Review with ops team

### 4. Execute Migration (Zero Downtime)
- Deploy application code first (with backward compat)
- Run migration during low-traffic window
- Add new tables/columns without locking
- Create indexes online (non-blocking)
- Update statistics/query optimizer

### 5. Dual Write / Dual Read Period
- Application writes to both old and new columns
- Application reads from new column with fallback to old
- Validate data consistency between old/new
- Monitor performance impact
- Duration: 2-4 weeks (verify data integrity)

### 6. Deprecation Phase
- Stop writing to old column
- Continue reading from old for safety
- Run parallel reads for 1-2 weeks
- Verify no queries still depend on old column

### 7. Cleanup & Rollback
- Remove old column (once confident new column works)
- Drop old indexes
- Update schema documentation
- Commit final migration to version control
- Document lessons learned

## Key Principles

- **Zero downtime:** Use online migration tools
- **Backward compatible:** Old code works with new schema
- **Reversible:** Can rollback if issues discovered
- **Validated:** Test thoroughly before production
- **Monitored:** Watch for performance regressions
