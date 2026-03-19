"""Base Builder class for all output builders.

This module provides the Builder abstract base class that defines the interface
for all AI tool-specific output builders. Each builder transforms the prompt
registry into the specific format required by different AI assistant tools.

Classes:
    Builder: Abstract base class for output builders.
"""

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from promptosaurus.builders.template_handlers.abstract_class_style_handler import (
    AbstractClassStyleHandler,
)
from promptosaurus.builders.template_handlers.coverage_handler import CoverageHandler
from promptosaurus.builders.template_handlers.formatter_handler import FormatterHandler
from promptosaurus.builders.template_handlers.language_handler import LanguageHandler
from promptosaurus.builders.template_handlers.linter_handler import LinterHandler
from promptosaurus.builders.template_handlers.package_manager_handler import PackageManagerHandler
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
        _substitute_template_variables: Replace {{VARIABLE}} templates with values from config.
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

    def _substitute_template_variables(
        self, content: str, config: dict[str, Any] | None = None
    ) -> str:
        """Replace {{VARIABLE}} templates with values from config.

        This method performs template variable substitution on content,
        replacing placeholders like {{LANGUAGE}} with actual values
        from the configuration. It uses registered template variable handlers
        to determine how to substitute each variable.

        Args:
            content: The template content with {{VARIABLE}} placeholders.
            config: Optional configuration dict containing spec values.

        Returns:
            Content with all template variables replaced.
        """
        if config is None:
            config = {}

        # Handle both single-language (dict) and multi-language (list) configs
        if isinstance(config.get("spec"), list):
            # Multi-language monorepo: get config from first folder
            spec = config.get("spec", [{}])
            config = spec[0] if spec and len(spec) > 0 else {}
        else:
            config = config.get("spec", {})

        # Import regex here to avoid top-level import if not used
        import re

        # Find all template variables in the content
        template_pattern = r"\{\{([A-Z_][A-Z0-9_]*)\}\}"
        matches = re.findall(template_pattern, content)

        # Process each unique template variable
        substitutions = {}
        for var_name in set(matches):
            template_var = f"{{{{{var_name}}}}}"
            if config is not None:
                value = self._get_variable_value(var_name, config)
                if value is not None:  # Only substitute if we have a value
                    substitutions[template_var] = value

        # Perform substitutions
        for template_var, value in substitutions.items():
            content = content.replace(template_var, value)

        return content

    def _get_variable_value(self, variable_name: str, config: dict[str, Any]) -> str | None:
        """Get the value for a template variable by consulting registered handlers.

        Args:
            variable_name: The name of the template variable (without braces)
            config: The configuration dictionary

        Returns:
            The substituted value, or None if no handler can process the variable
        """
        handler = self._template_handler_registry.get_handler_for_variable(variable_name)
        if handler:
            return handler.handle(variable_name, config)
        return None

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
        ]
        for handler in fallback_handlers:
            registry.register_handler(handler)

        return registry

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
