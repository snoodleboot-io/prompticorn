# Phase 4A: Template Audit and Refactoring Strategy

## Executive Summary

**Audit Date:** 2026-04-08  
**Total Files Analyzed:** 65 template files  
**Refactoring Opportunity Score:** HIGH  
**Estimated Code Reduction:** 25-40% through Jinja2 features  

This audit identifies which of the 65 prompt template files would benefit most from Jinja2 advanced features (macros, template inheritance, loops, filters). The goal is to reduce repetition, improve maintainability, and enable dynamic content generation.

---

## Key Findings

### 1. Repetition Patterns

**Critical Finding:** Core conventions files are 80-90% repeated content with language-specific variations:

- **Naming Conventions:** Present in 30/30 files (100%) - **MACRO CANDIDATE**
- **Testing:** Present in 29/30 files (100%) - **MACRO CANDIDATE**
- **Error Handling:** Present in 26/30 files (87%) - **MACRO CANDIDATE**
- **Code Style:** Present in 19/30 files (63%) - **MACRO CANDIDATE**
- **Type System:** Present in 16/30 files (53%) - **MACRO CANDIDATE**

### 2. Template Variable Usage

- **Total config variables:** 212 references across all templates
- **Most common config fields:**
  - `config.testing_framework` (27 uses)
  - `config.coverage_tool` (27 uses)
  - `config.language` (25 uses)
  - `config.linter` (24 uses)
  - `config.formatter` (23 uses)

### 3. Code Examples

- **Code blocks:** 70+ examples across language convention files
- **Languages:** bash (16), yaml (11), python (9), and others
- **Total lines of code:** 542 lines of examples
- **Opportunity:** Many examples follow same pattern (install, run, configure)

### 4. File Size Analysis

**Largest Templates (candidates for refactoring):**

1. `agents/core/core-conventions-python.md` (417 lines)
2. `agents/review/subagents/review-code.md` (309 lines)
3. `agents/orchestrator/subagents/orchestrator-pr-description.md` (211 lines)
4. `agents/compliance/subagents/compliance-review.md` (185 lines)
5. `agents/core/core-conventions.md` (153 lines)

---

## Template Audit Matrix

### A. Core Conventions Files (30 files)

**Category:** Language-specific coding standards

**Repetition Score:** ⚠️⚠️⚠️ VERY HIGH

| Template | Lines | Config Vars | Refactor Score | Top Opportunity |
|----------|-------|-------------|-----------------|-----------------|
| core-conventions-python.md | 417 | 5 | **CRITICAL** | Testing sections (3 variants) |
| core-conventions-typescript.md | 128 | 5 | **HIGH** | Testing sections (5 variants) |
| core-conventions-java.md | 114 | 9 | **HIGH** | Testing sections (4 variants) |
| core-conventions-golang.md | 126 | 8 | **HIGH** | Testing sections (3 variants) |
| core-conventions-sql.md | 132 | 6 | **HIGH** | Coverage target lists |
| core-conventions-terraform.md | 114 | 5 | **HIGH** | Testing sections |
| core-conventions-rust.md | 110 | 4 | **MEDIUM** | Error handling examples |
| core-conventions-csharp.md | 90 | 5 | **MEDIUM** | Testing sections |
| core-conventions-kotlin.md | 87 | 4 | **MEDIUM** | Testing sections |
| core-conventions-javascript.md | 87 | 4 | **MEDIUM** | Testing sections |
| core-conventions-cpp.md | 86 | 3 | **MEDIUM** | Code examples |
| core-conventions-swift.md | 83 | 3 | **MEDIUM** | Testing sections |
| core-conventions-scala.md | 89 | 3 | **MEDIUM** | Testing sections |
| core-conventions-elixir.md | 99 | 4 | **MEDIUM** | Testing sections |
| core-conventions-ruby.md | 78 | 3 | **MEDIUM** | Error handling |
| core-conventions-php.md | 76 | 3 | **MEDIUM** | Testing sections |
| core-conventions.md | 153 | 0 | **MEDIUM** | Structure definition |
| (Other 13 language files) | ~1,100 | ~48 | **MEDIUM** | Various |

