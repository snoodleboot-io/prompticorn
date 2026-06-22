"""Coverage-focused unit tests for Jinja2TemplateRenderer.

These tests target public methods, error/recovery branches, validation,
variable detection, and caching that are not exercised by the existing
inheritance/macro/include/import test suite.
"""

import jinja2
import pytest

from prompticorn.builders.template_handlers.resolvers.jinja2_template_renderer import (
    Jinja2TemplateRenderer,
)
from prompticorn.builders.template_handlers.resolvers.template_rendering_error import (
    TemplateRenderingError,
)


def _make_environment(templates: dict[str, str] | None = None) -> jinja2.Environment:
    """Build a real Jinja2 environment, optionally with a DictLoader."""
    loader = jinja2.DictLoader(templates) if templates is not None else None
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
def renderer() -> Jinja2TemplateRenderer:
    """Renderer backed by a loader-less real environment."""
    return Jinja2TemplateRenderer(_make_environment())


class TestInitAndProperties:
    """Construction and read-only property access."""

    def test_environment_property_returns_injected_environment(self):
        # Arrange
        env = _make_environment()

        # Act
        instance = Jinja2TemplateRenderer(env)

        # Assert
        assert instance.environment is env

    def test_initial_error_log_is_empty(self, renderer):
        # Act / Assert
        assert renderer.get_error_log() == []


class TestErrorLog:
    """register_fallback_template, get_error_log, clear_error_log, _record_error."""

    def test_register_fallback_template_stores_content(self, renderer):
        # Arrange / Act
        renderer.register_fallback_template("missing.md", "fallback body")

        # Assert
        assert renderer._fallback_templates["missing.md"] == "fallback body"

    def test_record_error_appends_record_with_message_and_severity(self, renderer):
        # Act
        renderer._record_error("custom_type", "boom", template_name="t.md", severity="error")

        # Assert
        log = renderer.get_error_log()
        assert len(log) == 1
        assert log[0]["message"] == "boom"
        assert log[0]["severity"] == "error"

    def test_record_error_unknown_severity_defaults_to_warning(self, renderer):
        # Act: unknown severity should not raise (falls back to logger.warning)
        renderer._record_error("custom_type", "msg", severity="nonsense")

        # Assert
        assert renderer.get_error_log()[0]["severity"] == "nonsense"

    def test_get_error_log_returns_copy(self, renderer):
        # Arrange
        renderer._record_error("t", "m")

        # Act
        snapshot = renderer.get_error_log()
        snapshot.append({"injected": True})

        # Assert: mutating the returned list does not affect internal state
        assert len(renderer.get_error_log()) == 1

    def test_clear_error_log_empties_history(self, renderer):
        # Arrange
        renderer._record_error("t", "m")
        assert renderer.get_error_log()

        # Act
        renderer.clear_error_log()

        # Assert
        assert renderer.get_error_log() == []


class TestValidateTemplateSyntax:
    """_validate_template_syntax happy and error branches."""

    def test_valid_template_returns_true_none(self, renderer):
        # Act
        is_valid, error = renderer._validate_template_syntax("Hello {{ name }}")

        # Assert
        assert is_valid is True
        assert error is None

    def test_invalid_syntax_returns_false_and_message(self, renderer):
        # Act
        is_valid, error = renderer._validate_template_syntax("{% if %}")

        # Assert
        assert is_valid is False
        assert "Syntax error" in error


class TestValidateAndGetVariables:
    """validate_and_get_variables extraction logic."""

    def test_extracts_variable_and_control_names(self, renderer):
        # Arrange
        template = (
            "{{ user.name }} {% if active %}x{% endif %} {% for i in items %}{{ i }}{% endfor %}"
        )

        # Act
        names = renderer.validate_and_get_variables(template)

        # Assert: dotted access reduced to top-level; if/for vars captured.
        # NOTE: the control regex captures the token right after the keyword,
        # so for-loops yield the loop variable ('i'), not the iterable.
        assert "user" in names
        assert "active" in names
        assert "i" in names

    def test_no_variables_returns_empty_list(self, renderer):
        # Act
        names = renderer.validate_and_get_variables("plain text no markup")

        # Assert
        assert names == []


class TestCheckMissingVariables:
    """check_missing_variables and _find_similar_variables."""

    def test_reports_undefined_with_suggestions(self, renderer):
        # Arrange
        template = "{{ usernam }}"

        # Act
        result = renderer.check_missing_variables(template, {"username": "x"})

        # Assert
        assert result["total_required"] == 1
        undefined = result["undefined"]
        assert undefined[0]["variable"] == "usernam"
        assert "username" in undefined[0]["suggestions"]

    def test_no_undefined_when_all_present(self, renderer):
        # Act
        result = renderer.check_missing_variables("{{ name }}", {"name": "x"})

        # Assert
        assert result["undefined"] == []

    def test_find_similar_exact_match_ranked_first(self, renderer):
        # Act
        similar = renderer._find_similar_variables("name", {"name", "namespace", "nope"})

        # Assert: exact match present and ranked highest
        assert similar[0] == "name"

    def test_find_similar_no_match_returns_empty(self, renderer):
        # Act
        similar = renderer._find_similar_variables("xyz", {"abc", "def"})

        # Assert
        assert similar == []


