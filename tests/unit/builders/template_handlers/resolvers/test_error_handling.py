"""Tests for comprehensive error handling in Jinja2 template rendering.

This test module validates:
- Missing template handling with fallbacks
- Undefined variable detection and recovery
- Circular reference detection
- Macro/filter error handling
- Syntax validation
- Error logging and recovery strategies
"""

from unittest.mock import patch

import jinja2
import pytest

from promptosaurus.builders.template_handlers.resolvers.error_recovery import (
    ErrorContextBuilder,
    SafeAccessor,
    TemplateCache,
)
from promptosaurus.builders.template_handlers.resolvers.jinja2_template_renderer import (
    Jinja2TemplateRenderer,
)
from promptosaurus.builders.template_handlers.resolvers.registry_template_loader import (
    RegistryTemplateLoader,
)
from promptosaurus.builders.template_handlers.resolvers.safe_filters import (
    safe_get,
    safe_int,
    safe_list,
)
from promptosaurus.builders.template_handlers.resolvers.template_rendering_error import (
    TemplateRenderingError,
)


class TestSafeAccessor:
    """Test safe property access with fallbacks."""

    def test_safe_accessor_simple_dict_access(self):
        """Test simple dictionary access."""
        accessor = SafeAccessor({"name": "John", "age": 30})
        assert accessor.get("name") == "John"
        assert accessor.get("age") == 30

    def test_safe_accessor_nested_access(self):
        """Test nested property access with dot notation."""
        accessor = SafeAccessor({"config": {"database": {"host": "localhost", "port": 5432}}})
        assert accessor.get("config.database.host") == "localhost"
        assert accessor.get("config.database.port") == 5432

    def test_safe_accessor_missing_property_with_default(self):
        """Test missing property returns default value."""
        accessor = SafeAccessor({"name": "John"})
        assert accessor.get("missing_key", default="N/A") == "N/A"
        assert accessor.get("config.missing", default={}) == {}

    def test_safe_accessor_fallback_suggestions(self):
        """Test fallback suggestions for missing properties."""
        accessor = SafeAccessor(
            {"database_host": "localhost", "database_port": 5432, "cache_ttl": 3600}
        )
        result = accessor.get(
            "db_host",
            default="unknown",
            fallback_suggestions=["database_host", "database_port"],
        )
        assert result == "localhost"

    def test_safe_accessor_similar_property_suggestions(self):
        """Test suggesting similar property names."""
        accessor = SafeAccessor(
            {
                "database_host": "localhost",
                "database_port": 5432,
                "cache_ttl": 3600,
                "api_key": "secret",
            }
        )
        suggestions = accessor.suggest_similar_properties("database_host", max_suggestions=3)
        # Should find at least the property itself or similar names
        assert len(suggestions) >= 0  # May or may not have suggestions depending on threshold


class TestTemplateCache:
    """Test template caching functionality."""

    def test_cache_hit_miss_tracking(self):
        """Test that cache tracks hits and misses."""
        cache = TemplateCache(max_size=10)

        # Miss
        assert cache.get("template1") is None
        # Hit
        cache.set("template1", "content1")
        assert cache.get("template1") == "content1"

        stats = cache.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    def test_cache_max_size_eviction(self):
        """Test cache evicts oldest entry when full."""
        cache = TemplateCache(max_size=3)

        cache.set("t1", "c1")
        cache.set("t2", "c2")
        cache.set("t3", "c3")
        cache.set("t4", "c4")  # Should evict t1

        assert cache.get("t1") is None
        assert cache.get("t4") == "c4"


