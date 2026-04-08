# Phase 4A: Macro Examples & Implementation Patterns

This document shows concrete examples of the 6 macros that will be created in Phase 4B.

---

## Macro 1: Testing Sections Macro

**File:** `promptosaurus/prompts/_macros/testing_sections.jinja2`

**Current Repetition:** Found in 29 language files (200+ lines total)

**Problem Being Solved:**
Every language convention file has Testing section with 5-6 subsections that are 95% identical:
- Testing subsection header
- Coverage targets table
- Test Types subsection with 3-5 test type descriptions
- Framework & Tools table
- Scaffolding code examples

### Current Code (Repeated 29x)

```markdown
### Testing

#### Coverage Targets
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%
Statement:      {{config.coverage.statement}}      e.g., 85%
Mutation:       {{config.coverage.mutation}}       e.g., 80%
Path:           {{config.coverage.path}}           e.g., 60%

#### Test Types

##### Unit Tests
[Language-specific content - 3-5 lines]
...

##### Integration Tests
[Language-specific content - 3-5 lines]
...

[Similar for E2E, Mutation, etc.]

#### Framework & Tools
Framework:       {{config.testing_framework}}        e.g., pytest
Mocking library: {{config.mocking_library}}              e.g., pytest-mock
Coverage tool:  {{config.coverage_tool}}              e.g., pytest-cov
Mutation tool:  {{config.mutation_tool}}          e.g., mutmut
```

### Macro Implementation

```jinja2
{# testing_sections.jinja2 - Reusable testing section macro #}

{% macro coverage_targets() %}
#### Coverage Targets
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%
Statement:      {{config.coverage.statement}}      e.g., 85%
Mutation:       {{config.coverage.mutation}}       e.g., 80%
Path:           {{config.coverage.path}}           e.g., 60%
{% endmacro %}

{% macro testing_section(language, has_unit=true, has_integration=true, has_e2e=false, has_mutation=false) %}
### Testing

{{ coverage_targets() }}

#### Test Types

{% if has_unit %}
##### Unit Tests
{{ unit_tests_guidance[language] | default("One function or method in isolation\nMock external dependencies\nTest behavior, not implementation") }}
{% endif %}

{% if has_integration %}
##### Integration Tests
{{ integration_tests_guidance[language] | default("Test at service or module boundary\nUse real database or in-memory alternatives\nTest API endpoints, database queries") }}
{% endif %}

{% if has_e2e %}
##### E2E Tests
{{ e2e_tests_guidance[language] | default("Test complete user flows end-to-end\nUse real services or testing frameworks") }}
{% endif %}

{% if has_mutation %}
##### Mutation Tests
{{ mutation_tests_guidance[language] | default("Use mutation testing tools to verify test quality\nRun after unit tests pass") }}
{% endif %}

#### Framework & Tools
{{ framework_and_tools_table(language) }}

#### Scaffolding

```bash
{{ scaffolding_examples[language] | default("# Testing scaffolding for " + language) }}
```
{% endmacro %}
```

### Usage in Language File

**Before (repeated 29x):**
```markdown
# 200+ lines of repeated content across 29 files
```

**After:**
```jinja2
{% from 'macros/testing_sections.jinja2' import testing_section %}

{{ testing_section('python', has_unit=true, has_integration=true, has_mutation=true) }}
```

**Savings:** 150-200 lines per file × 29 files = 4,350-5,800 lines reduced to ~200 lines total

---

## Macro 2: Coverage Targets Macro

**File:** `promptosaurus/prompts/_macros/coverage_targets.jinja2`

**Current Repetition:** Found in 28 language files (6 lines each = 168 lines total)

**Problem:** Identical table structure repeated with only language config variables changing

### Macro Implementation