class TestGetOrCompileTemplate:
    """_get_or_compile_template caching and error conversion."""

    def test_caches_compiled_template_by_content_hash(self, renderer):
        # Arrange
        content = "Hello {{ name }}"

        # Act
        first = renderer._get_or_compile_template(content)
        second = renderer._get_or_compile_template(content)

        # Assert: identical object returned from cache
        assert first is second
        assert hash(content) in renderer._template_cache

    def test_syntax_error_raises_template_rendering_error(self, renderer):
        # Act / Assert
        with pytest.raises(TemplateRenderingError) as exc:
            renderer._get_or_compile_template("{% if %}")
        assert "syntax error" in str(exc.value).lower()


class TestHandleHappyPath:
    """handle() successful rendering."""

    def test_simple_variable_substitution(self, renderer):
        # Act
        result = renderer.handle("Hello {{ name }}!", {"name": "World"})

        # Assert
        assert result == "Hello World!"

    def test_conditional_and_loop_render(self, renderer):
        # Arrange
        template = "{% for i in items %}[{{ i }}]{% endfor %}"

        # Act
        result = renderer.handle(template, {"items": [1, 2, 3]})

        # Assert
        assert result == "[1][2][3]"

    def test_undefined_variable_records_warning_in_log(self, renderer):
        # Act: 'missing' is referenced but not provided -> recorded before render
        renderer.handle("{{ provided }} {{ missing }}", {"provided": "ok"})

        # Assert: an undefined_variable warning was recorded
        types = [e["error_type"] for e in renderer.get_error_log()]
        assert "undefined_variable" in types


class TestHandleSyntaxError:
    """handle() early syntax validation branch."""

    def test_syntax_error_records_error_and_recovers(self, renderer):
        # Act: the early-validation TemplateRenderingError is re-caught by the
        # broad Exception handler, which records it and recovers gracefully.
        result = renderer.handle("{% if %}", {}, allow_recovery=True)

        # Assert: a syntax_error was recorded and a string was returned.
        assert isinstance(result, str)
        assert any(e["error_type"] == "syntax_error" for e in renderer.get_error_log())

    def test_syntax_error_no_recovery_raises_rendering_error(self, renderer):
        # Act / Assert: with recovery disabled the early raise propagates as the
        # compile step fails before the broad handler swallows it.
        with pytest.raises(TemplateRenderingError) as exc:
            renderer.handle("{% if %}", {}, allow_recovery=False)
        assert "syntax error" in str(exc.value).lower()


class TestHandleUndefinedRecovery:
    """handle() undefined variable runtime path with StrictUndefined."""

    def test_recovery_replaces_undefined_with_placeholder(self, renderer):
        # Arrange: StrictUndefined raises at render time for 'missing'
        template = "Value: {{ missing }}"

        # Act
        result = renderer.handle(template, {}, allow_recovery=True)

        # Assert: placeholder substituted by _recover_with_placeholders
        assert "[UNDEFINED: missing]" in result

    def test_no_recovery_raises_rendering_error(self, renderer):
        # Act / Assert
        with pytest.raises(TemplateRenderingError) as exc:
            renderer.handle("Value: {{ missing }}", {}, allow_recovery=False)
        assert "Undefined variable" in str(exc.value)


class TestHandleUnexpectedRecovery:
    """handle() generic Exception branch via graceful recovery."""

    def test_unexpected_error_recovers_gracefully(self, renderer, monkeypatch):
        # Arrange: force a non-Jinja error during compilation
        def boom(_content):
            raise RuntimeError("kaboom")

        # Patch compile step used after syntax validation passes.
        monkeypatch.setattr(renderer, "_get_or_compile_template", boom)

        # Act: template has a control structure so graceful recovery alters it
        result = renderer.handle("{% if x %}hi{% endif %}", {"x": True})

        # Assert: graceful recovery removed the if block
        assert "REMOVED: if block" in result
        assert any(e["error_type"] == "unexpected_error" for e in renderer.get_error_log())

    def test_unexpected_error_no_recovery_raises(self, renderer, monkeypatch):
        # Arrange
        def boom(_content):
            raise RuntimeError("kaboom")

        monkeypatch.setattr(renderer, "_get_or_compile_template", boom)

        # Act / Assert
        with pytest.raises(TemplateRenderingError) as exc:
            renderer.handle("{{ x }}", {"x": 1}, allow_recovery=False)
        assert "Unexpected error" in str(exc.value)


