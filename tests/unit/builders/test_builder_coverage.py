"""Coverage-focused unit tests for prompticorn.builders.builder.

These tests exercise the public surface of the Builder base class and the
TemplateHandlerRegistry, including registration, template substitution, the
handler lifecycle hooks, and the _copy file helper. TUI/curses behavior is
intentionally not exercised.
"""

from pathlib import Path
from typing import Any

import jinja2
import pytest

from prompticorn.builders.builder import Builder, TemplateHandlerRegistry
from prompticorn.builders.template_handlers.template_handler import TemplateHandler


class RecordingHandler(TemplateHandler):
    """A minimal handler that records lifecycle calls for assertions."""

    def __init__(self, variable: str = "FAKE_VAR", value: str = "fake-value"):
        self.variable = variable
        self.value = value
        self.injected: dict[str, Any] | None = None
        self.initialized = False
        self.configured_with: dict[str, Any] | None = None
        self.cleaned_up = False
        self.errors: list[str] = []

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == self.variable

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return self.value

    def inject_dependencies(self, dependencies: dict[str, Any]) -> None:
        self.injected = dependencies

    def initialize(self) -> None:
        self.initialized = True

    def configure(self, config: dict[str, Any]) -> None:
        self.configured_with = config

    def validate_configuration(self, config: dict[str, Any]) -> list[str]:
        return self.errors

    def cleanup(self) -> None:
        self.cleaned_up = True


class ConcreteBuilder(Builder):
    """Concrete Builder used to instantiate the abstract base class."""


# --------------------------------------------------------------------------- #
# TemplateHandlerRegistry
# --------------------------------------------------------------------------- #


class TestTemplateHandlerRegistry:
    """Tests for the TemplateHandlerRegistry."""

    def test_register_and_get_handlers_returns_copy(self):
        # Arrange
        registry = TemplateHandlerRegistry()
        handler = RecordingHandler()

        # Act
        registry.register_handler(handler)
        handlers = registry.get_handlers()
        handlers.clear()  # mutating the returned list must not affect the registry

        # Assert
        assert registry.get_handlers() == [handler]

    def test_unregister_removes_registered_handler(self):
        # Arrange
        registry = TemplateHandlerRegistry()
        handler = RecordingHandler()
        registry.register_handler(handler)

        # Act
        registry.unregister_handler(handler)

        # Assert
        assert registry.get_handlers() == []

    def test_unregister_unknown_handler_is_noop(self):
        # Arrange
        registry = TemplateHandlerRegistry()
        handler = RecordingHandler()

        # Act / Assert (should not raise)
        registry.unregister_handler(handler)
        assert registry.get_handlers() == []

    def test_get_handler_for_variable_returns_matching_handler(self):
        # Arrange
        registry = TemplateHandlerRegistry()
        handler = RecordingHandler(variable="ABC")
        registry.register_handler(handler)

        # Act
        found = registry.get_handler_for_variable("ABC")

        # Assert
        assert found is handler

    def test_get_handler_for_variable_returns_none_when_no_match(self):
        # Arrange
        registry = TemplateHandlerRegistry()
        registry.register_handler(RecordingHandler(variable="ABC"))

        # Act
        found = registry.get_handler_for_variable("UNKNOWN")

        # Assert
        assert found is None

    def test_get_handler_for_variable_returns_first_match(self):
        # Arrange
        registry = TemplateHandlerRegistry()
        first = RecordingHandler(variable="DUP")
        second = RecordingHandler(variable="DUP")
        registry.register_handler(first)
        registry.register_handler(second)

        # Act
        found = registry.get_handler_for_variable("DUP")

        # Assert
        assert found is first


# --------------------------------------------------------------------------- #
# Builder construction
# --------------------------------------------------------------------------- #


