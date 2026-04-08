"""Unit tests for the Builder class template substitution functionality."""

import sys
from pathlib import Path

# Add the promptosaurus directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from promptosaurus.builders.builder import Builder
from promptosaurus.builders.template_handlers.resolvers.template_rendering_error import (
    TemplateRenderingError,
)


def test_basic_substitution():
    """Test basic template substitution functionality."""
    # Create a builder instance
    builder = Builder()

    # Test content with template variables
    content = """
    Language: {{config.language}}
    Runtime: {{config.runtime}}
    Package Manager: {{config.package_manager}}
    Linter: {{config.linter}}
    Formatter: {{config.formatter}}
    Abstract Class Style: {{config.abstract_class_style}}
    Testing Framework: {{config.test_framework}}
    Test Runner: {{config.test_runner}}
    Line Coverage: {{config.coverage.line}}%
    Branch Coverage: {{config.coverage.branch}}%
    Function Coverage: {{config.coverage.function}}%
    Statement Coverage: {{config.coverage.statement}}%
    Mutation Coverage: {{config.coverage.mutation}}%
    Path Coverage: {{config.coverage.path}}%
    """

    # Test config
    config = {
        "spec": {
            "language": "python",
            "runtime": "CPython 3.11",
            "package_manager": "uv",
            "linter": "ruff",
            "formatter": "ruff",
            "abstract_class_style": "interface",
            "test_framework": "pytest",
            "test_runner": "pytest",
            "coverage": {
                "line": 80,
                "branch": 70,
                "function": 90,
                "statement": 85,
                "mutation": 80,
                "path": 60,
            },
        }
    }

    # Perform substitution
    result = builder._substitute_template_variables(content, config)

    # Check that substitutions worked
    assert "Language: python" in result
    assert "Runtime: CPython 3.11" in result
    assert "Package Manager: uv" in result
    assert "Linter: ruff" in result
    assert "Formatter: ruff" in result
    assert "Abstract Class Style: interface" in result
    assert "Testing Framework: pytest" in result
    assert "Test Runner: pytest" in result
    assert "Line Coverage: 80%" in result
    assert "Branch Coverage: 70%" in result
    assert "Function Coverage: 90%" in result
    assert "Statement Coverage: 85%" in result
    assert "Mutation Coverage: 80%" in result
    assert "Path Coverage: 60%" in result


def test_coverage_presets():
    """Test coverage preset functionality."""
    builder = Builder()

    content = "Line: {{config.coverage.line}}%, Branch: {{config.coverage.branch}}%"

    # Test strict preset with explicit values
    config_strict = {
        "spec": {
            "coverage": {
                "line": 90,
                "branch": 80,
                "function": 95,
                "statement": 90,
                "mutation": 85,
                "path": 70,
            }
        }
    }
    result_strict = builder._substitute_template_variables(content, config_strict)
    assert "Line: 90%" in result_strict
    assert "Branch: 80%" in result_strict

    # Test standard preset with explicit values
    config_standard = {
        "spec": {
            "coverage": {
                "line": 80,
                "branch": 70,
                "function": 90,
                "statement": 85,
                "mutation": 80,
                "path": 60,
            }
        }
    }
    result_standard = builder._substitute_template_variables(content, config_standard)
    assert "Line: 80%" in result_standard
    assert "Branch: 70%" in result_standard

    # Test minimal preset with explicit values
    config_minimal = {
        "spec": {
            "coverage": {
                "line": 70,
                "branch": 60,
                "function": 80,
                "statement": 75,
                "mutation": 70,
                "path": 50,
            }
        }
    }
    result_minimal = builder._substitute_template_variables(content, config_minimal)
    assert "Line: 70%" in result_minimal
    assert "Branch: 60%" in result_minimal


def test_multilanguage_config():
    """Test multi-language configuration handling."""
    builder = Builder()

    content = "Language: {{config.language}}"

    # Multi-language config (list)
    config_multi = {"spec": [{"language": "python"}, {"language": "javascript"}]}
    result = builder._substitute_template_variables(content, config_multi)
    # Should use the first language in the list
    assert "Language: python" in result


def test_no_config():
    """Test behavior with empty config - missing keys raise UndefinedError."""
    builder = Builder()

    content = "Language: {{config.language}}"
    # Accessing a missing key in Jinja2 raises an error
    with pytest.raises(TemplateRenderingError, match="language"):
        builder._substitute_template_variables(content, {"spec": {}})


def test_extensibility():
    """Test that custom config values work through the config object."""
    builder = Builder()
    content = "Custom: {{config.custom_var}}"
    config = {"spec": {"custom_var": "custom_value"}}
    result = builder._substitute_template_variables(content, config)
    assert "Custom: custom_value" in result


def test_list_iteration():
    """Test that list values in config can be iterated over in templates."""
    builder = Builder()

    content = """
{% for linter in config.linters %}
- {{ linter }}
{% endfor %}
"""

    config = {"spec": {"linters": ["ruff", "flake8", "pylint"]}}

    result = builder._substitute_template_variables(content, config)

    # Check that all linters are listed
    assert "- ruff" in result
    assert "- flake8" in result
    assert "- pylint" in result


