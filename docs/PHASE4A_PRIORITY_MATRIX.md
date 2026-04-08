# Phase 4A: Refactoring Priority Matrix & Execution Roadmap

## Matrix Overview

This document ranks all 65 templates by refactoring opportunity and provides a clear execution roadmap.

---

## Priority Matrix (Heat Map)

```
IMPACT
  ^
  |
  | 🔴 🔴 🔴 🔴
  | CRITICAL (1-4 templates)
  |
  | 🟠 🟠 🟠 🟠 🟠
  | HIGH (5-15 templates)
  |
  | 🟡 🟡 🟡 🟡
  | MEDIUM (16-25 templates)
  |
  | 🟢 🟢
  | LOW (26-40 templates)
  |
  +----------------> EFFORT
  QUICK            COMPLEX
```

---

## Tier 1: CRITICAL Priority (4 templates)

**Rationale:** These 4 templates represent 80% of refactoring opportunity with manageable effort.

### 1.1 core-conventions-python.md
- **Size:** 417 lines
- **Effort:** 3-4 hours
- **Impact Score:** 95/100
- **Reduction Potential:** 150-200 lines (36-48%)
- **Dependencies:** None
- **Jinja2 Features:** Macros (3), extends (1), for loop (2), if conditions (1)
- **Benefits:**
  - Largest single template (unblocks language conventions)
  - Multiple macro candidates
  - Serves as template for refactoring other languages
- **Recommended Action:** **START HERE** - Complete by end of Week 1

### 1.2 core-conventions (base)
- **Size:** 153 lines
- **Effort:** 2-3 hours
- **Impact Score:** 90/100
- **Reduction Potential:** 50-80 lines (33-52%)
- **Dependencies:** After 1.1 (to avoid moving target)
- **Jinja2 Features:** Extends (1), blocks (5+), includes (3)
- **Benefits:**
  - Enables inheritance for all 29 language files
  - Centralizes common sections
  - Critical for template inheritance strategy
- **Recommended Action:** **PRIORITY 2** - Complete by mid-Week 1

### 1.3 All 29 language convention files (grouped)
- **Size:** ~2,000 lines combined
- **Effort:** 12-16 hours
- **Impact Score:** 92/100
- **Reduction Potential:** 800-1,200 lines (40-60%)
- **Dependencies:** 1.2 (base template) completed first
- **Jinja2 Features:** Extends (29), blocks (5+ each), includes (3 each)
- **Benefits:**
  - Single macro update affects all 29 files
  - Consistent structure across all languages
  - Massive maintenance improvement
- **Recommended Action:** **PRIORITY 3** - Phased rollout Weeks 2-3
- **Execution Strategy:**
  - Week 2a: Process 10 small files (75-90 lines each)
  - Week 2b: Process 10 medium files (100-120 lines each)
  - Week 3a: Process 9 large files (110-150 lines each)

### 1.4 review-code.md
- **Size:** 309 lines
- **Effort:** 2-3 hours
- **Impact Score:** 75/100
- **Reduction Potential:** 80-120 lines (26-39%)
- **Dependencies:** None
- **Jinja2 Features:** Macros (2), for loops (2), if conditions (1)
- **Benefits:**
  - Large template with clear patterns
  - Checklist repetition is eliminable
  - Code examples can be templated
- **Recommended Action:** **PRIORITY 4** - Week 1-2

---

## Tier 2: HIGH Priority (8 templates)

**Rationale:** These templates have good refactoring opportunities with 1-3 hours effort each.

### 2.1 orchestrator-pr-description.md
- **Size:** 211 lines
- **Effort:** 1-2 hours
- **Impact:** 60-80 lines saved (28-38%)
- **Opportunity:** Repeated PR example sections
- **Jinja2 Features:** Macros (2), for loop (1)
- **Timeline:** Week 2

### 2.2 compliance-review.md
- **Size:** 185 lines
- **Effort:** 1-2 hours
- **Impact:** 50-70 lines saved (27-38%)
- **Opportunity:** Compliance checklist patterns
- **Jinja2 Features:** Macros (1), for loops (2)
- **Timeline:** Week 2