```jinja2
{# coverage_targets.jinja2 - Reusable coverage table #}

{% macro coverage_targets(metrics=none) %}
#### Coverage Targets
{% if metrics %}
{% for metric, target in metrics.items() %}
{{ metric | capitalize }}:{{ ' ' * (16 - metric|length) }}{{target}}
{% endfor %}
{% else %}
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%
Statement:      {{config.coverage.statement}}      e.g., 85%
Mutation:       {{config.coverage.mutation}}       e.g., 80%
Path:           {{config.coverage.path}}           e.g., 60%
{% endif %}
{% endmacro %}
```

### Usage

```jinja2
{% from 'macros/coverage_targets.jinja2' import coverage_targets %}

{{ coverage_targets() }}
```

**Savings:** 6 lines × 28 files = 168 lines → ~15 lines total

---

## Macro 3: Naming Conventions Macro

**File:** `promptosaurus/prompts/_macros/naming_conventions.jinja2`

**Current Repetition:** Found in 30 language files (8-10 lines each = 240+ lines total)

**Problem:** Similar structure with language-specific conventions

### Macro Implementation

```jinja2
{# naming_conventions.jinja2 - Reusable naming section #}

{% macro naming_conventions(conventions) %}
### Naming Conventions

{% for convention_type, convention_value in conventions.items() %}
{{ convention_type | replace('_', '/') | capitalize }}:{{ ' ' * (20 - (convention_type|length)) }}{{ convention_value }}
{% endfor %}
{% endmacro %}

{# Default conventions for common cases #}
{% set default_conventions = {
    'files': 'snake_case',
    'variables': 'camelCase',
    'constants': 'UPPER_SNAKE',
    'classes_types': 'PascalCase',
    'functions': 'camelCase',
    'database_tables': 'snake_case',
    'environment_vars': 'UPPER_SNAKE_CASE always',
} %}

{% macro naming_conventions_default() %}
### Naming Conventions

Files:               snake_case
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          camelCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always
{% endmacro %}
```

### Usage

```jinja2
{% from 'macros/naming_conventions.jinja2' import naming_conventions_default %}

{{ naming_conventions_default() }}
```

**Savings:** 8 lines × 30 files = 240 lines → ~20 lines total

---

## Macro 4: Code Examples Macro

**File:** `promptosaurus/prompts/_macros/code_examples.jinja2`

**Current Repetition:** Found in 19 language files with similar structure

**Problem:** Install/run/configure patterns repeated with language-specific syntax

### Macro Implementation

```jinja2
{# code_examples.jinja2 - Reusable code example patterns #}

{% macro bash_example(title, commands) %}
#### {{ title }}

```bash
{{ commands }}
```
{% endmacro %}

{% macro yaml_example(title, yaml_content) %}
#### {{ title }}

```yaml
{{ yaml_content }}
```
{% endmacro %}

{% macro code_block(language, title, code) %}
#### {{ title }}

```{{ language }}
{{ code }}
```
{% endmacro %}

{# Common patterns - e.g. install examples #}
{% macro install_examples(language, package_manager, commands) %}
### Installation

```bash
{{ commands['install'] }}
```
{% endmacro %}

{% macro test_commands(language, test_framework, commands) %}
### Running Tests

```bash
{{ commands['run_all'] }}
{{ commands['with_coverage'] }}
{{ commands['mutation_test'] }}
```
{% endmacro %}
```

### Usage

```jinja2
{% from 'macros/code_examples.jinja2' import bash_example, test_commands %}

{{ bash_example('Install Dependencies', 'pip install pytest pytest-cov') }}

{{ test_commands('python', 'pytest', {
    'run_all': 'pytest',
    'with_coverage': 'pytest --cov',
    'mutation_test': 'mutmut run'
}) }}
```

**Savings:** 60-80 lines across 19 files

---

## Macro 5: Error Handling Section Macro

**File:** `promptosaurus/prompts/_macros/error_handling.jinja2`

**Current Repetition:** Found in 26 language files (6-10 lines each = 156+ lines total)

### Macro Implementation