def test_nested_object_access():
    """Test nested object access in config."""
    builder = Builder()

    content = """
Database Host: {{config.database.host}}
Database Port: {{config.database.port}}
"""

    config = {"spec": {"database": {"host": "localhost", "port": 5432}}}

    result = builder._substitute_template_variables(content, config)

    assert "Database Host: localhost" in result
    assert "Database Port: 5432" in result


def test_mixed_types_in_config():
    """Test config with mixed types: strings, numbers, booleans, lists, objects."""
    builder = Builder()

    content = """
Language: {{config.language}} ({{config.language_type}})
Version: {{config.version}}
Active: {{config.active}}
Linters: {% for linter in config.linters %}{{ linter }}{% if not loop.last %}, {% endif %}{% endfor %}
Database: {{config.database.host}}:{{config.database.port}}
"""

    config = {
        "spec": {
            "language": "python",
            "language_type": "dynamic",
            "version": 3.11,
            "active": True,
            "linters": ["ruff", "mypy"],
            "database": {"host": "db.example.com", "port": 5432},
        }
    }

    result = builder._substitute_template_variables(content, config)

    assert "Language: python (dynamic)" in result
    assert "Version: 3.11" in result
    assert "Active: True" in result
    assert "Linters: ruff, mypy" in result
    assert "Database: db.example.com:5432" in result


def test_jinja2_filters():
    """Test Jinja2 built-in filters work with config data."""
    builder = Builder()

    content = """
Default missing: {{ config.missing_var | default('fallback') }}
Default database: {{ config.database.host | default('localhost') }}
Join linters: {{ config.linters | join(', ') }}
Upper project: {{ config.project_name | upper }}
Default boolean: {{ config.optional_setting | default(false) }}
"""

    config = {
        "spec": {
            "linters": ["ruff", "flake8"],
            "project_name": "Promptosaurus",
            "database": {"host": "db.example.com"},
            # optional_setting is missing
        }
    }

    result = builder._substitute_template_variables(content, config)

    assert "Default missing: fallback" in result
    assert "Default database: db.example.com" in result
    assert "Join linters: ruff, flake8" in result
    assert "Upper project: PROMPTOSAURUS" in result
    assert "Default boolean: False" in result


def test_jinja2_conditionals():
    """Test Jinja2 conditional logic works with config data."""
    builder = Builder()

    content = """
{% if config.use_typescript %}TypeScript setup{% endif %}
{% if config.linters | length > 0 %}Linters: {{ config.linters | join(', ') }}{% endif %}
{% if config.database.host == 'localhost' %}Development DB{% else %}Production DB{% endif %}
{% if config.debug and config.verbose %}Debug mode enabled{% endif %}
{% if config.database.port in [5432, 3306] %}Standard port{% else %}Custom port{% endif %}
{% if config.optional_setting is defined %}Optional is set{% else %}Optional not set{% endif %}
{% if config.linters %}Has linters{% elif config.formatters %}Has formatters{% else %}No tools{% endif %}
"""

    config = {
        "spec": {
            "use_typescript": True,
            "linters": ["ruff", "flake8"],
            "database": {"host": "localhost", "port": 5432},
            "debug": True,
            "verbose": False,
            "formatters": ["black"],
            # optional_setting is missing
        }
    }

    result = builder._substitute_template_variables(content, config)

    # Basic if
    assert "TypeScript setup" in result
    # If with filter
    assert "Linters: ruff, flake8" in result
    # If-else with comparison
    assert "Development DB" in result
    assert "Production DB" not in result
    # And operator
    assert "Debug mode enabled" not in result  # verbose is False
    # In operator
    assert "Standard port" in result
    # Is defined
    assert "Optional not set" in result
    # If-elif-else
    assert "Has linters" in result
    assert "Has formatters" not in result
    assert "No tools" not in result


def test_jinja2_loop_variables():
    """Test Jinja2 loop variables like loop.index, loop.first, loop.last."""
    builder = Builder()

    content = """
{% for linter in config.linters %}
{{ loop.index }}. {{ linter }}{% if loop.first %} (first){% endif %}{% if loop.last %} (last){% endif %}
{% endfor %}
Total: {{ config.linters | length }}
"""

    config = {
        "spec": {
            "linters": ["ruff", "flake8", "pylint"],
        }
    }

    result = builder._substitute_template_variables(content, config)

    # Check loop.index
    assert "1. ruff (first)" in result
    assert "2. flake8" in result
    assert "3. pylint (last)" in result
    # Check loop.length via filter
    assert "Total: 3" in result


def test_jinja2_nested_loops():
    """Test nested loops with complex data structures."""
    builder = Builder()

    content = """
{% for db in config.databases %}
Database: {{ db.name }}
{% for table in db.tables %}
  - {{ table.name }} ({{ table.type }})
{% endfor %}
{% endfor %}
"""

    config = {
        "spec": {
            "databases": [
                {
                    "name": "users_db",
                    "tables": [
                        {"name": "users", "type": "primary"},
                        {"name": "sessions", "type": "secondary"},
                    ],
                },
                {
                    "name": "orders_db",
                    "tables": [
                        {"name": "orders", "type": "primary"},
                        {"name": "items", "type": "secondary"},
                    ],
                },
            ]
        }
    }

    result = builder._substitute_template_variables(content, config)

    assert "Database: users_db" in result
    assert "  - users (primary)" in result
    assert "  - sessions (secondary)" in result
    assert "Database: orders_db" in result
    assert "  - orders (primary)" in result
    assert "  - items (secondary)" in result