### 2.3 security-review.md
- **Size:** 143 lines
- **Effort:** 1-2 hours
- **Impact:** 40-60 lines saved (28-42%)
- **Opportunity:** Checklist consolidation
- **Jinja2 Features:** Macros (1), for loops (1)
- **Timeline:** Week 2

### 2.4 document-strategy-for-applications.md
- **Size:** 129 lines
- **Effort:** 1-2 hours
- **Impact:** 35-50 lines saved (27-39%)
- **Opportunity:** Documentation section patterns
- **Jinja2 Features:** Macros (1), includes (1)
- **Timeline:** Week 2

### 2.5 migration-strategy.md
- **Size:** 120 lines
- **Effort:** 1-2 hours
- **Impact:** 30-45 lines saved (25-38%)
- **Opportunity:** Step-by-step pattern consolidation
- **Jinja2 Features:** Macros (1), for loop (1)
- **Timeline:** Week 3

### 2.6 test-strategy.md
- **Size:** 108 lines
- **Effort:** 1-2 hours
- **Impact:** 30-45 lines saved (28-42%)
- **Opportunity:** Test type description patterns, overlap with ask-testing.md
- **Jinja2 Features:** Macros (1), includes (1)
- **Timeline:** Week 3

### 2.7 ask-testing.md
- **Size:** 112 lines
- **Effort:** 1-2 hours
- **Impact:** 35-50 lines saved (31-45%)
- **Opportunity:** Shared testing patterns with test-strategy.md (consolidate)
- **Jinja2 Features:** Macros (1), includes (1)
- **Timeline:** Week 3

### 2.8 explain-strategy.md
- **Size:** 114 lines
- **Effort:** 1-2 hours
- **Impact:** 30-40 lines saved (26-35%)
- **Opportunity:** Query/response pattern consolidation
- **Jinja2 Features:** Macros (1), if conditions (1)
- **Timeline:** Week 3

---

## Tier 3: MEDIUM Priority (12 templates)

**Rationale:** Good opportunities but slightly lower impact or more complexity.

### 3.1 refactor-strategy.md
- **Size:** 108 lines
- **Effort:** 1-2 hours
- **Impact:** 25-35 lines saved (23-32%)
- **Timeline:** Week 4

### 3.2 review-performance.md
- **Size:** 77 lines
- **Effort:** 1 hour
- **Impact:** 20-30 lines saved (26-39%)
- **Timeline:** Week 3

### 3.3 review-accessibility.md
- **Size:** 82 lines
- **Effort:** 1 hour
- **Impact:** 22-32 lines saved (27-39%)
- **Timeline:** Week 3

### 3.4 ask-docs.md
- **Size:** 55 lines
- **Effort:** 45 minutes
- **Impact:** 15-25 lines saved (27-45%)
- **Timeline:** Week 4

### 3.5 architect-task-breakdown.md
- **Size:** 40 lines
- **Effort:** 1 hour
- **Impact:** 10-15 lines saved (25-38%)
- **Timeline:** Week 4

### 3.6 architect-data-model.md
- **Size:** 41 lines
- **Effort:** 1 hour
- **Impact:** 10-15 lines saved (24-37%)
- **Timeline:** Week 4

### 3.7 architect-scaffold.md
- **Size:** 45 lines
- **Effort:** 1 hour
- **Impact:** 12-18 lines saved (27-40%)
- **Timeline:** Week 4

### 3.8 ask-decision-log.md
- **Size:** 57 lines
- **Effort:** 1 hour
- **Impact:** 15-20 lines saved (26-35%)
- **Timeline:** Week 4

### 3.9 code-boilerplate.md
- **Size:** 35 lines
- **Effort:** 45 minutes
- **Impact:** 8-12 lines saved (23-34%)
- **Timeline:** Week 4

