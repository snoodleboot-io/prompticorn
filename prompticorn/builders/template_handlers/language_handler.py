"""Handler for LANGUAGE template variable."""

from typing import Any

from prompticorn.builders.template_handlers.template_handler import TemplateHandler


class LanguageHandler(TemplateHandler):
    """Handler for LANGUAGE template variable.

    This handler provides the programming language value from the configuration
    for use in template substitution. It's commonly used to customize templates
    based on the target language (e.g., 'python', 'javascript', 'java').

    Example:
        >>> handler = LanguageHandler()
        >>> handler.can_handle("LANGUAGE")
        True
        >>> handler.handle("LANGUAGE", {"language": "python"})
        'python'
        >>> handler.handle("LANGUAGE", {})
        ''
    """

    def can_handle(self, variable_name: str) -> bool:
        """Determine if this handler can process the LANGUAGE variable.

        Args:
            variable_name: The name of the template variable to check

        Returns:
            True if variable_name is 'LANGUAGE', False otherwise

        Example:
            >>> handler = LanguageHandler()
            >>> handler.can_handle("LANGUAGE")
            True
            >>> handler.can_handle("RUNTIME")
            False
        """
        return variable_name == "LANGUAGE"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        """Handle substitution of the LANGUAGE template variable.

        Extracts the 'language' value from the configuration dictionary and
        returns it as a string. If no language is configured, returns an
        empty string.

        Args:
            variable_name: The name of the template variable (should be 'LANGUAGE')
            config: Configuration dictionary containing language settings

        Returns:
            The language value as a string, or empty string if not configured

        Example:
            >>> handler = LanguageHandler()
            >>> handler.handle("LANGUAGE", {"language": "python"})
            'python'
            >>> handler.handle("LANGUAGE", {"language": "javascript"})
            'javascript'
            >>> handler.handle("LANGUAGE", {})
            ''
        """
        return str(config.get("language", ""))