def test_jinja2_complex_loop_logic():
    """Test complex loop logic with conditionals and filters inside loops."""
    builder = Builder()

    content = """
{% for item in config.database.connections %}
{% if loop.first %}First connection: {% endif %}
{{ item.host }}:{{ item.port }}{% if item.ssl %} (SSL){% endif %}
{% if loop.last and loop.index > 1 %}Total: {{ loop.length }} connections{% endif %}
{% endfor %}

Filtered hosts: {% for conn in config.database.connections | selectattr('ssl') %}{{ conn.host }}{% if not loop.last %}, {% endif %}{% endfor %}
"""

    config = {
        "spec": {
            "database": {
                "connections": [
                    {"host": "db1.example.com", "port": 5432, "ssl": True},
                    {"host": "db2.example.com", "port": 5433, "ssl": False},
                    {"host": "db3.example.com", "port": 5434, "ssl": True},
                ]
            }
        }
    }

    result = builder._substitute_template_variables(content, config)

    # Check loop.first
    assert "First connection: db1.example.com:5432 (SSL)" in result
    # Check conditional SSL flag
    assert "db2.example.com:5433" in result  # No (SSL)
    assert "db3.example.com:5434 (SSL)" in result
    # Check loop.last with condition
    assert "Total: 3 connections" in result
    # Check complex filter in loop
    assert "Filtered hosts: db1.example.com, db3.example.com" in result


def test_jinja2_template_inheritance():
    """Test Jinja2 template inheritance with {% extends %} and {% block %}."""
    from unittest.mock import patch

    # Create a builder instance
    builder = Builder()

    # Mock registry to return test templates
    base_template = """Base Template
{% block header %}Default Header{% endblock %}
{% block content %}Default Content{% endblock %}
{% block footer %}Default Footer{% endblock %}"""

    child_template = """{% extends "base-template.md" %}
{% block header %}Custom Header{% endblock %}
{% block content %}
Child content here.
{{config.language}}
{% endblock %}"""

    def mock_prompt_body(filename: str) -> str:
        if filename == "base-template.md":
            return base_template
        elif filename == "child-template.md":
            return child_template
        else:
            raise FileNotFoundError(f"Template {filename} not found")

    with patch("promptosaurus.registry.registry.prompt_body", side_effect=mock_prompt_body):
        # Test rendering child template that extends base
        result = builder._substitute_template_variables(
            child_template, {"spec": {"language": "python"}}
        )

        # Check that inheritance worked
        assert "Base Template" in result
        assert "Custom Header" in result
        assert "Child content here." in result
        assert "python" in result
        assert "Default Footer" in result

        # Check that default content was overridden
        assert "Default Content" not in result


def test_jinja2_template_inheritance_by_name():
    """Test name-based template rendering with inheritance."""
    from unittest.mock import patch

    # Create a builder instance
    builder = Builder()

    # Mock registry to return test templates
    base_template = """Base Template
{% block content %}Default Content{% endblock %}"""

    child_template = """{% extends "base-template.md" %}
{% block content %}Overridden Content{% endblock %}"""

    def mock_prompt_body(filename: str) -> str:
        if filename == "base-template.md":
            return base_template
        elif filename == "child-template.md":
            return child_template
        else:
            raise FileNotFoundError(f"Template {filename} not found")

    with patch("promptosaurus.registry.registry.prompt_body", side_effect=mock_prompt_body):
        # Test rendering by name using the new handle_by_name method
        result = builder._jinja2_renderer.handle_by_name("child-template.md", {"config": {}})

        # Check that inheritance worked
        assert "Base Template" in result
        assert "Overridden Content" in result
        assert "Default Content" not in result


def test_jinja2_circular_inheritance_detection():
    """Test that circular template inheritance is detected and prevented."""
    from unittest.mock import patch

    # Create a builder instance
    builder = Builder()

    # Mock registry to return circular templates
    template_a = """{% extends "template-b.md" %}{% block content %}A{% endblock %}"""
    template_b = """{% extends "template-a.md" %}{% block content %}B{% endblock %}"""

    def mock_prompt_body(filename: str) -> str:
        if filename == "template-a.md":
            return template_a
        elif filename == "template-b.md":
            return template_b
        else:
            raise FileNotFoundError(f"Template {filename} not found")

    with patch("promptosaurus.registry.registry.prompt_body", side_effect=mock_prompt_body):
        # Test that circular inheritance raises an error
        with pytest.raises(TemplateRenderingError):
            builder._jinja2_renderer.handle_by_name("template-a.md", {})


