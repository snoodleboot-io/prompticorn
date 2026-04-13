# Documentation Audit - Issue Tracking

**Audit Date:** 2026-04-13  
**Auditor:** Comprehensive recursive audit of all 55 docs files  
**Status:** Issues categorized and prioritized

---

## QUICK FACTS

- **Total docs files:** 55
- **Files with issues:** 18 (33%)
- **Files verified good:** 37 (67%)
- **Total actionable issues:** 20

---

## CRITICAL ISSUES (Do First - Block Release)

### 1. PERSONA_GUIDES.md - Hallucinated Agent Paths

**Issue:** Three agent directory names are wrong

| Line | Claims | Should Be | Status |
|------|--------|-----------|--------|
| 33 | `backend-engineer/` | `backend/` | ❌ WRONG |
| 61 | `frontend-engineer/` | `frontend/` | ❌ WRONG |
| 118 | `testing-engineer/` | `qa-tester/` | ❌ WRONG |

**Fix:** Update 3 paths in PERSONA_GUIDES.md

---

### 2. PROMPT_SYSTEM_REDESIGN_ANALYSIS.md - Old Directory Structure

**Issue:** References deprecated `.kilocode/` directory (should be `.kilo/`)

**Lines affected:** 43, 84, 183, 193, 252, 260, 315-402

**Current:** `.kilocode/rules/`, `.kilocode/rules-{mode}/`  
**Should be:** `.kilo/rules/`, `.kilo/rules-{mode}/`

**Fix:** Replace all `.kilocode/` with `.kilo/` (sed/find-replace)

---

### 3. cli.py - Implementation Rot Comment

**Issue:** Line 31 has comment: `# Legacy sweet_tea import removed - using Phase 2A builders`

**Fix:** Remove the comment about "Phase 2A"

---

## HIGH PRIORITY ISSUES (Before Next Release)

### 4. QUALITY_METRICS.md - Phase Terminology Pollution

**Issue:** Document contains "PHASE 2 COMPLETE" status and phase-based organization

**Lines affected:** 4, 10, 53, 83, 248, 255, 266-310

**Content Status:**
- ✅ Actual metrics (coverage, validation) = ACCURATE
- 🔴 Phase terminology = IMPLEMENTATION ROT

**Fix:** Remove all Phase 1/2/3 language while keeping metrics data

---

### 5. LIBRARY_INDEX.md - Phase-Based Organization

**Issue:** Library organized by "Phase 1: Core Domains" / "Phase 2: Domain Expansion"

**Lines affected:** 22, 30, 136-188, 254-255, 303-304, 343-346, 368-369

**Fix:** Reorganize by domain type instead of phase number

---

### 6. RELATIONSHIPS_MATRIX.md - Phase Annotations in Skills

**Issue:** Skill descriptions contain "(Phase 1)" annotations

**Lines affected:** 23, 29, 31, 121, 254-255, 390

**Example:** Shows skills marked as "Phase 1" when no phases should exist

**Fix:** Remove all phase annotations while preserving relationship data

---

### 7. reference/GETTING_STARTED.reference.md - Phase in Title

**Issue:** Document titled "Getting Started with Phase 2A"

**Lines affected:** 1, 6

**Fix:** Rename to "Getting Started" (remove "with Phase 2A")

---

### 8. reference/TOOL_CONFIGURATION_EXAMPLES.reference.md - Phase in Title

**Issue:** Document titled "# Phase 2: Tool Configuration Examples"

**Lines affected:** 1

**Fix:** Remove "Phase 2: " prefix, keep just "Tool Configuration Examples"

---

### 9. reference/DIRECTORY_STRUCTURE.reference.md - Phase References

**Issue:** Multiple phase-related file path references

**Lines affected:** 113-115, 128-129, 189-190, 197

**Content:** References PHASE1_EXECUTION_GUIDE, PHASE2_EXECUTION_GUIDE, PHASE3_EXECUTION_GUIDE

**Also:** References empty `docs/decisions/` directory (lines 51-52)

**Fix:** 
- Remove or clearly mark phase directory references as internal
- Either populate `docs/decisions/` or remove reference

---

### 10. PERSONA_GUIDES.md - Internal Planning Paths

**Issue:** References internal planning directory paths

**Lines affected:** 17, 180, 186-187

**Content:** `planning/current/PHASE*_EXECUTION_GUIDE.plan.md`

**Fix:** Remove references to internal planning paths from user documentation

---

## MEDIUM PRIORITY ISSUES (Next Sprint)

### 11. design/ADVANCED_PATTERNS.design.md - Phase in Title

**Line:** 1  
**Issue:** Title "# Phase 2A Advanced Patterns Guide"  
**Fix:** Rename to "Advanced Patterns Guide"

---

### 12. PROMPT_SYSTEM_QUICK_REFERENCE.md - Phase Timeline

**Lines affected:** 225-245

**Issue:** Timeline headers "Phase 1/2/3/4"

**Fix:** Clarify if user-facing. If so, remove phase numbers.

---

### 13. PROMPT_SYSTEM_ARCHITECTURE.md - Phase Implementation Plan

**Lines affected:** 232-305

