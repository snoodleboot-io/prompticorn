# Wave 3: Custom Jinja2 Extensions

This guide documents Wave 3 of the Jinja2 template system implementation: Custom Extensions for domain-specific template needs.

## Overview

Wave 3 extends Jinja2 templating with custom filters, the `{% set %}` tag for template-level variables, and `{% with %}` blocks for variable scoping. These features enable more powerful and expressive template authoring for code generation scenarios.

## Custom Filters

Custom filters provide domain-specific string transformations commonly needed in code generation. All filters are automatically registered with the Jinja2 environment when the Builder is initialized.

### String Case Conversion Filters

#### `kebab_case` - Convert to kebab-case

Converts strings to hyphen-separated lowercase format.

```jinja2
{{ 'my_variable_name' | kebab_case }}        →  my-variable-name
{{ 'MyClassName' | kebab_case }}             →  my-class-name
{{ 'my variable name' | kebab_case }}        →  my-variable-name
{{ 'multiple   spaces' | kebab_case }}       →  multiple-spaces
```

Use cases:
- CSS class names
- URL slugs
- Kebab-cased identifiers
- Configuration keys

#### `snake_case` - Convert to snake_case

Converts strings to underscore-separated lowercase format.

```jinja2
{{ 'my variable name' | snake_case }}        →  my_variable_name
{{ 'MyClassName' | snake_case }}             →  my_class_name
{{ 'kebab-case-var' | snake_case }}          →  kebab_case_var
{{ 'camelCaseVar' | snake_case }}            →  camel_case_var
```

Use cases:
- Python variable names
- Python function names
- Python file names (with .py extension)
- Database column names
- Configuration keys

#### `pascal_case` - Convert to PascalCase

Converts strings to capitalized word format suitable for class names.

```jinja2
{{ 'my variable name' | pascal_case }}       →  MyVariableName
{{ 'snake_case_var' | pascal_case }}         →  SnakeCaseVar
{{ 'kebab-case-var' | pascal_case }}         →  KebabCaseVar
{{ 'camelCaseVar' | pascal_case }}           →  CamelCaseVar
```

Use cases:
- Python class names
- TypeScript/C# class names
- Type/interface names
- Component names

#### `camel_case` - Convert to camelCase

Converts strings to lower-first-letter capitalized format.

```jinja2
{{ 'my variable name' | camel_case }}        →  myVariableName
{{ 'snake_case_var' | camel_case }}          →  snakeCaseVar
{{ 'MyPascalCase' | camel_case }}            →  myPascalCase
{{ 'kebab-case-var' | camel_case }}          →  kebabCaseVar
```

Use cases:
- JavaScript variable names
- JavaScript function names
- camelCase identifiers
- JSON property names

#### `title_case` - Convert to Title Case

Capitalizes each word separated by spaces.

```jinja2
{{ 'my variable name' | title_case }}        →  My Variable Name
{{ 'snake_case_var' | title_case }}          →  Snake Case Var
{{ 'kebab-case-var' | title_case }}          →  Kebab Case Var
{{ 'camelCaseVar' | title_case }}            →  Camel Case Var
```

Use cases:
- Display names
- Titles
- Headings
- User-friendly labels

### Text Formatting Filters

#### `indent` - Indent text by N spaces

Adds spaces to the beginning of each line (except first by default).

```jinja2
{{ code_block | indent(4) }}                 →  (indents lines 2+ by 4 spaces)
{{ code_block | indent(8, first=true) }}     →  (indents all lines by 8 spaces)
```

Parameters:
- `width` (default: 4) - Number of spaces to indent
- `first` (default: false) - Whether to indent the first line

Use cases:
- Code generation (indenting code blocks)
- Template formatting
- Nested code structure
- YAML/JSON formatting

Example:

```jinja2
{% set method_body %}
print("Hello")
return True
{% endset %}

def my_method(self):
{{ method_body | indent(4) }}
```

Output:

```python
def my_method(self):
    print("Hello")
    return True
```

#### `pluralize` - Simple pluralization

Adds 's' or 'es' based on English pluralization rules (or count parameter).

```jinja2
{{ 'file' | pluralize }}                     →  files
{{ 'box' | pluralize }}                      →  boxes
{{ 'class' | pluralize }}                    →  classes
{{ 'baby' | pluralize }}                     →  babies
{{ 'file' | pluralize(count=1) }}            →  file
{{ 'file' | pluralize(count=5) }}            →  files
```

Parameters:
- `count` (optional) - If provided and equals 1, returns singular form

Rules:
- Words ending in s, x, z, ch, sh → add 'es'
- Words ending in consonant + y → replace y with 'ies'
- All others → add 's'

Use cases:
- Generating natural language in comments
- Conditional pluralization in templates
- User-friendly output generation

### Chaining Filters

Filters can be chained together for powerful transformations:

```jinja2
{{ 'my variable name' | kebab_case | upper }}         →  MY-VARIABLE-NAME
{{ config.class_name | pascal_case | lower }}         →  myvarname
{{ 'undefined_var' | default('default') | snake_case }} →  default
```

## Template-Level Variables with `{% set %}`