**Subtotal for Language Conventions: ~2,600 lines, 30 files**

---

### B. Subagent Templates (28 files)

**Category:** Agent-specific behavior and guidelines

**Repetition Score:** ⚠️ MODERATE

| Template | Lines | Type | Refactor Score | Opportunity |
|----------|-------|------|-----------------|-------------|
| review-code.md | 309 | Code Review | **HIGH** | Repeated checklist patterns |
| orchestrator-pr-description.md | 211 | PR Management | **HIGH** | PR template structure |
| compliance-review.md | 185 | Compliance | **MEDIUM** | Checklist patterns |
| security-review.md | 143 | Security | **MEDIUM** | Checklist patterns |
| document-strategy-for-applications.md | 129 | Documentation | **MEDIUM** | Section templates |
| migration-strategy.md | 120 | Migration | **MEDIUM** | Step-by-step patterns |
| explain-strategy.md | 114 | Explanation | **MEDIUM** | Query/Response pattern |
| test-strategy.md | 108 | Testing | **MEDIUM** | Test type descriptions |
| ask-testing.md | 112 | Testing | **MEDIUM** | Shared testing guidance |
| refactor-strategy.md | 108 | Refactoring | **MEDIUM** | Methodology sections |
| review-performance.md | 77 | Code Review | **MEDIUM** | Checklist patterns |
| review-accessibility.md | 82 | Code Review | **MEDIUM** | Checklist patterns |
| ask-docs.md | 55 | Documentation | **LOW** | Reference format |
| ask-decision-log.md | 57 | Architecture | **LOW** | Template structure |
| (Other 14 templates) | ~480 | Various | **LOW** | Minor refactoring |

**Subtotal for Subagents: ~2,250 lines, 28 files**

---

### C. Core System Files (7 files)

**Category:** System-wide conventions and session management

| Template | Lines | Refactor Score | Notes |
|----------|-------|-----------------|-------|
| core-session.md | 444 | **LOW** | Well-structured, minimal repetition |
| core-system.md | ~200 | **LOW** | Unique content |
| core-session-troubleshooting.md | ~200 | **LOW** | Unique content |
| core-decision-log-template.md | ~100 | **MEDIUM** | Template blocks can be extracted |
| (Other core files) | ~200 | **LOW** | Minimal repetition |

**Subtotal for Core System: ~1,200 lines, 7 files**

---

## Refactoring Opportunities Ranked by Impact

### TIER 1: CRITICAL (Apply immediately)

#### 1. **Testing Section Template** (Macro)
- **Found in:** 29 core-conventions files (100%)
- **Current:** Each file has 5-6 testing subsections (Unit, Integration, E2E, Mutation, etc.)
- **Repetition:** >200 lines across all files
- **Jinja2 Solution:** Create `{% macro testing_section(language, framework, tools) %}`
- **Estimated Reduction:** 400-500 lines
- **Effort:** 2-3 hours
- **Priority:** 🔴 CRITICAL

```jinja2
{% macro testing_section(config) %}
#### Test Types

##### Unit Tests
{{ config.language | upper }} unit tests should cover:
1. Happy path — expected inputs produce expected outputs
2. Edge cases
3. Error cases — invalid inputs, failures, exceptions

##### Integration Tests
- Test at service or module boundary
- Use real database or in-memory alternatives
...
{% endmacro %}
```

#### 2. **Coverage Targets Block** (Macro)
- **Found in:** 28 language files
- **Current:** 6-line block repeated 28 times
- **Repetition:** ~170 lines
- **Jinja2 Solution:** Create `{% macro coverage_targets() %}`
- **Estimated Reduction:** 120-150 lines
- **Effort:** 30 minutes
- **Priority:** 🔴 CRITICAL

