# Macro Libraries

This directory contains reusable Jinja2 macro libraries for generating standardized documentation and guidance across the promptosaurus project.

## Overview

Six macro libraries provide templates for:
- **Testing** - Testing framework setup and coverage guidance
- **Coverage** - Coverage metrics and targets
- **Naming** - Naming conventions for different languages
- **Code Examples** - Pattern examples and anti-patterns
- **Error Handling** - Error patterns and recovery strategies
- **Checklists** - Verification and task checklists

## Quick Start

### Import a macro library

```jinja2
{% import 'macros/testing_sections.jinja2' as testing %}

{{ testing.render_testing_section('python', 'pytest', coverage_targets) }}
```

### Compose multiple libraries

```jinja2
{% import 'macros/testing_sections.jinja2' as testing %}
{% import 'macros/coverage_targets.jinja2' as coverage %}
{% import 'macros/checklist.jinja2' as checklists %}

# Testing Guide

{{ testing.render_testing_section(language, framework, coverage_targets) }}

{{ coverage.render_coverage_checklist(language) }}

{{ checklists.render_code_quality_checklist(language) }}
```

## Macro Libraries

### 1. testing_sections.jinja2

Generates testing framework setup sections with coverage targets and test types.

**Available Macros:**

- `render_testing_section(language, framework, coverage_targets)` - Complete testing section
- `render_test_types(language)` - Test types organized by category
- `render_test_scaffolding(language, package_manager)` - Installation and setup code
- `render_ci_integration(language)` - CI/CD pipeline examples

**Example:**

```jinja2
{% import 'macros/testing_sections.jinja2' as testing %}

{{ testing.render_testing_section('python', 'pytest', {
    'line': 80,
    'branch': 70,
    'function': 90,
    'statement': 85,
    'mutation': 80,
    'path': 60
}) }}
```

**Supported Languages:** python, typescript

### 2. coverage_targets.jinja2

Generates coverage target tables and coverage guidance.

**Available Macros:**

- `render_coverage_table(line, branch, function, statement, mutation, path)` - Coverage table
- `render_coverage_details(language)` - Metric definitions and explanations
- `render_coverage_table_simple(targets)` - Simplified coverage table
- `render_coverage_checklist(language)` - Coverage quality checklist
- `render_coverage_improvement_guide()` - Strategies for improving coverage

**Example:**

```jinja2
{% import 'macros/coverage_targets.jinja2' as coverage %}

{{ coverage.render_coverage_table(80, 70, 90, 85, 80, 60) }}
{{ coverage.render_coverage_checklist('python') }}
```

**Supported Languages:** python, typescript

### 3. naming_conventions.jinja2

Generates naming convention tables and examples for different languages.

**Available Macros:**

- `render_naming_conventions(language)` - Complete naming conventions table
- `render_naming_table(language, patterns)` - Custom naming table
- `render_naming_examples(language)` - Good and bad naming examples
- `render_naming_checklist(language)` - Naming conventions checklist

**Example:**

```jinja2
{% import 'macros/naming_conventions.jinja2' as naming %}

{{ naming.render_naming_conventions('python') }}
{{ naming.render_naming_examples('python') }}
{{ naming.render_naming_checklist('python') }}
```

**Supported Languages:** python, typescript, go

### 4. code_examples.jinja2

Generates code examples with patterns, anti-patterns, and best practices.

**Available Macros:**

- `render_code_example(language, code, description)` - Code example with syntax highlighting
- `render_pattern_comparison(language, good_code, bad_code, title)` - Good vs bad pattern
- `render_python_import_pattern()` - Python import organization
- `render_python_type_hints()` - Python type hints examples
- `render_python_error_handling()` - Python error handling patterns
- `render_typescript_pattern()` - TypeScript type safety examples
- `render_async_patterns(language)` - Async/await patterns
- `render_code_review_checklist(language)` - Code review verification checklist

**Example:**

```jinja2
{% import 'macros/code_examples.jinja2' as examples %}

{{ examples.render_python_import_pattern() }}
{{ examples.render_python_type_hints() }}
{{ examples.render_code_review_checklist('python') }}
```

**Supported Languages:** python, typescript

### 5. error_handling.jinja2

Generates error handling patterns, strategies, and recovery guides.

**Available Macros:**

- `render_error_section(pattern, description)` - Error handling section header
- `render_error_pattern(language, pattern_name)` - Specific error pattern implementation
- `render_error_recovery_guide(scenario)` - Error recovery strategies
- `render_error_monitoring_checklist()` - Error logging and monitoring checklist

**Supported Error Patterns:**
- `exception_hierarchy` - Exception hierarchy design
- `context_preservation` - Error context preservation
- `typed_errors` - Typed error definitions
- `logging_errors` - Error logging strategies
- `async_error_handling` - Async error handling patterns

**Supported Recovery Scenarios:**
- `database_failures` - Database failure recovery
- `external_api_calls` - External API failure recovery
- `validation_errors` - Validation error recovery

**Example:**

```jinja2
{% import 'macros/error_handling.jinja2' as errors %}

{{ errors.render_error_pattern('python', 'exception_hierarchy') }}
{{ errors.render_error_recovery_guide('database_failures') }}
{{ errors.render_error_monitoring_checklist() }}
```

**Supported Languages:** python, typescript

### 6. checklist.jinja2

Generates reusable checklists for various development tasks.

**Available Macros:**