def test_jinja2_multi_level_inheritance():
    """Test multi-level template inheritance (child -> parent -> grandparent)."""
    from unittest.mock import patch

    # Create a builder instance
    builder = Builder()

    # Mock registry to return three-level inheritance
    grandparent = """Grandparent Template
{% block header %}Default Header{% endblock %}
{% block content %}Grandparent Content{% endblock %}
{% block footer %}Default Footer{% endblock %}"""

    parent = """{% extends "grandparent.md" %}
{% block header %}Parent Header{% endblock %}
{% block content %}Parent Content{% endblock %}"""

    child = """{% extends "parent.md" %}
{% block content %}Child Content{{config.language}}{% endblock %}
{% block footer %}Child Footer{% endblock %}"""

    def mock_prompt_body(filename: str) -> str:
        if filename == "grandparent.md":
            return grandparent
        elif filename == "parent.md":
            return parent
        elif filename == "child.md":
            return child
        else:
            raise FileNotFoundError(f"Template {filename} not found")

    with patch("promptosaurus.registry.registry.prompt_body", side_effect=mock_prompt_body):
        # Test multi-level inheritance
        result = builder._substitute_template_variables(child, {"spec": {"language": "python"}})

        # Check inheritance worked across all levels
        assert "Grandparent Template" in result
        assert "Parent Header" in result  # Overridden by parent
        assert "Child Contentpython" in result  # Overridden by child
        assert "Child Footer" in result  # Overridden by child

        # Check that intermediate content was properly overridden
        assert "Grandparent Content" not in result
        assert "Parent Content" not in result


def test_jinja2_complex_block_structures():
    """Test complex block structures with nested blocks and super() calls."""
    from unittest.mock import patch

    # Create a builder instance
    builder = Builder()

    # Mock registry with complex block structures
    base = """Base Template
{% block content %}
Base content start
{% block inner %}Default inner{% endblock %}
Base content end
{% endblock %}
{% block footer %}Base footer{% endblock %}"""

    child = """{% extends "base.md" %}
{% block content %}
Child content start
{% block inner %}Child inner{% endblock %}
{% super() %}
Child content end
{% endblock %}
{% block footer %}{% super() %} + Child footer{% endblock %}"""

    def mock_prompt_body(filename: str) -> str:
        if filename == "base.md":
            return base
        elif filename == "child.md":
            return child
        else:
            raise FileNotFoundError(f"Template {filename} not found")

    with patch("promptosaurus.registry.registry.prompt_body", side_effect=mock_prompt_body):
        # Test complex block structures with super() calls
        result = builder._substitute_template_variables(child, {})

        # Check that nested blocks work
        assert "Base Template" in result
        assert "Child content start" in result
        assert "Child inner" in result
        assert "Base content start" in result
        assert "Default inner" in result  # Should be overridden
        assert "Base content end" in result
        assert "Child content end" in result
        assert "Base footer" in result
        assert "Child footer" in result


def test_jinja2_inheritance_error_handling():
    """Test error handling for malformed inheritance structures."""
    from unittest.mock import patch

    # Create a builder instance
    builder = Builder()

    # Test missing base template
    child_template = """{% extends "missing-template.md" %}
{% block content %}Content{% endblock %}"""

    with patch(
        "promptosaurus.registry.registry.prompt_body",
        side_effect=FileNotFoundError("Template not found"),
    ):
        with pytest.raises(TemplateRenderingError) as exc_info:
            builder._substitute_template_variables(child_template, {})
        assert "Failed to load base template" in str(exc_info.value)

    # Test malformed block syntax
    malformed_template = """{% extends "base.md" %}
{% block content %}Content{% endblock"""  # Missing closing %}

    base_template = """Base{% block content %}Default{% endblock %}"""

    def mock_prompt_body(filename: str) -> str:
        if filename == "base.md":
            return base_template
        else:
            raise FileNotFoundError(f"Template {filename} not found")

    with patch("promptosaurus.registry.registry.prompt_body", side_effect=mock_prompt_body):
        with pytest.raises(TemplateRenderingError) as exc_info:
            builder._substitute_template_variables(malformed_template, {})
        assert "Malformed block syntax" in str(exc_info.value)

        assert "Circular template inheritance detected" in str(exc_info.value)


# ============================================================================
# WAVE 3: Custom Jinja2 Extensions Tests
# ============================================================================