```jinja2
{% macro coverage_targets() %}
#### Coverage Targets
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%
Statement:      {{config.coverage.statement}}      e.g., 85%
Mutation:       {{config.coverage.mutation}}       e.g., 80%
Path:           {{config.coverage.path}}           e.g., 60%
{% endmacro %}
```

#### 3. **Naming Conventions Block** (Macro or Base Template)
- **Found in:** 30 language files (100%)
- **Current:** Similar structure with language-specific examples
- **Repetition:** ~180 lines
- **Jinja2 Solution:** Create `{% macro naming_conventions(config) %}` with conditional examples
- **Estimated Reduction:** 150-200 lines
- **Effort:** 2-3 hours
- **Priority:** 🔴 CRITICAL

### TIER 2: HIGH (Implement next)

#### 4. **Code Examples Pattern** (Macro or Loop)
- **Found in:** 19 language files with code blocks
- **Current:** Bash, YAML, Python examples repeated in similar structures
- **Repetition:** ~250 lines
- **Jinja2 Solution:** Create `{% macro bash_example(title, commands) %}` with loop
- **Estimated Reduction:** 150-200 lines
- **Effort:** 2-3 hours
- **Priority:** 🟠 HIGH

#### 5. **Framework & Tools Section** (Loop + Macro)
- **Found in:** 28+ language files
- **Current:** Repeated table/field definitions with language-specific tools
- **Repetition:** ~180 lines
- **Jinja2 Solution:** Create `{% for tool_type in config.tools %} ... {% endfor %}`
- **Estimated Reduction:** 150-180 lines
- **Effort:** 2 hours
- **Priority:** 🟠 HIGH

#### 6. **Checklist Patterns** (Macro)
- **Found in:** 5 review/compliance templates
- **Current:** Similar checklist format with language variations
- **Repetition:** ~100 lines
- **Jinja2 Solution:** Create `{% macro checklist_section(items, category) %}`
- **Estimated Reduction:** 80-120 lines
- **Effort:** 1-2 hours
- **Priority:** 🟠 HIGH

### TIER 3: MEDIUM (Plan for later phases)

#### 7. **Error Handling Section** (Macro)
- **Found in:** 26 language files (87%)
- **Repetition:** ~140 lines
- **Jinja2 Solution:** Create `{% macro error_handling_section(language_specific_content) %}`
- **Estimated Reduction:** 100-120 lines
- **Effort:** 1-2 hours

#### 8. **Base Template Inheritance** ({% extends %})
- **Opportunity:** All core-conventions files share common structure
- **Solution:** Create `core-conventions-base.md` with blocks:
  - `{% block naming_conventions %}`
  - `{% block testing %}`
  - `{% block error_handling %}`
  - `{% block type_system %}`
- **Estimated Reduction:** 30-40% total (800-1,100 lines)
- **Effort:** 4-5 hours
- **Priority:** 🟡 MEDIUM

#### 9. **PR Description Template** (Loop + Macro)
- **File:** orchestrator-pr-description.md (211 lines)
- **Opportunity:** Repeated example sections, PR structure definitions
- **Solution:** Create `{% macro pr_example(title, context, summary) %}`
- **Estimated Reduction:** 60-80 lines
- **Effort:** 1-2 hours

#### 10. **Configuration List Generation** (Loop)
- **Opportunity:** Config field lists in multiple templates
- **Solution:** Use `{% for field in config.fields %} ... {% endfor %}`
- **Estimated Reduction:** 80-100 lines
- **Effort:** 1 hour

---

## Top 5-10 Templates for Phase 4A Refactoring

### HIGH-PRIORITY CANDIDATES

**Rank 1: core-conventions-python.md**
- **Size:** 417 lines (largest)
- **Opportunity:** 5+ macro candidates, base template compatible
- **Estimated Reduction:** 150-200 lines
- **Benefit:** Unblocks all other language conventions
- **Effort:** 3-4 hours
- **Priority:** 🔴 CRITICAL