```jinja2
{# error_handling.jinja2 - Reusable error handling section #}

{% macro error_handling_guidelines(language_content='') %}
### Error Handling

- Use specific exception types, not generic errors
- Never silently swallow errors
- Always include context in error messages
- Log at the boundary where the error is handled
- Use typed errors or result types where appropriate

{{ language_content }}
{% endmacro %}

{% macro error_handling_with_examples(language, examples=[]) %}
### Error Handling

- Use specific exception types, not generic Exception
- Never catch generic errors unless rethrowing
- Always add context: "failed to fetch user: {userId}"
- Log at the boundary where the error is handled

{% if examples %}
#### {{ language }} Examples

{% for example_title, example_code in examples %}
##### {{ example_title }}
```{{ language | lower }}
{{ example_code }}
```
{% endfor %}
{% endif %}
{% endmacro %}
```

### Usage

```jinja2
{% from 'macros/error_handling.jinja2' import error_handling_guidelines %}

{{ error_handling_guidelines("
- Python-specific: Use exception hierarchies, never bare Exception
- Wrap errors with context using f-strings") }}
```

**Savings:** 8 lines × 26 files = 208 lines → ~30 lines total

---

## Macro 6: Checklist Macro

**File:** `promptosaurus/prompts/_macros/checklist.jinja2`

**Current Repetition:** Found in 5 review/compliance templates (20+ lines each = 100+ lines total)

### Macro Implementation

```jinja2
{# checklist.jinja2 - Reusable checklist patterns #}

{% macro numbered_checklist(items, intro='', outro='') %}
{% if intro %}
{{ intro }}

{% endif %}
{% for item in items %}
{{ loop.index }}. {{ item }}
{% endfor %}

{% if outro %}
{{ outro }}
{% endif %}
{% endmacro %}

{% macro checkbox_checklist(items, intro='', outro='', category='') %}
{% if intro %}
{{ intro }}

{% endif %}
{% if category %}
## {{ category }}

{% endif %}
{% for item in items %}
- [ ] {{ item }}
{% endfor %}

{% if outro %}

{{ outro }}
{% endif %}
{% endmacro %}

{% macro layered_checklist(categories, intro='') %}
{% if intro %}
{{ intro }}

{% endif %}
{% for category_name, items in categories.items() %}
### {{ category_name }}

{% for item in items %}
- [ ] {{ item }}
{% endfor %}

{% endfor %}
{% endmacro %}
```

### Usage

```jinja2
{% from 'macros/checklist.jinja2' import checkbox_checklist %}

{{ checkbox_checklist(
  items=[
    'Code follows style guidelines',
    'Tests cover happy path and edge cases',
    'No hardcoded secrets or credentials',
    'Error handling is comprehensive'
  ],
  intro='## Code Review Checklist',
  category='Code Quality'
) }}
```

**Savings:** 30-50 lines across 5 files

---

## Macro Usage Statistics

| Macro | Files Used | Lines Repeated | Macro Size | Savings |
|-------|-----------|-----------------|------------|---------|
| testing_section | 29 | 200-250 | 80 | 120-170 |
| coverage_targets | 28 | 168 | 20 | 148 |
| naming_conventions | 30 | 240+ | 20 | 220+ |
| code_examples | 19 | 250+ | 80 | 170+ |
| error_handling | 26 | 156+ | 40 | 116+ |
| checklist | 5 | 100+ | 60 | 40+ |
| **TOTAL** | **137** | **~1,100+** | **300** | **~800+** |

---

## Base Template Pattern

**File:** `promptosaurus/prompts/_base/conventions-base.jinja2`

### Structure