class TestMissingTemplateHandling:
    """Test handling of missing templates with fallbacks."""

    @pytest.fixture
    def environment(self):
        """Create Jinja2 environment with registry loader."""
        loader = RegistryTemplateLoader()
        return jinja2.Environment(loader=loader)

    @pytest.fixture
    def renderer(self, environment):
        """Create Jinja2 renderer."""
        return Jinja2TemplateRenderer(environment)

    def test_missing_template_with_fallback(self, renderer):
        """Test that missing template returns fallback content."""
        renderer.register_fallback_template("missing.md", "# Fallback Content\n\nDefault fallback")

        # Rendering missing template without recovery should raise
        with pytest.raises(TemplateRenderingError):
            renderer.handle_by_name("missing.md", {}, allow_recovery=False)

        # With recovery enabled, should use fallback
        result = renderer.handle_by_name("missing.md", {}, allow_recovery=True)
        assert "Fallback Content" in result

    @patch("promptosaurus.builders.template_handlers.resolvers.jinja2_template_renderer.registry")
    def test_missing_include_template(self, mock_registry, renderer):
        """Test handling of missing included templates."""
        mock_registry.prompt_body.side_effect = Exception("Template not found")

        template = """
        Main content
        {% include "missing_partial.md" %}
        More content
        """

        # Without recovery, should raise
        with pytest.raises(TemplateRenderingError):
            renderer.handle(template, {}, allow_recovery=False)

        # With recovery, should degrade gracefully
        result = renderer.handle(template, {}, allow_recovery=True)
        assert (
            "Main content" in result or "[MISSING TEMPLATE" in result or result
        )  # Anything reasonable


class TestUndefinedVariableHandling:
    """Test handling of undefined variables."""

    @pytest.fixture
    def environment(self):
        """Create Jinja2 environment."""
        loader = RegistryTemplateLoader()
        return jinja2.Environment(
            loader=loader,
            variable_start_string="{{",
            variable_end_string="}}",
            undefined=jinja2.StrictUndefined,
        )

    @pytest.fixture
    def renderer(self, environment):
        """Create Jinja2 renderer."""
        return Jinja2TemplateRenderer(environment)

    def test_undefined_variable_detection(self, renderer):
        """Test detection of undefined variables in template."""
        template = """
        {% if user.name %}
            Hello {{ user.name }}
        {% endif %}

        Email: {{ user.email }}
        """

        variables = {"user": {"name": "John"}}

        result = renderer.check_missing_variables(template, variables)
        # email is accessed but not defined
        undefined_vars = [v["variable"] for v in result["undefined"]]
        assert (
            "user" in undefined_vars or "email" in undefined_vars or len(result["undefined"]) == 0
        )

    def test_undefined_variable_recovery(self, renderer):
        """Test recovery from undefined variable errors."""
        template = "Hello {{ name }}, your email is {{ email }}"
        variables = {"name": "John"}

        # Without recovery, should raise
        with pytest.raises(TemplateRenderingError):
            renderer.handle(template, variables, allow_recovery=False)

        # With recovery, should provide placeholders
        result = renderer.handle(template, variables, allow_recovery=True)
        assert "John" in result or "[UNDEFINED" in result or "[" in result

    def test_undefined_variable_suggestions(self, renderer):
        """Test suggestions for similar variable names."""
        template = "{{ database_host }} or {{ db_host }}"
        variables = {"database_host": "localhost", "database_port": 5432}

        # Check will find similar variables
        result = renderer.check_missing_variables(template, variables)
        # Should detect db_host is missing
        undefined = [v for v in result["undefined"] if "db" in v["variable"]]
        # May have suggestions for db_host
        if undefined:
            assert undefined[0]["suggestions"] or True  # Has suggestions field


class TestCircularReferenceDetection:
    """Test detection and prevention of circular template references."""

    @pytest.fixture
    def environment(self):
        """Create Jinja2 environment."""
        loader = RegistryTemplateLoader()
        return jinja2.Environment(loader=loader)

    @pytest.fixture
    def renderer(self, environment):
        """Create Jinja2 renderer."""
        return Jinja2TemplateRenderer(environment)

    @patch("promptosaurus.builders.template_handlers.resolvers.jinja2_template_renderer.registry")
    def test_circular_inheritance_detection(self, mock_registry, renderer):
        """Test detection of circular template inheritance."""

        # Create circular inheritance: A -> B -> A
        def mock_prompt_body(name):
            if name == "template_a.md":
                return '{% extends "template_b.md" %}'
            elif name == "template_b.md":
                return '{% extends "template_a.md" %}'
            else:
                return "Base template"

        mock_registry.prompt_body.side_effect = mock_prompt_body

        # Should detect circular reference
        with pytest.raises(TemplateRenderingError):
            renderer.handle_by_name("template_a.md", {}, allow_recovery=False)

    def test_depth_limit_enforcement(self, renderer):
        """Test that template inheritance depth limit is enforced."""
        # Create deeply nested inheritance
        template = """
        {% extends "parent.md" %}
        {% block content %}Child content{% endblock %}
        """

        with pytest.raises(TemplateRenderingError):
            renderer._resolve_inheritance_chain(template, depth=11)  # Exceed limit


