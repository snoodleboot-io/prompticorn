# Subagent Minimal/Verbose Variant Audit Report

**Date:** 2026-04-10  
**Total Subagents Audited:** 28  
**Status:** ❌ CRITICAL ISSUE IDENTIFIED

---

## Executive Summary

**96% of subagent variants are IDENTICAL duplicates** (27 out of 28). Only 1 subagent (`code/feature`) has proper differentiation, and even that difference is minimal (only YAML frontmatter differs).

**The minimal/verbose variant system is completely non-functional.**

---

## Detailed Findings

### Status Breakdown

| Status | Count | Percentage |
|--------|-------|------------|
| ❌ IDENTICAL (Complete duplicates) | 27 | 96% |
| ⚠️ METADATA ONLY (Only YAML differs) | 1 | 4% |
| ✅ PROPERLY DIFFERENTIATED | 0 | 0% |

### All 28 Subagents Analyzed

| Agent | Subagent | Status | Minimal Lines | Verbose Lines | Diff |
|-------|----------|--------|---------------|---------------|------|
| architect | data-model | ❌ IDENTICAL | 53 | 53 | 0 |
| architect | scaffold | ❌ IDENTICAL | 30 | 30 | 0 |
| architect | task-breakdown | ❌ IDENTICAL | 48 | 48 | 0 |
| ask | decision-log | ❌ IDENTICAL | 66 | 66 | 0 |
| ask | docs | ❌ IDENTICAL | 64 | 64 | 0 |
| ask | testing | ❌ IDENTICAL | 120 | 120 | 0 |
| code | boilerplate | ❌ IDENTICAL | 34 | 34 | 0 |
| code | dependency-upgrade | ❌ IDENTICAL | 38 | 38 | 0 |
| code | feature | ⚠️ METADATA | 45 | 40 | 15 |
| code | house-style | ❌ IDENTICAL | 36 | 36 | 0 |
| code | migration | ❌ IDENTICAL | 38 | 38 | 0 |
| code | refactor | ❌ IDENTICAL | 39 | 39 | 0 |
| compliance | review | ❌ IDENTICAL | 193 | 193 | 0 |
| debug | log-analysis | ❌ IDENTICAL | 34 | 34 | 0 |
| debug | root-cause | ❌ IDENTICAL | 44 | 44 | 0 |
| debug | rubber-duck | ❌ IDENTICAL | 33 | 33 | 0 |
| document | strategy-for-applications | ❌ IDENTICAL | 137 | 137 | 0 |
| explain | strategy | ❌ IDENTICAL | 122 | 122 | 0 |
| migration | strategy | ❌ IDENTICAL | 128 | 128 | 0 |
| orchestrator | devops | ❌ IDENTICAL | 59 | 59 | 0 |
| orchestrator | meta | ❌ IDENTICAL | 42 | 42 | 0 |
| orchestrator | pr-description | ❌ IDENTICAL | 217 | 217 | 0 |
| refactor | strategy | ❌ IDENTICAL | 117 | 117 | 0 |
| review | accessibility | ❌ IDENTICAL | 91 | 91 | 0 |
| review | code | ❌ IDENTICAL | 317 | 317 | 0 |
| review | performance | ❌ IDENTICAL | 86 | 86 | 0 |
| security | review | ❌ IDENTICAL | 151 | 151 | 0 |
| test | strategy | ❌ IDENTICAL | 120 | 120 | 0 |

---

## The One "Different" Subagent

**code/feature** is the only subagent with ANY difference, but the difference is trivial:

### Difference Analysis

**Only the YAML frontmatter differs:**

```diff
--- minimal/prompt.md
+++ verbose/prompt.md
@@ -1,14 +1,9 @@
 ---
 name: feature
-description: Implement new features following a structured plan-confirm-implement workflow
-tools:
-- read
-skills:
-- feature-planning
-- incremental-implementation
-- post-implementation-checklist
+description: Code - feature
+tools: [read]
 workflows:
-- feature-workflow
+  - feature-workflow
 ---
```

**The actual content (instructions) is IDENTICAL.**

This is not meaningful differentiation — it's just YAML formatting differences.

---

