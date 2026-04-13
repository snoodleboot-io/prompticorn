"""Base Builder class for all output builders.

This module provides the Builder abstract base class that defines the interface
for all AI tool-specific output builders. Each builder transforms the prompt
registry into the specific format required by different AI assistant tools.

Classes:
    Builder: Abstract base class for output builders.
"""

import logging
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

import jinja2

from promptosaurus.builders.template_handlers.abstract_class_style_handler import (
    AbstractClassStyleHandler,
)
from promptosaurus.builders.template_handlers.coverage_handler import CoverageHandler
from promptosaurus.builders.template_handlers.coverage_tool_handler import CoverageToolHandler
from promptosaurus.builders.template_handlers.e2e_tool_handler import E2EToolHandler
from promptosaurus.builders.template_handlers.formatter_handler import FormatterHandler
from promptosaurus.builders.template_handlers.language_handler import LanguageHandler
from promptosaurus.builders.template_handlers.linter_handler import LinterHandler
from promptosaurus.builders.template_handlers.mocking_library_handler import MockingLibraryHandler
from promptosaurus.builders.template_handlers.mutation_tool_handler import MutationToolHandler
from promptosaurus.builders.template_handlers.package_manager_handler import PackageManagerHandler
from promptosaurus.builders.template_handlers.primary_agents_handler import PrimaryAgentsHandler
from promptosaurus.builders.template_handlers.resolvers.custom_filters import (
    register_custom_filters,
)
from promptosaurus.builders.template_handlers.resolvers.jinja2_template_renderer import (
    Jinja2TemplateRenderer,
)
from promptosaurus.builders.template_handlers.resolvers.registry_template_loader import (
    RegistryTemplateLoader,
)
from promptosaurus.builders.template_handlers.runtime_handler import RuntimeHandler
from promptosaurus.builders.template_handlers.template_handler import (
    TemplateHandler,
    TemplateVariableHandler,
)
from promptosaurus.builders.template_handlers.test_runner_handler import TestRunnerHandler
from promptosaurus.builders.template_handlers.testing_framework_handler import (
    TestingFrameworkHandler,
)
from promptosaurus.registry import registry

logger = logging.getLogger(__name__)


class TemplateHandlerRegistry:
    """Registry for template variable handlers."""

    def __init__(self):
        self._handlers: list[TemplateVariableHandler] = []

    def register_handler(self, handler: TemplateVariableHandler) -> None:
        """Register a template variable handler.

        Args:
            handler: The handler to register
        """
        self._handlers.append(handler)

    def unregister_handler(self, handler: TemplateVariableHandler) -> None:
        """Unregister a template variable handler.

        Args:
            handler: The handler to unregister
        """
        if handler in self._handlers:
            self._handlers.remove(handler)

    def get_handlers(self) -> list[TemplateVariableHandler]:
        """Get all registered handlers.

        Returns:
            List of registered template variable handlers
        """
        return self._handlers.copy()

    def get_handler_for_variable(self, variable_name: str) -> TemplateVariableHandler | None:
        """Get the first handler that can handle the given variable.

        Args:
            variable_name: The name of the template variable (without braces)

        Returns:
            The handler that can process the variable, or None if no handler can
        """
        for handler in self._handlers:
            if handler.can_handle(variable_name):
                return handler
        return None