class TestBuilderConstruction:
    """Tests for Builder initialization and defaults."""

    def test_default_factory_populates_template_handlers(self):
        # Arrange / Act
        builder = ConcreteBuilder()

        # Assert
        assert builder._template_handlers
        assert isinstance(builder._jinja2_environment, jinja2.Environment)

    def test_custom_factory_is_used_and_handlers_initialized(self):
        # Arrange
        handler = RecordingHandler()

        # Act
        builder = ConcreteBuilder(template_handler_factory=lambda: [handler])

        # Assert
        assert builder._template_handlers == [handler]
        assert handler.initialized is True
        assert handler.injected == {}

    def test_jinja2_environment_uses_strict_undefined(self):
        # Arrange / Act
        builder = ConcreteBuilder()

        # Assert
        assert builder._jinja2_environment.undefined is jinja2.StrictUndefined
        assert builder._jinja2_environment.variable_start_string == "{{"
        assert builder._jinja2_environment.variable_end_string == "}}"

    def test_build_raises_not_implemented(self):
        # Arrange
        builder = ConcreteBuilder()

        # Act / Assert
        with pytest.raises(NotImplementedError):
            builder.build(Path("/tmp/output"))

    def test_get_template_substitutions_base_returns_empty(self):
        # Arrange
        builder = ConcreteBuilder()

        # Act
        result = builder._get_template_substitutions({"x": 1}, lambda v: v)

        # Assert
        assert result == {}


# --------------------------------------------------------------------------- #
# Handler registration on the builder
# --------------------------------------------------------------------------- #


class TestBuilderHandlerRegistration:
    """Tests for register/unregister template handlers on the Builder."""

    def test_register_template_handler_adds_to_registry(self):
        # Arrange
        builder = ConcreteBuilder()
        handler = RecordingHandler(variable="REGVAR")

        # Act
        builder.register_template_handler(handler)

        # Assert
        assert builder._template_handler_registry.get_handler_for_variable("REGVAR") is handler

    def test_unregister_template_handler_removes_from_registry(self):
        # Arrange
        builder = ConcreteBuilder()
        handler = RecordingHandler(variable="REGVAR")
        builder.register_template_handler(handler)

        # Act
        builder.unregister_template_handler(handler)

        # Assert
        assert builder._template_handler_registry.get_handler_for_variable("REGVAR") is None


# --------------------------------------------------------------------------- #
# Template substitution
# --------------------------------------------------------------------------- #


class TestSubstituteTemplateVariables:
    """Tests for _substitute_template_variables."""

    def test_none_config_renders_plain_text(self):
        # Arrange
        builder = ConcreteBuilder()

        # Act
        result = builder._substitute_template_variables("hello world", None)

        # Assert
        assert result == "hello world"

    def test_config_spec_dict_is_exposed_as_config_namespace(self):
        # Arrange
        builder = ConcreteBuilder()
        config = {"spec": {"name": "Widget"}}

        # Act
        result = builder._substitute_template_variables("{{config.name}}", config)

        # Assert
        assert result == "Widget"

    def test_config_spec_list_uses_first_element(self):
        # Arrange
        builder = ConcreteBuilder()
        config = {"spec": [{"name": "First"}, {"name": "Second"}]}

        # Act
        result = builder._substitute_template_variables("{{config.name}}", config)

        # Assert
        assert result == "First"

    def test_config_spec_empty_list_yields_empty_namespace(self):
        # Arrange
        builder = ConcreteBuilder()
        config = {"spec": []}

        # Act
        result = builder._substitute_template_variables("static text", config)

        # Assert
        assert result == "static text"

    def test_registered_known_variable_is_resolved(self):
        # Arrange: install a fresh registry whose only handler resolves a known
        # variable name, so it is the first (and only) match.
        builder = ConcreteBuilder()
        registry = TemplateHandlerRegistry()
        handler = RecordingHandler(variable="LANGUAGE", value="python")
        registry.register_handler(handler)
        builder._template_handler_registry = registry

        # Act
        result = builder._substitute_template_variables("lang={{LANGUAGE}}", {"spec": {}})

        # Assert
        assert result == "lang=python"