## Impact Assessment

### Why This Is Critical

1. **Storage waste:** Storing duplicate files with no differentiation
2. **Maintenance burden:** Updates must be made to both files identically
3. **Broken promise:** Users selecting "minimal" vs "verbose" get NO difference
4. **Technical debt:** System designed for differentiation but not implemented
5. **Confusion:** Developers maintaining these files face cognitive overhead

### What Should Exist

**Minimal variants should:**
- Strip examples
- Remove verbose explanations
- Keep only essential rules and steps
- Be 40-60% shorter than verbose

**Verbose variants should:**
- Include comprehensive examples
- Provide detailed explanations
- Include edge case guidance
- Show anti-patterns and best practices

### Current Reality

**Both variants are byte-for-byte identical.** There is NO difference in verbosity, examples, or explanations.

---

## Recommendations

### Option 1: Implement Proper Differentiation (HIGH EFFORT)

Rewrite all 28 subagent pairs to have meaningful differences:

**Estimated effort:** 28 subagents × 2 hours each = **56 hours** (1.5 weeks)

**For each subagent:**
1. Keep verbose version as-is (current content)
2. Rewrite minimal version to remove:
   - Examples
   - Detailed explanations
   - Extended guidance
   - Anti-pattern lists
3. Test both variants to ensure they work correctly

**Pros:**
- Honors original design intent
- Provides user choice
- Meaningful differentiation

**Cons:**
- Significant effort
- Ongoing maintenance burden (2× the files)
- Risk of variants diverging over time

---

### Option 2: Eliminate Variants (LOW EFFORT) ⭐ RECOMMENDED

Remove the minimal/verbose distinction entirely:

**Estimated effort:** 28 subagents × 15 minutes = **7 hours** (1 day)

**Steps:**
1. Delete all `/minimal/` directories
2. Rename `/verbose/` → `/` (make it the only version)
3. Update any references in code/config
4. Document that verbosity is controlled via agent-level settings, not subagent-level

**Pros:**
- Eliminates duplicate maintenance
- Reduces storage
- Simplifies system
- No loss of functionality (they're identical anyway)

**Cons:**
- Removes user choice (though choice is currently illusory)
- Requires updating references

---

### Option 3: Single Source with Templates (MEDIUM EFFORT)

Use a single source file with conditional sections:

**Estimated effort:** 28 subagents × 1 hour = **28 hours** (1 week)

**Approach:**
```markdown
---
name: data-model
variants:
  minimal:
    include_examples: false
    include_antipatterns: false
  verbose:
    include_examples: true
    include_antipatterns: true
---

# Content here with conditional blocks

{{#if verbose}}
## Examples
[verbose examples]
{{/if}}
```

Build minimal/verbose at runtime from template.

**Pros:**
- Single source of truth
- Automatic consistency
- User choice preserved

**Cons:**
- Requires templating system
- More complex build process
- Migration effort

---

## Conclusion

The current minimal/verbose variant system is **non-functional**. 96% of subagents are exact duplicates, and the one "different" subagent only differs in YAML formatting.

**Recommended action:** Option 2 (Eliminate Variants)

This is the simplest, fastest solution that eliminates waste and maintenance burden while losing no actual functionality (since the variants are currently identical anyway).

If differentiation is desired in the future, it can be implemented properly with a clear plan rather than maintaining 28 pairs of identical files.

---

## Next Steps

1. **Decide:** Choose Option 1, 2, or 3
2. **Plan:** Create implementation plan for chosen option
3. **Execute:** Implement changes across all 28 subagents
4. **Validate:** Test that subagent loading still works correctly
5. **Document:** Update documentation to reflect new approach

---

## Appendix: Complete File Comparison Data

### Sample Verified Duplicates

The following were manually inspected and confirmed as byte-for-byte identical:

- **architect/data-model**: 53 lines × 2 = 106 total (0 diff)
- **code/boilerplate**: 34 lines × 2 = 68 total (0 diff)
- **review/code**: 317 lines × 2 = 634 total (0 diff)
- **test/strategy**: 120 lines × 2 = 240 total (0 diff)

All other subagents follow the same pattern: complete duplication.
