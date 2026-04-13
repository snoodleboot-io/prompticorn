---
name: migration-workflow
languages: [all]
subagents: [migration/dependency-upgrade, migration/framework, test/integration]
version: "1.0"
---

# Migration Workflow (Minimal)

## Step 1: Plan Migration

- Identify current version and target version with all breaking changes
- Document dependencies and systems affected by the migration
- Create rollback plan with specific commands and verification steps
- Estimate timeline with buffer for unexpected issues

## Step 2: Create Test Plan

- List all critical user flows that must work post-migration
- Create test scripts for each flow before starting migration
- Set up monitoring to compare metrics before/after migration
- Document acceptance criteria with measurable thresholds

## Step 3: Execute Migration in Stages

- Create feature branch and run migration on isolated environment first
- Migrate development environment, run full test suite, verify functionality
- Deploy to staging with gradual traffic increase (10% → 50% → 100%)
- Monitor error rates, performance metrics, and user reports at each stage

## Step 4: Verify No Regressions

- Run automated test suite and compare results to baseline
- Execute manual smoke tests on all critical features
- Check performance benchmarks against pre-migration baseline
- Review error logs for new exceptions or failures

## Step 5: Document Changes

- Update dependency versions in package.json/requirements.txt/go.mod
- Add migration notes to CHANGELOG.md with breaking changes highlighted
- Update documentation to reflect new API usage patterns
- Create internal wiki entry with migration steps for team reference

## Step 6: Communicate to Team

- Send migration summary email with what changed and why
- Hold team sync to answer questions and share lessons learned
- Update runbooks with new commands, configurations, or procedures
- Post announcement in team chat with link to documentation
