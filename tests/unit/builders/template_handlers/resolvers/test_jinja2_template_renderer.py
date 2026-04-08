"""Unit tests for the Jinja2TemplateRenderer class inheritance and macro functionality."""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add the promptosaurus directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import jinja2
import pytest

from promptosaurus.builders.template_handlers.resolvers.jinja2_template_renderer import (
    Jinja2TemplateRenderer,
)
from promptosaurus.builders.template_handlers.resolvers.template_rendering_error import (
    TemplateRenderingError,
)


class TestJinja2TemplateRendererInheritance:
    """Test inheritance functionality in Jinja2TemplateRenderer."""

    @pytest.fixture
    def mock_environment(self):
        """Create a mock Jinja2 environment for testing."""
        env = Mock(spec=jinja2.Environment)
        env.from_string = Mock()
        return env

    @pytest.fixture
    def renderer(self, mock_environment):
        """Create a Jinja2TemplateRenderer instance for testing."""
        return Jinja2TemplateRenderer(mock_environment)

    def test_detect_inheritance_no_inheritance(self, renderer):
        """Test _detect_inheritance returns None when no inheritance is used."""
        template = "Simple template without inheritance"
        result = renderer._detect_inheritance(template)
        assert result is None

    def test_detect_inheritance_with_extends(self, renderer):
        """Test _detect_inheritance detects extends directive."""
        template = """{% extends "base-template.md" %}
{% block content %}Child content{% endblock %}"""
        result = renderer._detect_inheritance(template)
        assert result == "base-template.md"

    def test_detect_inheritance_with_quotes_variations(self, renderer):
        """Test _detect_inheritance works with different quote styles."""
        # Double quotes
        template1 = """{% extends "base.md" %}"""
        assert renderer._detect_inheritance(template1) == "base.md"

        # Single quotes
        template2 = """{% extends 'base.md' %}"""
        assert renderer._detect_inheritance(template2) == "base.md"

    def test_detect_inheritance_with_whitespace(self, renderer):
        """Test _detect_inheritance handles whitespace around extends."""
        template = """   {% extends "base.md" %}   """
        result = renderer._detect_inheritance(template)
        assert result == "base.md"

    def test_extract_blocks_simple(self, renderer):
        """Test _extract_blocks extracts simple blocks correctly."""
        template = """Base content
{% block header %}Default Header{% endblock %}
More content
{% block footer %}Default Footer{% endblock %}"""

        blocks = renderer._extract_blocks(template)

        assert "header" in blocks
        assert "footer" in blocks
        assert blocks["header"] == "Default Header"
        assert blocks["footer"] == "Default Footer"

    def test_extract_blocks_nested(self, renderer):
        """Test _extract_blocks handles nested blocks correctly."""
        template = """{% block outer %}
Outer start
{% block inner %}Inner content{% endblock %}
Outer end
{% endblock %}"""

        blocks = renderer._extract_blocks(template)

        assert "outer" in blocks
        assert "inner" in blocks
        assert "Inner content" in blocks["inner"]
        assert (
            "Outer start\n{% block inner %}Inner content{% endblock %}\nOuter end"
            in blocks["outer"]
        )

    def test_extract_blocks_malformed_syntax(self, renderer):
        """Test _extract_blocks raises error for malformed block syntax."""
        # Missing closing %}
        template = """{% block content %}Content{% endblock"""

        with pytest.raises(TemplateRenderingError) as exc_info:
            renderer._extract_blocks(template)
        assert "Malformed block syntax" in str(exc_info.value)

    def test_extract_blocks_invalid_declaration(self, renderer):
        """Test _extract_blocks raises error for invalid block declaration."""
        template = """{% block %}Content{% endblock %}"""

        with pytest.raises(TemplateRenderingError) as exc_info:
            renderer._extract_blocks(template)
        assert "Invalid block declaration" in str(exc_info.value)

    def test_extract_blocks_unclosed_block(self, renderer):
        """Test _extract_blocks raises error for unclosed blocks."""
        template = """{% block content %}Content without endblock"""

        with pytest.raises(TemplateRenderingError) as exc_info:
            renderer._extract_blocks(template)
        assert "Unclosed block" in str(exc_info.value)

    def test_resolve_inheritance_chain_no_inheritance(self, renderer):
        """Test _resolve_inheritance_chain returns template as-is when no inheritance."""
        template = "Simple template"
        content, blocks = renderer._resolve_inheritance_chain(template)

        assert content == template
        assert isinstance(blocks, dict)

    @patch("promptosaurus.registry.registry.prompt_body")
    def test_resolve_inheritance_chain_single_level(self, mock_prompt_body, renderer):
        """Test _resolve_inheritance_chain resolves single-level inheritance."""
        base_template = """Base
{% block content %}Default{% endblock %}"""

        child_template = """{% extends "base.md" %}
{% block content %}Overridden{% endblock %}"""

        mock_prompt_body.return_value = base_template

        content, blocks = renderer._resolve_inheritance_chain(child_template)

        assert content == base_template
        assert "content" in blocks
        assert blocks["content"] == "Overridden"

    @patch("promptosaurus.registry.registry.prompt_body")
    def test_resolve_inheritance_chain_multi_level(self, mock_prompt_body, renderer):
        """Test _resolve_inheritance_chain resolves multi-level inheritance."""
        grandparent = """Grandparent
{% block header %}Default Header{% endblock %}
{% block content %}Grandparent Content{% endblock %}"""

        parent = """{% extends "grandparent.md" %}
{% block header %}Parent Header{% endblock %}"""

        child = """{% extends "parent.md" %}
{% block content %}Child Content{% endblock %}"""

        def mock_body(filename):
            if filename == "grandparent.md":
                return grandparent
            elif filename == "parent.md":
                return parent
            else:
                raise FileNotFoundError()

        mock_prompt_body.side_effect = mock_body

        content, blocks = renderer._resolve_inheritance_chain(child)

        assert content == grandparent
        assert blocks["header"] == "Parent Header"
        assert blocks["content"] == "Child Content"

    def test_resolve_inheritance_chain_circular_dependency(self, renderer):
        """Test _resolve_inheritance_chain detects circular dependencies."""
        # This would require mocking the registry to create a circular reference
        # For now, we'll test the detection logic by manually calling with visited set
        template = """{% extends "self.md" %}"""

        with pytest.raises(TemplateRenderingError) as exc_info:
            renderer._resolve_inheritance_chain(template, visited_templates={"self.md"})

        assert "Circular template inheritance detected" in str(exc_info.value)

    def test_resolve_inheritance_chain_depth_limit(self, renderer):
        """Test _resolve_inheritance_chain enforces depth limit."""
        # Create a deep inheritance chain that exceeds the limit
        templates = {}
        for i in range(12):  # More than max_depth of 10
            templates[f"template{i}.md"] = f"""{{% extends "template{i + 1}.md" %}}"""

        # Mock the registry to return these templates
        with patch("promptosaurus.registry.registry.prompt_body") as mock_body:
            mock_body.side_effect = lambda name: templates.get(name, "")

            deep_template = """{% extends "template0.md" %}"""

            with pytest.raises(TemplateRenderingError) as exc_info:
                renderer._resolve_inheritance_chain(deep_template)

            assert "inheritance depth limit" in str(exc_info.value)

    @patch("promptosaurus.registry.registry.prompt_body")
    def test_merge_templates_basic(self, mock_prompt_body, renderer):
        """Test _merge_templates merges basic inheritance."""
        base = """Base
{% block content %}Default{% endblock %}"""

        child = """{% extends "base.md" %}
{% block content %}Overridden{% endblock %}"""

        mock_prompt_body.return_value = base

        result = renderer._merge_templates(child)

        # Should contain base content with child block substituted
        assert "Base" in result
        assert "Overridden" in result
        assert "Default" not in result

    @patch("promptosaurus.registry.registry.prompt_body")
    def test_merge_templates_with_super(self, mock_prompt_body, renderer):
        """Test _merge_templates handles {% super() %} calls."""
        base = """Base
{% block content %}Default content{% endblock %}"""

        child = """{% extends "base.md" %}
{% block content %}Child content {{ super() }}{% endblock %}"""

        mock_prompt_body.return_value = base

        result = renderer._merge_templates(child)

        # Should contain both child and parent content
        assert "Base" in result
        assert "Child content" in result
        assert "Default content" in result

    @patch("promptosaurus.registry.registry.prompt_body")
    def test_merge_templates_missing_base(self, mock_prompt_body, renderer):
        """Test _merge_templates handles missing base templates."""
        child = """{% extends "missing.md" %}
{% block content %}Content{% endblock %}"""

        mock_prompt_body.side_effect = FileNotFoundError("Template not found")

        with pytest.raises(TemplateRenderingError) as exc_info:
            renderer._merge_templates(child)

        assert "Failed to load base template" in str(exc_info.value)


