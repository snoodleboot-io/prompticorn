# Jinja2 Template Error Handling Guide

## Overview

Phase 4C implements comprehensive error handling for production safety in the Jinja2 template system. The system provides:

- **Graceful error recovery** - Templates degrade gracefully instead of crashing
- **Missing template handling** - Fallback templates for missing includes
- **Undefined variable detection** - Smart suggestions for misspelled variables
- **Circular reference detection** - Prevents infinite loops in template inheritance
- **Safe filters** - Error-tolerant filters for common operations
- **Error logging** - Comprehensive error tracking for diagnostics

## Quick Start

### Enable Error Recovery

```python
from promptosaurus.builders.builder import Builder

# Create builder (error recovery enabled by default)
builder = Builder()

# Render with recovery enabled (graceful degradation)
result = builder._jinja2_renderer.handle(
    template_content,
    variables,
    allow_recovery=True  # Optional: errors don't crash rendering
)

# Or disable recovery for strict validation
result = builder._jinja2_renderer.handle(
    template_content,
    variables,
    allow_recovery=False  # Raise errors instead
)
```

### Register Fallback Templates

```python
# Register fallback content for missing templates
renderer.register_fallback_template(
    "missing_template.md",
    "# Fallback Content\n\nDefault content for missing templates"
)

# Now if template is missing, fallback will be used
result = renderer.handle_by_name(
    "missing_template.md",
    variables,
    allow_recovery=True
)
```

## Features

### 1. Missing Template Handling

**Problem:** Templates reference other templates that don't exist

```jinja2
{% include "missing_partial.md" %}
{% extends "base_template.md" %}
```

**Solution:** Fallback templates and graceful degradation

```python
# Register fallback
renderer.register_fallback_template(
    "missing_partial.md",
    "<!-- Partial unavailable -->"
)

# With recovery, uses fallback
result = renderer.handle_by_name(
    "my_template.md",
    variables,
    allow_recovery=True
)
# Returns content with fallback inserted
```

### 2. Undefined Variable Detection

**Problem:** Templates access variables not provided in context

```jinja2
Hello {{ user.name }}
Email: {{ user.email }}
```

**Solution:** Early detection with helpful suggestions

```python
# Check for undefined variables
result = renderer.check_missing_variables(
    template_content,
    {"user": {"name": "John"}}  # Missing 'email'
)

# Returns: {
#   "undefined": [
#     {"variable": "user", "suggestions": ["user_name", "user_email"]}
#   ],
#   "total_required": 2
# }
```

**With recovery:** Variables are replaced with placeholders

```jinja2
Hello {{ user.name }}
Email: [UNDEFINED: user.email]
```

### 3. Circular Reference Detection

**Problem:** Templates inherit from each other in a circle

```
template_a.md → extends template_b.md
template_b.md → extends template_a.md
```

**Solution:** Depth limiting and cycle detection

```python
try:
    result = renderer.handle(
        template_with_circular_ref,
        variables,
        allow_recovery=False  # Detect and report cycle
    )
except TemplateRenderingError as e:
    # Error: "Circular template inheritance detected: template_a -> template_b -> template_a"
    print(e)
```

### 4. Macro Error Handling

**Problem:** Macros called with wrong arguments or types

```jinja2
{% macro greet(name, age) %}
    Hello {{ name }}, you are {{ age }} years old
{% endmacro %}

{{ greet("John") }}  <!-- Missing age parameter -->
```

**Solution:** Validation and recovery

```python
# Without recovery: raises TemplateRenderingError
# With recovery: produces output with error markers
result = renderer.handle(template, {}, allow_recovery=True)
# Output includes error information
```

### 5. Filter Error Handling

**Problem:** Filters receive invalid arguments or data

```jinja2
{{ "hello" | indent(width="invalid") }}
{{ value | custom_filter }}  <!-- Custom filter doesn't exist -->
```

**Solution:** Safe filters with fallback values

```jinja2
{{ value | safe_int(default=0) }}           <!-- Returns 0 if not a number -->
{{ text | safe_str(default='N/A') }}        <!-- Returns 'N/A' if conversion fails -->
{{ config.items | safe_list(default=[]) }}  <!-- Returns [] if not a list -->
{{ json_str | safe_json(default={}) }}      <!-- Returns {} if not valid JSON -->
```

