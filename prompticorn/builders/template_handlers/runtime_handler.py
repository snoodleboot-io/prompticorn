"""Handler for RUNTIME template variable."""

from typing import Any

from prompticorn.builders.template_handlers.template_handler import TemplateHandler


class RuntimeHandler(TemplateHandler):
    """Handler for RUNTIME template variable.

    This handler provides the runtime environment value from the configuration
    for use in template substitution. It's commonly used to customize templates
    based on the target runtime (e.g., '3.11', 'node18', 'java11').

    Example:
        >>> handler = RuntimeHandler()
        >>> handler.can_handle("RUNTIME")
        True
        >>> handler.handle("RUNTIME", {"runtime": "3.11"})
        '3.11'
        >>> handler.handle("RUNTIME", {})
        ''
    """

    def can_handle(self, variable_name: str) -> bool:
        """Determine if this handler can process the RUNTIME variable.

        Args:
            variable_name: The name of the template variable to check

        Returns:
            True if variable_name is 'RUNTIME', False otherwise

        Example:
            >>> handler = RuntimeHandler()
            >>> handler.can_handle("RUNTIME")
            True
            >>> handler.can_handle("LANGUAGE")
            False
        """
        return variable_name == "RUNTIME"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        """Handle substitution of the RUNTIME template variable.

        Extracts the 'runtime' value from the configuration dictionary and
        returns it as a string. If no runtime is configured, returns an
        empty string.

        Args:
            variable_name: The name of the template variable (should be 'RUNTIME')
            config: Configuration dictionary containing runtime settings

        Returns:
            The runtime value as a string, or empty string if not configured

        Example:
            >>> handler = RuntimeHandler()
            >>> handler.handle("RUNTIME", {"runtime": "3.11"})
            '3.11'
            >>> handler.handle("RUNTIME", {"runtime": "node18"})
            'node18'
            >>> handler.handle("RUNTIME", {})
            ''
        """
        return str(config.get("runtime", ""))