class TestJinja2TemplateRendererMacros:
    """Test macro functionality in Jinja2TemplateRenderer."""

    @pytest.fixture
    def real_environment(self):
        """Create a real Jinja2 environment for macro testing."""
        return jinja2.Environment(
            variable_start_string="{{",
            variable_end_string="}}",
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            cache_size=400,
            undefined=jinja2.StrictUndefined,
        )

    @pytest.fixture
    def renderer(self, real_environment):
        """Create a Jinja2TemplateRenderer instance with real environment for testing."""
        return Jinja2TemplateRenderer(real_environment)

    def test_macro_definition_and_calling(self, renderer):
        """Test basic macro definition and calling."""
        template = """
{% macro render_list(items) %}
{% for item in items %}- {{ item }}
{% endfor %}
{% endmacro %}

{{ render_list(config.linters) }}
"""

        variables = {"config": {"linters": ["ruff", "eslint", "mypy"]}}

        result = renderer.handle(template, variables)

        # Should render the list
        assert "- ruff" in result
        assert "- eslint" in result
        assert "- mypy" in result

    def test_macro_with_parameters(self, renderer):
        """Test macro with positional and keyword parameters."""
        template = """
{% macro format_item(name, value, prefix="Item: ") %}
{{ prefix }}{{ name }} = {{ value }}
{% endmacro %}

{{ format_item("timeout", 30) }}
{{ format_item("retries", 3, prefix="Config: ") }}
"""

        variables = {}
        result = renderer.handle(template, variables)

        assert "Item: timeout = 30" in result
        assert "Config: retries = 3" in result

    def test_macro_scoping_variable_isolation(self, renderer):
        """Test that macros have proper variable scoping and isolation."""
        template = """
{% macro test_scope(local_var) %}
{% set outer_var = "modified_in_macro" %}
Local: {{ local_var }}
Outer in macro: {{ outer_var }}
{% endmacro %}

Outer before: {{ outer_var|default("not_set") }}
{{ test_scope("macro_value") }}
Outer after: {{ outer_var|default("still_not_set") }}
"""

        variables = {}
        result = renderer.handle(template, variables)

        assert "Outer before: not_set" in result
        assert "Local: macro_value" in result
        assert "Outer in macro: modified_in_macro" in result
        assert "Outer after: still_not_set" in result

    def test_macro_with_config_context(self, renderer):
        """Test macro working with typical config context."""
        template = """
{% macro render_section(title, items) %}
## {{ title }}
{% for item in items %}
- {{ item.name }}: {{ item.description }}
{% endfor %}
{% endmacro %}

{{ render_section("Linters", config.linters) }}
{{ render_section("Formatters", config.formatters) }}
"""

        variables = {
            "config": {
                "linters": [
                    {"name": "ruff", "description": "Fast Python linter"},
                    {"name": "mypy", "description": "Type checker"},
                ],
                "formatters": [
                    {"name": "black", "description": "Python formatter"},
                    {"name": "prettier", "description": "JavaScript formatter"},
                ],
            }
        }

        result = renderer.handle(template, variables)

        assert "## Linters" in result
        assert "- ruff: Fast Python linter" in result
        assert "- mypy: Type checker" in result
        assert "## Formatters" in result
        assert "- black: Python formatter" in result
        assert "- prettier: JavaScript formatter" in result

    def test_macro_with_conditionals_and_loops(self, renderer):
        """Test macro containing conditionals and loops."""
        template = """
{% macro render_optional_list(title, items, show_empty=true) %}
{% if items or show_empty %}
## {{ title }}
{% if items %}
{% for item in items %}
- {{ item }}
{% endfor %}
{% else %}
_No items_
{% endif %}
{% endif %}
{% endmacro %}

{{ render_optional_list("Dependencies", config.dependencies) }}
{{ render_optional_list("Scripts", [], show_empty=false) }}
"""

        variables = {"config": {"dependencies": ["requests", "jinja2", "pytest"]}}

        result = renderer.handle(template, variables)

        assert "## Dependencies" in result
        assert "- requests" in result
        assert "- jinja2" in result
        assert "- pytest" in result
        # Should not contain Scripts section since show_empty=false and items is empty
        assert "## Scripts" not in result

    def test_macro_error_handling(self, renderer):
        """Test error handling when macro is called incorrectly."""
        template = """
{% macro requires_param(param) %}
Value: {{ param }}
{% endmacro %}

{{ requires_param() }}
"""

        variables = {}

        with pytest.raises(TemplateRenderingError) as exc_info:
            renderer.handle(template, variables)

        # Jinja2 should report the missing argument (or undefined variable)
        error_msg = str(exc_info.value)
        assert (
            "Undefined" in error_msg or "runtime error" in error_msg.lower() or "param" in error_msg
        )

    def test_macro_in_block_context(self, renderer):
        """Test macros work properly within blocks and complex template contexts."""
        # Test that macros defined and used in complex contexts work
        template = """
{% macro section_header(title) %}
## {{ title }}
{% endmacro %}

{% set title = "Configuration" %}
{{ section_header(title) }}

Content below header
"""

        variables = {}
        result = renderer.handle(template, variables)

        # Should contain macro output
        assert "## Configuration" in result
        assert "Content below header" in result