### 6. Template Syntax Validation

**Problem:** Malformed Jinja2 syntax causes rendering errors

```jinja2
{% if condition %}
    Content
{% endif  <!-- Missing closing % -->
```

**Solution:** Early validation with line numbers

```python
is_valid, error_msg = renderer._validate_template_syntax(template)
if not is_valid:
    print(f"Syntax error: {error_msg}")
    # Output: "Syntax error at line 3: unexpected end of template"
```

## Safe Filters Reference

Safe filters gracefully handle errors and provide fallback values.

### safe_get

Get nested values with fallback

```jinja2
{{ config | safe_get('database.host', 'localhost') }}
<!-- Returns 'localhost' if database.host not found -->

{{ user | safe_get('profile.bio', default='No bio provided') }}
```

### safe_int

Convert to integer with error handling

```jinja2
{{ "42" | safe_int(default=0) }}        <!-- Returns 42 -->
{{ "invalid" | safe_int(default=0) }}   <!-- Returns 0 -->
{{ "42ms" | safe_int(default=0) }}      <!-- Returns 42 (strips units) -->
```

### safe_str

Convert to string with fallback

```jinja2
{{ value | safe_str(default='N/A') }}
{{ None | safe_str(default='None') }}    <!-- Returns 'None' -->
{{ ["a", "b"] | safe_str }}             <!-- Returns '["a", "b"]' -->
```

### safe_list

Convert to list with fallback

```jinja2
{{ "a,b,c" | safe_list }}               <!-- Returns ['a', 'b', 'c'] -->
{{ value | safe_list(default=[]) }}     <!-- Returns [] if not list-like -->
```

### safe_json

Parse JSON with fallback

```jinja2
{{ '{"key": "value"}' | safe_json }}         <!-- Returns parsed dict -->
{{ "invalid" | safe_json(default={}) }}      <!-- Returns {} on parse error -->
```

### safe_regex

Apply regex with fallback

```jinja2
{{ text | safe_regex(pattern='[0-9]+', replacement='X') }}
{{ value | safe_regex(pattern='[invalid', replacement='', default=value) }}
```

### safe_list conversion

Convert various types to list

```jinja2
{{ [1, 2, 3] | safe_list }}         <!-- Already a list -->
{{ (1, 2, 3) | safe_list }}         <!-- Converts tuple -->
{{ {"a": 1, "b": 2} | safe_list }}  <!-- Converts dict values to list -->
{{ None | safe_list(default=[]) }}  <!-- Returns empty list -->
```

## Error Recovery Strategies

### Strategy 1: Graceful Degradation (Default)

With `allow_recovery=True`, templates render with error markers instead of crashing.

**Undefined variables:** Replaced with `[UNDEFINED: varname]`
**Missing templates:** Replaced with `[MISSING TEMPLATE: name]`
**Runtime errors:** Replaced with `[RUNTIME ERROR: ...]`

### Strategy 2: Strict Validation

With `allow_recovery=False`, errors are raised immediately.

```python
try:
    result = renderer.handle(template, variables, allow_recovery=False)
except TemplateRenderingError as e:
    # Handle error with full context
    print(e.template_content)
    print(e.variables)
    print(e.original_error)
```

### Strategy 3: Error Logging

All errors are recorded in the error log for diagnostics.

```python
# Get error history
errors = renderer.get_error_log()

for error in errors:
    print(f"Type: {error['error_type']}")
    print(f"Message: {error['message']}")
    print(f"Template: {error['template_name']}")
    print(f"Severity: {error['severity']}")

# Clear log
renderer.clear_error_log()
```

## Best Practices

### 1. Use Safe Filters in Production

```jinja2
<!-- Good: handles missing values -->
{{ config | safe_get('database.host', 'localhost') }}

<!-- Avoid: will crash if config.database is None -->
{{ config.database.host }}
```

### 2. Validate Templates Early

```python
# Check syntax before rendering
is_valid, error_msg = renderer._validate_template_syntax(template)
if not is_valid:
    logger.error(f"Invalid template: {error_msg}")
    return None  # Or use fallback

# Check for undefined variables
missing = renderer.check_missing_variables(template, context)
if missing["undefined"]:
    logger.warning(f"Undefined variables: {missing}")
    # Either error or recover with defaults
```