The `{% set %}` tag creates variables within templates, allowing you to:
- Transform and store values
- Create intermediate calculations
- Apply filters and store results
- Build reusable template content

### Simple Variable Assignment

```jinja2
{% set variable_name = value %}
{{ variable_name }}
```

Example:

```jinja2
{% set class_name = config.name | pascal_case %}
class {{ class_name }}:
    pass
```

### Assignment with Filters

Apply filters when assigning values:

```jinja2
{% set kebab_name = config.name | kebab_case %}
{% set snake_name = config.name | snake_case %}

Kebab: {{ kebab_name }}
Snake: {{ snake_name }}
```

### Block Assignment

Assign multi-line content to a variable:

```jinja2
{% set docstring %}
This is a multi-line
docstring that will
be stored in a variable
{% endset %}

def my_function():
    """{{ docstring | trim }}"""
    pass
```

### Assignment with Config Values

Use config values in assignments:

```jinja2
{% set language = config.language %}
{% set package_manager = config.package_manager %}

Language: {{ language }}
Package Manager: {{ package_manager }}
```

### Arithmetic and Expressions

Perform calculations:

```jinja2
{% set total = 10 + 5 %}
{% set doubled = total * 2 %}

Total: {{ total }}        →  Total: 15
Doubled: {{ doubled }}    →  Doubled: 30
```

### With Lists and Iteration

Store and iterate over lists:

```jinja2
{% set linters = config.linters %}
{% set linter_count = linters | length %}

Linters ({{ linter_count }}):
{% for linter in linters %}
  - {{ linter }}
{% endfor %}
```

## Variable Scoping with `{% with %}`

The `{% with %}` block creates a local scope for variables. Variables defined in a `{% with %}` block are isolated to that block.

### Basic Usage

```jinja2
{% with variable = value %}
    {{ variable }}      ← accessible here
{% endwith %}
{{ variable }}          ← NOT accessible here (undefined)
```

### Multiple Variables

Create multiple scoped variables using nested blocks:

```jinja2
{% with var1 = value1 %}
    {% with var2 = value2 %}
        Var1: {{ var1 }}
        Var2: {{ var2 }}
    {% endwith %}
{% endwith %}
```

### With Config Values

Scope config access to reduce verbosity:

```jinja2
{% with host = config.database.host, port = config.database.port %}
    # Connection settings
    DATABASE_URL = "postgresql://{{ host }}:{{ port }}/mydb"
{% endwith %}
```

### With Filters

Apply and scope filter results:

```jinja2
{% with class_name = config.name | pascal_case %}
    class {{ class_name }}:
        pass
{% endwith %}
```

### Nested Blocks

Combine multiple scoped sections:

```jinja2
{% with outer = 'outer_value' %}
    Outer: {{ outer }}
    
    {% with inner = 'inner_value' %}
        Both: {{ outer }} and {{ inner }}
    {% endwith %}
    
    Only outer again: {{ outer }}
{% endwith %}
```

### In Conditionals

Use `{% with %}` inside conditionals:

```jinja2
{% if config.use_typescript %}
    {% with lang = 'TypeScript' %}
        Language: {{ lang }}
    {% endwith %}
{% else %}
    {% with lang = 'JavaScript' %}
        Language: {{ lang }}
    {% endwith %}
{% endif %}
```

### In Loops

Combine `{% with %}` and `{% for %}`:

```jinja2
{% for item in config.items %}
    {% with formatted = item | upper %}
        Processing: {{ formatted }}
    {% endwith %}
{% endfor %}
```

## Practical Code Generation Examples

### Python Class Generation

```jinja2
{% set class_name = config.class_name | pascal_case %}
{% set file_name = config.class_name | snake_case %}

class {{ class_name }}:
    """{{ config.description }}"""
    
    {% for method in config.methods %}
    {% set method_name = method | camel_case %}
    def {{ method_name }}(self):
        """{{ method | title_case }} operation."""
        pass
    
    {% endfor %}

# File: {{ file_name }}.py
```

### TypeScript Configuration

```jinja2
{% set config_key = 'APP_' + (config.name | upper | replace('-', '_')) %}

{% with api_host = config.api.host, api_port = config.api.port %}
export const API_CONFIG = {
    host: "{{ api_host }}",
    port: {{ api_port }},
    configKey: "{{ config_key }}",
};
{% endwith %}
```

### Markdown Documentation

```jinja2
{% set project_title = config.name | title_case %}
{% set indent_level = config.depth | default(0) %}

# {{ project_title }}

{% set description %}
{{ config.description }}
{% endset %}

{{ description | trim }}

## Getting Started

1. Install dependencies: `{{ config.package_manager }} install`
2. Run tests: `{{ config.test_runner }} run`
3. Build: `{{ config.build_command | default('npm run build') }}`
```

### API Endpoint Generation

```jinja2
{% set endpoint_path = config.endpoint | kebab_case %}
{% set handler_func = config.endpoint | camel_case %}

@app.route("/api/{{ endpoint_path }}", methods=["GET", "POST"])
def {{ handler_func }}():
    """Handle {{ config.endpoint | title_case }} requests."""
    
    {% for field in config.fields %}
    {% set field_var = field.name | snake_case %}
    {{ field_var }} = request.args.get("{{ field.name | kebab_case }}")
    {% endfor %}
    
    return jsonify({"status": "success"})
```