class TestCustomFilters:
    """Tests for custom Jinja2 filters."""

    def test_kebab_case_filter(self):
        """Test kebab_case filter for various inputs."""
        builder = Builder()

        test_cases = [
            ("my variable name", "my-variable-name"),
            ("MyClassName", "my-class-name"),
            ("snake_case_var", "snake-case-var"),
            ("SCREAMING_SNAKE", "screaming-snake"),
            ("camelCaseVar", "camel-case-var"),
            ("Already-kebab-case", "already-kebab-case"),
            ("multiple   spaces", "multiple-spaces"),
            ("trailing-spaces   ", "trailing-spaces"),
        ]

        for input_val, expected in test_cases:
            content = f"{{{{ '{input_val}' | kebab_case }}}}"
            result = builder._substitute_template_variables(content, {})
            assert result.strip() == expected, f"Failed for input: {input_val}"

    def test_snake_case_filter(self):
        """Test snake_case filter for various inputs."""
        builder = Builder()

        test_cases = [
            ("my variable name", "my_variable_name"),
            ("MyClassName", "my_class_name"),
            ("kebab-case-var", "kebab_case_var"),
            ("camelCaseVar", "camel_case_var"),
            ("SCREAMING_SNAKE", "screaming_snake"),
            ("mixed-case_variable", "mixed_case_variable"),
            ("multiple   spaces", "multiple_spaces"),
        ]

        for input_val, expected in test_cases:
            content = f"{{{{ '{input_val}' | snake_case }}}}"
            result = builder._substitute_template_variables(content, {})
            assert result.strip() == expected, f"Failed for input: {input_val}"

    def test_pascal_case_filter(self):
        """Test pascal_case filter for various inputs."""
        builder = Builder()

        test_cases = [
            ("my variable name", "MyVariableName"),
            ("snake_case_var", "SnakeCaseVar"),
            ("kebab-case-var", "KebabCaseVar"),
            ("camelCaseVar", "CamelCaseVar"),
            ("already pascal case", "AlreadyPascalCase"),
            ("single", "Single"),
            ("", ""),
        ]

        for input_val, expected in test_cases:
            content = f"{{{{ '{input_val}' | pascal_case }}}}"
            result = builder._substitute_template_variables(content, {})
            assert result.strip() == expected, f"Failed for input: {input_val}"

    def test_camel_case_filter(self):
        """Test camel_case filter for various inputs."""
        builder = Builder()

        test_cases = [
            ("my variable name", "myVariableName"),
            ("snake_case_var", "snakeCaseVar"),
            ("kebab-case-var", "kebabCaseVar"),
            ("MyPascalCase", "myPascalCase"),
            ("single", "single"),
        ]

        for input_val, expected in test_cases:
            content = f"{{{{ '{input_val}' | camel_case }}}}"
            result = builder._substitute_template_variables(content, {})
            assert result.strip() == expected, f"Failed for input: {input_val}"

    def test_title_case_filter(self):
        """Test title_case filter for various inputs."""
        builder = Builder()

        test_cases = [
            ("my variable name", "My Variable Name"),
            ("snake_case_var", "Snake Case Var"),
            ("kebab-case-var", "Kebab Case Var"),
            ("camelCaseVar", "Camel Case Var"),
            ("multiple   spaces", "Multiple Spaces"),
        ]

        for input_val, expected in test_cases:
            content = f"{{{{ '{input_val}' | title_case }}}}"
            result = builder._substitute_template_variables(content, {})
            assert result.strip() == expected, f"Failed for input: {input_val}"

    def test_indent_filter(self):
        """Test indent filter with various widths."""
        builder = Builder()

        # Test basic indentation
        content = "{{ 'line1\nline2\nline3' | indent(4) }}"
        result = builder._substitute_template_variables(content, {})
        lines = result.split("\n")
        # First line should not be indented by default
        assert lines[0] == "line1", f"Expected 'line1', got '{lines[0]}'"
        # Other lines should be indented
        assert lines[1].startswith("    "), f"Expected indentation, got '{lines[1]}'"
        assert lines[2].startswith("    "), f"Expected indentation, got '{lines[2]}'"

    def test_pluralize_filter(self):
        """Test pluralize filter for simple pluralization."""
        builder = Builder()

        # Test simple pluralization
        test_cases = [
            ("file", "files"),
            ("box", "boxes"),
            ("class", "classes"),
            ("dish", "dishes"),
            ("wish", "wishes"),
            ("baby", "babies"),
            ("person", "persons"),
        ]

        for input_val, expected in test_cases:
            content = f"{{{{ '{input_val}' | pluralize }}}}"
            result = builder._substitute_template_variables(content, {})
            assert result.strip() == expected, f"Failed for input: {input_val}"

        # Test with count parameter
        content = "{{ 'file' | pluralize(count=1) }}"
        result = builder._substitute_template_variables(content, {})
        assert result.strip() == "file"

        content = "{{ 'file' | pluralize(count=5) }}"
        result = builder._substitute_template_variables(content, {})
        assert result.strip() == "files"

    def test_multiple_filters_chain(self):
        """Test chaining multiple filters together."""
        builder = Builder()

        # Chain kebab_case then upper
        content = "{{ 'my variable name' | kebab_case | upper }}"
        result = builder._substitute_template_variables(content, {})
        assert result.strip() == "MY-VARIABLE-NAME"

        # Chain snake_case with default
        content = "{{ undefined_var | default('default_value') | snake_case }}"
        result = builder._substitute_template_variables(content, {})
        assert result.strip() == "default_value"


