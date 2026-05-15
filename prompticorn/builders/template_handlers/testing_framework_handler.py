"""Handler for TESTING_FRAMEWORK template variable."""

from typing import Any

from prompticorn.builders.template_handlers.template_handler import TemplateHandler


class TestingFrameworkHandler(TemplateHandler):
    """Handler for TESTING_FRAMEWORK template variable.

    This handler provides the testing framework value from the configuration
    for use in template substitution. It's used to customize prompts based on
    the project's test framework (e.g., 'pytest', 'vitest', 'go test').

    Example:
        >>> handler = TestingFrameworkHandler()
        >>> handler.can_handle("TESTING_FRAMEWORK")
        True
        >>> handler.handle("TESTING_FRAMEWORK", {"testing_framework": "pytest"})
        'pytest'
        >>> handler.handle("TESTING_FRAMEWORK", {})
        ''
    """

    def can_handle(self, variable_name: str) -> bool:
        """Determine if this handler can process the TESTING_FRAMEWORK variable.

        Args:
            variable_name: The name of the template variable to check

        Returns:
            True if variable_name is 'TESTING_FRAMEWORK', False otherwise

        Example:
            >>> handler = TestingFrameworkHandler()
            >>> handler.can_handle("TESTING_FRAMEWORK")
            True
            >>> handler.can_handle("LANGUAGE")
            False
        """
        return variable_name == "TESTING_FRAMEWORK"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        """Handle substitution of the TESTING_FRAMEWORK template variable.

        Extracts the 'testing_framework' value from the configuration dictionary
        and returns it as a string. If no testing framework is configured, returns
        an empty string.

        Args:
            variable_name: The name of the template variable (should be 'TESTING_FRAMEWORK')
            config: Configuration dictionary containing testing framework settings

        Returns:
            The testing framework value as a string, or empty string if not configured

        Example:
            >>> handler = TestingFrameworkHandler()
            >>> handler.handle("TESTING_FRAMEWORK", {"testing_framework": "pytest"})
            'pytest'
            >>> handler.handle("TESTING_FRAMEWORK", {"testing_framework": "vitest"})
            'vitest'
            >>> handler.handle("TESTING_FRAMEWORK", {})
            ''
        """
        value = config.get("testing_framework", "")
        if value is None:
            return "None"
        return str(value)
