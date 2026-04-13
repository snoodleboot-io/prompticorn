"""Handler for PACKAGE_MANAGER template variable."""

from typing import Any

from promptosaurus.builders.template_handlers.template_handler import TemplateHandler


class PackageManagerHandler(TemplateHandler):
    """Handler for PACKAGE_MANAGER template variable.
    
    This handler provides the package manager value from the configuration
    for use in template substitution. It's used to customize prompts based on
    the project's dependency management tool (e.g., 'uv', 'npm', 'cargo').
    
    Example:
        >>> handler = PackageManagerHandler()
        >>> handler.can_handle("PACKAGE_MANAGER")
        True
        >>> handler.handle("PACKAGE_MANAGER", {"package_manager": "uv"})
        'uv'
        >>> handler.handle("PACKAGE_MANAGER", {})
        ''
    """

    def can_handle(self, variable_name: str) -> bool:
        """Determine if this handler can process the PACKAGE_MANAGER variable.
        
        Args:
            variable_name: The name of the template variable to check
            
        Returns:
            True if variable_name is 'PACKAGE_MANAGER', False otherwise
            
        Example:
            >>> handler = PackageManagerHandler()
            >>> handler.can_handle("PACKAGE_MANAGER")
            True
            >>> handler.can_handle("LANGUAGE")
            False
        """
        return variable_name == "PACKAGE_MANAGER"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        """Handle substitution of the PACKAGE_MANAGER template variable.
        
        Extracts the 'package_manager' value from the configuration dictionary
        and returns it as a string. If no package manager is configured, returns
        an empty string.
        
        Args:
            variable_name: The name of the template variable (should be 'PACKAGE_MANAGER')
            config: Configuration dictionary containing package manager settings
            
        Returns:
            The package manager value as a string, or empty string if not configured
            
        Example:
            >>> handler = PackageManagerHandler()
            >>> handler.handle("PACKAGE_MANAGER", {"package_manager": "uv"})
            'uv'
            >>> handler.handle("PACKAGE_MANAGER", {"package_manager": "npm"})
            'npm'
            >>> handler.handle("PACKAGE_MANAGER", {})
            ''
        """
        return str(config.get("package_manager", ""))