class TestJinja2TemplateRendererIncludes:
    """Test include functionality in Jinja2TemplateRenderer.

    Note: Includes require a loader to fetch templates. These tests verify
    that the Jinja2 environment is properly configured to support includes
    with the RegistryTemplateLoader.
    """

    @pytest.fixture
    def real_environment(self):
        """Create a real Jinja2 environment for include testing."""
        import jinja2

        # Use a simple DictLoader for testing includes without registry mocking
        loader = jinja2.DictLoader(
            {
                "header.md": "## Included Header\nThis is included content.",
                "footer.md": "# Footer Content",
                "level1.md": "Level 1 Start\n{% include 'level2.md' %}\nLevel 1 End",
                "level2.md": "Level 2 Content",
                "item.md": "Item: {{ item }}",
                "user.md": "Username: {{ username }}\nEmail: {{ email }}",
                "optional.md": "Optional Content Included",
            }
        )

        return jinja2.Environment(
            loader=loader,
            variable_start_string="{{",
            variable_end_string="}}",
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            cache_size=400,
            undefined=jinja2.StrictUndefined,
        )

    @pytest.fixture
    def renderer(self, real_environment):
        """Create a Jinja2TemplateRenderer instance with real environment for testing."""
        return Jinja2TemplateRenderer(real_environment)

    def test_include_simple_template(self, renderer):
        """Test including a simple template with content."""
        main_template = """# Main Title
{% include "header.md" %}
More content below."""

        result = renderer.handle(main_template, {})

        assert "# Main Title" in result
        assert "## Included Header" in result
        assert "This is included content." in result
        assert "More content below." in result

    def test_include_with_variables(self, renderer):
        """Test including template that uses variables from parent context."""
        main_template = """User Profile:
{% include "user.md" %}
---"""

        result = renderer.handle(main_template, {"username": "john", "email": "john@example.com"})

        assert "User Profile:" in result
        assert "Username: john" in result
        assert "Email: john@example.com" in result

    def test_include_multiple_templates(self, renderer):
        """Test including multiple templates in the same parent."""
        main_template = """{% include "header.md" %}
Middle content
{% include "footer.md" %}"""

        result = renderer.handle(main_template, {})

        assert "## Included Header" in result
        assert "Middle content" in result
        assert "# Footer Content" in result

    def test_include_nested_includes(self, renderer):
        """Test that includes can contain includes."""
        main_template = """Main Start
{% include "level1.md" %}
Main End"""

        result = renderer.handle(main_template, {})

        assert "Main Start" in result
        assert "Level 1 Start" in result
        assert "Level 2 Content" in result
        assert "Level 1 End" in result
        assert "Main End" in result

    def test_include_with_conditionals_in_parent(self, renderer):
        """Test conditional include based on parent context."""
        main_template = """Main Content
{% if config.include_optional %}
{% include "optional.md" %}
{% endif %}
End Content"""

        # Test with include_optional = True
        result = renderer.handle(main_template, {"config": {"include_optional": True}})
        assert "Optional Content Included" in result

        # Test with include_optional = False
        result = renderer.handle(main_template, {"config": {"include_optional": False}})
        assert "Optional Content Included" not in result

    def test_include_in_loop(self, renderer):
        """Test including template inside a loop."""
        main_template = """Items:
{% for item in items %}
{% include "item.md" %}
{% endfor %}
Done"""

        result = renderer.handle(main_template, {"items": ["A", "B", "C"]})

        assert "Item: A" in result
        assert "Item: B" in result
        assert "Item: C" in result