**Rank 2: core-conventions (base)**
- **Size:** 153 lines
- **Opportunity:** Define base template structure and shared macros
- **Impact:** Enables template inheritance for all language files
- **Effort:** 2-3 hours
- **Priority:** 🔴 CRITICAL

**Rank 3: All language conventions files** (treat as group)
- **Files:** 29 language-specific convention files
- **Total Size:** ~2,000 lines
- **Refactoring Strategy:** 
  1. Extract shared testing macro
  2. Extract coverage targets macro
  3. Extract naming conventions macro
  4. Create base template with blocks
  5. Update each language file to extend base + override language-specific blocks
- **Estimated Total Reduction:** 800-1,200 lines (40-50%)
- **Effort:** 12-16 hours
- **Priority:** 🔴 CRITICAL

**Rank 4: review-code.md**
- **Size:** 309 lines
- **Opportunity:** Repeated checklist patterns, numbered lists
- **Estimated Reduction:** 80-120 lines
- **Effort:** 2-3 hours
- **Priority:** 🟠 HIGH

**Rank 5: orchestrator-pr-description.md**
- **Size:** 211 lines
- **Opportunity:** Repeated example structure, template boilerplate
- **Estimated Reduction:** 60-90 lines
- **Effort:** 1-2 hours
- **Priority:** 🟠 HIGH

**Rank 6: compliance-review.md**
- **Size:** 185 lines
- **Opportunity:** Checklist patterns, repeated sections
- **Estimated Reduction:** 50-70 lines
- **Effort:** 1-2 hours
- **Priority:** 🟠 HIGH

**Rank 7: security-review.md**
- **Size:** 143 lines
- **Opportunity:** Checklist patterns
- **Estimated Reduction:** 40-60 lines
- **Effort:** 1 hour
- **Priority:** 🟠 HIGH

**Rank 8: ask-testing.md**
- **Size:** 112 lines
- **Opportunity:** Shared with test-strategy.md, redundancy elimination
- **Estimated Reduction:** 30-50 lines
- **Effort:** 1 hour
- **Priority:** 🟠 HIGH

**Rank 9: ask-docs.md**
- **Size:** 55 lines
- **Opportunity:** Template reference consolidation
- **Estimated Reduction:** 20-30 lines
- **Effort:** 30-45 minutes
- **Priority:** 🟡 MEDIUM

**Rank 10: core-decision-log-template.md**
- **Size:** ~150 lines
- **Opportunity:** Template structure extraction
- **Estimated Reduction:** 30-50 lines
- **Effort:** 1 hour
- **Priority:** 🟡 MEDIUM

---

## Implementation Strategy for Phase 4A

### Phase 4A Execution Plan

**Duration:** 3-4 weeks  
**Goal:** Refactor top 10 templates using Jinja2 features  
**Success Criteria:** 25-40% code reduction while maintaining clarity

#### Week 1: Macro Extraction & Base Templates

**Step 1: Create macro library** (4 hours)
- Location: `promptosaurus/prompts/_macros/` (new directory)
- Files to create:
  1. `testing_sections.jinja2` - Testing macro variants
  2. `coverage_targets.jinja2` - Coverage table macro
  3. `naming_conventions.jinja2` - Naming convention macro
  4. `code_examples.jinja2` - Code block templates

**Step 2: Create base template** (3 hours)
- File: `agents/core/core-conventions-base.jinja2`
- Structure:
  ```jinja2
  # Core Conventions {{ config.language }}
  
  {% block language_meta %}
  Language: {{ config.language }}
  Runtime: {{ config.runtime }}
  {% endblock %}
  
  {% block naming_conventions %}
  {% include 'macros/naming_conventions.jinja2' %}
  {% endblock %}
  
  {% block testing %}
  {% include 'macros/testing_sections.jinja2' %}
  {% endblock %}
  
  {% block type_system %}
  [Language-specific content]
  {% endblock %}
  ```

