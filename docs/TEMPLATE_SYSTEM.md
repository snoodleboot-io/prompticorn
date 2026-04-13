# Template Substitution System

Promptosaurus uses a powerful template substitution system to customize agent prompts based on your project configuration.

## Table of Contents

- [Overview](#overview)
- [Available Template Variables](#available-template-variables)
- [How Templates Work](#how-templates-work)
- [Usage in Prompts](#usage-in-prompts)
- [Template Handler Architecture](#template-handler-architecture)
- [Creating Custom Handlers](#creating-custom-handlers)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

---

## Overview

### What is Template Substitution?

Template substitution allows you to write **dynamic prompts** that adapt to your project's configuration. Instead of hardcoding language-specific details, you use template variables that get replaced at build time.

**Example:**

```markdown
You are a {{LANGUAGE}} developer. Use {{PACKAGE_MANAGER}} for dependencies
and {{TESTING_FRAMEWORK}} for tests.
```

**After substitution (Python project):**

```markdown
You are a python developer. Use uv for dependencies
and pytest for tests.
```

### Why Use Templates?

- **DRY Principle** - Write prompts once, work for any language
- **Consistency** - All agents use correct project settings
- **Maintainability** - Change config once, updates everywhere
- **Language-Agnostic** - Same prompt structure for Python, TypeScript, Go, etc.

### When Are Templates Applied?

Templates are substituted when you run:
- `promptosaurus init` - During initial configuration generation
- `promptosaurus switch` - When switching AI tools
- `promptosaurus swap` - When swapping personas

---

## Available Template Variables

All template variables use the format: `{{VARIABLE_NAME}}`

### Language & Runtime

| Variable | Example Value | Source |
|----------|---------------|---------|
| `{{LANGUAGE}}` | `python`, `typescript`, `go` | `spec.language` in `.promptosaurus.yaml` |
| `{{RUNTIME}}` | `3.12`, `5.4`, `1.21` | `spec.runtime` |

### Package Management

| Variable | Example Value | Source |
|----------|---------------|---------|
| `{{PACKAGE_MANAGER}}` | `uv`, `npm`, `go mod` | `spec.package_manager` |

### Testing

| Variable | Example Value | Source |
|----------|---------------|---------|
| `{{TESTING_FRAMEWORK}}` | `pytest`, `vitest`, `go test` | `spec.testing_framework` |
| `{{TEST_RUNNER}}` | `pytest`, `npm test`, `go test` | `spec.test_runner` |
| `{{COVERAGE_TOOL}}` | `pytest-cov`, `c8`, `go test -cover` | `spec.coverage_tool` |
| `{{E2E_TOOL}}` | `playwright`, `cypress`, `selenium` | `spec.e2e_tool` |
| `{{MOCKING_LIBRARY}}` | `unittest.mock`, `vitest.mock`, `gomock` | `spec.mocking_library` |
| `{{MUTATION_TOOL}}` | `mutmut`, `stryker`, `go-mutesting` | `spec.mutation_tool` |

### Code Quality

| Variable | Example Value | Source |
|----------|---------------|---------|
| `{{LINTER}}` | `ruff`, `eslint`, `golangci-lint` | `spec.linter` |
| `{{FORMATTER}}` | `black`, `prettier`, `gofmt` | `spec.formatter` |

### Design Patterns

| Variable | Example Value | Source |
|----------|---------------|---------|
| `{{ABSTRACT_CLASS_STYLE}}` | `abc`, `Protocol`, `interface` | `spec.abstract_class_style` |

### Agents

| Variable | Example Value | Source |
|----------|---------------|---------|
| `{{PRIMARY_AGENTS}}` | `code, test, review` | Derived from active personas |

---

## How Templates Work

### 1. Configuration Storage

Your project configuration is stored in `.promptosaurus.yaml`:

```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
  testing_framework: "pytest"
  linter: ["ruff"]
  formatter: ["black"]
```

### 2. Template Resolution

When building agent configurations, the template system:

1. **Reads** your `.promptosaurus.yaml`
2. **Finds** all template variables (e.g., `{{LANGUAGE}}`)
3. **Looks up** values from config
4. **Substitutes** variables with actual values
5. **Outputs** final agent configuration

### 3. Handler Chain

Each template variable has a **handler** responsible for substitution:

```
{{LANGUAGE}} → LanguageHandler → config.get("language") → "python"
{{RUNTIME}} → RuntimeHandler → config.get("runtime") → "3.12"
{{PACKAGE_MANAGER}} → PackageManagerHandler → config.get("package_manager") → "uv"
```

---

## Usage in Prompts

### Basic Substitution

**In agent prompt file (`promptosaurus/agents/code/minimal/prompt.md`):**

```markdown
---
name: code
description: Code implementation agent
---

# System Prompt

You are an expert {{LANGUAGE}} developer using {{RUNTIME}}.

Use {{PACKAGE_MANAGER}} for dependency management.
Write tests with {{TESTING_FRAMEWORK}}.
Format code with {{FORMATTER}}.
Lint code with {{LINTER}}.
```

**After substitution (for Python project):**

```markdown
---
name: code
description: Code implementation agent
---

# System Prompt

You are an expert python developer using 3.12.

Use uv for dependency management.
Write tests with pytest.
Format code with black.
Lint code with ruff.
```

### Conditional Rendering

Use Jinja2 syntax for conditions:

```markdown
{% if LANGUAGE == "python" %}
Use type hints for all function signatures.
Follow PEP 8 style guidelines.
{% elif LANGUAGE == "typescript" %}
Use strict TypeScript mode.
Follow ESLint rules.
{% endif %}
```

### Lists and Iteration

If a config value is a list (like `linter: ["ruff", "mypy"]`):

```markdown
Run these linters:
{% for tool in LINTER %}
- {{tool}}
{% endfor %}
```

**Output:**
```markdown
Run these linters:
- ruff
- mypy
```

### Default Values

Provide fallback if variable not set:

```markdown
Package manager: {{PACKAGE_MANAGER | default("pip")}}
```

---

## Template Handler Architecture

### Handler Interface

All handlers implement the `TemplateVariableHandler` protocol:

```python
class TemplateVariableHandler(Protocol):
    def can_handle(self, variable_name: str) -> bool:
        """Return True if this handler processes this variable."""
        ...
    
    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        """Return the substituted value."""
        ...
```

### Built-in Handlers

Located in `promptosaurus/builders/template_handlers/`:

| Handler | Variable | Config Key |
|---------|----------|------------|
| `LanguageHandler` | `LANGUAGE` | `spec.language` |
| `RuntimeHandler` | `RUNTIME` | `spec.runtime` |
| `PackageManagerHandler` | `PACKAGE_MANAGER` | `spec.package_manager` |
| `TestingFrameworkHandler` | `TESTING_FRAMEWORK` | `spec.testing_framework` |
| `TestRunnerHandler` | `TEST_RUNNER` | `spec.test_runner` |
| `LinterHandler` | `LINTER` | `spec.linter` |
| `FormatterHandler` | `FORMATTER` | `spec.formatter` |
| `CoverageToolHandler` | `COVERAGE_TOOL` | `spec.coverage_tool` |
| `E2EToolHandler` | `E2E_TOOL` | `spec.e2e_tool` |
| `MutationToolHandler` | `MUTATION_TOOL` | `spec.mutation_tool` |
| `MockingLibraryHandler` | `MOCKING_LIBRARY` | `spec.mocking_library` |
| `AbstractClassStyleHandler` | `ABSTRACT_CLASS_STYLE` | `spec.abstract_class_style` |
| `PrimaryAgentsHandler` | `PRIMARY_AGENTS` | Derived from personas |

### Jinja2 Integration

Templates use **Jinja2** for advanced rendering:

**Location:** `promptosaurus/builders/template_handlers/resolvers/jinja2_template_renderer.py`

**Features:**
- Variable substitution
- Conditionals (`{% if %}`)
- Loops (`{% for %}`)
- Filters (`| default`, `| upper`, etc.)
- Custom filters (safe access, error recovery)

---

## Creating Custom Handlers

### Step 1: Create Handler Class

Create a new file in `promptosaurus/builders/template_handlers/`:

```python
# my_custom_handler.py

from typing import Any
from promptosaurus.builders.template_handlers.template_handler import TemplateHandler

class MyCustomHandler(TemplateHandler):
    """Handler for MY_CUSTOM_VAR template variable."""
    
    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "MY_CUSTOM_VAR"
    
    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        # Extract value from config
        return str(config.get("my_custom_field", "default_value"))
```

### Step 2: Register Handler

Register in `promptosaurus/builders/template_handlers/__init__.py`:

```python
from .my_custom_handler import MyCustomHandler

# Add to handler list
ALL_HANDLERS = [
    LanguageHandler(),
    RuntimeHandler(),
    # ... existing handlers ...
    MyCustomHandler(),  # Add your handler
]
```

### Step 3: Use in Templates

Now you can use `{{MY_CUSTOM_VAR}}` in any prompt:

```markdown
Custom configuration: {{MY_CUSTOM_VAR}}
```

### Step 4: Add to Config Schema

Update `.promptosaurus.yaml` to include your field:

```yaml
spec:
  language: "python"
  my_custom_field: "my_value"
```

---

## Advanced Features

### Template Caching

**Location:** `promptosaurus/builders/template_handlers/resolvers/error_recovery.py`

Templates are cached after first render for performance:

```python
class TemplateCache:
    """Cache compiled Jinja2 templates."""
    
    def get_or_compile(self, template_str: str) -> Template:
        # Returns cached template or compiles new one
        ...
```

### Safe Filters

**Location:** `promptosaurus/builders/template_handlers/resolvers/safe_filters.py`

Safely access nested config values:

```jinja2
{{ config.spec.language | safe_get("python") }}
```

If `config.spec.language` doesn't exist, returns `"python"` instead of error.

### Custom Jinja2 Filters

**Location:** `promptosaurus/builders/template_handlers/resolvers/custom_filters.py`

Add custom filters for advanced transformations:

```python
def uppercase_filter(value: str) -> str:
    return value.upper()

# Register filter
env.filters['uppercase'] = uppercase_filter
```

**Usage:**
```jinja2
Language: {{LANGUAGE | uppercase}}
```

**Output:**
```
Language: PYTHON
```

### Error Recovery

**Location:** `promptosaurus/builders/template_handlers/resolvers/error_recovery.py`

If a template variable is missing, the system:

1. Logs a warning
2. Returns a placeholder: `[MISSING: VARIABLE_NAME]`
3. Continues rendering (doesn't crash)

**Example:**

Template:
```markdown
Use {{NONEXISTENT_VAR}} for deployment.
```

Output (if variable missing):
```markdown
Use [MISSING: NONEXISTENT_VAR] for deployment.
```

### Template Validation

**Location:** `promptosaurus/builders/template_handlers/resolvers/template_validator.py`

Validate templates before rendering:

```python
from promptosaurus.builders.template_handlers.resolvers.template_validator import TemplateValidator

validator = TemplateValidator()
errors = validator.validate(template_string)

if errors:
    for error in errors:
        print(f"Template error: {error}")
```

---

## Best Practices

### 1. Use Templates for Language-Specific Content

✅ **Good:**
```markdown
Install dependencies: {{PACKAGE_MANAGER}} install
```

❌ **Bad (hardcoded):**
```markdown
Install dependencies: npm install
```

### 2. Provide Fallback Values

✅ **Good:**
```markdown
Linter: {{LINTER | default("eslint")}}
```

❌ **Bad (crashes if missing):**
```markdown
Linter: {{LINTER}}
```

### 3. Use Conditionals for Complex Logic

✅ **Good:**
```jinja2
{% if LANGUAGE == "python" %}
Use virtual environments with {{PACKAGE_MANAGER}}
{% elif LANGUAGE == "javascript" %}
Use node_modules with {{PACKAGE_MANAGER}}
{% endif %}
```

### 4. Keep Templates Readable

✅ **Good:**
```markdown
Testing: Use {{TESTING_FRAMEWORK}} with {{COVERAGE_TOOL}} for coverage.
```

❌ **Bad (too dense):**
```jinja2
{% if LANGUAGE == "python" %}{{TESTING_FRAMEWORK}}{% else %}{{TEST_RUNNER}}{% endif %}
```

### 5. Document Custom Variables

If you add custom handlers, document them in your project:

```markdown
# Custom Template Variables

- `{{MY_CUSTOM_VAR}}` - Description of what this does
- `{{ANOTHER_VAR}}` - Description here
```

---

## Troubleshooting

### Template Variable Not Substituted

**Problem:** Variable appears as `{{LANGUAGE}}` in output

**Causes:**
1. Variable name misspelled
2. Handler not registered
3. Config missing the value

**Solution:**
```bash
# Check your config
cat .promptosaurus.yaml

# Verify variable name matches handler
grep "LANGUAGE" promptosaurus/builders/template_handlers/language_handler.py

# Check if handler is registered
grep "LanguageHandler" promptosaurus/builders/template_handlers/__init__.py
```

### Template Rendering Error

**Problem:** Error during template rendering

**Example error:**
```
TemplateRenderingError: Undefined variable 'NONEXISTENT_VAR'
```

**Solution:**
```jinja2
# Use default filter
{{NONEXISTENT_VAR | default("fallback")}}

# Or check if defined
{% if NONEXISTENT_VAR is defined %}
  {{NONEXISTENT_VAR}}
{% else %}
  fallback value
{% endif %}
```

### Jinja2 Syntax Error

**Problem:** Jinja2 template syntax is invalid

**Example:**
```jinja2
{% if LANGUAGE == "python" }  # Missing closing %
```

**Solution:**
```jinja2
# Correct syntax
{% if LANGUAGE == "python" %}
  Python-specific content
{% endif %}
```

### Missing Config Value

**Problem:** Config value is `None` or empty

**Check config:**
```bash
cat .promptosaurus.yaml

# Should have:
spec:
  language: "python"  # NOT empty
  runtime: "3.12"     # NOT null
```

**Solution:**
```bash
# Re-run init to fix config
promptosaurus init
```

### List Variables Not Iterating

**Problem:** `{{LINTER}}` shows as string instead of list

**Example:**
```yaml
# Wrong
linter: "ruff, mypy"

# Correct
linter: ["ruff", "mypy"]
```

**Solution:** Use YAML list syntax in `.promptosaurus.yaml`

---

## Examples

### Example 1: Python Project Template

**Config (`.promptosaurus.yaml`):**
```yaml
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
  testing_framework: "pytest"
  formatter: ["black"]
  linter: ["ruff", "mypy"]
```

**Template:**
```markdown
You are a {{LANGUAGE}} {{RUNTIME}} developer.

**Setup:**
- Package manager: {{PACKAGE_MANAGER}}
- Testing: {{TESTING_FRAMEWORK}}
- Formatting: {{FORMATTER}}
- Linting: {% for tool in LINTER %}{{tool}}{% if not loop.last %}, {% endif %}{% endfor %}
```

**Output:**
```markdown
You are a python 3.12 developer.

**Setup:**
- Package manager: uv
- Testing: pytest
- Formatting: black
- Linting: ruff, mypy
```

### Example 2: TypeScript Project Template

**Config:**
```yaml
spec:
  language: "typescript"
  runtime: "5.4"
  package_manager: "npm"
  testing_framework: "vitest"
  formatter: ["prettier"]
  linter: ["eslint"]
```

**Same template, different output:**
```markdown
You are a typescript 5.4 developer.

**Setup:**
- Package manager: npm
- Testing: vitest
- Formatting: prettier
- Linting: eslint
```

### Example 3: Conditional Content

**Template:**
```markdown
# Testing Strategy

{% if TESTING_FRAMEWORK == "pytest" %}
Use pytest fixtures for dependency injection.
Run with: `pytest tests/`
Coverage: `pytest --cov={{PACKAGE_NAME}}`
{% elif TESTING_FRAMEWORK == "vitest" %}
Use vitest for unit and integration tests.
Run with: `npm test`
Coverage: `npm test -- --coverage`
{% endif %}

Mock dependencies using {{MOCKING_LIBRARY}}.
```

---

## Reference

### File Locations

| Component | Path |
|-----------|------|
| **Handlers** | `promptosaurus/builders/template_handlers/` |
| **Base Class** | `promptosaurus/builders/template_handlers/template_handler.py` |
| **Jinja2 Renderer** | `promptosaurus/builders/template_handlers/resolvers/jinja2_template_renderer.py` |
| **Error Recovery** | `promptosaurus/builders/template_handlers/resolvers/error_recovery.py` |
| **Custom Filters** | `promptosaurus/builders/template_handlers/resolvers/custom_filters.py` |
| **Safe Filters** | `promptosaurus/builders/template_handlers/resolvers/safe_filters.py` |
| **Validator** | `promptosaurus/builders/template_handlers/resolvers/template_validator.py` |

### Related Documentation

- [ADVANCED_CONFIGURATION.md](./ADVANCED_CONFIGURATION.md) - Configuration schema
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues

---

**Last Updated:** 2026-04-13  
**Version:** 0.1.0
