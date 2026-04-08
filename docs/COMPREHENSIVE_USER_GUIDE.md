# Comprehensive Jinja2 Template User Guide

**Version:** 1.0  
**Date:** April 2026  
**Status:** Production Ready  
**Audience:** Template Authors, Developers, Content Creators

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [Core Concepts](#core-concepts)
4. [Basic Templating](#basic-templating)
5. [Advanced Features](#advanced-features)
6. [Real-World Examples](#real-world-examples)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Introduction

### What is Jinja2 Templating?

Jinja2 is a powerful templating language that allows you to create dynamic templates with variables, conditionals, loops, and more. This guide will help you master Jinja2 template authoring for the Promptosaurus project.

### Why Jinja2?

- **Power**: Go beyond simple text substitution with logic and control flow
- **Readability**: Clear, intuitive syntax that's easy to understand
- **Reusability**: Share common code patterns across multiple templates
- **Maintainability**: Reduce duplication through macros and inheritance
- **Safety**: Built-in protection against common templating vulnerabilities

### When to Use Jinja2

✅ **Use Jinja2 when you need to:**
- Insert variables into templates
- Show/hide content based on conditions
- Repeat blocks of content
- Format values with filters
- Build modular template libraries
- Share code across multiple templates

❌ **Don't use Jinja2 for:**
- Complex business logic (use Python instead)
- Database queries (not allowed in templates)
- Cryptography operations
- File system access

---

## Quick Start (5 minutes)

### Installation

Jinja2 is pre-configured in Promptosaurus. No additional setup needed!

```bash
# Verify Jinja2 is available
python -c "import jinja2; print(jinja2.__version__)"
```

### Your First Template

Create a simple template with a variable:

```jinja2
# config.yaml
Hello, {{ user_name }}!
Project: {{ project_name }}
Language: {{ language }}
```

When rendered with data:
```python
config = {
    "user_name": "Alice",
    "project_name": "MyApp",
    "language": "Python"
}
```

Output:
```
Hello, Alice!
Project: MyApp
Language: Python
```

### Quick Reference Card

| Feature | Syntax | Example |
|---------|--------|---------|
| Variable | `{{ variable }}` | `{{ user_name }}` |
| Filter | `{{ var \| filter }}` | `{{ name \| upper }}` |
| Conditional | `{% if condition %}...{% endif %}` | `{% if debug %}...{% endif %}` |
| Loop | `{% for item in list %}...{% endfor %}` | `{% for lib in libs %}...{% endfor %}` |
| Set Variable | `{% set var = value %}` | `{% set count = 5 %}` |

---

## Core Concepts

### 1. Variables

Variables are placeholders for data. Jinja2 substitutes them with actual values.

#### Basic Variables

```jinja2
# Template
Author: {{ author }}
Version: {{ version }}
Created: {{ created_date }}
```

#### Accessing Nested Data

```jinja2
# Template with nested objects
Database Host: {{ database.host }}
Database Port: {{ database.port }}
Database Name: {{ database.name }}

# With data:
# database = {"host": "localhost", "port": 5432, "name": "mydb"}
# Output:
# Database Host: localhost
# Database Port: 5432
# Database Name: mydb
```

#### List Access

```jinja2
# Template with lists
First dependency: {{ dependencies[0] }}
Last dependency: {{ dependencies[-1] }}

# With data:
# dependencies = ["requests", "flask", "sqlalchemy"]
# Output:
# First dependency: requests
# Last dependency: sqlalchemy
```

#### Dictionary Access

```jinja2
# Two ways to access dictionary values
Config value 1: {{ config['key_name'] }}
Config value 2: {{ config.key_name }}

# Both work the same way
```

### 2. Filters

Filters transform variable values. They use the `|` pipe operator.

#### Common Filters

```jinja2
# String filters
Uppercase: {{ name | upper }}
Lowercase: {{ name | lower }}
Title case: {{ title | title }}
Length: {{ items | length }}
Join list: {{ items | join(', ') }}

# Number filters
Absolute value: {{ number | abs }}
Round: {{ price | round(2) }}

# Default values
Name or 'Guest': {{ name | default('Guest') }}
Safe HTML: {{ html | safe }}

# Custom filters
CamelCase: {{ text | camel_case }}
KebabCase: {{ text | kebab_case }}
PascalCase: {{ text | pascal_case }}
```

#### Chaining Filters

```jinja2
# Apply multiple filters in sequence
{{ name | upper | length }}
{{ description | trim | lower }}
{{ items | default([]) | join(', ') | upper }}

# Right to left evaluation
# Example: "  hello  " → trim → "hello" → lower → "hello"
```

### 3. Conditionals

Conditionals let you show/hide content based on conditions.

#### If/Elif/Else

```jinja2
{% if user.is_admin %}
  <p>Welcome, Admin!</p>
{% elif user.is_moderator %}
  <p>Welcome, Moderator!</p>
{% else %}
  <p>Welcome, User!</p>
{% endif %}
```

#### Comparison Operators

```jinja2
{% if count > 10 %}Large number{% endif %}
{% if price >= 100 %}Expensive{% endif %}
{% if status == 'active' %}Active{% endif %}
{% if name != 'admin' %}Not admin{% endif %}
{% if items is defined %}Has items{% endif %}
{% if value is not defined %}No value{% endif %}
```

#### Logical Operators

```jinja2
{% if user.is_admin and user.is_active %}
  Full access
{% elif user.is_active or user.is_pending %}
  Limited access
{% endif %}

{% if not archived %}
  Still active
{% endif %}
```

#### Testing Membership

```jinja2
{% if 'python' in languages %}
  Python is supported
{% endif %}

{% if 'java' not in languages %}
  Java not included
{% endif %}
```

### 4. Loops

Loops repeat blocks of content for each item.

#### Basic Loop

```jinja2
{% for item in items %}
  - {{ item }}
{% endfor %}

# With data: items = ['apple', 'banana', 'cherry']
# Output:
# - apple
# - banana
# - cherry
```

#### Loop with Index

```jinja2
{% for item in items %}
  {{ loop.index }}. {{ item }}
{% endfor %}

# Output:
# 1. apple
# 2. banana
# 3. cherry
```

#### Loop Variables Reference

| Variable | Meaning |
|----------|---------|
| `loop.index` | Position (1-indexed) |
| `loop.index0` | Position (0-indexed) |
| `loop.revindex` | Reverse position (counting down) |
| `loop.first` | True if first iteration |
| `loop.last` | True if last iteration |
| `loop.length` | Total items in loop |

#### Loop Examples

```jinja2
# First item special formatting
{% for item in items %}
  {% if loop.first %}
    <h2>{{ item }}</h2>
  {% else %}
    <p>{{ item }}</p>
  {% endif %}
{% endfor %}

# Alternate row colors
{% for item in items %}
  {% if loop.index is odd %}
    <tr class="light">
  {% else %}
    <tr class="dark">
  {% endif %}
    <td>{{ item }}</td>
  </tr>
{% endfor %}

# Add comma separator
{% for tag in tags %}
  {{ tag }}{% if not loop.last %}, {% endif %}
{% endfor %}
```

#### Nested Loops

```jinja2
{% for user in users %}
  User: {{ user.name }}
  {% for skill in user.skills %}
    - {{ skill }}
  {% endfor %}
{% endfor %}
```

#### Loop with Conditional

```jinja2
{% for item in items %}
  {% if item.is_active %}
    - {{ item.name }} (active)
  {% endif %}
{% endfor %}
```

---

## Advanced Features

### 1. Template Inheritance

Share common structure across multiple templates using base templates.

#### Define a Base Template

Create `base.html`:
```jinja2
<!DOCTYPE html>
<html>
<head>
  <title>{% block title %}My Site{% endblock %}</title>
</head>
<body>
  <header>
    {% block header %}
      <h1>Welcome</h1>
    {% endblock %}
  </header>
  
  <main>
    {% block content %}
      Default content here
    {% endblock %}
  </main>
  
  <footer>
    {% block footer %}
      © 2026
    {% endblock %}
  </footer>
</body>
</html>
```

#### Extend the Base Template

Create `page.html`:
```jinja2
{% extends "base.html" %}

{% block title %}My Page{% endblock %}

{% block content %}
  <h2>Page content goes here</h2>
  {{ super() }}  {# Include parent block content #}
  <p>Additional content</p>
{% endblock %}

{% block footer %}
  © 2026 My Company
{% endblock %}
```

#### Multi-Level Inheritance

```jinja2
# base.html
{% block content %}Base content{% endblock %}

# article.html
{% extends "base.html" %}
{% block content %}Article content{% endblock %}

# post.html
{% extends "article.html" %}
{% block content %}
  Post header
  {{ super() }}  {# Get "Article content" #}
  Post footer
{% endblock %}
```

### 2. Macros

Reusable template code blocks, like functions for templates.

#### Define a Macro

```jinja2
{% macro greeting(name, title='Friend') %}
  Hello {{ name }}!
  Welcome, {{ title }}.
{% endmacro %}

{# Call the macro #}
{{ greeting('Alice') }}
{{ greeting('Bob', title='Manager') }}
```

#### Macro with Logic

```jinja2
{% macro render_list(items, ordered=False) %}
  {% if ordered %}
    <ol>
    {% for item in items %}
      <li>{{ item }}</li>
    {% endfor %}
    </ol>
  {% else %}
    <ul>
    {% for item in items %}
      <li>{{ item }}</li>
    {% endfor %}
    </ul>
  {% endif %}
{% endmacro %}

{{ render_list(['a', 'b', 'c']) }}
{{ render_list(['1', '2', '3'], ordered=True) }}
```

#### Macro with Caller Block

```jinja2
{% macro dialog(title) %}
  <div class="dialog">
    <h2>{{ title }}</h2>
    <div class="content">
      {{ caller() }}
    </div>
  </div>
{% endmacro %}

{% call dialog('Important') %}
  <p>This is the dialog content</p>
{% endcall %}
```

### 3. Includes

Load and render other templates.

#### Basic Include

```jinja2
# main.html
<div class="page">
  {% include "header.html" %}
  
  <main>
    {% include "content.html" %}
  </main>
  
  {% include "footer.html" %}
</div>
```

#### Include with Variables

```jinja2
# main.html
{% include "user_card.html" with context %}

# Passing specific variables
{% include "item.html" with {"name": "Product", "price": 99} %}
```

#### Conditional Include

```jinja2
{% if show_sidebar %}
  {% include "sidebar.html" %}
{% endif %}
```

### 4. Set and With

Create and scope variables within templates.

#### Set Variable

```jinja2
{% set greeting = "Hello" %}
{{ greeting }}, {{ name }}!

# Set from block
{% set content %}
  This is a multi-line
  block of content
{% endset %}
<div>{{ content }}</div>
```

#### With Block (Variable Scoping)

```jinja2
{% with user_count = users | length %}
  Total users: {{ user_count }}
  Average age: {{ total_age / user_count }}
{% endwith %}
{# user_count is no longer defined #}
```

### 5. Custom Filters

Domain-specific text transformations.

#### Built-in Filter Examples

```jinja2
{{ "hello world" | upper }}          # HELLO WORLD
{{ "HELLO" | lower }}                # hello
{{ "hello world" | title }}          # Hello World
{{ [1, 2, 3] | length }}             # 3
{{ [1, 2, 3] | join(", ") }}         # 1, 2, 3
{{ 3.14159 | round(2) }}             # 3.14
{{ "hello" | default("hi") }}        # hello
```

#### Custom Project Filters

```jinja2
{{ "hello_world" | camel_case }}     # helloWorld
{{ "hello world" | pascal_case }}    # HelloWorld
{{ "hello-world" | snake_case }}     # hello_world
{{ "hello world" | kebab_case }}     # hello-world
{{ "hello" | pluralize }}            # hellos
{{ content | indent(2) }}            # Content indented 2 spaces
```

---

## Real-World Examples

### Example 1: Configuration File

```jinja2
# app_config.yaml (Template)
name: {{ app_name }}
version: {{ version }}
debug: {{ debug_mode }}

database:
  host: {{ db_config.host }}
  port: {{ db_config.port }}
  name: {{ db_config.name }}
  {% if db_config.ssl_enabled %}
  ssl: true
  certificate: {{ db_config.cert_path }}
  {% endif %}

logging:
  level: {{ log_level | upper }}
  format: json
  handlers:
    {% for handler in logging_handlers %}
    - type: {{ handler.type }}
      destination: {{ handler.destination }}
    {% endfor %}

features:
  {% if enable_auth %}
  authentication:
    provider: {{ auth_provider }}
    {% if auth_provider == 'oauth' %}
    client_id: {{ oauth_client_id }}
    client_secret: {{ oauth_client_secret }}
    {% endif %}
  {% endif %}
  
  {% if enable_api %}
  api:
    version: {{ api_version }}
    rate_limit: {{ api_rate_limit }}
  {% endif %}

# When rendered with:
# app_name: MyApp
# version: 1.0.0
# debug_mode: true
# db_config: {host: localhost, port: 5432, name: mydb, ssl_enabled: false}
# log_level: info
# logging_handlers: [{type: console, destination: stdout}]
# enable_auth: true
# auth_provider: oauth
# oauth_client_id: abc123
# oauth_client_secret: secret456
# enable_api: true
# api_version: v2
# api_rate_limit: 1000

# Output:
# name: MyApp
# version: 1.0.0
# debug: true
#
# database:
#   host: localhost
#   port: 5432
#   name: mydb
#
# logging:
#   level: INFO
#   format: json
#   handlers:
#     - type: console
#       destination: stdout
#
# features:
#   authentication:
#     provider: oauth
#     client_id: abc123
#     client_secret: secret456
#
#   api:
#     version: v2
#     rate_limit: 1000
```

### Example 2: Code Generation Template

```jinja2
# Generated endpoint file template
from flask import Blueprint, request, jsonify
from typing import Dict, Any

bp = Blueprint('{{ module_name }}', __name__, url_prefix='/api/{{ route_prefix }}')

{% for endpoint in endpoints %}
@bp.route('{{ endpoint.path }}', methods=['{{ endpoint.method | upper }}'])
def {{ endpoint.function_name }}():
    """
    {{ endpoint.description }}
    
    {% if endpoint.params %}
    Parameters:
    {% for param in endpoint.params %}
      - {{ param.name }} ({{ param.type }}): {{ param.description }}
    {% endfor %}
    {% endif %}
    
    Returns:
      {{ endpoint.return_type }}: {{ endpoint.return_description }}
    """
    {% if endpoint.requires_auth %}
    # Check authentication
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Unauthorized'}), 401
    
    {% endif %}
    {% if endpoint.method == 'get' %}
    # Handle GET request
    params = request.args.to_dict()
    {% elif endpoint.method == 'post' %}
    # Handle POST request
    data = request.get_json()
    {% endif %}
    
    # TODO: Implement {{ endpoint.function_name }}
    return jsonify({'message': 'Not implemented'}), 501

{% endfor %}

# When rendered with:
# module_name: users
# route_prefix: users
# endpoints:
#   - path: /
#     method: get
#     function_name: list_users
#     description: Get all users
#     requires_auth: true
#     params:
#       - name: page
#         type: int
#         description: Page number
#     return_type: List[User]
#     return_description: List of users
#   - path: /
#     method: post
#     function_name: create_user
#     description: Create a new user
#     requires_auth: true
#     return_type: User
#     return_description: Created user

# Output:
# from flask import Blueprint, request, jsonify
# from typing import Dict, Any
# 
# bp = Blueprint('users', __name__, url_prefix='/api/users')
# 
# @bp.route('/', methods=['GET'])
# def list_users():
#     """
#     Get all users
#     
#     Parameters:
#       - page (int): Page number
#     
#     Returns:
#       List[User]: List of users
#     """
#     # Check authentication
#     token = request.headers.get('Authorization')
#     if not token:
#         return jsonify({'error': 'Unauthorized'}), 401
#     
#     # Handle GET request
#     params = request.args.to_dict()
#     
#     # TODO: Implement list_users
#     return jsonify({'message': 'Not implemented'}), 501
#
# @bp.route('/', methods=['POST'])
# def create_user():
#     """
#     Create a new user
#     
#     Returns:
#       User: Created user
#     """
#     # Check authentication
#     token = request.headers.get('Authorization')
#     if not token:
#         return jsonify({'error': 'Unauthorized'}), 401
#     
#     # Handle POST request
#     data = request.get_json()
#     
#     # TODO: Implement create_user
#     return jsonify({'message': 'Not implemented'}), 501
```

### Example 3: Documentation Template

```jinja2
# Project README template
# {{ project_name }}

{% if tagline %}
> {{ tagline }}
{% endif %}

## Overview

{{ description }}

## Quick Start

### Installation

```bash
{{ install_command }}
```

### Basic Usage

```python
{{ basic_example | safe }}
```

## Features

{% for feature in features %}
- **{{ feature.name }}**: {{ feature.description }}
{% endfor %}

## Requirements

- Python {{ python_version }}
{% for dep in dependencies %}
- {{ dep.name }}{% if dep.version %} ({{ dep.version }}){% endif %}
{% endfor %}

## Documentation

{% if docs_url %}
📖 [Full Documentation]({{ docs_url }})
{% endif %}

## Contributing

{% if contributing_guidelines %}
{{ contributing_guidelines }}
{% endif %}

## License

{{ license }}

---

**Project maintained by**: {{ author }}  
**Last updated**: {{ last_updated }}
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Variable Not Found

**Error**: `UndefinedError: 'variable_name' is undefined`

**Cause**: The variable doesn't exist in the template context.

**Solution**:
```jinja2
# Use default filter
{{ missing_var | default('default_value') }}

# Or check if defined
{% if my_var is defined %}
  {{ my_var }}
{% else %}
  No value
{% endif %}
```

#### 2. List Index Out of Range

**Error**: Template renders nothing or shows wrong data

**Solution**:
```jinja2
# Check list length before accessing
{% if items | length > 0 %}
  {{ items[0] }}
{% endif %}

# Use safe access
{% if items %}
  First: {{ items[0] }}
  Last: {{ items[-1] }}
{% endif %}
```

#### 3. Nested Object Access

**Error**: Can't access deep nested values

**Solution**:
```jinja2
# Use dot notation
{{ user.profile.address.city }}

# Or bracket notation
{{ user['profile']['address']['city'] }}

# With safe defaults
{{ user.profile.address.city | default('Unknown') }}
```

#### 4. Filter Chain Not Working

**Problem**: Filters don't chain as expected

**Solution**:
```jinja2
# Remember filters are right-associative
{{ name | lower | title }}  # Works: lower first, then title
{{ (name | lower) | title }}  # Same result

# Check filter availability
# Some filters may not be available in all contexts
```

#### 5. Circular Dependencies in Inheritance

**Error**: Stack overflow or infinite loop

**Solution**:
- Don't have templates extend each other in a circle
- Base template shouldn't extend child template
- Verify inheritance chain: child → parent → grandparent (one direction only)

#### 6. Macro Not Found

**Error**: `UndefinedError: 'macro_name' is undefined`

**Solution**:
```jinja2
# Import macro from another template
{% import "macros.html" as m %}
{{ m.my_macro() }}

# Or use include with context
{% include "macros.html" %}
{{ my_macro() }}
```

### Debug Tips

#### 1. Print Variable Values

```jinja2
{# Show raw value #}
DEBUG: {{ variable }}

{# Show variable type #}
Type: {{ variable | type }}

{# Show variable contents #}
Contents:
{% if variable is iterable %}
  {% for item in variable %}
    - {{ item }}
  {% endfor %}
{% else %}
  {{ variable }}
{% endif %}
```

#### 2. Trace Template Rendering

```jinja2
{# Mark important points in template #}
<!-- SECTION: Header Processing -->
{% if header %}
  <!-- Header found: {{ header | length }} items -->
{% endif %}
<!-- SECTION: Footer Processing -->
```

#### 3. Test Conditionals

```jinja2
{# Verify condition is True/False #}
Is admin? {{ user.is_admin }}
Is undefined? {{ missing_var is undefined }}
Is iterable? {{ items is iterable }}
Is string? {{ text is string }}
```

---

## Best Practices

### 1. Template Organization

✅ **DO**: Keep templates small and focused
```jinja2
# Good: One responsibility per template
# user_card.html - Just renders a user card
{% block user_card %}
  <div class="card">
    <h3>{{ user.name }}</h3>
    <p>{{ user.email }}</p>
  </div>
{% endblock %}
```

❌ **DON'T**: Put everything in one template
```jinja2
# Bad: Too many responsibilities
# app.html - Everything mixed together
<html>
  <body>
    <!-- User card, product list, shopping cart, payment form, etc -->
  </body>
</html>
```

### 2. Naming Conventions

```jinja2
# Variables: snake_case
{% set user_name = "Alice" %}
{% for config_item in config_items %}

# Macros: descriptive, verb-noun
{% macro render_card(item) %}
{% macro format_date(date, format) %}
{% macro list_items(items, ordered=False) %}

# Template files: descriptive.html or module_name.html
# base.html - Root template
# user_profile.html - User related
# form_section.html - Form components
```

### 3. Error Handling

```jinja2
# Always provide defaults
{{ user.name | default('Anonymous') }}

# Check existence before access
{% if config.advanced_options %}
  {{ config.advanced_options.setting }}
{% endif %}

# Safe filter usage
{{ html_content | safe }}  # Only when HTML is trusted
```

### 4. Performance

```jinja2
# ❌ DON'T: Process in template (too slow)
{% for user in users %}
  {% set age = current_year - user.birth_year %}
  Age: {{ age }}
{% endfor %}

# ✅ DO: Process in Python, pass to template
# Python: user.age = current_year - user.birth_year
{{ user.age }}

# ❌ DON'T: Multiple similar loops
{% for active_user in users %}
  {% if user.is_active %}...{% endif %}
{% endfor %}

# ✅ DO: Filter in Python
# Python: active_users = [u for u in users if u.is_active]
{% for user in active_users %}...{% endfor %}
```

### 5. Readability

```jinja2
# Use consistent indentation
{% if condition %}
  {% for item in items %}
    {{ item }}
  {% endfor %}
{% endif %}

# Add comments for complex logic
{# Check if user has admin privileges #}
{% if user.is_admin and user.is_active %}

# Use meaningful variable names
{% set active_user_count = users | length %}
{% set template_version = "1.0" %}

# Break long lines
{{ very_long_variable_name | 
   filter_one | 
   filter_two | 
   filter_three }}
```

### 6. Maintainability

```jinja2
# Use inheritance for common structure
# Base: base.html - Header, footer, nav
# Children: page.html, article.html - Specific content

# Use macros for repeated patterns
{% macro render_error(message) %}
  <div class="error">{{ message }}</div>
{% endmacro %}

# Use includes for modular sections
{% include "header.html" %}
{% include "content.html" %}
{% include "footer.html" %}

# Keep templates DRY (Don't Repeat Yourself)
# Shared patterns should become macros or base templates
```

### 7. Security

```jinja2
# ❌ DON'T: Render untrusted HTML
{{ user_input }}  {# Could contain XSS #}

# ✅ DO: Escape by default (auto-escaped)
{{ user_input }}  {# Safe: automatically escaped #}

# ❌ DON'T: Force safe on untrusted data
{{ untrusted_html | safe }}  {# DANGEROUS #}

# ✅ DO: Only mark safe when intentional
{{ system_generated_html | safe }}  {# OK if truly trusted #}

# ✅ DO: Use custom safe filters for validation
{{ user_html | safe_html }}  {# Custom filter validates first #}
```

---

## Summary

This guide covered:

1. **Basics**: Variables, filters, conditionals, loops
2. **Advanced**: Inheritance, macros, includes, set/with
3. **Real-world**: Practical examples you can use immediately
4. **Troubleshooting**: Common issues and how to solve them
5. **Best practices**: How to write good templates

### Next Steps

- Explore the API Reference for detailed filter documentation
- Review the Migration Guide to convert existing templates
- Check out the Best Practices guide for advanced patterns
- See Troubleshooting for help with specific issues

### Quick Links

- [Jinja2 Official Documentation](https://jinja.palletsprojects.com/)
- [API Reference](JINJA2_API_REFERENCE.md)
- [Best Practices](JINJA2_BEST_PRACTICES.md)
- [Migration Guide](MIGRATION_GUIDE_DETAILED.md)
- [Troubleshooting](features/JINJA2_TROUBLESHOOTING.md)

---

**Questions?** Check the [Troubleshooting Guide](features/JINJA2_TROUBLESHOOTING.md) or review the [Best Practices](JINJA2_BEST_PRACTICES.md) document.