class TestJinja2TemplateRendererImports:
    """Test import functionality in Jinja2TemplateRenderer.

    Note: Imports require a loader to fetch templates. These tests verify
    that the Jinja2 environment is properly configured to support imports
    with the RegistryTemplateLoader.
    """

    @pytest.fixture
    def real_environment(self):
        """Create a real Jinja2 environment for import testing."""
        import jinja2

        # Use a simple DictLoader for testing imports without registry mocking
        loader = jinja2.DictLoader(
            {
                "macros.md": """{% macro greet(name) %}Hello, {{ name }}!{% endmacro %}
{% macro farewell(name) %}Goodbye, {{ name }}!{% endmacro %}
{% macro format_list(items) %}{% for item in items %}* {{ item }}
{% endfor %}{% endmacro %}
{% macro item1() %}Item 1{% endmacro %}
{% macro item2() %}Item 2{% endmacro %}
{% macro item3() %}Item 3{% endmacro %}
{% macro render_config_item(item) %}- {{ item.name }}: {{ item.value }}
{% endmacro %}""",
                "string.md": """{% macro uppercase(text) %}{{ text | upper }}{% endmacro %}""",
                "list.md": """{% macro count_items(items) %}Count: {{ items | length }}{% endmacro %}""",
                "base.md": """{% macro base_macro() %}Base Macro Output{% endmacro %}""",
                "helpers.md": """{% import "base.md" as base %}
{% macro helper_macro() %}{{ base.base_macro() }} + Helper{% endmacro %}""",
                "header.md": "Project Header",
                "helper_macros.md": """{% macro format_header(title) %}
## {{ title }}
{% endmacro %}""",
            }
        )

        return jinja2.Environment(
            loader=loader,
            variable_start_string="{{",
            variable_end_string="}}",
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
            cache_size=400,
            undefined=jinja2.StrictUndefined,
        )

    @pytest.fixture
    def renderer(self, real_environment):
        """Create a Jinja2TemplateRenderer instance with real environment for testing."""
        return Jinja2TemplateRenderer(real_environment)

    def test_import_macros_basic(self, renderer):
        """Test importing macros from another template."""
        main_template = """{% import "macros.md" as m %}
{{ m.greet("World") }}
{{ m.farewell("Friends") }}"""

        result = renderer.handle(main_template, {})

        assert "Hello, World!" in result
        assert "Goodbye, Friends!" in result

    def test_import_macros_with_context(self, renderer):
        """Test that imported macros have access to parent context."""
        main_template = """{% import "macros.md" as m %}
Configuration:
{% for item in config_items %}
{{ m.render_config_item(item) }}
{% endfor %}"""

        variables = {
            "config_items": [
                {"name": "debug", "value": "true"},
                {"name": "timeout", "value": "30"},
            ]
        }

        result = renderer.handle(main_template, variables)

        assert "- debug: true" in result
        assert "- timeout: 30" in result

    def test_import_with_alias(self, renderer):
        """Test importing macros with a specific alias."""
        main_template = """{% import "macros.md" as helpers %}
{% import "macros.md" as utils %}

Using helpers:
{{ helpers.format_list(list1) }}

Using utils:
{{ utils.format_list(list2) }}"""

        variables = {"list1": ["a", "b"], "list2": ["x", "y", "z"]}

        result = renderer.handle(main_template, variables)

        assert "* a" in result
        assert "* b" in result
        assert "* x" in result
        assert "* y" in result
        assert "* z" in result

    def test_import_macros_nested(self, renderer):
        """Test importing from a template that itself imports macros."""
        main_template = """{% import "helpers.md" as h %}
{{ h.helper_macro() }}"""

        result = renderer.handle(main_template, {})

        assert "Base Macro Output" in result
        assert "Helper" in result

    def test_import_multiple_macro_modules(self, renderer):
        """Test importing multiple macro modules in one template."""
        main_template = """{% import "string.md" as strings %}
{% import "list.md" as lists %}

{{ strings.uppercase("hello world") }}
{{ lists.count_items(my_items) }}"""

        variables = {"my_items": ["a", "b", "c"]}

        result = renderer.handle(main_template, variables)

        assert "HELLO WORLD" in result
        assert "Count: 3" in result

    def test_import_from_and_import_syntax(self, renderer):
        """Test {% from %} ... {% import %} syntax for selective imports."""
        # Using 'from ... import' syntax to import specific macros
        main_template = """{% from "macros.md" import item1, item2 %}

{{ item1() }}
{{ item2() }}"""

        result = renderer.handle(main_template, {})

        assert "Item 1" in result
        assert "Item 2" in result

    def test_include_and_import_together(self, renderer):
        """Test using both include and import in the same template."""
        # Add include templates to the loader's dict
        main_template = """# Project
{% import "helper_macros.md" as m %}
{{ m.format_header("Configuration") }}
Content here"""

        result = renderer.handle(main_template, {})

        assert "# Project" in result
        assert "## Configuration" in result
        assert "Content here" in result