### 3.10 code-house-style.md
- **Size:** 23 lines
- **Effort:** 30 minutes
- **Impact:** 5-8 lines saved (22-35%)
- **Timeline:** Week 4

### 3.11 code-feature.md
- **Size:** 30 lines
- **Effort:** 30 minutes
- **Impact:** 5-10 lines saved (17-33%)
- **Timeline:** Week 4

### 3.12 core-decision-log-template.md
- **Size:** ~150 lines (complex)
- **Effort:** 1-2 hours
- **Impact:** 30-50 lines saved (20-33%)
- **Timeline:** Week 4

---

## Tier 4: LOW Priority (10+ templates)

**Rationale:** Minimal refactoring opportunities or complex structures not yet worth optimizing.

### 4.1 code-refactor.md (34 lines)
- **Impact:** 5-8 lines saved (15-24%)
- **Timeline:** Later phases

### 4.2 code-migration.md (31 lines)
- **Impact:** 5-7 lines saved (16-23%)
- **Timeline:** Later phases

### 4.3 code-dependency-upgrade.md (27 lines)
- **Impact:** 3-5 lines saved (11-19%)
- **Timeline:** Later phases

### 4.4 debug-root-cause.md (35 lines)
- **Impact:** 5-8 lines saved (14-23%)
- **Timeline:** Later phases

### 4.5 debug-rubber-duck.md (20 lines)
- **Impact:** 2-3 lines saved (10-15%)
- **Timeline:** Later phases

### 4.6 debug-log-analysis.md (27 lines)
- **Impact:** 3-5 lines saved (11-19%)
- **Timeline:** Later phases

### 4.7 orchestrator-meta.md (34 lines)
- **Impact:** 5-8 lines saved (15-24%)
- **Timeline:** Later phases

### 4.8 orchestrator-devops.md (52 lines)
- **Impact:** 10-15 lines saved (19-29%)
- **Timeline:** Later phases

### 4.9 core-session-troubleshooting.md (~200 lines)
- **Impact:** 20-30 lines saved (10-15%)
- **Timeline:** Later phases

### 4.10 core-system.md (~200 lines)
- **Impact:** 15-25 lines saved (8-13%)
- **Timeline:** Later phases

### 4.11-4.40+ Other small templates
- **Combined:** <100 lines of refactoring potential
- **Timeline:** Post-Phase 4A

---

## Weekly Execution Schedule

### Week 1: Foundation & Quick Wins

**Goal:** Set up macro library and refactor critical templates

**Monday-Tuesday (4 hours):**
- Create `_macros/` directory structure
- Implement `testing_sections.jinja2` macro
- Implement `coverage_targets.jinja2` macro
- Implement `naming_conventions.jinja2` macro
- Write unit tests for macros

**Wednesday (3 hours):**
- Refactor `core-conventions.md` to base template
- Create `_base/conventions-base.jinja2`
- Implement template blocks

**Thursday (4 hours):**
- Start `core-conventions-python.md` refactoring
- Test macro integration
- Validate output against original

**Friday (3 hours):**
- Complete `core-conventions-python.md`
- Write refactoring guide
- Commit Week 1 work

**Week 1 Total:** 14 hours  
**Estimated Lines Saved:** 200-300

---

### Week 2: Language Conventions Cascade

**Goal:** Refactor 20 language convention files using base template

**Monday-Tuesday (8 hours):**
- Refactor 10 small language files (75-90 lines each)
- Validate each against original
- Test inheritance chains

**Wednesday-Thursday (8 hours):**
- Refactor 10 medium language files (100-120 lines each)
- Batch testing for consistency
- Fix any macro issues

**Friday (4 hours):**
- Complete any remaining language files
- Commit Week 2 work
- Generate metrics

**Week 2 Total:** 20 hours  
**Estimated Lines Saved:** 400-600

---

### Week 3: High-Priority Subagents

**Goal:** Refactor 8 high-priority subagent templates

**Monday-Tuesday (6 hours):**
- Refactor `review-code.md`
- Refactor `orchestrator-pr-description.md`
- Create subagent-specific macros