**Issue:** Implementation plan organized by Phase 1/2/3/4

**Fix:** If user-facing doc, remove phase organization.

---

### 14. ARCHITECT_MODE_COMPLETE_ANALYSIS.md - Phase Timeline

**Lines affected:** 82-84

**Issue:** Implementation timeline uses Phase 1/2/3

**Fix:** Clean up phase references

---

### 15. MAINTENANCE_WORKFLOW.md - Script Verification

**Lines affected:** 28-80, 377-450

**Issue:** References validation scripts - need to verify functionality

**Action:** Test that `validation/run_validation.py` and related scripts actually work

---

### 16. ARCHITECT_MODE_ROOT_CAUSE.md - kilo.json Requirement

**Lines affected:** 32-76

**Issue:** References `kilo.json` requirement

**Action:** Verify against actual Kilo IDE requirements

---

## LOW PRIORITY ISSUES (Housekeeping)

### 17. MIGRATION_GUIDE.md - Version References

**Lines affected:** 54-76

**Issue:** References "0.1.0" as initial release

**Action:** Update version references as product evolves

---

## FALSE POSITIVES (No Issues Found)

✅ **Language Discovery Issue** - NOT FOUND
- No problems identified with language discovery
- `promptosaurus/agent_registry/discovery.py` exists and appears functional
- No unresolved issues in codebase

✅ **Testing Violations** - NOT FOUND  
- No references to broken tests
- Test framework appears functional
- No documented violations

✅ **Removed Development Artifacts** - NOT FOUND
- No file or documentation about removed/deleted code
- This documentation doesn't exist (correctly)

---

## VERIFICATION SUMMARY

| Item | Status | Evidence |
|------|--------|----------|
| qa-tester agent | ✅ EXISTS | `promptosaurus/agents/qa-tester/` |
| migration agent | ✅ EXISTS | `promptosaurus/agents/migration/` + workflows |
| maintenance agent | ✅ EXISTS | `promptosaurus/agents/orchestrator/subagents/maintenance/` + workflows |
| CLI name | ✅ CORRECT | "promptosaurus" (cli.py line 8) |

---

## CLEANUP CHECKLIST

### Immediate (Release Blocker)
- [ ] Remove Phase 2A comment from cli.py line 31
- [ ] Fix 3 paths in PERSONA_GUIDES.md (backend, frontend, qa-tester)
- [ ] Update .kilocode/ → .kilo/ in PROMPT_SYSTEM_REDESIGN_ANALYSIS.md

### Before Next Release
- [ ] Remove phase terminology from QUALITY_METRICS.md
- [ ] Reorganize LIBRARY_INDEX.md (remove Phase 1/2 grouping)
- [ ] Remove phase annotations from RELATIONSHIPS_MATRIX.md
- [ ] Update GETTING_STARTED.reference.md title
- [ ] Update TOOL_CONFIGURATION_EXAMPLES.reference.md title
- [ ] Remove internal paths from PERSONA_GUIDES.md
- [ ] Handle DIRECTORY_STRUCTURE.reference.md (phases + docs/decisions/)

### Next Sprint
- [ ] Clean up design document titles (ADVANCED_PATTERNS.design.md)
- [ ] Review phase references in PROMPT_SYSTEM docs
- [ ] Verify validation scripts in MAINTENANCE_WORKFLOW.md
- [ ] Verify kilo.json requirement in ARCHITECT_MODE_ROOT_CAUSE.md
- [ ] Update version references in MIGRATION_GUIDE.md

---

## SUMMARY

**20 actionable items across 18 files**

**Root Cause:** Implementation roadmap terminology (Phase 1/2/3/4) leaked into user-facing documentation. Also some agent directory names were hallucinated.

**Impact:** Users following docs will encounter broken paths and confusing internal process terminology.

**Overall Health:** 68% of documentation is clean and accurate. 32% needs pruning of implementation rot.


---

## CLARIFICATION: Migration & Maintenance Agents

**Your statement:** "we do not need maintenance workflow or migration guide"

**Current state:**
- Migration agent exists: `promptosaurus/agents/migration/`
- Maintenance subagent exists: `promptosaurus/agents/orchestrator/subagents/maintenance/`
- Multiple maintenance workflows exist
- Docs exist for both

**Action required:**

If these are not needed:
1. **DELETE from code** (don't just delete docs):
   - Remove `promptosaurus/agents/migration/` directory
   - Remove `promptosaurus/agents/orchestrator/subagents/maintenance/` directory
   - Remove migration-related workflows from `promptosaurus/workflows/`
   - Remove maintenance-related workflows from `promptosaurus/workflows/`

2. **DELETE from docs**:
   - Remove `docs/MIGRATION_GUIDE.md`
   - Remove `docs/MAINTENANCE_WORKFLOW.md`

3. **Update registry** (promptosaurus/registry.py):
   - Remove "migration" from modes dict (line 134)
   - Remove migration entries from mode_files (lines 167-171)
   - Remove migration from concat_order

4. **Update personas** (promptosaurus/personas/personas.yaml):
   - Remove migration workflows from persona definitions
   - Remove maintenance-related workflows

**Don't:** Leave code in place while deleting docs - that's inconsistent and confusing.