class TestSetTag:
    """Tests for Jinja2 {% set %} tag for template-level variables."""

    def test_simple_set_assignment(self):
        """Test simple variable assignment with {% set %}."""
        builder = Builder()

        content = """
        {% set var_name = 'my-test' %}
        Variable: {{ var_name }}
        """
        result = builder._substitute_template_variables(content, {})
        assert "my-test" in result
        assert "Variable: my-test" in result

    def test_set_with_filter(self):
        """Test {% set %} with filter application."""
        builder = Builder()

        content = """
        {% set formatted = 'my_variable_name' | kebab_case %}
        Formatted: {{ formatted }}
        """
        result = builder._substitute_template_variables(content, {})
        assert "my-variable-name" in result

    def test_set_with_config_variable(self):
        """Test {% set %} using config values."""
        builder = Builder()

        config = {
            "spec": {
                "language": "python",
                "package_manager": "uv",
            }
        }

        content = """
        {% set lang = config.language %}
        {% set pkg_mgr = config.package_manager %}
        Language: {{ lang }}
        Package Manager: {{ pkg_mgr }}
        """
        result = builder._substitute_template_variables(content, config)
        assert "Language: python" in result
        assert "Package Manager: uv" in result

    def test_set_block_assignment(self):
        """Test block assignment with {% set %}...{% endset %}."""
        builder = Builder()

        content = """
        {% set message %}
        This is a multi-line
        message content that spans
        multiple lines
        {% endset %}
        Result: {{ message | trim }}
        """
        result = builder._substitute_template_variables(content, {})
        assert "This is a multi-line" in result

    def test_set_with_arithmetic(self):
        """Test {% set %} with arithmetic operations."""
        builder = Builder()

        content = """
        {% set total = 5 + 3 %}
        Total: {{ total }}
        {% set doubled = total * 2 %}
        Doubled: {{ doubled }}
        """
        result = builder._substitute_template_variables(content, {})
        assert "Total: 8" in result
        assert "Doubled: 16" in result

    def test_set_with_list_and_loop(self):
        """Test {% set %} with list variables and loops."""
        builder = Builder()

        config = {
            "spec": {
                "linters": ["ruff", "mypy", "pylint"],
            }
        }

        content = """
        {% set linter_list = config.linters %}
        Linters: {{ linter_list | join(', ') }}
        Count: {{ linter_list | length }}
        """
        result = builder._substitute_template_variables(content, config)
        assert "Linters: ruff, mypy, pylint" in result
        assert "Count: 3" in result

    def test_set_variable_scope(self):
        """Test that set variables are scoped to template."""
        builder = Builder()

        content = """
        {% set my_var = 'value1' %}
        Before: {{ my_var }}
        {% if true %}
            {% set my_var = 'value2' %}
            Inside: {{ my_var }}
        {% endif %}
        After: {{ my_var }}
        """
        result = builder._substitute_template_variables(content, {})
        # In Jinja2, set modifies the variable in the current scope
        assert "Before: value1" in result
        assert "Inside: value2" in result


class TestWithBlocks:
    """Tests for Jinja2 {% with %} blocks for variable scoping."""

    def test_simple_with_block(self):
        """Test basic {% with %} block for variable scoping."""
        builder = Builder()

        content = """
        {% set outer = 'outer_value' %}
        Outer: {{ outer }}
        {% with inner = 'inner_value' %}
            Inner: {{ inner }}
            Outer accessible: {{ outer }}
        {% endwith %}
        After block: {{ outer }}
        """
        result = builder._substitute_template_variables(content, {})
        assert "Outer: outer_value" in result
        assert "Inner: inner_value" in result
        assert "Outer accessible: outer_value" in result

    def test_with_config_values(self):
        """Test {% with %} using config values."""
        builder = Builder()

        config = {
            "spec": {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                }
            }
        }

        content = """
        {% with db_host = config.database.host, db_port = config.database.port %}
            Connecting to {{ db_host }}:{{ db_port }}
        {% endwith %}
        """
        result = builder._substitute_template_variables(content, config)
        assert "Connecting to localhost:5432" in result

    def test_with_multiple_assignments(self):
        """Test {% with %} with multiple variable assignments."""
        builder = Builder()

        # In Jinja2, multiple assignments in with need separate statements
        content = """
        {% with var1 = 'value1' %}
            {% with var2 = 'value2' %}
                Var1: {{ var1 }}
                Var2: {{ var2 }}
            {% endwith %}
        {% endwith %}
        """
        result = builder._substitute_template_variables(content, {})
        assert "Var1: value1" in result
        assert "Var2: value2" in result

    def test_with_filter_application(self):
        """Test {% with %} applying filters to variables."""
        builder = Builder()

        content = """
        {% with kebab = 'my_variable_name' | kebab_case %}
            Original format applied: {{ kebab }}
        {% endwith %}
        """
        result = builder._substitute_template_variables(content, {})
        assert "my-variable-name" in result

    def test_nested_with_blocks(self):
        """Test nested {% with %} blocks."""
        builder = Builder()

        content = """
        {% with outer = 'outer' %}
            Outer: {{ outer }}
            {% with inner = 'inner' %}
                Outer in inner: {{ outer }}
                Inner: {{ inner }}
            {% endwith %}
        {% endwith %}
        """
        result = builder._substitute_template_variables(content, {})
        assert "Outer: outer" in result
        assert "Outer in inner: outer" in result
        assert "Inner: inner" in result

    def test_with_in_conditional(self):
        """Test {% with %} blocks inside conditionals."""
        builder = Builder()

        config = {
            "spec": {
                "use_typescript": True,
            }
        }

        content = """
        {% if config.use_typescript %}
            {% with lang = 'TypeScript' %}
                Language: {{ lang }}
            {% endwith %}
        {% else %}
            {% with lang = 'JavaScript' %}
                Language: {{ lang }}
            {% endwith %}
        {% endif %}
        """
        result = builder._substitute_template_variables(content, config)
        assert "Language: TypeScript" in result

    def test_with_in_loop(self):
        """Test {% with %} blocks inside loops."""
        builder = Builder()

        config = {"spec": {"list_items": ["item1", "item2", "item3"]}}

        content = """
        {% for item in config.list_items %}
            {% with formatted = item | upper %}
                Processing: {{ formatted }}
            {% endwith %}
        {% endfor %}
        """
        result = builder._substitute_template_variables(content, config)
        assert "Processing: ITEM1" in result
        assert "Processing: ITEM2" in result
        assert "Processing: ITEM3" in result

    def test_with_variable_isolation(self):
        """Test that with block variables don't leak outside."""
        builder = Builder()

        content = """
        {% set shared = 'shared_value' %}
        {% with scoped = 'scoped_value' %}
            In block - scoped: {{ scoped }}
        {% endwith %}
        After block - shared still works: {{ shared }}
        """
        result = builder._substitute_template_variables(content, {})
        assert "In block - scoped: scoped_value" in result
        assert "After block - shared still works: shared_value" in result


