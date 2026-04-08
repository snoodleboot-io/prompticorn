# Jinja2 Macros, Includes, and Imports Guide

This guide covers the three advanced Jinja2 features for template reusability and composition in promptosaurus.

## Overview

After Phase 3 Wave 2, the template system supports three complementary features for creating reusable, modular templates:

| Feature | Purpose | Use Case |
|---------|---------|----------|
| **Macros** | Reusable template functions | Formatting, conditional rendering, data transformation |
| **Includes** | Insert template content with shared context | Page layouts, navigation, repeated sections |
| **Imports** | Load macros from other templates | Code reuse, library of helpers, cross-template functions |

## Macros: Reusable Template Functions

Macros are the most powerful way to DRY (Don't Repeat Yourself) your templates.

### Basic Macro Definition

```jinja2
{% macro greet(name) %}
Hello, {{ name }}!
{% endmacro %}

{{ greet("World") }}  # Output: Hello, World!
```

### Macros with Default Parameters

```jinja2
{% macro render_list(items, separator=', ') %}
{% for item in items %}{{ item }}{% if not loop.last %}{{ separator }}{% endif %}{% endfor %}
{% endmacro %}

{{ render_list(['a', 'b', 'c']) }}           # Output: a, b, c
{{ render_list(['x', 'y'], separator=' | ') }}  # Output: x | y
```

### Macros with Config Context

Macros have access to all variables in your template context, including config:

```jinja2
{% macro render_linters(config) %}
Configured linters:
{% for linter in config.linters %}
  - {{ linter }}
{% endfor %}
{% endmacro %}

{{ render_linters(config) }}
```

### Practical Example: Section Headers

```jinja2
{% macro section(title, content) %}
## {{ title }}

{{ content }}
{% endmacro %}

{{ section("Getting Started", "First, install the package") }}
{{ section("Configuration", "Then configure your settings") }}
```

### Macro Variable Scoping

Variables defined inside macros are isolated and don't affect the outer template:

```jinja2
{% macro isolated() %}
  {% set local_var = "macro value" %}
  Inside: {{ local_var }}
{% endmacro %}

Outer before: {{ local_var | default("undefined") }}
{{ isolated() }}
Outer after: {{ local_var | default("undefined") }}

# Output:
# Outer before: undefined
# Inside: macro value
# Outer after: undefined
```

## Includes: Template Composition

Use includes to organize large templates into smaller, reusable parts.

### Basic Include

```jinja2
# main.md
# Project Setup

{% include "installation.md" %}

{% include "usage.md" %}
```

The included template shares the same context as the parent, so it can access all variables:

```jinja2
# header.md
Project: {{ config.project_name }}
Version: {{ config.version }}

# main.md
{% include "header.md" %}

Documentation...
```

### Conditional Includes

```jinja2
{% if config.include_advanced_guide %}
{% include "advanced-setup.md" %}
{% endif %}
```

### Includes in Loops

```jinja2
{% for tool in config.tools %}
{% include "tool-section.md" %}
{% endfor %}
```

The loop variable is available in the included template, so each iteration can render different content.

### Nested Includes

Included templates can themselves include other templates:

```jinja2
# header.md includes branding.md
# main.md includes header.md
# main.md can then use branding content
```

## Imports: Macro Libraries

Import macros from other templates to build reusable macro libraries.

### Basic Import

```jinja2
{% import "helpers.md" as h %}

{{ h.greet("World") }}
{{ h.format_list(['a', 'b', 'c']) }}
```

### Importing Multiple Macros

Import an entire template of macros:

```jinja2
# macros.md
{% macro uppercase(text) %}{{ text | upper }}{% endmacro %}
{% macro lowercase(text) %}{{ text | lower }}{% endmacro %}
{% macro capitalize(text) %}{{ text | capitalize }}{% endmacro %}

# main.md
{% import "macros.md" as str %}

{{ str.uppercase("hello") }}    # HELLO
{{ str.lowercase("WORLD") }}    # world
{{ str.capitalize("promptosaurus") }}  # Promptosaurus
```

### Selective Imports

Import only specific macros using `from...import`:

```jinja2
{% from "macros.md" import uppercase, lowercase %}

{{ uppercase("hello") }}  # HELLO
{{ lowercase("WORLD") }}  # world
# capitalize is not imported
```

### Multiple Import Aliases

Import the same module with different aliases:

```jinja2
{% import "macros.md" as helpers %}
{% import "macros.md" as utils %}

{{ helpers.format_list(['a', 'b']) }}
{{ utils.format_list(['x', 'y']) }}
```

### Nested Imports

Imported templates can import other templates:

```jinja2
# base.md
{% macro base_function() %}Base Output{% endmacro %}

# helpers.md  
{% import "base.md" as base %}
{% macro my_helper() %}{{ base.base_function() }} + Helper{% endmacro %}

# main.md
{% import "helpers.md" as h %}
{{ h.my_helper() }}  # Output: Base Output + Helper
```

### Build Macro Libraries

Create reusable macro libraries for common tasks:

```jinja2
# lib/formatting.md
{% macro code_block(language, code) %}
\`\`\`{{ language }}
{{ code }}
\`\`\`
{% endmacro %}

{% macro inline_code(code) %}\`{{ code }}\`{% endmacro %}

# main.md
{% import "lib/formatting.md" as fmt %}

{{ fmt.code_block("python", "print('hello')") }}
Use {{ fmt.inline_code("config.name") }} to set the project name.
```

## Combining All Three Features

Create sophisticated templates by combining macros, includes, and imports:

```jinja2
# lib/helpers.md - Macro library
{% macro section_header(title) %}## {{ title }}{% endmacro %}
{% macro item_list(items) %}
{% for item in items %}
- {{ item }}
{% endfor %}
{% endmacro %}

# templates/intro.md - Reusable include
## Introduction

This is the introduction section.

# main.md - Combined template
{% import "lib/helpers.md" as lib %}

{{ lib.section_header("Setup") }}
{% include "templates/intro.md" %}

{{ lib.section_header("Tools") }}
{{ lib.item_list(config.tools) }}

{{ lib.section_header("Dependencies") }}
{% if config.dependencies %}
{{ lib.item_list(config.dependencies) }}
{% else %}
No dependencies required.
{% endif %}
```

## Template Search Path

All template names in includes and imports are resolved from the promptosaurus registry:

```jinja2
{% include "section-name" %}
{% import "utilities.md" as utils %}
```

Templates are loaded from your prompt files in the registry. Organization follows your directory/naming structure.

## Best Practices

### 1. Use Macros for Reusable Logic

```jinja2
# ✅ Good - macro handles complex logic
{% macro format_tool(tool) %}
**{{ tool.name }}**: {{ tool.description }}
{% endmacro %}

# ❌ Avoid - repeated code
**Tool 1**: Description 1
**Tool 2**: Description 2
**Tool 3**: Description 3
```

### 2. Use Includes for Page Structure

```jinja2
# ✅ Good - modular, maintainable
{% include "header.md" %}
{% include "content.md" %}
{% include "footer.md" %}

# ❌ Avoid - single large file
[everything in one file]
```

### 3. Use Imports for Macro Libraries

```jinja2
# ✅ Good - organized macro library
# lib/formatting.md - contains all formatting macros
{% import "lib/formatting.md" as fmt %}

# ❌ Avoid - macros scattered across templates
{% macro format1() %}...{% endmacro %}
{% macro format2() %}...{% endmacro %}
```

### 4. Keep Macros Focused

```jinja2
# ✅ Good - single responsibility
{% macro render_item(item) %}
- {{ item.name }}: {{ item.value }}
{% endmacro %}

# ❌ Avoid - multiple responsibilities
{% macro render_everything(item, config) %}
- {{ item.name }}: {{ item.value }}
Config: {{ config.name }}
...
{% endmacro %}
```

### 5. Document Macro Parameters

```jinja2
{% macro render_section(title, items, show_count=true) %}
{# 
  Render a section with title and item list.
  
  Args:
    title (str): Section title
    items (list): List of items to render
    show_count (bool): Whether to show item count (default: true)
#}
## {{ title }} {% if show_count %}({{ items | length }}){% endif %}
{% for item in items %}
- {{ item }}
{% endfor %}
{% endmacro %}
```

## Performance Considerations

- **Macro caching**: Compiled templates are cached, so defining macros has minimal overhead
- **Include caching**: Included templates are compiled once and reused
- **Import caching**: Macros from imports are compiled once per session
- **Avoid deep nesting**: Too many nested includes/imports can impact readability

## Error Handling

### Undefined Macro
```
Error: 'my_macro' is undefined
```
**Solution**: Check that macro is defined or properly imported

### Template Not Found
```
Error: Template 'missing.md' not found in registry
```
**Solution**: Verify template name matches registry entries

### Missing Macro Arguments
```
Error: parameter 'required_param' was not provided
```
**Solution**: Check macro call includes all required parameters

## Summary

| Feature | When to Use |
|---------|------------|
| **Macros** | When you need reusable template functions with parameters and conditional logic |
| **Includes** | When organizing large templates into logical sections with shared context |
| **Imports** | When building macro libraries for code reuse across multiple templates |

Use all three together to build modular, maintainable template systems.