**Step 3: Update core-conventions.md** (2 hours)
- Convert to base template structure
- Extract common sections as macros
- Make language-specific sections overridable

#### Week 2: Language Conventions Refactoring

**Step 4: Refactor core-conventions-python.md** (4 hours)
- Extract testing sections → macro call
- Extract coverage targets → macro call
- Remove duplicate error handling
- Update to extend base template
- Validate formatting

**Step 5: Refactor remaining language files** (8 hours total)
- Process in groups by file size
- Apply same pattern to each
- Total reduction: ~800-1,200 lines

#### Week 3: Subagent Template Refactoring

**Step 6: Refactor review-code.md** (3 hours)
- Extract checklist patterns
- Create reusable checklist macro
- Consolidate code examples

**Step 7: Refactor orchestrator-pr-description.md** (2 hours)
- Extract PR example template
- Create macro for PR sections
- Reduce boilerplate

**Step 8: Refactor compliance-review.md** (2 hours)
- Extract compliance checklist
- Create generic checklist macro

#### Week 4: Testing & Documentation

**Step 9: Comprehensive testing** (3 hours)
- Verify all template variables resolve correctly
- Check formatting output matches original
- Validate Jinja2 syntax

**Step 10: Documentation & Metrics** (2 hours)
- Update REFACTORING.md with results
- Document macro library API
- Create usage guidelines

### Expected Outcomes

**Code Reduction:**
- Language conventions: 800-1,200 lines saved (40-50%)
- Subagent templates: 200-300 lines saved (10-15%)
- Core system files: 100-150 lines saved (5-10%)
- **Total:** ~1,100-1,650 lines saved (25-40%)

**Quality Improvements:**
- Single source of truth for repeated sections
- Easier to update standards across all languages
- Consistent formatting and structure
- Reduced maintenance burden

**Maintenance Benefit:**
- Change testing guidance → updates 29 language files automatically
- Update naming conventions → propagates to all languages
- Add new test type → available to all languages immediately

---

## Jinja2 Features Required by Template Type

| Feature | Use Cases | Templates Affected |
|---------|-----------|-------------------|
| {% macro %} | Reusable sections | Testing, coverage, naming conventions (29+ files) |
| {% extends %} | Template inheritance | Language conventions (30 files) |
| {% include %} | Modular sections | All files (potential) |
| {% for %} | List iteration | Tool lists, config fields (15+ files) |
| {% if %} | Conditional content | Language-specific variants (20+ files) |
| {% set %} | Variable assignment | Configuration, examples (10+ files) |
| Custom filters | Text transformation | Code examples, naming (15+ files) |

---

## Risk Assessment

### Low Risk
- ✅ Macro extraction (isolated, non-breaking)
- ✅ Coverage targets macro (simple structure)
- ✅ Checklist macros (well-defined patterns)

### Medium Risk
- ⚠️ Base template inheritance (affects 30 language files)
  - *Mitigation:* Phased rollout, extensive testing
- ⚠️ Loop-based list generation (formatting sensitive)
  - *Mitigation:* Test whitespace handling

### High Risk
- 🔴 Converting all files simultaneously
  - *Mitigation:* One file at a time with validation

---

## Success Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Code reduction | 25-40% | Line count comparison |
| Template errors | 0 | Jinja2 syntax validation |
| Output consistency | 100% | Diff against originals |
| Test coverage | ≥95% | Integration tests |
| Build time | ≤500ms | Performance measurement |

---

## Files to Create

```
promptosaurus/prompts/
├── _macros/                          (NEW)
│   ├── testing_sections.jinja2
│   ├── coverage_targets.jinja2
│   ├── naming_conventions.jinja2
│   ├── code_examples.jinja2
│   ├── checklist.jinja2
│   └── error_handling.jinja2
├── _base/                            (NEW)
│   ├── conventions-base.jinja2
│   ├── subagent-base.jinja2
│   └── checklist-base.jinja2
└── (existing files - refactored)
```