### 3. Handle Recovery Mode

```python
# Always use recovery for user-provided templates
result = renderer.handle(
    user_template,
    context,
    allow_recovery=True
)

# Use strict mode for system templates
result = renderer.handle(
    system_template,
    context,
    allow_recovery=False
)
```

### 4. Provide Helpful Context

```python
# Include available variables in error context
variables = {
    "config": {...},
    "user": {...},
    "system": {...},
}

result = renderer.handle(
    template,
    variables,
    allow_recovery=True
)

# If error occurs, logs will show available variables
```

### 5. Use Fallback Templates

```python
# Register fallbacks for critical templates
critical_templates = [
    ("base.md", "# Default Base Template"),
    ("footer.md", "<!-- Footer -->"),
    ("errors/404.md", "# 404 Not Found"),
]

for name, fallback in critical_templates:
    renderer.register_fallback_template(name, fallback)
```

## Error Diagnostics

### View Error Log

```python
errors = renderer.get_error_log()

# Example error record:
# {
#     'error_type': 'undefined_variable',
#     'template_name': 'my_template.md',
#     'line_number': 5,
#     'available_variables': ['config', 'user', 'debug'],
#     'original_error': {
#         'type': 'UndefinedError',
#         'message': "name 'email' is undefined"
#     },
#     'message': "Undefined variable in template: name 'email' is undefined",
#     'severity': 'warning'
# }
```

### Get Error Suggestions

```python
from promptosaurus.builders.template_handlers.resolvers.error_recovery import (
    ErrorContextBuilder,
)

# Get suggestion for fix
suggestion = ErrorContextBuilder.suggest_fix(
    'undefined_variable',
    {'variable_name': 'config.debug'}
)
# "Check if 'config.debug' is passed to the template context"
```

### Enable Detailed Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now all template errors are logged with details
result = renderer.handle(template, variables)
# Logs will show what variables are available, what was missing, etc.
```

## Performance Considerations

### Template Caching

Templates are cached after compilation for performance:

```python
# First render: template is compiled
result1 = renderer.handle(template, vars1)  # ~5ms

# Second render: uses cached compiled template
result2 = renderer.handle(template, vars2)  # ~1ms
```

### Error Log Size

Error log grows with each error. Clear periodically:

```python
# Clear after processing
if len(renderer.get_error_log()) > 100:
    renderer.clear_error_log()
```

## Testing Error Handling

Example test for error handling:

```python
import pytest
from promptosaurus.builders.template_handlers.resolvers import (
    Jinja2TemplateRenderer,
    TemplateRenderingError,
)

def test_undefined_variable_recovery():
    renderer = Jinja2TemplateRenderer(environment)
    
    template = "Hello {{ name }}"
    
    # Without recovery: raises error
    with pytest.raises(TemplateRenderingError):
        renderer.handle(template, {}, allow_recovery=False)
    
    # With recovery: provides placeholders
    result = renderer.handle(template, {}, allow_recovery=True)
    assert "[UNDEFINED" in result or "{{ name }}" in result

def test_fallback_templates():
    renderer = Jinja2TemplateRenderer(environment)
    renderer.register_fallback_template("missing.md", "Fallback")
    
    # With recovery and fallback: uses fallback
    result = renderer.handle_by_name("missing.md", {}, allow_recovery=True)
    assert "Fallback" in result
```

## Production Checklist

- [ ] Enable error recovery for user-facing templates
- [ ] Register fallback templates for critical resources
- [ ] Use safe filters for external data access
- [ ] Validate templates early in build process
- [ ] Monitor error log for recurring issues
- [ ] Log all production errors for analysis
- [ ] Test error recovery with malformed templates
- [ ] Document template variable requirements
- [ ] Provide helpful error messages to users
- [ ] Review and handle edge cases

## Summary

The comprehensive error handling system ensures zero unhandled exceptions in production through:

1. **Early validation** - Detect errors before rendering
2. **Graceful recovery** - Degrade gracefully when errors occur
3. **Safe filters** - Handle errors in filter operations
4. **Fallback templates** - Provide fallback content for missing templates
5. **Error logging** - Track all errors for diagnostics
6. **Smart suggestions** - Help users fix template issues

This enables robust template rendering for production systems while maintaining helpful error messages for developers.
