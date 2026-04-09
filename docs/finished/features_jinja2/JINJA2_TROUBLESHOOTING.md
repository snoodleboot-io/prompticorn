# Jinja2 Template Troubleshooting Guide

## Common Issues and Solutions

This guide covers common template rendering issues and how to diagnose and fix them.

---

## Issue: Undefined Variables

### Symptom
Template rendering fails with `Undefined variable: X is not defined`

### Diagnosis
```python
# Check what variables are required
variables = renderer.validate_and_get_variables(template)
print(variables)  # ['user', 'config', ...]

# Check what's available
available = set(context.keys())
missing = set(variables) - available
print(f"Missing variables: {missing}")
```

### Solutions

**Solution 1: Add Missing Variable**
```python
context['missing_var'] = "value"
result = renderer.handle(template, context)
```

**Solution 2: Use Safe Filter**
```jinja2
{{ user | safe_get('email', default='noemail@example.com') }}
```

**Solution 3: Use Default Filter**
```jinja2
{{ undefined_var | default('fallback_value') }}
```

**Solution 4: Conditional Check**
```jinja2
{% if user %}
    Email: {{ user.email | default('No email') }}
{% else %}
    User not available
{% endif %}
```

**Solution 5: Enable Error Recovery**
```python
# Renders with placeholders instead of crashing
result = renderer.handle(template, context, allow_recovery=True)
# Output shows [UNDEFINED: var_name] where variables are missing
```

---

## Issue: Missing Templates

### Symptom
Template rendering fails with `Template 'name' not found in registry`

### Diagnosis
```python
# Check if template exists in registry
from promptosaurus.registry import registry
try:
    content = registry.prompt_body('template_name.md')
    print("Template found")
except Exception as e:
    print(f"Template not found: {e}")
```

### Solutions

**Solution 1: Create the Template**
```
Create the missing template file in the registry
```

**Solution 2: Use Different Template Name**
```python
# Check available templates
# Fix the reference name
```

**Solution 3: Register Fallback**
```python
renderer.register_fallback_template(
    'missing.md',
    '# Fallback Content'
)
result = renderer.handle_by_name('missing.md', context, allow_recovery=True)
```

**Solution 4: Use Conditional Include**
```jinja2
{% if template_exists %}
    {% include "optional_template.md" %}
{% endif %}
```

---

## Issue: Circular Template Inheritance

### Symptom
Template rendering fails with `Circular template inheritance detected: A -> B -> A`

### Diagnosis
```python
# Trace the inheritance chain
template_a = "{% extends 'template_b' %}"
template_b = "{% extends 'template_a' %}"
# This creates a circle!

# Use a validator to detect
is_valid, error = renderer._validate_template_syntax(template_a)
```

### Solutions

**Solution 1: Fix Inheritance Chain**
```
template_a.md: (no extends)
template_b.md: {% extends 'template_a.md' %}
template_c.md: {% extends 'template_b.md' %}
```

**Solution 2: Use Composition Instead**
```jinja2
<!-- Instead of inheritance, use includes -->
{% include 'header.md' %}
{% include 'content.md' %}
{% include 'footer.md' %}
```

**Solution 3: Check Depth Limit**
```
Max inheritance depth: 10 levels
If you have: A → B → C → D → E → F → G → H → I → J → K
This exceeds the limit!
```

---

## Issue: Syntax Errors

### Symptom
Template rendering fails with `Template syntax error: ...`

### Diagnosis
```python
is_valid, error_msg = renderer._validate_template_syntax(template)
if not is_valid:
    print(f"Syntax error: {error_msg}")
    # Shows exact line number and issue
```

### Common Syntax Errors

**Unclosed Tags**
```jinja2
<!-- WRONG: Missing endfor -->
{% for item in items %}
    {{ item }}

<!-- CORRECT: Has endfor -->
{% for item in items %}
    {{ item }}
{% endfor %}
```