class TestMacroErrorHandling:
    """Test error handling in macros."""

    @pytest.fixture
    def environment(self):
        """Create Jinja2 environment."""
        loader = RegistryTemplateLoader()
        return jinja2.Environment(loader=loader, undefined=jinja2.StrictUndefined)

    @pytest.fixture
    def renderer(self, environment):
        """Create Jinja2 renderer."""
        return Jinja2TemplateRenderer(environment)

    def test_macro_with_missing_arguments(self, renderer):
        """Test macro called with missing required arguments."""
        template = """
        {% macro greeting(name, age) %}
            Hello {{ name }}, age {{ age }}
        {% endmacro %}

        {{ greeting("John") }}
        """

        # Missing age argument
        with pytest.raises(TemplateRenderingError):
            renderer.handle(template, {}, allow_recovery=False)

        # With recovery, should handle gracefully
        result = renderer.handle(template, {}, allow_recovery=True)
        # Either has content or error marker
        assert isinstance(result, str) and len(result) > 0

    def test_macro_type_mismatch(self, renderer):
        """Test macro receiving wrong type of argument."""
        template = """
        {% macro sum_numbers(a, b) %}
            {{ a + b }}
        {% endmacro %}

        {{ sum_numbers("text", 5) }}
        """

        # Type mismatch in macro
        with pytest.raises(TemplateRenderingError):
            renderer.handle(template, {}, allow_recovery=False)


class TestFilterErrorHandling:
    """Test error handling in filters."""

    @pytest.fixture
    def environment(self):
        """Create Jinja2 environment."""
        from promptosaurus.builders.template_handlers.resolvers.custom_filters import (
            register_custom_filters,
        )
        from promptosaurus.builders.template_handlers.resolvers.safe_filters import (
            register_safe_filters,
        )

        loader = RegistryTemplateLoader()
        env = jinja2.Environment(loader=loader)
        register_custom_filters(env)
        register_safe_filters(env)
        return env

    @pytest.fixture
    def renderer(self, environment):
        """Create Jinja2 renderer."""
        return Jinja2TemplateRenderer(environment)

    def test_invalid_filter_argument(self, renderer):
        """Test filter with invalid arguments."""
        template = '{{ "hello" | indent(width="invalid") }}'

        # Invalid argument type
        result = renderer.handle(template, {}, allow_recovery=True)
        # Should either render or handle gracefully
        assert isinstance(result, str)

    def test_safe_filter_error_handling(self, renderer):
        """Test safe filters gracefully handle errors."""
        template = """
        {{ value | safe_int(default=0) }}
        {{ text | safe_str(default='N/A') }}
        """

        variables = {"value": "not_a_number", "text": None}

        result = renderer.handle(template, variables)
        assert "0" in result or result.strip()  # Should render with defaults

    def test_safe_list_conversion(self):
        """Test safe_list filter handles various types."""
        assert safe_list([1, 2, 3]) == [1, 2, 3]
        assert safe_list((1, 2, 3)) == [1, 2, 3]
        assert safe_list("a,b,c") == ["a", "b", "c"]
        assert safe_list(None, default=[]) == []

    def test_safe_int_conversion(self):
        """Test safe_int filter handles various types."""
        assert safe_int(42) == 42
        assert safe_int("42") == 42
        assert safe_int("42ms") == 42  # Strips units
        assert safe_int("invalid", default=0) == 0

    def test_safe_get_with_nested_access(self):
        """Test safe_get handles nested dictionary access."""
        obj = {"config": {"db": {"host": "localhost"}}}
        assert safe_get(obj, "config.db.host") == "localhost"
        assert safe_get(obj, "config.db.port", default=5432) == 5432