---

## Next Steps

1. **Review this audit** - Confirm priorities and scope
2. **Week 1 Sprint:** Extract macros and base templates
3. **Week 2-3 Sprint:** Refactor language conventions and subagents
4. **Week 4 Sprint:** Testing, validation, and documentation
5. **Commit & Deploy:** Push refactored templates to production

---

## Appendix: Complete Template Inventory

### All 65 Templates (Categorized)

**Core System (7 files):**
- agents/core/core-system.md
- agents/core/core-conventions.md
- agents/core/core-session.md
- agents/core/core-session-troubleshooting.md
- agents/core/core-decision-log-template.md
- agents/project_planning/planning.md
- agents/project_planning/methodology.md

**Language Conventions (30 files):**
- core-conventions-python.md
- core-conventions-typescript.md
- core-conventions-java.md
- core-conventions-golang.md
- core-conventions-sql.md
- core-conventions-terraform.md
- core-conventions-rust.md
- core-conventions-csharp.md
- core-conventions-kotlin.md
- core-conventions-javascript.md
- core-conventions-cpp.md
- core-conventions-swift.md
- core-conventions-scala.md
- core-conventions-elixir.md
- core-conventions-ruby.md
- core-conventions-php.md
- core-conventions-c.md
- core-conventions-groovy.md
- core-conventions-haskell.md
- core-conventions-html.md
- core-conventions-julia.md
- core-conventions-lua.md
- core-conventions-objc.md
- core-conventions-r.md
- core-conventions-shell.md
- core-conventions-clojure.md
- core-conventions-dart.md
- core-conventions-elm.md
- core-conventions-fsharp.md

**Architect Subagents (3 files):**
- agents/architect/subagents/architect-task-breakdown.md
- agents/architect/subagents/architect-data-model.md
- agents/architect/subagents/architect-scaffold.md

**Ask Subagents (3 files):**
- agents/ask/subagents/ask-testing.md
- agents/ask/subagents/ask-docs.md
- agents/ask/subagents/ask-decision-log.md

**Code Subagents (6 files):**
- agents/code/subagents/code-feature.md
- agents/code/subagents/code-boilerplate.md
- agents/code/subagents/code-house-style.md
- agents/code/subagents/code-refactor.md
- agents/code/subagents/code-migration.md
- agents/code/subagents/code-dependency-upgrade.md

**Review Subagents (3 files):**
- agents/review/subagents/review-code.md
- agents/review/subagents/review-performance.md
- agents/review/subagents/review-accessibility.md

**Debug Subagents (3 files):**
- agents/debug/subagents/debug-root-cause.md
- agents/debug/subagents/debug-log-analysis.md
- agents/debug/subagents/debug-rubber-duck.md

**Other Subagents (10 files):**
- agents/test/subagents/test-strategy.md
- agents/refactor/subagents/refactor-strategy.md
- agents/migration/subagents/migration-strategy.md
- agents/compliance/subagents/compliance-review.md
- agents/security/subagents/security-review.md
- agents/explain/subagents/explain-strategy.md
- agents/document/subagents/document-strategy-for-applications.md
- agents/orchestrator/subagents/orchestrator-pr-description.md
- agents/orchestrator/subagents/orchestrator-devops.md
- agents/orchestrator/subagents/orchestrator-meta.md
- agents/enforcement/enforcement.md

---

## Document Metadata

- **Created:** 2026-04-08T12:42:16Z
- **Phase:** Phase 4A - Real-World Integration Audit
- **Status:** AUDIT COMPLETE - Ready for Planning & Prioritization
- **Next Phase:** Phase 4B - Macro Extraction & Base Templates
- **Estimated Total Effort:** 20-30 hours across 4 weeks
