# Jinja2 API Reference

**Version:** 1.0  
**Date:** April 2026  
**Audience:** Template Developers, API Consumers

---

## Table of Contents

1. [Variable Syntax](#variable-syntax)
2. [Built-in Filters](#built-in-filters)
3. [Custom Filters](#custom-filters)
4. [Template Tags](#template-tags)
5. [Tests](#tests)
6. [Global Functions](#global-functions)

---

## Variable Syntax

### Basic Variable Access

```jinja2
{{ variable }}                    # Simple variable
{{ object.attribute }}            # Attribute access
{{ object['key'] }}               # Dictionary access
{{ list[0] }}                     # List index
{{ list[-1] }}                    # Negative index (last item)
```

### Variable Examples

```jinja2
# All of these access the same value if data structure permits:
{{ user.email }}
{{ user['email'] }}
{{ data.user.email }}
{{ data['user']['email'] }}

# With nested lists and dictionaries:
{{ users[0].name }}
{{ config['database']['host'] }}
{{ matrix[0][1] }}
```

### Undefined Behavior

```jinja2
# Undefined variables render as empty string (no error by default)
{{ undefined_variable }}          # → ''

# Check if defined
{% if variable is defined %}
  {{ variable }}
{% endif %}

# Use default filter for safety
{{ undefined_var | default('fallback') }}
```

---

## Built-in Filters

### String Filters

#### `upper` - Convert to uppercase
```jinja2
{{ "hello" | upper }}             # → HELLO
{{ name | upper }}                # Alice → ALICE
```

#### `lower` - Convert to lowercase
```jinja2
{{ "HELLO" | lower }}             # → hello
{{ NAME | lower }}                # ALICE → alice
```

#### `title` - Title case
```jinja2
{{ "hello world" | title }}       # → Hello World
{{ sentence | title }}            # converts each word first letter
```

#### `capitalize` - Capitalize first letter
```jinja2
{{ "hello world" | capitalize }}  # → Hello world
{{ text | capitalize }}           # Only first letter capitalized
```

#### `replace` - Replace text
```jinja2
{{ "hello" | replace("l", "L") }} # → heLLo
{{ url | replace(" ", "-") }}
```

#### `trim` - Remove whitespace
```jinja2
{{ "  hello  " | trim }}          # → hello
{{ text | trim }}
```

#### `truncate` - Truncate text
```jinja2
{{ "hello world" | truncate(8) }} # → hello...
{{ long_text | truncate(50, True, '...') }}

# Parameters:
# - length: max length (default: 255)
# - killwords: keep words intact (default: False)
# - end: suffix when truncated (default: '...')
```

#### `wordwrap` - Wrap text at width
```jinja2
{{ text | wordwrap(40) }}         # Wrap at 40 chars

# Parameters:
# - width: character width (default: 79)
# - break_long_words: break long words (default: False)
```

#### `center` - Center text
```jinja2
{{ "hello" | center(11) }}        # →    hello    
{{ text | center(50) }}
```

#### `ljust` - Left justify
```jinja2
{{ "hello" | ljust(10) }}         # → hello     
{{ text | ljust(20) }}
```

#### `rjust` - Right justify
```jinja2
{{ "hello" | rjust(10) }}         # →      hello
{{ text | rjust(20) }}
```

#### `indent` - Indent text
```jinja2
{{ code | indent(2) }}            # Indent by 2 spaces
{{ text | indent(4, True) }}      # Indent 4 spaces, first line too
```

#### `urlencode` - URL encode
```jinja2
{{ "hello world" | urlencode }}   # → hello%20world
{{ string | urlencode }}
```

#### `urlize` - Convert URLs to links
```jinja2
{{ "Visit http://example.com" | urlize }}
# → Visit <a href="...">http://example.com</a>
```

#### `wordcount` - Count words
```jinja2
{{ "hello world" | wordcount }}   # → 2
{{ text | wordcount }}
```

#### `string` - Convert to string
```jinja2
{{ 123 | string }}                # → '123'
{{ value | string }}
```

### Numeric Filters

#### `abs` - Absolute value
```jinja2
{{ -5 | abs }}                    # → 5
{{ number | abs }}
```

#### `round` - Round number
```jinja2
{{ 3.14159 | round }}             # → 3
{{ 3.14159 | round(2) }}          # → 3.14
{{ price | round(2) }}            # Round to cents
```

#### `int` - Convert to integer
```jinja2
{{ "123" | int }}                 # → 123
{{ 3.7 | int }}                   # → 3
{{ value | int }}
```

#### `float` - Convert to float
```jinja2
{{ "3.14" | float }}              # → 3.14
{{ 3 | float }}                   # → 3.0
{{ value | float }}
```

### List Filters

#### `length` - Get length
```jinja2
{{ [1, 2, 3] | length }}          # → 3
{{ "hello" | length }}            # → 5
{{ items | length }}
```

#### `join` - Join list items
```jinja2
{{ ['a', 'b', 'c'] | join(', ') }} # → a, b, c
{{ tags | join(' | ') }}
{{ lines | join('\n') }}
```

#### `first` - Get first item
```jinja2
{{ [1, 2, 3] | first }}           # → 1
{{ items | first }}
```

#### `last` - Get last item
```jinja2
{{ [1, 2, 3] | last }}            # → 3
{{ items | last }}
```

#### `unique` - Remove duplicates
```jinja2
{{ [1, 2, 2, 3] | unique | list }} # → [1, 2, 3]
{{ items | unique }}

# Keep order with list conversion
{{ items | unique | list }}
```

#### `select` - Filter items
```jinja2
{{ numbers | select("odd") | list }}    # Filter odd numbers
{{ items | select("defined") | list }}  # Keep defined items
```

#### `reject` - Inverse filter
```jinja2
{{ numbers | reject("odd") | list }}    # Keep even numbers
{{ items | reject("undefined") }}
```

#### `map` - Transform items
```jinja2
{{ users | map(attribute="name") | list }}
{{ items | map("upper") | list }}
```

#### `sort` - Sort list
```jinja2
{{ [3, 1, 2] | sort }}            # → [1, 2, 3]
{{ items | sort }}
```

#### `reverse` - Reverse list
```jinja2
{{ [1, 2, 3] | reverse | list }}  # → [3, 2, 1]
{{ items | reverse }}
```

#### `shuffle` - Randomize order
```jinja2
{{ items | shuffle }}             # Random order
```

#### `batch` - Group items
```jinja2
{{ items | batch(3) | list }}     # Group into 3-item batches
{{ products | batch(4) }}
```

#### `slice` - Slice list
```jinja2
{{ items | slice(2) }}            # Slice into 2 parts
{{ list | slice(3, True) }}       # Fill incomplete groups
```

#### `sum` - Sum numeric values
```jinja2
{{ [1, 2, 3] | sum }}             # → 6
{{ prices | sum }}

# Sum attribute values
{{ items | sum(attribute="price") }}
```

#### `min` - Minimum value
```jinja2
{{ [3, 1, 2] | min }}             # → 1
{{ numbers | min }}
```

#### `max` - Maximum value
```jinja2
{{ [3, 1, 2] | max }}             # → 3
{{ numbers | max }}
```

### Default and Other Filters

#### `default` - Provide default value
```jinja2
{{ undefined_var | default("fallback") }}  # → fallback
{{ "" | default("empty") }}                # → empty
{{ false_val | default("no value") }}      # → no value

# Only if completely undefined
{{ var | default("fallback", true) }}
```

#### `safe` - Mark as safe HTML
```jinja2
{{ html_content | safe }}         # Don't escape HTML
{{ generated_markup | safe }}

# ONLY use on trusted content!
```

#### `escape` - Escape special chars
```jinja2
{{ "<script>" | escape }}         # → &lt;script&gt;
{{ user_input | escape }}
```

#### `striptags` - Remove HTML tags
```jinja2
{{ "<p>hello</p>" | striptags }}  # → hello
{{ html_content | striptags }}
```

#### `tojson` - Convert to JSON
```jinja2
{{ {"name": "Alice"} | tojson }}  # → {"name": "Alice"}
{{ data | tojson }}
```

#### `fromjson` - Parse JSON
```jinja2
{{ '{"name": "Alice"}' | fromjson }}  # → {name: Alice}
{{ json_string | fromjson }}
```

### Filter Chain Examples

```jinja2
# Convert string, uppercase, get length
{{ text | string | upper | length }}

# List of numbers: sum, convert to string, right justify
{{ numbers | sum | string | rjust(10) }}

# Get unique items, sort, join with commas
{{ items | unique | sort | join(", ") }}

# User names: get names, uppercase, join
{{ users | map(attribute="name") | map("upper") | join(", ") }}

# Complex: filter active items, get names, sort, join
{{ users 
   | selectattr("is_active") 
   | map(attribute="name") 
   | sort 
   | join(", ") 
}}
```

---

## Custom Filters

### Case Conversion Filters

#### `camel_case` - Convert to camelCase
```jinja2
{{ "hello_world" | camel_case }}  # → helloWorld
{{ "hello-world" | camel_case }}  # → helloWorld
{{ text | camel_case }}
```

#### `pascal_case` - Convert to PascalCase
```jinja2
{{ "hello_world" | pascal_case }} # → HelloWorld
{{ "hello-world" | pascal_case }} # → HelloWorld
{{ class_name | pascal_case }}
```

#### `snake_case` - Convert to snake_case
```jinja2
{{ "HelloWorld" | snake_case }}   # → hello_world
{{ "hello-world" | snake_case }}  # → hello_world
{{ variable_name | snake_case }}
```

#### `kebab_case` - Convert to kebab-case
```jinja2
{{ "HelloWorld" | kebab_case }}   # → hello-world
{{ "hello_world" | kebab_case }}  # → hello-world
{{ url_slug | kebab_case }}
```

#### `title_case` - Convert to Title Case
```jinja2
{{ "hello world" | title_case }}  # → Hello World
{{ sentence | title_case }}
```

### Special Filters

#### `pluralize` - Pluralize English words
```jinja2
{{ "cat" | pluralize }}           # → cats
{{ "dog" | pluralize }}           # → dogs
{{ item_name | pluralize }}

# With count
{{ count }} {{ item | pluralize(count) }}  # "1 cat" or "5 cats"
```

### Safe Filters for Error Handling

#### `safe_get` - Safe dictionary access
```jinja2
{{ config | safe_get("database.host") }}    # Safe nested access
{{ data | safe_get("user.profile.name") }}
```

#### `safe_int` - Safe integer conversion
```jinja2
{{ "123" | safe_int }}            # → 123
{{ "invalid" | safe_int(0) }}     # → 0 (default)
{{ value | safe_int }}
```

#### `safe_str` - Safe string conversion
```jinja2
{{ none_value | safe_str("unknown") }}  # → "unknown"
{{ value | safe_str }}
```

#### `safe_list` - Ensure is list
```jinja2
{{ item | safe_list }}            # Single item → [item]
{{ [1, 2] | safe_list }}          # Already list → [1, 2]
{{ undefined | safe_list([]) }}   # Undefined → []
```

#### `safe_html` - Safe HTML validation
```jinja2
{{ user_html | safe_html }}       # Validates and escapes unsafe HTML
{{ html_content | safe_html }}
```

---

## Template Tags

### Variable Assignment

#### `set` - Set a variable
```jinja2
{% set name = "Alice" %}
{{ name }}                        # → Alice

{% set age = 25 %}
{% set is_admin = true %}

# Block assignment
{% set content %}
  Multi-line
  content
  here
{% endset %}
{{ content }}
```

### Control Flow

#### `if` / `elif` / `else` - Conditional
```jinja2
{% if condition %}
  <p>True branch</p>
{% elif other_condition %}
  <p>Elif branch</p>
{% else %}
  <p>False branch</p>
{% endif %}
```

#### `for` - Loop
```jinja2
{% for item in items %}
  {{ item }}
{% endfor %}

# With else (when list is empty)
{% for item in items %}
  {{ item }}
{% else %}
  <p>No items</p>
{% endfor %}

# Loop variable access
{% for item in items %}
  {{ loop.index }}: {{ item }}  {# 1-indexed #}
{% endfor %}
```

#### `while` - While loop
```jinja2
{% set i = 0 %}
{% while i < 5 %}
  {{ i }}
  {% set i = i + 1 %}
{% endwhile %}
```

### Template Composition

#### `extends` - Inherit from template
```jinja2
{% extends "base.html" %}

{% block content %}
  Child content
{% endblock %}
```

#### `block` - Define override block
```jinja2
{% block name %}
  Default content
{% endblock %}
```

#### `super()` - Include parent block
```jinja2
{% block content %}
  {{ super() }}  {# Parent content #}
  Child content
{% endblock %}
```

#### `include` - Include another template
```jinja2
{% include "header.html" %}
{% include "content.html" with context %}
{% include "footer.html" %}
```

#### `import` - Import macros
```jinja2
{% import "macros.html" as m %}
{{ m.render_card(item) }}

# Import specific macro
{% from "macros.html" import render_card %}
{{ render_card(item) }}
```

### Macro Definition

#### `macro` - Define reusable code
```jinja2
{% macro greeting(name) %}
  Hello {{ name }}!
{% endmacro %}

{{ greeting("Alice") }}

# With defaults
{% macro message(text, level="info") %}
  [{{ level | upper }}] {{ text }}
{% endmacro %}

# With caller
{% macro card(title) %}
  <div class="card">
    <h2>{{ title }}</h2>
    {{ caller() }}
  </div>
{% endmacro %}

{% call card("Title") %}
  <p>Content</p>
{% endcall %}
```

### Variable Scoping

#### `with` - Create local scope
```jinja2
{% with %}
  {% set x = 5 %}
  {{ x }}  {# 5 #}
{% endwith %}
{# x is no longer defined #}

# With initial values
{% with total = items | length %}
  Total: {{ total }}
{% endwith %}
```

### Comments

#### Comment syntax
```jinja2
{# This is a comment #}
{# Comments don't appear in output #}
{% comment %}
  Multi-line comment
  (using comment tag)
{% endcomment %}
```

---

## Tests

Tests check conditions. Syntax: `variable is test_name`

### Defined/Undefined

```jinja2
{% if var is defined %}Exists{% endif %}
{% if var is undefined %}Missing{% endif %}
{% if var is not defined %}Undefined{% endif %}
```

### Truth Value

```jinja2
{% if value is true %}Boolean true{% endif %}
{% if value is false %}Boolean false{% endif %}
{% if value %}Truthy{% endif %}
{% if not value %}Falsy{% endif %}
```

### Type Tests

```jinja2
{% if value is string %}Is string{% endif %}
{% if value is number %}Is number{% endif %}
{% if value is integer %}Is integer{% endif %}
{% if value is float %}Is float{% endif %}
{% if value is iterable %}Can loop{% endif %}
{% if value is mapping %}Is dict-like{% endif %}
{% if value is none %}Is None/null{% endif %}
```

### Comparison Tests

```jinja2
{% if value is odd %}Odd number{% endif %}
{% if value is even %}Even number{% endif %}
{% if value is divisibleby(2) %}Divisible by 2{% endif %}
```

### Collection Tests

```jinja2
{% if items is empty %}No items{% endif %}
{% if items is not empty %}Has items{% endif %}
{% if item in items %}Item exists{% endif %}
```

### Test Examples

```jinja2
{# Type checking #}
{% if age is integer and age >= 18 %}
  Adult
{% endif %}

{# Collection validation #}
{% if users is iterable and users is not empty %}
  {% for user in users %}
    {{ user.name }}
  {% endfor %}
{% endif %}

{# Conditional rendering #}
{% if config is defined and config is mapping %}
  {% for key, value in config.items() %}
    {{ key }}: {{ value }}
  {% endfor %}
{% endif %}
```

---

## Global Functions

### `range` - Generate range of numbers
```jinja2
{% for i in range(5) %}
  {{ i }}  {# 0, 1, 2, 3, 4 #}
{% endfor %}

{% for i in range(1, 5) %}
  {{ i }}  {# 1, 2, 3, 4 #}
{% endfor %}

{% for i in range(0, 10, 2) %}
  {{ i }}  {# 0, 2, 4, 6, 8 #}
{% endfor %}
```

### `dict` - Create dictionary
```jinja2
{% set config = dict(host="localhost", port=5432) %}
{{ config.host }}  {# → localhost #}
```

### `lipsum` - Lorem ipsum
```jinja2
{{ lipsum(n) }}  {# n paragraphs #}
{{ lipsum(3, min=5, max=15) }}  {# 3 paragraphs, 5-15 sentences each #}
```

### `cycler` - Cycle through values
```jinja2
{% set row_colors = cycler("white", "gray") %}
{% for item in items %}
  <tr class="{{ row_colors.next() }}">
    <td>{{ item }}</td>
  </tr>
{% endfor %}
```

### `joiner` - Add separator between items
```jinja2
{% set pipe = joiner("|") %}
{% for item in items %}
  {{ pipe() }}{{ item }}
{% endfor %}
{# Output: |item1|item2|item3 #}
```

---

## API Summary Reference Table

| Category | Item | Syntax |
|----------|------|--------|
| **Variables** | Simple | `{{ var }}` |
| | Nested | `{{ obj.attr }}` |
| | Index | `{{ list[0] }}` |
| **Strings** | Upper | `\| upper` |
| | Lower | `\| lower` |
| | Replace | `\| replace(old, new)` |
| | Truncate | `\| truncate(len)` |
| **Numbers** | Abs | `\| abs` |
| | Round | `\| round(2)` |
| | Int | `\| int` |
| | Float | `\| float` |
| **Lists** | Length | `\| length` |
| | Join | `\| join(sep)` |
| | Sort | `\| sort` |
| | Reverse | `\| reverse` |
| | Sum | `\| sum` |
| **Control** | If/Else | `{% if %}...{% endif %}` |
| | For Loop | `{% for x in y %}...{% endfor %}` |
| | Set Variable | `{% set x = y %}` |
| **Templates** | Extends | `{% extends "base" %}` |
| | Block | `{% block name %}...{% endblock %}` |
| | Include | `{% include "file" %}` |
| | Macro | `{% macro name() %}...{% endmacro %}` |
| **Tests** | Defined | `is defined` |
| | String | `is string` |
| | Even/Odd | `is even / is odd` |

---

## Complete Example: Using All Features

```jinja2
{# Define base configuration #}
{% set config = dict(
  app_name="MyApp",
  version="1.0.0",
  debug=true,
  max_users=100
) %}

{# Define reusable macro #}
{% macro render_field(label, value, required=false) %}
  <div class="field">
    <label>
      {{ label }}
      {% if required %}<span class="required">*</span>{% endif %}
    </label>
    <value>{{ value | default("N/A") }}</value>
  </div>
{% endmacro %}

{# Main content #}
<!DOCTYPE html>
<html>
  <head>
    <title>{{ config.app_name }} v{{ config.version }}</title>
  </head>
  <body>
    <h1>{{ config.app_name | upper }}</h1>
    
    {% if config.debug %}
      <div class="debug-banner">
        Running in DEBUG mode
      </div>
    {% endif %}
    
    {# List users with conditional styling #}
    {% if users is defined and users | length > 0 %}
      <h2>Users ({{ users | length }}/{{ config.max_users }})</h2>
      <ul>
        {% for user in users %}
          <li class="{% if loop.odd %}odd{% else %}even{% endif %}">
            {{ loop.index }}.
            {% if user.is_admin %}[ADMIN]{% endif %}
            {{ user.name | title }}
            <small>({{ user.email | lower }})</small>
          </li>
        {% endfor %}
      </ul>
    {% else %}
      <p>No users found</p>
    {% endif %}
    
    {# Use macros #}
    {{ render_field("Application", config.app_name) }}
    {{ render_field("Version", config.version) }}
    {{ render_field("Owner", app_owner, true) }}
  </body>
</html>
```

---

## Performance Notes

### Filter Performance

- **Fast**: `upper`, `lower`, `length`, `first`, `last`
- **Medium**: `join`, `sort`, `reverse`, `replace`
- **Slow**: `select`, `reject`, `unique` (on large lists)

### Best Practices

1. Process data in Python when possible
2. Avoid complex loops in templates
3. Cache computed values with `{% set %}`
4. Use filters efficiently (don't loop and filter)

---

## API Versioning

- **Jinja2 Version**: 3.x
- **Custom Filters**: 1.0
- **Last Updated**: April 2026
- **Backward Compatible**: Yes

---

## Quick Links

- [User Guide](COMPREHENSIVE_USER_GUIDE.md)
- [Best Practices](JINJA2_BEST_PRACTICES.md)
- [Migration Guide](MIGRATION_GUIDE_DETAILED.md)
- [Troubleshooting](features/JINJA2_TROUBLESHOOTING.md)
- [Official Jinja2 Docs](https://jinja.palletsprojects.com/)