```jinja2
# Core Conventions {{ config.language }}

Language:             {{config.language}}           e.g., Python 3.12
Runtime:              {{config.runtime}}            e.g., CPython 3.12
Package Manager:      {{config.package_manager}}        e.g., pip, poetry, uv
Linter:               {{config.linter}}             e.g., ruff, pylint
Formatter:            {{config.formatter}}          e.g., ruff, black

{% from 'macros/naming_conventions.jinja2' import naming_conventions_default %}
{{ naming_conventions_default() }}

## {{ config.language }}-Specific Rules

{% block language_specific_intro %}
### Type Hints
[Language-specific content]
{% endblock %}

{% block error_handling %}
{% from 'macros/error_handling.jinja2' import error_handling_guidelines %}
{{ error_handling_guidelines() }}
{% endblock %}

{% from 'macros/testing_sections.jinja2' import testing_section %}
{{ testing_section(config.language | lower) }}

{% block additional_sections %}
[Optional language-specific sections]
{% endblock %}
```

### How It Works

Each language file extends the base:

```jinja2
{% extends "_base/conventions-base.jinja2" %}

{% block language_specific_intro %}
### Type Hints
- Type hints required on all public functions
- Use `T | None` instead of `Optional[T]`
- Use proper type narrowing with `isinstance`
{% endblock %}

{% block additional_sections %}
### Python-Specific Async
- Use `asyncio` for concurrency
- Use `async`/`await` syntax
- Never mix sync/async without explicit bridging
{% endblock %}
```

---

## Implementation Sequence for Phase 4B

**Week 1 - Create Macros:**
1. Create `_macros/` directory
2. Implement `coverage_targets.jinja2` (simplest)
3. Implement `naming_conventions.jinja2`
4. Implement `testing_sections.jinja2`
5. Implement `code_examples.jinja2`
6. Implement `error_handling.jinja2`
7. Implement `checklist.jinja2`

**Week 1 - Create Base Templates:**
1. Create `_base/` directory
2. Implement `conventions-base.jinja2`
3. Implement `subagent-base.jinja2`
4. Implement `checklist-base.jinja2`

**Week 2-3 - Apply Macros:**
1. Update language convention files (use macros + extends)
2. Update subagent files (use macros)
3. Validate output consistency

**Week 4 - Testing & Deployment:**
1. Run full test suite
2. Measure code reduction
3. Benchmark performance
4. Commit and deploy

---

## Testing Strategy for Macros

### Unit Tests for Each Macro

```python
def test_coverage_targets_macro():
    """Test coverage_targets macro generates correct table."""
    template = jinja2_env.from_string("""
    {% from '_macros/coverage_targets.jinja2' import coverage_targets %}
    {{ coverage_targets() }}
    """)
    
    output = template.render(config={
        'coverage': {
            'line': '80%',
            'branch': '70%',
            'function': '90%',
            'statement': '85%',
            'mutation': '80%',
            'path': '60%'
        }
    })
    
    assert 'Line:' in output
    assert '80%' in output
    assert '#### Coverage Targets' in output

def test_naming_conventions_macro():
    """Test naming_conventions macro."""
    template = jinja2_env.from_string("""
    {% from '_macros/naming_conventions.jinja2' import naming_conventions_default %}
    {{ naming_conventions_default() }}
    """)
    
    output = template.render()
    
    assert 'Files:' in output
    assert 'snake_case' in output
    assert 'Variables:' in output
    assert 'camelCase' in output
```

---

## Expected Phase 4B Outcomes

- ✅ 6 macros created with comprehensive documentation
- ✅ 3 base templates created for template inheritance
- ✅ 40-45 templates refactored to use macros
- ✅ 1,000-1,600 lines eliminated (25-40% reduction)
- ✅ 30-40 unit tests for macros
- ✅ 100% output validation (diffs match originals)
- ✅ 0 regressions in existing functionality
- ✅ Performance optimized (template caching)

---

## Document Metadata

- **Created:** 2026-04-08
- **Phase:** Phase 4A - Macro Examples & Patterns
- **Status:** Reference document for Phase 4B implementation
- **Next:** Phase 4B begins with macro library creation