# --------------------------------------------------------------------------- #
# Handler lifecycle: configure / cleanup
# --------------------------------------------------------------------------- #


class TestHandlerLifecycle:
    """Tests for _configure_handlers and _cleanup_handlers."""

    def test_configure_handlers_calls_configure_and_collects_errors(self):
        # Arrange
        handler = RecordingHandler()
        handler.errors = ["boom"]
        builder = ConcreteBuilder(template_handler_factory=lambda: [handler])
        config = {"key": "value"}

        # Act
        errors = builder._configure_handlers(config)

        # Assert
        assert handler.configured_with == config
        assert "boom" in errors

    def test_configure_handlers_with_none_uses_empty_config(self):
        # Arrange
        handler = RecordingHandler()
        builder = ConcreteBuilder(template_handler_factory=lambda: [handler])

        # Act
        errors = builder._configure_handlers(None)

        # Assert
        assert handler.configured_with == {}
        assert errors == []

    def test_cleanup_handlers_calls_cleanup(self):
        # Arrange
        handler = RecordingHandler()
        builder = ConcreteBuilder(template_handler_factory=lambda: [handler])

        # Act
        builder._cleanup_handlers()

        # Assert
        assert handler.cleaned_up is True


# --------------------------------------------------------------------------- #
# _copy file helper
# --------------------------------------------------------------------------- #


class TestCopy:
    """Tests for the _copy helper."""

    def test_dry_run_returns_preview_without_writing(self, tmp_path):
        # Arrange
        builder = ConcreteBuilder()
        source = tmp_path / "source.md"
        source.write_text("content", encoding="utf-8")
        destination = tmp_path / ".kilocode" / "out.md"

        # Act
        result = builder._copy(source, destination, dry_run=True)

        # Assert
        assert result.startswith("[dry-run]")
        assert "source.md" in result
        assert not destination.exists()

    def test_plain_copy_copies_file_contents(self, tmp_path):
        # Arrange
        builder = ConcreteBuilder()
        source = tmp_path / "plain.md"
        source.write_text("plain body", encoding="utf-8")
        destination = tmp_path / ".kilocode" / "nested" / "plain.md"

        # Act
        result = builder._copy(source, destination, dry_run=False)

        # Assert
        assert destination.read_text(encoding="utf-8") == "plain body"
        assert result.startswith("✓")

    def test_core_file_with_config_substitutes_template(self, tmp_path):
        # Arrange: a core- file triggers template substitution.
        builder = ConcreteBuilder()
        source = tmp_path / "core-conventions.md"
        source.write_text("name={{config.name}}", encoding="utf-8")
        destination = tmp_path / ".kilocode" / "core-conventions.md"
        config = {"spec": {"name": "Project"}}

        # Act
        result = builder._copy(source, destination, dry_run=False, config=config)

        # Assert
        assert destination.read_text(encoding="utf-8") == "name=Project"
        assert result.startswith("✓")

    def test_core_file_without_config_does_plain_copy(self, tmp_path):
        # Arrange: core- prefix but no config -> shutil copy, no substitution.
        builder = ConcreteBuilder()
        source = tmp_path / "core-system.md"
        source.write_text("raw {{config.name}}", encoding="utf-8")
        destination = tmp_path / ".kilocode" / "core-system.md"

        # Act
        builder._copy(source, destination, dry_run=False, config=None)

        # Assert
        assert destination.read_text(encoding="utf-8") == "raw {{config.name}}"

    def test_label_includes_kilocode_relative_path(self, tmp_path):
        # Arrange
        builder = ConcreteBuilder()
        source = tmp_path / "file.md"
        source.write_text("x", encoding="utf-8")
        destination = tmp_path / ".kilocode" / "rules" / "file.md"

        # Act
        result = builder._copy(source, destination, dry_run=True)

        # Assert
        assert ".kilocode/rules/file.md" in result