**Wednesday (4 hours):**
- Refactor `compliance-review.md`
- Refactor `security-review.md`
- Create checklist macros

**Thursday (4 hours):**
- Refactor `document-strategy-for-applications.md`
- Refactor `migration-strategy.md`
- Test all macros together

**Friday (2 hours):**
- Complete remaining High-priority templates
- Commit Week 3 work

**Week 3 Total:** 16 hours  
**Estimated Lines Saved:** 300-500

---

### Week 4: Polish & Medium-Priority

**Goal:** Complete Phase 4A with comprehensive testing

**Monday-Tuesday (6 hours):**
- Refactor remaining Medium-priority templates (12 files)
- Create comprehensive test suite
- Validate all Jinja2 features

**Wednesday-Thursday (4 hours):**
- Final validation and testing
- Performance benchmarking
- Documentation review

**Friday (2 hours):**
- Final commit and metrics report
- Create Phase 4A completion summary

**Week 4 Total:** 12 hours  
**Estimated Lines Saved:** 100-200

---

## Total Phase 4A Effort & Outcomes

| Metric | Estimate |
|--------|----------|
| **Total Effort** | 62 hours over 4 weeks |
| **Files Refactored** | 40-45 templates |
| **Lines Eliminated** | 1,000-1,600 lines (25-40% total) |
| **Macros Created** | 8-10 macros |
| **Base Templates** | 2-3 base templates |
| **Tests Added** | 30-40 unit tests |
| **Quality Gates** | 100% validation |

---

## Critical Dependencies & Risk Mitigation

### Dependency Chain

```
Week 1: Macros → Base Template
           ↓
Week 2: Language Conventions (all 29 files)
           ↓
Week 3: High-Priority Subagents
           ↓
Week 4: Testing & Validation
```

### Risk Mitigation Strategies

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Macro breaking changes | HIGH | Version macros, extensive unit tests |
| Output formatting changes | HIGH | Diff validation, side-by-side comparison |
| Template variable resolution | MEDIUM | Integration tests with full config |
| Whitespace sensitivity | MEDIUM | Jinja2 whitespace control testing |
| Circular inheritance | MEDIUM | Depth limiting, cycle detection |

---

## Success Criteria Checklist

- [ ] All 40-45 refactored templates produce identical output
- [ ] Macros have ≥95% test coverage
- [ ] No linting errors (ruff validation)
- [ ] No type errors (pyright validation)
- [ ] Template rendering <500ms
- [ ] 25-40% code reduction achieved
- [ ] Documentation complete
- [ ] Team review passed

---

## Monitoring & Metrics

### Weekly Metrics Collection

**Lines Saved:**
```
Week 1: +200-300 lines saved
Week 2: +400-600 lines saved
Week 3: +300-500 lines saved
Week 4: +100-200 lines saved
TOTAL: 1,000-1,600 lines saved (25-40%)
```

**Quality Metrics:**
```
Jinja2 Syntax Errors: 0
Output Diffs: 0
Test Coverage: ≥95%
Code Quality: ✓ (ruff + pyright)
```

---

## Phase 4B Planning (After Phase 4A)

Once Phase 4A is complete, Phase 4B will focus on:

1. **Custom Filters Implementation** (from Phase 3 Wave 3)
   - Apply to code examples and naming conventions
   - Create `kebab_case`, `snake_case`, `pascal_case` filters

2. **Advanced Template Composition**
   - Multi-level inheritance chains
   - Template dependency graphs

3. **Dynamic Configuration**
   - Loop-based field generation
   - Conditional content blocks

4. **Performance Optimization**
   - Template caching strategies
   - Build time optimization

---

## Document Metadata

- **Created:** 2026-04-08T12:42:16Z
- **Phase:** Phase 4A - Refactoring Priority & Roadmap
- **Status:** READY FOR EXECUTION
- **Next Step:** Begin Week 1 implementation
- **Expected Completion:** 2026-04-29