**Wrong End Tags**
```jinja2
<!-- WRONG: Mismatched tags -->
{% if condition %}
    content
{% endblock %}  <!-- Wrong: should be endif -->

<!-- CORRECT: Matched tags -->
{% if condition %}
    content
{% endif %}
```

**Missing Quotes**
```jinja2
<!-- WRONG: No quotes -->
{% extends template_name %}

<!-- CORRECT: Quoted name -->
{% extends "template_name" %}
```

**Invalid Expressions**
```jinja2
<!-- WRONG: Invalid syntax -->
{{ item.name or }}

<!-- CORRECT: Valid syntax -->
{{ item.name or 'Unknown' }}
```

### Solutions

**Solution 1: Validate Early**
```python
is_valid, error = renderer._validate_template_syntax(template)
if not is_valid:
    logger.error(error)
    return None  # Handle error gracefully
```

**Solution 2: Use Linter**
```bash
# Some IDEs have Jinja2 linters
# Enable them to catch syntax errors early
```

**Solution 3: Test Incrementally**
```python
# Test template pieces individually
for piece in template.split('\n'):
    try:
        env.from_string(piece)
    except Exception as e:
        print(f"Error in line: {piece}")
```

---

## Issue: Type Mismatches in Filters

### Symptom
Filter fails with `Cannot apply filter to this type`

### Diagnosis
```python
# Check variable types
for key, value in context.items():
    print(f"{key}: {type(value).__name__} = {value!r}")

# Test filter with explicit type
try:
    result = some_filter(value)
except TypeError as e:
    print(f"Type mismatch: {e}")
```

### Solutions

**Solution 1: Use Type Conversion**
```jinja2
<!-- WRONG: String can't be used with math filter -->
{{ "42" + 8 }}

<!-- CORRECT: Convert to number first -->
{{ "42" | safe_int + 8 }}
```

**Solution 2: Use Safe Filters**
```jinja2
{{ value | safe_int(default=0) }}
{{ value | safe_str(default='N/A') }}
{{ value | safe_list(default=[]) }}
{{ value | safe_json(default={}) }}
```

**Solution 3: Check Type in Condition**
```jinja2
{% if value is string %}
    {{ value | upper }}
{% elif value is number %}
    {{ value | round }}
{% elif value is iterable %}
    {{ value | length }}
{% endif %}
```

**Solution 4: Convert Before Use**
```jinja2
{% set count = items | length %}
{% if count > 0 %}
    Total: {{ count }}
{% endif %}
```

---

## Issue: Macro Errors

### Symptom
Macro fails with `Missing required parameter X` or type mismatch

### Diagnosis
```python
# Check macro definition
macro_template = """
{% macro greeting(name, age) %}
    Hello {{ name }}, age {{ age }}
{% endmacro %}
"""

# Check calls
call_template = """
{{ greeting("John") }}  <!-- Missing age! -->
"""

# Validate before calling
```

### Solutions

**Solution 1: Provide All Required Parameters**
```jinja2
<!-- WRONG: Missing age -->
{{ greeting("John") }}

<!-- CORRECT: All parameters -->
{{ greeting("John", 30) }}
```

**Solution 2: Use Default Values**
```jinja2
{% macro greeting(name, age=25) %}
    Hello {{ name }}, age {{ age }}
{% endmacro %}

<!-- Now optional -->
{{ greeting("John") }}  <!-- age defaults to 25 -->
{{ greeting("Jane", 28) }}  <!-- explicit age -->
```

**Solution 3: Handle Type Conversion**
```jinja2
{% macro sum_values(a, b) %}
    {% set a_num = a | safe_int(default=0) %}
    {% set b_num = b | safe_int(default=0) %}
    {{ a_num + b_num }}
{% endmacro %}

{{ sum_values("10", "20") }}  <!-- Converts strings to numbers -->
```

**Solution 4: Document Parameters**
```jinja2
{# Macro to calculate discounted price
   Parameters:
   - price: original price (number)
   - discount: discount percentage (number, 0-100)
   Returns: discounted price
#}
{% macro discounted_price(price, discount) %}
    {% set discount_num = discount | safe_int(default=0) %}
    {{ (price * (100 - discount_num) / 100) | round(2) }}
{% endmacro %}
```

