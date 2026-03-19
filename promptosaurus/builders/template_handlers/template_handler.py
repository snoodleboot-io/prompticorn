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


class TemplateHandler(TemplateVariableHandler):
    """Base class for template variable handlers."""

    def can_handle(self, variable_name: str) -> bool:
        raise NotImplementedError("Subclasses must implement can_handle method")

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        raise NotImplementedError("Subclasses must implement handle method")