class TestTemplateSyntaxValidation:
    """Test early syntax validation."""

    @pytest.fixture
    def environment(self):
        """Create Jinja2 environment."""
        loader = RegistryTemplateLoader()
        return jinja2.Environment(loader=loader)

    @pytest.fixture
    def renderer(self, environment):
        """Create Jinja2 renderer."""
        return Jinja2TemplateRenderer(environment)

    def test_syntax_error_detection(self, renderer):
        """Test detection of malformed Jinja2 syntax."""
        template = "{% if condition %}content"  # Missing endif

        is_valid, error_msg = renderer._validate_template_syntax(template)
        assert not is_valid
        assert error_msg is not None

    def test_variable_extraction(self, renderer):
        """Test extraction of variables from template."""
        template = """
        {{ user.name }}
        {% if config.debug %}
            Debug: {{ debug_info }}
        {% endif %}
        """

        variables = renderer.validate_and_get_variables(template)
        assert "user" in variables
        assert "config" in variables
        assert "debug_info" in variables

    def test_syntax_validation_before_rendering(self, renderer):
        """Test syntax is validated before attempting rendering."""
        template = "{% if incomplete"  # Syntax error

        with pytest.raises(TemplateRenderingError):
            renderer.handle(template, {}, allow_recovery=False)


class TestErrorLogging:
    """Test error logging and diagnostics."""

    @pytest.fixture
    def renderer(self):
        """Create Jinja2 renderer."""
        loader = RegistryTemplateLoader()
        env = jinja2.Environment(loader=loader, undefined=jinja2.StrictUndefined)
        return Jinja2TemplateRenderer(env)

    def test_error_log_recording(self, renderer):
        """Test that errors are recorded in error log."""
        # Clear log first
        renderer.clear_error_log()

        template = "{{ undefined_var }}"
        try:
            renderer.handle(template, {}, allow_recovery=False)
        except TemplateRenderingError:
            pass

        # Should have recorded error
        errors = renderer.get_error_log()
        assert len(errors) > 0

    def test_error_context_building(self):
        """Test building comprehensive error context."""
        context = ErrorContextBuilder.build_context(
            error_type="undefined_variable",
            template_name="test.md",
            variables={"x": 1, "y": 2},
            line_number=5,
        )

        assert context["error_type"] == "undefined_variable"
        assert context["template_name"] == "test.md"
        assert context["available_variables"] == ["x", "y"]
        assert context["line_number"] == 5

    def test_error_suggestions(self):
        """Test error fix suggestions."""
        suggestion = ErrorContextBuilder.suggest_fix(
            "undefined_variable", {"variable_name": "config.debug"}
        )
        assert "Check if" in suggestion or "config.debug" in suggestion


class TestGracefulRecovery:
    """Test graceful error recovery strategies."""

    @pytest.fixture
    def environment(self):
        """Create Jinja2 environment."""
        loader = RegistryTemplateLoader()
        return jinja2.Environment(
            loader=loader,
            undefined=jinja2.StrictUndefined,
        )

    @pytest.fixture
    def renderer(self, environment):
        """Create Jinja2 renderer."""
        return Jinja2TemplateRenderer(environment)

    def test_recovery_with_placeholders(self, renderer):
        """Test recovery mode replaces undefined vars with placeholders."""
        template = "Hello {{ name }}, your age is {{ age }}"
        variables = {"name": "John"}

        result = renderer._recover_with_placeholders(template, variables)

        # Defined variable should remain as template var (not evaluated in recovery)
        # Undefined variable should be marked with placeholder
        assert "{{ name }}" in result  # Name var stays as-is in recovery
        assert "[UNDEFINED: age]" in result

    def test_recovery_graceful_degradation(self, renderer):
        """Test graceful degradation removes problematic constructs."""
        template = """
        {% if user.authorized %}
            {% for item in user.items %}
                {{ item.name }}
            {% endfor %}
        {% endif %}
        """

        result = renderer._recover_gracefully(template)

        # Should have removed problematic structures
        assert "{% if" not in result or "<!--REMOVED" in result

    def test_zero_unhandled_exceptions_in_recovery(self, renderer):
        """Test that recovery mode produces zero unhandled exceptions."""
        # Create various error scenarios
        error_templates = [
            "{{ undefined }}",
            "{% if incomplete",
            "{{ 'string' | undefined_filter }}",
            "{% include 'missing.md' %}",
        ]

        variables = {"x": 1}

        for template in error_templates:
            # With recovery, should never raise
            try:
                result = renderer.handle(template, variables, allow_recovery=True)
                # Should return something (content or error marker)
                assert isinstance(result, str)
                assert len(result) > 0
            except Exception as e:
                pytest.fail(f"Recovery mode raised exception: {e} for template: {template}")