---

## Issue: Missing Includes

### Symptom
Include fails with `Included template 'name' not found`

### Diagnosis
```python
# Check if included template exists
try:
    content = registry.prompt_body('included_template.md')
except Exception as e:
    print(f"Included template not found: {e}")

# Check references in template
includes = re.findall(r"{%\s*include\s+['\"]([^'\"]+)", template)
print(f"Includes: {includes}")
```

### Solutions

**Solution 1: Create the Included Template**
```
Create the missing template file in the registry
```

**Solution 2: Use Fallback Include**
```jinja2
<!-- Conditional include for optional content -->
{% if "sidebar.md" in available_templates %}
    {% include "sidebar.md" %}
{% else %}
    <!-- Default sidebar -->
{% endif %}
```

**Solution 3: Use Try/Except Pattern** (not natively supported, use recovery mode)
```python
# With recovery mode, missing includes degrade gracefully
result = renderer.handle(template, context, allow_recovery=True)
```

**Solution 4: Pass Variables to Include**
```jinja2
<!-- Include with explicit context -->
{% include "user_card.md" with context %}
{% include "stats.md" with context %}

<!-- Or pass specific variables -->
{% include "item_list.md" with items=cart_items %}
```

---

## Issue: Filter Errors

### Symptom
Filter fails with `Filter error: ...`

### Diagnosis
```python
# Test filter in isolation
try:
    result = custom_filter(value)
    print(f"Result: {result}")
except Exception as e:
    print(f"Filter error: {e}")
    print(f"Value type: {type(value)}")
    print(f"Value: {value!r}")
```

### Solutions

**Solution 1: Check Filter Exists**
```python
# List available filters
print(environment.filters.keys())

# Register missing filters if needed
from promptosaurus.builders.template_handlers.resolvers.custom_filters import (
    register_custom_filters,
)
register_custom_filters(environment)
```

**Solution 2: Use Safe Filters**
```jinja2
<!-- Safe filters handle errors gracefully -->
{{ value | safe_int(default=0) }}
{{ value | safe_str(default='N/A') }}
{{ value | safe_list(default=[]) }}
{{ value | safe_json(default={}) }}
{{ value | safe_regex(pattern='[0-9]+', replacement='X') }}
```

**Solution 3: Check Filter Arguments**
```jinja2
<!-- WRONG: Invalid argument -->
{{ text | indent(width="invalid") }}

<!-- CORRECT: Valid argument -->
{{ text | indent(4) }}
{{ text | indent(width=4) }}
```

**Solution 4: Chain Filters Carefully**
```jinja2
<!-- WRONG: Type mismatch after first filter -->
{{ items | first | length }}  <!-- first returns item, not list -->

<!-- CORRECT: Proper chaining -->
{{ items | length }}  <!-- Get length directly -->
{{ items | first }}  <!-- Get first item -->
{{ items | join(', ') }}  <!-- Join items -->
```

---

## Issue: Performance Problems

### Symptom
Template rendering is slow or times out

### Diagnosis
```python
import time

start = time.time()
result = renderer.handle(template, context)
elapsed = time.time() - start

print(f"Rendering took {elapsed:.2f}s")

# Check error log for repeated errors
errors = renderer.get_error_log()
print(f"Errors: {len(errors)}")
```

### Solutions

**Solution 1: Optimize Templates**
```jinja2
<!-- SLOW: Loop with condition inside -->
{% for item in items %}
    {% if item.active %}
        {{ item.name }}
    {% endif %}
{% endfor %}

<!-- FASTER: Filter before loop -->
{% for item in active_items %}
    {{ item.name }}
{% endfor %}
```

**Solution 2: Use Caching**
```python
# Templates are automatically cached
# Cache is based on template content hash
# First render: ~5ms
# Second render: ~1ms (cached)
```