class TestRecoveryHelpers:
    """_recover_with_placeholders and _recover_gracefully directly."""

    def test_recover_with_placeholders_only_missing_vars(self, renderer):
        # Act
        result = renderer._recover_with_placeholders("{{ have }} and {{ missing }}", {"have": "x"})

        # Assert
        assert "[UNDEFINED: missing]" in result
        assert "[UNDEFINED: have]" not in result

    def test_recover_gracefully_removes_if_and_for(self, renderer):
        # Act
        result = renderer._recover_gracefully("{% if a %}x{% endif %}{% for i in b %}y{% endfor %}")

        # Assert
        assert "REMOVED: if block" in result
        assert "REMOVED: for block" in result


class TestHandleByName:
    """handle_by_name() loader-based rendering and error branches."""

    def test_renders_named_template_with_variables(self):
        # Arrange
        env = _make_environment({"greet.md": "Hi {{ name }}"})
        instance = Jinja2TemplateRenderer(env)

        # Act
        result = instance.handle_by_name("greet.md", {"name": "Sam"})

        # Assert
        assert result == "Hi Sam"

    def test_missing_template_uses_registered_fallback(self):
        # Arrange
        env = _make_environment({})
        instance = Jinja2TemplateRenderer(env)
        instance.register_fallback_template("absent.md", "Fallback {{ x }}")

        # Act
        result = instance.handle_by_name("absent.md", {"x": "Y"})

        # Assert
        assert result == "Fallback Y"
        assert any(e["error_type"] == "missing_template" for e in instance.get_error_log())

    def test_missing_template_recovery_placeholder_when_no_fallback(self):
        # Arrange
        env = _make_environment({})
        instance = Jinja2TemplateRenderer(env)

        # Act
        result = instance.handle_by_name("absent.md", {})

        # Assert
        assert result == "[MISSING TEMPLATE: absent.md]"

    def test_missing_template_no_recovery_raises(self):
        # Arrange
        env = _make_environment({})
        instance = Jinja2TemplateRenderer(env)

        # Act / Assert
        with pytest.raises(TemplateRenderingError) as exc:
            instance.handle_by_name("absent.md", {}, allow_recovery=False)
        assert "not found in registry" in str(exc.value)

    def test_undefined_variable_recovery_returns_placeholder(self):
        # Arrange: StrictUndefined raises on render
        env = _make_environment({"t.md": "{{ needed }}"})
        instance = Jinja2TemplateRenderer(env)

        # Act
        result = instance.handle_by_name("t.md", {})

        # Assert
        assert result == "[UNDEFINED VARIABLES IN: t.md]"

    def test_undefined_variable_no_recovery_raises(self):
        # Arrange
        env = _make_environment({"t.md": "{{ needed }}"})
        instance = Jinja2TemplateRenderer(env)

        # Act / Assert
        with pytest.raises(TemplateRenderingError) as exc:
            instance.handle_by_name("t.md", {}, allow_recovery=False)
        assert "Undefined variable" in str(exc.value)

    def test_template_error_recovery_returns_placeholder(self):
        # Arrange: a template syntax error surfaces at get_template time
        env = _make_environment({"bad.md": "{% if %}"})
        instance = Jinja2TemplateRenderer(env)

        # Act
        result = instance.handle_by_name("bad.md", {})

        # Assert: caught as a TemplateError branch -> placeholder
        assert result == "[TEMPLATE ERROR IN: bad.md]"

    def test_template_error_no_recovery_raises(self):
        # Arrange
        env = _make_environment({"bad.md": "{% if %}"})
        instance = Jinja2TemplateRenderer(env)

        # Act / Assert
        with pytest.raises(TemplateRenderingError) as exc:
            instance.handle_by_name("bad.md", {}, allow_recovery=False)
        assert "rendering failed" in str(exc.value)

    def test_unexpected_error_recovery_returns_placeholder(self):
        # Arrange: force a non-Jinja error from get_template
        env = _make_environment({"t.md": "ok"})
        instance = Jinja2TemplateRenderer(env)

        def boom(_name):
            raise RuntimeError("explode")

        env.get_template = boom

        # Act
        result = instance.handle_by_name("t.md", {})

        # Assert
        assert result == "[ERROR IN: t.md]"
        assert any(e["error_type"] == "unexpected_error" for e in instance.get_error_log())

    def test_unexpected_error_no_recovery_raises(self):
        # Arrange
        env = _make_environment({"t.md": "ok"})
        instance = Jinja2TemplateRenderer(env)

        def boom(_name):
            raise RuntimeError("explode")

        env.get_template = boom

        # Act / Assert
        with pytest.raises(TemplateRenderingError) as exc:
            instance.handle_by_name("t.md", {}, allow_recovery=False)
        assert "Unexpected error" in str(exc.value)

    def test_loader_reset_inheritance_chain_invoked_when_available(self):
        # Arrange: loader exposes reset_inheritance_chain
        env = _make_environment({"t.md": "ok"})
        calls = {"count": 0}

        def reset():
            calls["count"] += 1

        env.loader.reset_inheritance_chain = reset
        instance = Jinja2TemplateRenderer(env)

        # Act
        instance.handle_by_name("t.md", {})

        # Assert
        assert calls["count"] == 1
