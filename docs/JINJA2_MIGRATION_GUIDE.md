# Jinja2 Template Migration Guide

## Overview

This document provides a comprehensive guide for migrating from the legacy string replacement template system to the new Jinja2-based templating system implemented in the promptosaurus codebase.

## Background

The legacy system used simple string replacement with `{variable}` syntax and basic filter support. The new system leverages Jinja2, a powerful templating engine that provides:

- Advanced variable interpolation with `{{variable}}` syntax
- Built-in filters and custom filter support
- Control structures (conditionals, loops)
- Template inheritance and includes
- Macros for reusable template components
- Comprehensive error handling and validation
- Performance optimizations with caching

## Key Changes

### Syntax Changes

| Legacy Syntax | Jinja2 Syntax | Description |
|---------------|---------------|-------------|
| `{variable}` | `{{variable}}` | Variable interpolation |
| `{value\|filter}` | `{{value \| filter}}` | Filter application |
| N/A | `{% if condition %}` | Conditional blocks |
| N/A | `{% for item in items %}` | Loop constructs |
| N/A | `{% macro name(params) %}` | Reusable macros |
| N/A | `{% include 'template' %}` | Template includes |

### API Changes

- **Old:** `TemplateHandler.handle(content, variables)`
- **New:** `Jinja2TemplateRenderer.render(content, variables)`

### Dependency Injection

The new system uses sweet_tea's AbstractFactory pattern for dependency injection:

```python
# Old
template_handler = TemplateHandler()

# New
renderer = factory.create()  # Via sweet_tea factory
```

## Migration Steps

### 1. Update Template Syntax

Convert all templates from legacy syntax to Jinja2 syntax:

**Before:**
```
Welcome {user.name}! Your balance is {balance|currency}.
```

**After:**
```
Welcome {{user.name}}! Your balance is {{balance | currency}}.
```

### 2. Convert Control Structures

Replace any custom logic with Jinja2 constructs:

**Before (pseudo-code):**
```
{user.name}
{if user.is_premium}
  Premium features available
{/if}
```

**After:**
```
{{user.name}}
{% if user.is_premium %}
  Premium features available
{% endif %}
```

### 3. Update Code References

Replace TemplateHandler usage with Jinja2TemplateRenderer:

```python
# Before
from promptosaurus.builders.template_handlers.template_handler import TemplateHandler

handler = TemplateHandler()
result = handler.handle(template, variables)

# After
from promptosaurus.builders.template_handlers.resolvers.jinja2_template_renderer import Jinja2TemplateRenderer

renderer = Jinja2TemplateRenderer()
result = renderer.render(template, variables)
```

### 4. Leverage New Features

Take advantage of Jinja2's advanced features:

```jinja2
{# Loops #}
{% for item in shopping_cart %}
  - {{item.name}}: ${{item.price}}
{% endfor %}

{# Conditionals #}
{% if user.age >= 18 %}
  Adult content available
{% else %}
  Please verify age
{% endif %}

{# Filters #}
{{user.email | lower}}
{{current_date | strftime('%Y-%m-%d')}}

{# Macros #}
{% macro render_user(user) %}
  <div class="user">
    <h3>{{user.name}}</h3>
    <p>{{user.bio}}</p>
  </div>
{% endmacro %}

{# Includes #}
{% include 'header.html' %}
{% include 'footer.html' %}
```

## Validation and Testing

### Use Validation Tools

Validate migrated templates with the provided utilities:

```bash
# Validate single template
python template_validation_script.py template.txt

# Validate with variables
python template_validation_script.py --variables '{"name": "test"}' template.txt

# Generate validation report
python template_validation_script.py --report report.json templates/
```

### Performance Testing

Benchmark template rendering performance:

```bash
# Basic benchmark
python template_performance_benchmark.py template.txt variables.json

# Compare cache configurations
python template_performance_benchmark.py --cache-sizes 0,50,400 template.txt variables.json
```

## Error Handling

The new system provides comprehensive error handling:

- **TemplateSyntaxError:** Invalid Jinja2 syntax
- **TemplateRenderingError:** Runtime rendering errors
- **TemplateValidationError:** Pre-rendering validation failures
- **TemplateMigrationError:** Migration-related errors

## Performance Optimizations

### Caching

Enable template caching for better performance:

```python
renderer = Jinja2TemplateRenderer(cache_size=400)  # Cache up to 400 templates
```

### Async Support

Enable async rendering for I/O-bound operations:

```python
renderer = Jinja2TemplateRenderer(enable_async=True)
result = await renderer.render_async(template, variables)
```

## Troubleshooting

### Common Issues

1. **UndefinedError:** Variable not provided
   - Solution: Ensure all required variables are passed to render()

2. **TemplateSyntaxError:** Invalid syntax
   - Solution: Use validation tools to check syntax

3. **Performance Issues:** Slow rendering
   - Solution: Enable caching, check cache size, use async rendering

### Debugging

Enable debug mode for detailed error information:

```python
renderer = Jinja2TemplateRenderer(environment_options={'undefined': jinja2.DebugUndefined})
```

## Best Practices

1. **Validate Templates:** Always validate templates before deployment
2. **Use Filters:** Leverage Jinja2's built-in filters for data formatting
3. **Enable Caching:** Use appropriate cache sizes for your use case
4. **Handle Errors:** Implement proper error handling for template failures
5. **Test Performance:** Regularly benchmark template rendering performance

## Migration Checklist

- [ ] Convert all `{variable}` to `{{variable}}`
- [ ] Update filter syntax from `{value|filter}` to `{{value | filter}}`
- [ ] Replace custom control logic with Jinja2 constructs
- [ ] Update code to use new renderer API
- [ ] Enable appropriate caching and performance optimizations
- [ ] Validate all templates with validation tools
- [ ] Test error handling scenarios
- [ ] Benchmark performance improvements

## Support

For migration assistance or issues, refer to:
- This migration guide
- Template validation and performance tools
- Updated API documentation
- Test suites for examples

The new Jinja2 system provides significant improvements in functionality, performance, and maintainability over the legacy string replacement system.
