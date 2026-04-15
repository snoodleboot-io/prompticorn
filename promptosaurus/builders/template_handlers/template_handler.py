"""Base class for template variable handlers."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class TemplateVariableHandler(Protocol):
    """Protocol for template variable handlers."""

    def can_handle(self, variable_name: str) -> bool:
        """Determine if this handler can process the given variable.

        Args:
            variable_name: The name of the template variable (without braces)

        Returns:
            True if this handler can process the variable, False otherwise
        """
        ...

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        """Handle the template variable substitution.

        Args:
            variable_name: The name of the template variable (without braces)
            config: The configuration dictionary

        Returns:
            The substituted value for the template variable
        """
        ...

    # Jinja2 Integration Methods
    def setup_jinja_environment(self, environment: Any) -> None:
        """Optional: Setup Jinja2 environment for advanced templating.

        Args:
            environment: The Jinja2 environment instance

        Default implementation does nothing.
        """
        pass

    def compile_template(self, template_str: str) -> Any:
        """Optional: Compile a Jinja2 template.

        Args:
            template_str: The template string to compile

        Returns:
            Compiled template object

        Default returns None.
        """
        return None

    def get_cached_template(self, template_str: str) -> Any:
        """Optional: Get cached compiled template.

        Args:
            template_str: The template string

        Returns:
            Cached template object or None

        Default returns None.
        """
        return None

    def resolve_variable(self, name: str, context: dict[str, Any]) -> Any:
        """Optional: Resolve variable in Jinja2 context.

        Args:
            name: Variable name
            context: Template context dictionary

        Returns:
            Resolved variable value

        Default returns None.
        """
        return None

    def get_filters(self) -> dict[str, Any]:
        """Optional: Get custom Jinja2 filters.

        Returns:
            Dictionary of filter name to function

        Default returns empty dict.
        """
        return {}

    def get_functions(self) -> dict[str, Any]:
        """Optional: Get custom Jinja2 functions.

        Returns:
            Dictionary of function name to function

        Default returns empty dict.
        """
        return {}

    def handle_macro(self, macro_name: str, args: list[Any], kwargs: dict[str, Any]) -> Any:
        """Optional: Handle Jinja2 macro calls.

        Args:
            macro_name: Name of the macro
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Macro result

        Default returns None.
        """
        return None

    # Validation Methods
    def validate_template(self, template_str: str) -> list[str]:
        """Optional: Validate template syntax.

        Args:
            template_str: Template string to validate

        Returns:
            List of validation error messages

        Default returns empty list.
        """
        return []

    # Error Integration Methods
    def handle_error(self, error: Exception, context: dict[str, Any]) -> None:
        """Optional: Handle template processing errors.

        Args:
            error: The exception that occurred
            context: Error context information

        Default implementation does nothing.
        """
        pass

    def create_error_context(self, error: Exception, template_str: str | None) -> dict[str, Any]:
        """Optional: Create error context for debugging.

        Args:
            error: The exception
            template_str: Template being processed (may be None)

        Returns:
            Error context dictionary

        Default returns basic context.
        """
        return {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "template_length": len(template_str) if template_str else 0,
        }

    def serialize_error_context(self, context: dict[str, Any]) -> str:
        """Optional: Serialize error context for logging.

        Args:
            context: Error context dictionary

        Returns:
            Serialized context string

        Default uses JSON with circular reference handling.
        """
        import json

        try:
            return json.dumps(context, default=str)
        except ValueError:
            # Handle circular references by creating a safe copy
            def make_serializable(obj: Any) -> Any:
                if isinstance(obj, dict):
                    return {k: make_serializable(v) for k, v in obj.items() if k != obj}
                elif isinstance(obj, list | tuple):
                    return [make_serializable(item) for item in obj]
                else:
                    return str(obj)

            safe_context = make_serializable(context)
            return json.dumps(safe_context, default=str)

    def share_error_context(
        self, context: dict[str, Any], target_handlers: list["TemplateVariableHandler"]
    ) -> None:
        """Optional: Share error context with other handlers.

        Args:
            context: Error context
            target_handlers: List of handlers to share with

        Default does nothing.
        """
        pass

    def get_recovery_strategy(self, error: Exception) -> str:
        """Optional: Get recovery strategy for error.

        Args:
            error: The exception

        Returns:
            Recovery strategy name

        Default returns 'none'.
        """
        return "none"

    def attempt_recovery(self, error: Exception, context: dict[str, Any]) -> Any:
        """Optional: Attempt error recovery.

        Args:
            error: The exception
            context: Recovery context

        Returns:
            Recovered result or raises error

        Default re-raises the error.
        """
        raise error

    def get_fallback_value(self, variable_name: str, error: Exception) -> str:
        """Optional: Get fallback value for failed variable.

        Args:
            variable_name: Variable that failed
            error: The exception

        Returns:
            Fallback string value

        Default returns empty string.
        """
        return ""

    # Factory Integration Methods
    def inject_dependencies(self, dependencies: dict[str, Any]) -> None:
        """Optional: Inject dependencies from factory.

        Args:
            dependencies: Dictionary of dependency name to instance

        Default does nothing.
        """
        pass

    def initialize(self) -> None:
        """Optional: Initialize the handler.

        Called after dependency injection.

        Default does nothing.
        """
        pass

    def cleanup(self) -> None:
        """Optional: Cleanup resources.

        Called when handler is no longer needed.

        Default does nothing.
        """
        pass

    def configure(self, config: dict[str, Any]) -> None:
        """Optional: Configure the handler.

        Args:
            config: Configuration dictionary

        Default does nothing.
        """
        pass

    def validate_configuration(self, config: dict[str, Any]) -> list[str]:
        """Optional: Validate configuration.

        Args:
            config: Configuration to validate

        Returns:
            List of validation error messages

        Default returns empty list.
        """
        return []


class TemplateHandler(TemplateVariableHandler):
    """Base class for template variable handlers."""

    def can_handle(self, variable_name: str) -> bool:
        raise NotImplementedError("Subclasses must implement can_handle method")

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        raise NotImplementedError("Subclasses must implement handle method")

    # Default implementations for extended protocol methods
    # (inherited from protocol, but can be overridden)