## API Reference

### Custom Filters

| Filter | Input | Output | Parameters |
|--------|-------|--------|-----------|
| `kebab_case` | string | kebab-case | none |
| `snake_case` | string | snake_case | none |
| `pascal_case` | string | PascalCase | none |
| `camel_case` | string | camelCase | none |
| `title_case` | string | Title Case | none |
| `indent` | string | indented string | width (int), first (bool) |
| `pluralize` | string | pluralized string | count (int, optional) |

### Tags

| Tag | Purpose | Scope |
|-----|---------|-------|
| `{% set var = value %}` | Create/assign variable | Template-wide |
| `{% set var %}...{% endset %}` | Assign block content | Template-wide |
| `{% with var = value %}...{% endwith %}` | Create scoped variable | Block-local |

## Best Practices

### 1. Use Custom Filters for Transformations

```jinja2
✓ GOOD: Transform at assignment
{% set class_name = config.name | pascal_case %}

✗ BAD: Repeat transformation
{{ config.name | pascal_case }}
... later ...
{{ config.name | pascal_case }}
```

### 2. Scope Complex Values

```jinja2
✓ GOOD: Use with block for scoped access
{% with api_host = config.api.host, api_port = config.api.port %}
    HOST: {{ api_host }}
    PORT: {{ api_port }}
{% endwith %}

✗ BAD: Verbosity and repetition
HOST: {{ config.api.host }}
PORT: {{ config.api.port }}
```

### 3. Use Meaningful Names

```jinja2
✓ GOOD: Descriptive variable names
{% set python_class_name = config.name | pascal_case %}
{% set python_file_name = config.name | snake_case %}

✗ BAD: Ambiguous names
{% set x = config.name | pascal_case %}
{% set y = config.name | snake_case %}
```

### 4. Keep Templates Readable

```jinja2
✓ GOOD: Logical grouping
{% set class_name = model.name | pascal_case %}
{% set file_name = model.name | snake_case %}

class {{ class_name }}:
    """Defined in {{ file_name }}.py"""

✗ BAD: Too many intermediate variables
{% set a = model.name | pascal_case %}
{% set b = model.name | snake_case %}
{% set c = a | lower %}
...
```

## Performance Considerations

- Filters are applied at template render time
- Variable assignments don't add performance overhead
- Scoped variables (`{% with %}`) are memory-efficient
- Custom filters are optimized with regex caching

## Compatibility

Wave 3 features are compatible with:
- All Jinja2 built-in filters
- All Jinja2 built-in tags (if, for, while, etc.)
- Wave 1 features (inheritance, blocks)
- Wave 2 features (macros, includes, imports)
- All existing handler patterns

## Examples by Use Case

### Web Framework Routes

```jinja2
{% set route_path = endpoint.name | kebab_case %}
@app.route("/{{ route_path }}", methods=["{{ method | upper }}"])
def {{ endpoint.handler_name | camel_case }}():
    """Handle requests to {{ endpoint.name | title_case }}"""
    pass
```

### Configuration Files

```jinja2
{% set config_name = 'APP_' + (app.name | upper | replace('-', '_')) %}

{{ config_name }}={{ app.value }}
{{ config_name }}_DEBUG={{ app.debug | lower }}
{{ config_name }}_PORT={{ app.port }}
```

### Database Migrations

```jinja2
{% set table_name = model.name | snake_case %}
{% set id_field = 'id_' + (model.name | snake_case) %}

CREATE TABLE {{ table_name }} (
    {{ id_field }} UUID PRIMARY KEY,
    {% for field in model.fields %}
    {{ field.name | snake_case }} {{ field.sql_type }},
    {% endfor %}
);
```

### Test Generation

```jinja2
{% set test_name = 'test_' + (method.name | snake_case) %}

def {{ test_name }}():
    """Test {{ method.name | title_case }} method."""
    {% with instance_name = class.name | snake_case %}
    {{ instance_name }} = {{ class.name }}()
    result = {{ instance_name }}.{{ method.name }}()
    assert result is not None
    {% endwith %}
```

## Related Documentation

- [Wave 1: Template Inheritance](./JINJA2_TEMPLATE_INHERITANCE.md)
- [Wave 2: Macros, Includes, Imports](./JINJA2_MACROS_INCLUDES_IMPORTS.md)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)

## Testing

Wave 3 includes comprehensive test coverage:

- **25+ test cases** covering all custom filters
- **Set tag tests** including block assignments and scope
- **With block tests** including nested scopes and conditionals
- **Combined feature tests** demonstrating real-world scenarios
- **Code generation examples** showing practical usage

Run tests with:

```bash
uv run pytest tests/unit/test_builder.py::TestCustomFilters -v
uv run pytest tests/unit/test_builder.py::TestSetTag -v
uv run pytest tests/unit/test_builder.py::TestWithBlocks -v
uv run pytest tests/unit/test_builder.py::TestCombinedFeatures -v
```
