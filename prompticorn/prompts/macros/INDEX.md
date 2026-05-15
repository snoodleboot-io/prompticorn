# Macro Libraries - Quick Index

**Created:** April 8, 2026  
**Status:** ✓ Complete and tested  
**Total Macros:** 34 across 6 libraries  

---

## Find What You Need

### By Use Case

**Testing & Coverage**
- See: `testing_sections.jinja2` and `coverage_targets.jinja2`
- Macros: 9 total (4 + 5)
- Use for: Testing setup, coverage metrics, test scaffolding

**Code Quality & Review**
- See: `code_examples.jinja2` and `checklist.jinja2`
- Macros: 17 total (8 + 9)
- Use for: Code patterns, review checklists, quality verification

**Naming & Conventions**
- See: `naming_conventions.jinja2`
- Macros: 4 total
- Use for: Naming tables, examples, verification

**Error Handling**
- See: `error_handling.jinja2`
- Macros: 4 total
- Use for: Error patterns, recovery guides, monitoring

---

### By Library

#### 1. testing_sections.jinja2
**4 macros** for testing framework setup

```jinja2
{% import 'macros/testing_sections.jinja2' as testing %}

{{ testing.render_testing_section(language, framework, coverage_targets) }}
{{ testing.render_test_types(language) }}
{{ testing.render_test_scaffolding(language, package_manager) }}
{{ testing.render_ci_integration(language) }}
```

---

#### 2. coverage_targets.jinja2
**5 macros** for coverage metrics and targets

```jinja2
{% import 'macros/coverage_targets.jinja2' as coverage %}

{{ coverage.render_coverage_table(80, 70, 90, 85, 80, 60) }}
{{ coverage.render_coverage_details(language) }}
{{ coverage.render_coverage_table_simple(targets) }}
{{ coverage.render_coverage_checklist(language) }}
{{ coverage.render_coverage_improvement_guide() }}
```

---

#### 3. naming_conventions.jinja2
**4 macros** for naming convention guidance

```jinja2
{% import 'macros/naming_conventions.jinja2' as naming %}

{{ naming.render_naming_conventions(language) }}
{{ naming.render_naming_table(language, patterns) }}
{{ naming.render_naming_examples(language) }}
{{ naming.render_naming_checklist(language) }}
```

---

#### 4. code_examples.jinja2
**8 macros** for code patterns and examples

```jinja2
{% import 'macros/code_examples.jinja2' as examples %}

{{ examples.render_code_example(language, code, description) }}
{{ examples.render_pattern_comparison(language, good, bad, title) }}
{{ examples.render_python_import_pattern() }}
{{ examples.render_python_type_hints() }}
{{ examples.render_python_error_handling() }}
{{ examples.render_typescript_pattern() }}
{{ examples.render_async_patterns(language) }}
{{ examples.render_code_review_checklist(language) }}
```

---

#### 5. error_handling.jinja2
**4 macros** for error handling patterns

```jinja2
{% import 'macros/error_handling.jinja2' as errors %}

{{ errors.render_error_section(pattern, description) }}
{{ errors.render_error_pattern(language, pattern_name) }}
{{ errors.render_error_recovery_guide(scenario) }}
{{ errors.render_error_monitoring_checklist() }}
```

**Pattern Names:**
- `exception_hierarchy` - Custom exception design
- `context_preservation` - Error context preservation
- `typed_errors` - Typed error definitions
- `logging_errors` - Error logging
- `async_error_handling` - Async error patterns

**Recovery Scenarios:**
- `database_failures` - Database failure handling
- `external_api_calls` - API failure handling
- `validation_errors` - Validation error handling

---

#### 6. checklist.jinja2
**9 macros** for checklist generation

```jinja2
{% import 'macros/checklist.jinja2' as checklists %}

{{ checklists.render_checklist(items, title) }}
{{ checklists.render_numbered_steps(steps, title) }}
{{ checklists.render_verification_checklist(checks, category) }}
{{ checklists.render_code_quality_checklist(language) }}
{{ checklists.render_review_checklist() }}
{{ checklists.render_deployment_checklist() }}
{{ checklists.render_testing_checklist(line, branch, function, statement, mutation) }}
{{ checklists.render_git_workflow_checklist() }}
{{ checklists.render_documentation_checklist() }}
```

---

## Common Patterns

### Single Library Usage
```jinja2
{% import 'macros/testing_sections.jinja2' as testing %}

# Testing Framework Setup
{{ testing.render_testing_section('python', 'pytest', coverage_targets) }}
```

### Multi-Library Composition
```jinja2
{% import 'macros/testing_sections.jinja2' as testing %}
{% import 'macros/coverage_targets.jinja2' as coverage %}
{% import 'macros/checklist.jinja2' as checklists %}

# Complete Testing Guide
{{ testing.render_testing_section(...) }}
{{ coverage.render_coverage_table(...) }}
{{ checklists.render_testing_checklist(...) }}
```

### All Libraries (Full Guide)
```jinja2
{% import 'macros/testing_sections.jinja2' as testing %}
{% import 'macros/coverage_targets.jinja2' as coverage %}
{% import 'macros/naming_conventions.jinja2' as naming %}
{% import 'macros/code_examples.jinja2' as examples %}
{% import 'macros/error_handling.jinja2' as errors %}
{% import 'macros/checklist.jinja2' as checklists %}

# Full Coding Standards Guide
# [Import all and compose...]
```

---

## Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Complete reference documentation |
| `__init__.jinja2` | Usage guide with detailed examples |
| `test_macros.jinja2` | Test template for all macros |
| `example_comprehensive.jinja2` | Full working example document |
| `INDEX.md` | This file |

---

## Language Support

**Python:** All 6 libraries  
**TypeScript:** All 6 libraries  
**Go:** Naming conventions only  

See individual library documentation for language-specific examples.

---

## Next Steps

1. **Start Small:** Import one library and use a single macro
2. **Explore:** Review example_comprehensive.jinja2 for full composition
3. **Expand:** Add more libraries as needed
4. **Customize:** Create organization-specific context variables

---

## Questions?

- See `README.md` for detailed documentation
- See `__init__.jinja2` for usage examples
- See `example_comprehensive.jinja2` for full working example
- Run `test_macros.jinja2` to verify everything works

---

Generated: April 8, 2026