class Builder:
    """Base class for all builders that generate output configs.

    This abstract class defines the interface that all tool-specific builders
    must implement. Subclasses should override the build() method to generate
    the appropriate output format for their target AI tool.

    Attributes:
        _base_files: List of core prompt files included in all builds.

    Methods:
        build: Generate output configuration files.
        _build_concatenated: Create concatenated rules file content.
        _substitute_template_variables: Replace {{config.variable}} templates with values from config.
        _copy: Copy a source file to destination with optional template substitution.
    """

    _base_files = [
        "agents/core/core-system.md",
        "agents/core/core-conventions.md",
        "agents/core/core-session.md",
    ]

    def __init__(self, template_handler_factory: Callable[[], list[TemplateHandler]] | None = None):
        """Initialize the builder with a template handler factory.

        Args:
            template_handler_factory: Optional factory that returns a list of TemplateHandler instances.
                                      If None, uses default factory with standard handlers.
        """
        self._template_handler_factory = (
            template_handler_factory or self._get_default_template_handler_factory()
        )
        self._template_handlers = self._template_handler_factory()
        self._template_handler_registry = self._get_default_template_handler_registry()

        # Protocol Extensions: Factory integration for template handlers
        self._initialize_handlers()

        # Initialize Jinja2 environment and renderer for advanced templating
        self._jinja2_environment = self._create_jinja2_environment()
        self._jinja2_renderer = Jinja2TemplateRenderer(self._jinja2_environment)

    def _create_jinja2_environment(self) -> jinja2.Environment:
        """Create and configure Jinja2 environment for template rendering.

        Returns:
            Configured Jinja2 Environment instance
        """
        # Create registry loader for template inheritance support
        loader = RegistryTemplateLoader()

        # Configure Jinja2 environment with sensible defaults for promptosaurus
        environment = jinja2.Environment(
            # Use registry loader for template inheritance support
            loader=loader,
            # Use {{variable}} syntax (same as existing templates)
            variable_start_string="{{",
            variable_end_string="}}",
            # Enable autoescape for safety (though most content is code/config)
            autoescape=False,  # We handle escaping in handlers if needed
            # Trim blocks for cleaner template syntax
            trim_blocks=True,
            lstrip_blocks=True,
            # Cache compiled templates for performance
            cache_size=400,
            # Use StrictUndefined to raise errors when accessing missing keys
            undefined=jinja2.StrictUndefined,
        )

        # Register custom filters for code generation and string transformations
        register_custom_filters(environment)

        # Register safe filters for error-tolerant template rendering
        from promptosaurus.builders.template_handlers.resolvers.safe_filters import (
            register_safe_filters,
        )

        register_safe_filters(environment)

        return environment

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """Build output configs.

        This method should be overridden by subclasses to generate tool-specific
        configuration files.

        Args:
            output: Directory to write output into.
            config: Optional configuration dict with template variables.
            dry_run: If True, preview what would be written without touching filesystem.

        Returns:
            List of messages describing what was done (or would have been done).
        """
        raise NotImplementedError

    def _build_concatenated_content(
        self, tool_comment: str, config: dict[str, Any] | None = None
    ) -> str:
        """Create concatenated rules file content.

        This method creates the content for a concatenated rules file by
        combining all the prompt files in the registry's concat_order.

        Args:
            tool_comment: Comment string to identify the tool (e.g., '# .clinerules').
            config: Optional configuration dict with template variables.

        Returns:
            Complete concatenated rules file content as a string.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines: list[str] = [
            tool_comment,
            "# Auto-generated by prompt CLI — edit files in prompts/ then rebuild",
            f"# Last built: {now}",
            "",
        ]

        for label, filename in registry.concat_order:
            try:
                body = registry.prompt_body(filename)
                # Apply template substitution if config is provided
                if config:
                    body = self._substitute_template_variables(body, config)
            except FileNotFoundError:
                lines.append(f"## {label} — MISSING: {filename}")
                lines.append("")
                continue

            lines.append("---")
            lines.append(f"## {label}")
            lines.append("")
            lines.append(body.rstrip())
            lines.append("")

        return "\n".join(lines) + "\n"

    def _build_concatenated(self, tool_comment: str, config: dict[str, Any] | None = None) -> str:
        """Alias for _build_concatenated_content for backward compatibility."""
        return self._build_concatenated_content(tool_comment, config)

    def _get_template_substitutions(self, defaults: dict[str, Any], format_value) -> dict[str, str]:
        """Get template variable substitutions.

        This method can be overridden by subclasses to add custom template
        variables beyond the default ones handled by registered handlers.

        Args:
            defaults: Default configuration values from spec
            format_value: Function to format values (unused in base implementation)

        Returns:
            Dictionary mapping template variables to their substituted values
        """
        # Base implementation returns empty dict - subclasses can add custom vars
        return {}

    def _substitute_template_variables(
        self, content: str, config: dict[str, Any] | None = None
    ) -> str:
        """Replace template variables using Jinja2 with handler-resolved context.

        Supports both {{config.variable}} syntax and legacy {{VARIABLE}} syntax
        by resolving variables through registered template handlers.
        """
        if config is None:
            config = {}
        if isinstance(config.get("spec"), list):
            spec_config = config["spec"][0] if config["spec"] else {}
        else:
            spec_config = config.get("spec", {})

        # Build context from registered handlers
        context: dict[str, Any] = {"config": spec_config}
        known_variables = [
            "LANGUAGE",
            "RUNTIME",
            "PACKAGE_MANAGER",
            "LINTER",
            "FORMATTER",
            "ABSTRACT_CLASS_STYLE",
            "TESTING_FRAMEWORK",
            "TEST_RUNNER",
            "E2E_TOOL",
            "MOCKING_LIBRARY",
            "COVERAGE_TOOL",
            "MUTATION_TOOL",
            "PRIMARY_AGENTS_LIST",
            "LINE_COVERAGE_%",
            "BRANCH_COVERAGE_%",
            "FUNCTION_COVERAGE_%",
            "STATEMENT_COVERAGE_%",
            "MUTATION_COVERAGE_%",
            "PATH_COVERAGE_%",
        ]
        for var_name in known_variables:
            handler = self._template_handler_registry.get_handler_for_variable(var_name)
            if handler:
                context[var_name] = handler.handle(var_name, spec_config)

        return self._jinja2_renderer.handle(content, context)

    def register_template_handler(self, handler: TemplateVariableHandler) -> None:
        """Register a custom template variable handler.

        Args:
            handler: The handler to register
        """
        self._template_handler_registry.register_handler(handler)

    def unregister_template_handler(self, handler: TemplateVariableHandler) -> None:
        """Unregister a template variable handler.

        Args:
            handler: The handler to unregister
        """
        self._template_handler_registry.unregister_handler(handler)

    def _get_default_template_handler_factory(self) -> Callable[[], list[TemplateHandler]]:
        """Get the default template handler factory.

        Returns:
            Callable that returns list of default TemplateHandler instances
        """
        return lambda: [
            LanguageHandler(),
            RuntimeHandler(),
            PackageManagerHandler(),
            LinterHandler(),
            FormatterHandler(),
            AbstractClassStyleHandler(),
            TestingFrameworkHandler(),
            TestRunnerHandler(),
            CoverageHandler(),
            E2EToolHandler(),
            MockingLibraryHandler(),
        ]

    def _get_default_template_handler_registry(self) -> TemplateHandlerRegistry:
        """Get the default template variable handler registry.

        Returns:
            TemplateHandlerRegistry with default template variable handlers
        """
        registry = TemplateHandlerRegistry()

        # Use basic fallback handlers
        fallback_handlers = [
            LanguageHandler(),
            RuntimeHandler(),
            PackageManagerHandler(),
            LinterHandler(),
            FormatterHandler(),
            AbstractClassStyleHandler(),
            TestingFrameworkHandler(),
            TestRunnerHandler(),
            CoverageHandler(),
            E2EToolHandler(),
            MockingLibraryHandler(),
            CoverageToolHandler(),
            MutationToolHandler(),
            PrimaryAgentsHandler(),
        ]
        for handler in fallback_handlers:
            registry.register_handler(handler)

        return registry

    def _initialize_handlers(self) -> None:
        """Initialize template handlers with factory integration.

        Calls inject_dependencies and initialize on all template handlers
        as part of the Protocol Extensions for Sprint 4.
        """
        # For now, inject empty dependencies dict - handlers can override to use it
        dependencies = {}

        for handler in self._template_handlers:
            handler.inject_dependencies(dependencies)
            handler.initialize()

        # Also initialize handlers in registry
        for handler in self._template_handler_registry.get_handlers():
            handler.inject_dependencies(dependencies)
            handler.initialize()

    def _configure_handlers(self, config: dict[str, Any] | None) -> list[str]:
        """Configure template handlers with config.

        Calls configure and validate_configuration on all template handlers.
        Returns list of validation error messages.

        Args:
            config: Configuration dict to pass to handlers

        Returns:
            List of validation error messages from all handlers
        """
        if config is None:
            config = {}

        validation_errors: list[str] = []

        for handler in self._template_handlers:
            handler.configure(config)
            errors = handler.validate_configuration(config)
            validation_errors.extend(errors)

        for handler in self._template_handler_registry.get_handlers():
            handler.configure(config)
            errors = handler.validate_configuration(config)
            validation_errors.extend(errors)

        return validation_errors

    def _cleanup_handlers(self) -> None:
        """Clean up template handlers.

        Calls cleanup on all template handlers to release resources.
        """
        for handler in self._template_handlers:
            handler.cleanup()

        for handler in self._template_handler_registry.get_handlers():
            handler.cleanup()

    def _copy(
        self,
        source_path: Path,
        destination: Path,
        dry_run: bool,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Copy a source file to destination with optional template substitution.

        Internal helper that handles file copying with support for
        template variable substitution in files that need it.

        Args:
            source_path: Source file path to copy from.
            destination: Destination file path to copy to.
            dry_run: If True, return preview string without copying.
            config: Optional config dict for template variable substitution.

        Returns:
            Action string describing the copy operation.
        """
        rel = str(destination).split(".kilocode/", 1)[-1]
        label = f".kilocode/{rel}"
        if dry_run:
            return f"[dry-run] {source_path.name} → {label}"
        destination.parent.mkdir(parents=True, exist_ok=True)

        # If config is provided and this is a language-specific conventions file,
        # perform template substitution
        if config and source_path.name.startswith("core-"):
            content = source_path.read_text(encoding="utf-8")
            content = self._substitute_template_variables(content, config)
            destination.write_text(content, encoding="utf-8")
        else:
            import shutil

            shutil.copy2(source_path, destination)

        return f"✓ {source_path.name} → {label}"