**Solution 3: Reduce Template Complexity**
```jinja2
<!-- Break complex templates into smaller pieces -->
{% include "header.md" %}
{% include "content.md" %}
{% include "footer.md" %}

<!-- Instead of one giant template -->
```

**Solution 4: Limit Recursion**
```
Template inheritance depth limit: 10 levels
If exceeding, either:
1. Simplify inheritance chain
2. Use includes instead
3. Increase limit (if aware of performance impact)
```

---

## Debugging Techniques

### Enable Verbose Logging

```python
import logging

# Set to DEBUG for detailed logs
logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger('promptosaurus.builders.template_handlers.resolvers')
logger.setLevel(logging.DEBUG)

# Now all template operations are logged
```

### Inspect Error Log

```python
# Get detailed error history
errors = renderer.get_error_log()

for error in errors:
    print(f"Error: {error['error_type']}")
    print(f"  Message: {error['message']}")
    print(f"  Template: {error['template_name']}")
    print(f"  Variables: {error.get('available_variables', [])}")
    print()

# Clear for next batch
renderer.clear_error_log()
```

### Test with Simple Templates

```python
# Start with simplest template
simple = "{{ x }}"
result = renderer.handle(simple, {"x": 1})
assert result == "1"

# Gradually increase complexity
with_filter = "{{ x | upper }}"
result = renderer.handle(with_filter, {"x": "hello"})
assert result == "HELLO"

# Test full template
full = """
{% if condition %}
    {{ content }}
{% endif %}
"""
result = renderer.handle(full, {"condition": True, "content": "Hello"})
```

### Use Recovery Mode for Diagnosis

```python
# Enable recovery to see what errors occur
result = renderer.handle(
    template,
    context,
    allow_recovery=True
)

# Check error log to see what went wrong
errors = renderer.get_error_log()
for error in errors:
    print(f"Issue: {error['message']}")
```

### Check Variable Availability

```python
# Before rendering, check what template needs
required = renderer.validate_and_get_variables(template)
available = set(context.keys())

missing = set(required) - available
if missing:
    print(f"Missing variables: {missing}")
    # Add them to context
    for var in missing:
        context[var] = None  # or some default

result = renderer.handle(template, context)
```

---

## Production Troubleshooting

### Monitor Error Rates

```python
# Track errors over time
from collections import defaultdict

error_counts = defaultdict(int)

errors = renderer.get_error_log()
for error in errors:
    error_counts[error['error_type']] += 1

print("Error summary:")
for error_type, count in sorted(error_counts.items(), key=lambda x: -x[1]):
    print(f"  {error_type}: {count}")
```

### Set Up Alerts

```python
# Alert if errors exceed threshold
errors = renderer.get_error_log()
if len(errors) > 100:
    logger.critical("Template error rate exceeded threshold!")
    # Notify operations team
    send_alert("High template error rate")

# Alert on specific error types
error_types = {e['error_type'] for e in errors}
if 'circular_reference' in error_types:
    logger.error("Circular reference detected in templates!")
```

### Recovery Statistics

```python
# Track recovery rate
errors = renderer.get_error_log()
recovery_errors = [e for e in errors if 'recovery' in e['message']]

if errors:
    recovery_rate = len(recovery_errors) / len(errors)
    print(f"Recovery rate: {recovery_rate * 100:.1f}%")
    
    # If recovery rate is high, investigate
    if recovery_rate > 0.3:
        logger.warning("High error recovery rate - check templates")
```

---

## Summary

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| Undefined variable | `check_missing_variables()` | Add variable or use safe filter |
| Missing template | Check registry | Create template or register fallback |
| Circular inheritance | Trace chain | Fix chain or use includes |
| Syntax error | `_validate_template_syntax()` | Fix Jinja2 syntax |
| Type mismatch | Type check value | Use `safe_*` filters or convert |
| Macro error | Check parameters | Provide all args or use defaults |
| Missing include | Check registry | Create or use conditional include |
| Filter error | Test in isolation | Use safe filters or check args |
| Performance | Time rendering | Optimize template or cache |

For more help, check the main error handling documentation and enable detailed logging.