class TestCombinedFeatures:
    """Tests combining custom filters, set tag, and with blocks."""

    def test_filters_in_set_and_with(self):
        """Test custom filters working together with set and with blocks."""
        builder = Builder()

        config = {
            "spec": {
                "project_name": "my awesome project",
            }
        }

        content = """
        {% set class_name = config.project_name | pascal_case %}
        {% with snake_name = config.project_name | snake_case %}
            Class: {{ class_name }}
            Variable: {{ snake_name }}
            Kebab: {{ config.project_name | kebab_case }}
        {% endwith %}
        """
        result = builder._substitute_template_variables(content, config)
        assert "Class: MyAwesomeProject" in result
        assert "Variable: my_awesome_project" in result
        assert "Kebab: my-awesome-project" in result

    def test_code_generation_example(self):
        """Test realistic code generation scenario with all Wave 3 features."""
        builder = Builder()

        config = {
            "spec": {
                "class_name": "user_manager",
                "methods": ["create", "update", "delete"],
            }
        }

        content = """
        {% set py_class = config.class_name | pascal_case %}
        {% set py_file = config.class_name | snake_case %}
        class {{ py_class }}:
            \"\"\"Managing {{ config.class_name }}.\"\"\"
            
            {% for method in config.methods %}
            {% with method_name = method | camel_case %}
            def {{ method_name }}(self):
                \"\"\"{{ method | title_case }} operation.\"\"\"
                pass
            {% endwith %}
            {% endfor %}
        
        # File: {{ py_file }}.py
        """
        result = builder._substitute_template_variables(content, config)
        assert "class UserManager:" in result
        assert "# File: user_manager.py" in result
        assert "def create(self):" in result
        assert "def update(self):" in result
        assert "def delete(self):" in result

    # ========== INTEGRATION TESTS: COMPLEX TEMPLATE COMPOSITIONS ==========

    def test_integration_macros_with_loops_and_filters(self):
        """Test macros combined with loops and filters."""
        builder = Builder()

        config = {
            "spec": {
                "methods": ["create_user", "update_user", "delete_user"],
            }
        }

        # Template with macro definition, loop, and filters
        template = """
        {% macro render_method(method_name) %}
        def {{ method_name | snake_case }}():
            \"\"\"Auto-generated method.\"\"\"
            pass
        {% endmacro %}
        
        class UserManager:
            \"\"\"Manages user operations.\"\"\"
            
            {% for method in config.methods %}
            {{ render_method(method) }}
            {% endfor %}
        """

        result = builder._substitute_template_variables(template, config)
        assert "class UserManager:" in result
        assert "def create_user():" in result
        assert "def update_user():" in result
        assert "def delete_user():" in result
        assert '"""Auto-generated method."""' in result

    def test_integration_conditionals_loops_and_filters(self):
        """Test conditionals, loops, and filters working together."""
        builder = Builder()

        config = {
            "spec": {
                "generate_tests": True,
                "test_methods": ["test_create", "test_update", "test_delete"],
                "linters": ["ruff", "pyright", "mypy"],
            }
        }

        # Template with conditionals, loops, and filters
        template = """
        {% if config.generate_tests %}
        # Test Suite
        {% for method in config.test_methods %}
        def {{ method | snake_case }}():
            \"\"\"{{ method | pascal_case }} test.\"\"\"
            assert True
        
        {% endfor %}
        {% endif %}
        
        # Linters: {{ config.linters | join(", ") | upper }}
        """

        result = builder._substitute_template_variables(template, config)
        assert "# Test Suite" in result
        assert "def test_create():" in result
        assert "def test_update():" in result
        assert "def test_delete():" in result
        assert "RUFF, PYRIGHT, MYPY" in result

    def test_integration_set_tag_with_loops_and_filters(self):
        """Test {% set %} tag with loops and custom filters."""
        builder = Builder()

        config = {
            "spec": {
                "project_name": "awesome_project",
                "modules": ["auth", "users", "posts"],
            }
        }

        # Template with set tag, loops, and filters
        template = """
        {% set class_name = config.project_name | pascal_case %}
        {% set file_name = config.project_name | snake_case %}
        
        # Generated for {{ class_name }} project
        # File: {{ file_name }}.py
        
        class {{ class_name }}:
            \"\"\"Main application class.\"\"\"
            
            MODULES = [
            {% for module in config.modules %}
                "{{ module | upper }}",
            {% endfor %}
            ]
        """

        result = builder._substitute_template_variables(template, config)
        assert "# Generated for AwesomeProject project" in result
        assert "# File: awesome_project.py" in result
        assert "class AwesomeProject:" in result
        assert '"AUTH",' in result
        assert '"USERS",' in result
        assert '"POSTS",' in result

    def test_integration_with_blocks_for_variable_scoping(self):
        """Test {% with %} blocks for variable scoping with filters."""
        builder = Builder()

        config = {
            "spec": {
                "database_url": "postgresql://localhost/mydb",
                "cache_ttl": 3600,
            }
        }

        # Template with with blocks for scoped variables
        template = """
        {% with db_host = config.database_url | lower %}
        Database Host: {{ db_host }}
        {% endwith %}
        
        {% with ttl_seconds = config.cache_ttl %}
        Cache TTL: {{ ttl_seconds }} seconds
        {% with ttl_minutes = ttl_seconds // 60 %}
        Cache TTL: {{ ttl_minutes }} minutes
        {% endwith %}
        {% endwith %}
        """

        result = builder._substitute_template_variables(template, config)
        assert "Database Host: postgresql://localhost/mydb" in result
        assert "Cache TTL: 3600 seconds" in result
        assert "Cache TTL: 60 minutes" in result

    def test_integration_complex_nested_loops_with_conditionals(self):
        """Test complex nesting of loops and conditionals with filters."""
        builder = Builder()

        config = {
            "spec": {
                "languages": [
                    {
                        "name": "python",
                        "frameworks": ["django", "fastapi", "flask"],
                        "primary": True,
                    },
                    {
                        "name": "typescript",
                        "frameworks": ["react", "nextjs"],
                        "primary": False,
                    },
                ],
            }
        }

        # Template with nested loops and conditionals
        template = """
        # Language Support
        
        {% for lang in config.languages %}
        ## {{ lang.name | pascal_case }}
        {% if lang.primary %}
        **Primary Language**
        {% endif %}
        
        Frameworks:
        {% for framework in lang.frameworks %}
        - {{ framework | upper }}
        {% endfor %}
        
        {% endfor %}
        """

        result = builder._substitute_template_variables(template, config)
        assert "## Python" in result
        assert "**Primary Language**" in result
        assert "## Typescript" in result
        assert "- DJANGO" in result
        assert "- FASTAPI" in result
        assert "- FLASK" in result
        assert "- REACT" in result
        assert "- NEXTJS" in result

    def test_integration_filters_with_default_values(self):
        """Test filters with default values for optional config."""
        builder = Builder()

        config = {
            "spec": {
                "project_name": "my_project",
            }
        }

        # Template with filters and defaults (accessing undefined field)
        template = """
        # Project: {{ config.project_name | pascal_case }}
        Description: {{ config.missing_field | default("No description provided") }}
        
        Indent example:
        {{ "Hello\\nWorld" | indent(4) }}
        """

        result = builder._substitute_template_variables(template, config)
        assert "# Project: MyProject" in result
        assert "Description: No description provided" in result
        assert "    Hello" in result  # Indented
        assert "    World" in result  # Indented

    def test_integration_multiple_filters_chaining(self):
        """Test chaining multiple filters together."""
        builder = Builder()

        config = {
            "spec": {
                "raw_name": "my awesome project name",
                "description": "hello world project",
                "languages": ["python", "typescript"],
            }
        }

        # Template with filter chaining
        template = """
        {% set name = config.raw_name | upper | replace(" ", "_") %}
        Processed Name: {{ name }}
        
        {% set desc_processed = config.description | snake_case | upper %}
        Description: {{ desc_processed }}
        
        Languages: {{ config.languages | join(", ") | upper }}
        
        Combined: {{ config.raw_name | lower | replace(" ", "-") | upper }}
        """

        result = builder._substitute_template_variables(template, config)
        assert "Processed Name: MY_AWESOME_PROJECT_NAME" in result
        assert "Description: HELLO_WORLD_PROJECT" in result
        assert "Languages: PYTHON, TYPESCRIPT" in result
        assert "Combined: MY-AWESOME-PROJECT-NAME" in result

    def test_integration_error_handling_with_graceful_fallback(self):
        """Test error handling with graceful fallback in complex templates."""
        builder = Builder()

        config = {"spec": {"name": "test"}}

        # Test 1: Using undefined variable with default filter provides fallback
        template_undefined_with_fallback = '{{ config.missing_field | default("fallback_value") }}'
        result = builder._substitute_template_variables(template_undefined_with_fallback, config)
        assert "fallback_value" in result

        # Test 2: Complex template with mixed undefined and defined variables
        template_mixed = """
        Project: {{ config.name }}
        Author: {{ config.author | default("Unknown") }}
        Status: {{ config.status | default("In Progress") }}
        """
        result = builder._substitute_template_variables(template_mixed, config)
        assert "Project: test" in result
        assert "Author: Unknown" in result
        assert "Status: In Progress" in result

        # Test 3: Using default filter with missing config key
        template_fallback = """
        Optional Value: {{ config.missing_value | default("fallback_text") }}
        """
        result = builder._substitute_template_variables(template_fallback, config)
        assert "fallback_text" in result