- `render_checklist(items, title)` - Generic checkbox checklist
- `render_numbered_steps(steps, title)` - Numbered steps list
- `render_verification_checklist(checks, category)` - Verification checklist
- `render_code_quality_checklist(language)` - Code quality verification
- `render_review_checklist()` - Code review checklist
- `render_deployment_checklist()` - Deployment verification
- `render_testing_checklist()` - Testing requirements checklist
- `render_git_workflow_checklist()` - Git workflow checklist
- `render_documentation_checklist()` - Documentation checklist

**Example:**

```jinja2
{% import 'macros/checklist.jinja2' as checklists %}

{{ checklists.render_code_quality_checklist('python') }}
{{ checklists.render_review_checklist() }}
{{ checklists.render_deployment_checklist() }}
{{ checklists.render_testing_checklist() }}
```

**Supported Languages:** python, typescript

## Context Variables

These variables should be available in your template context:

```python
{
    'language': 'python',           # 'python', 'typescript', 'go', etc.
    'framework': 'pytest',           # Testing framework
    'package_manager': 'uv',         # 'uv', 'pip', 'npm', 'pnpm', etc.
    'coverage_targets': {
        'line': 80,                  # Line coverage target %
        'branch': 70,                # Branch coverage target %
        'function': 90,              # Function coverage target %
        'statement': 85,             # Statement coverage target %
        'mutation': 80,              # Mutation score target %
        'path': 60,                  # Path coverage target %
    }
}
```

## Macro Composition

Combine multiple macros to create comprehensive guides:

```jinja2
{% import 'macros/testing_sections.jinja2' as testing %}
{% import 'macros/coverage_targets.jinja2' as coverage %}
{% import 'macros/code_examples.jinja2' as examples %}
{% import 'macros/checklist.jinja2' as checklists %}

# {{ language | capitalize }} Testing & Quality Guide

## Testing Framework

{{ testing.render_testing_section(language, framework, coverage_targets) }}

## Coverage Requirements

{{ coverage.render_coverage_table(
    coverage_targets.line,
    coverage_targets.branch,
    coverage_targets.function,
    coverage_targets.statement,
    coverage_targets.mutation,
    coverage_targets.path
) }}

## Code Quality

{{ examples.render_code_review_checklist(language) }}

## Pre-Deployment Verification

{{ checklists.render_deployment_checklist() }}
```

## Testing

All macro libraries have been tested for:
- Import compatibility
- Template composition (multiple imports in single template)
- Macro execution with various parameters

**Test Results:**
- ✓ All 6 macro libraries import successfully
- ✓ 30+ individual macros tested
- ✓ All context variables supported
- ✓ Multi-language support verified (Python, TypeScript)

**Run tests:**
```bash
python3 << 'EOF'
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('promptosaurus/prompts'))
template = env.get_template('macros/test_macros.jinja2')
context = {
    'language': 'python',
    'framework': 'pytest',
    'package_manager': 'uv',
    'coverage_targets': {
        'line': 80, 'branch': 70, 'function': 90,
        'statement': 85, 'mutation': 80, 'path': 60
    }
}
print(template.render(**context))
EOF
```

## Examples

### Generate Python Testing Guide

```jinja2
{% import 'macros/testing_sections.jinja2' as testing %}
{% import 'macros/checklist.jinja2' as checklists %}

# Python Testing Guide

{{ testing.render_testing_section('python', 'pytest', coverage_targets) }}

## Quality Checklist

{{ checklists.render_code_quality_checklist('python') }}
```

### Generate TypeScript Code Review Guide

```jinja2
{% import 'macros/code_examples.jinja2' as examples %}
{% import 'macros/checklist.jinja2' as checklists %}

# TypeScript Code Review Guide

{{ examples.render_code_review_checklist('typescript') }}

## Review Checklist

{{ checklists.render_review_checklist() }}
```

### Generate Naming Conventions Reference

```jinja2
{% import 'macros/naming_conventions.jinja2' as naming %}

# Naming Conventions

{{ naming.render_naming_conventions('python') }}
{{ naming.render_naming_examples('python') }}
{{ naming.render_naming_checklist('python') }}
```

## Extending Macros

To customize or extend macros, create a new template:

```jinja2
{% import 'macros/testing_sections.jinja2' as base_testing %}

{% macro custom_testing_guide(language) -%}
# Custom Testing Guide for {{ language | capitalize }}

{{ base_testing.render_testing_section(language, 'pytest', coverage_targets) }}

## Organization-Specific Guidance

Additional custom content here...

{%- endmacro %}
```

## Structure

```
macros/
├── __init__.jinja2              # Documentation and usage guide
├── testing_sections.jinja2      # Testing framework macros
├── coverage_targets.jinja2      # Coverage metrics macros
├── naming_conventions.jinja2    # Naming convention macros
├── code_examples.jinja2         # Code pattern example macros
├── error_handling.jinja2        # Error handling pattern macros
├── checklist.jinja2             # Checklist generation macros
├── test_macros.jinja2           # Test template for all macros
└── README.md                    # This file
```

## Notes

- All macros are language-aware and adapt output based on language parameter
- Macro libraries use Jinja2 native syntax for maximum compatibility
- Context variables are optional - macros provide sensible defaults
- Macros can be mixed and matched in any combination
- All templates are designed to work with existing promptosaurus config context

## Future Enhancements

Potential additions to macro libraries:
- API documentation generation macros
- Deployment strategy macros
- Security review checklists
- Performance optimization guides
- Architecture decision record templates
