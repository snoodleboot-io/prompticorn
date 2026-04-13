"""Registry for managing builder instances.

This module provides the BuilderRegistry class, which manages builder
instances separately from the factory. It can be useful when you want
to maintain singleton builder instances or apply custom configuration.

The registry stores actual builder instances rather than classes,
making it suitable for stateful builders or builders with
initialization parameters.
"""

from promptosaurus.builders.base import AbstractBuilder
from promptosaurus.builders.errors import BuilderNotFoundError


class BuilderRegistry:
    """Registry for managing builder instances.

    The registry maintains a collection of builder instances indexed by tool name.
    Unlike the factory (which creates instances on demand), the registry stores
    pre-instantiated builders.

    This is useful for:
    - Maintaining singleton builder instances
    - Applying custom configuration to builders
    - Caching expensive builder initialization
    - Managing builder lifecycle

    Example:
        # Create registry and register builders
        registry = BuilderRegistry()
        registry.register('kilo', kilo_builder_instance)
        registry.register('claude', claude_builder_instance)

        # Retrieve builders
        builder = registry.get('kilo')

        # List available tools
        tools = registry.list_tools()
    """

    def __init__(self) -> None:
        """Initialize an empty builder registry."""
        self._builders: dict[str, AbstractBuilder] = {}

    def register(self, tool_name: str, builder: AbstractBuilder) -> None:
        """Register a builder instance for a tool.

        Args:
            tool_name: The name of the tool (e.g., 'kilo', 'claude', 'cline')
            builder: The builder instance to register. Must be an instance of AbstractBuilder.

        Raises:
            TypeError: If builder is not an instance of AbstractBuilder
            ValueError: If tool_name is empty
        """
        if not tool_name or not tool_name.strip():
            raise ValueError("tool_name cannot be empty")

        if not isinstance(builder, AbstractBuilder):
            raise TypeError(
                f"builder must be an instance of AbstractBuilder, got {type(builder).__name__}"
            )

        tool_key = tool_name.lower().strip()
        self._builders[tool_key] = builder

    def get(self, tool_name: str) -> AbstractBuilder:
        """Get a builder instance for the specified tool.

        Args:
            tool_name: The name of the tool (e.g., 'kilo', 'claude', 'cline')

        Returns:
            The registered builder instance for the tool

        Raises:
            BuilderNotFoundError: If no builder is registered for the tool
            ValueError: If tool_name is empty
        """
        if not tool_name or not tool_name.strip():
            raise ValueError("tool_name cannot be empty")

        tool_key = tool_name.lower().strip()

        if tool_key not in self._builders:
            raise BuilderNotFoundError(tool_name)

        return self._builders[tool_key]

    def list_tools(self) -> list[str]:
        """List all registered tool names.

        Returns:
            List of registered tool names, sorted alphabetically
        """
        return sorted(self._builders.keys())

    def has_tool(self, tool_name: str) -> bool:
        """Check if a builder is registered for a tool.

        Args:
            tool_name: The tool name to check

        Returns:
            True if a builder is registered, False otherwise
        """
        if not tool_name or not tool_name.strip():
            return False
        return tool_name.lower().strip() in self._builders

    def unregister(self, tool_name: str) -> bool:
        """Unregister a builder from the registry.

        Args:
            tool_name: The tool name to unregister

        Returns:
            True if a builder was removed, False if not registered
        """
        if not tool_name or not tool_name.strip():
            return False

        tool_key = tool_name.lower().strip()
        if tool_key in self._builders:
            del self._builders[tool_key]
            return True
        return False

    def clear(self) -> None:
        """Clear all registered builders from the registry.

        This method removes all builders. Useful for testing or
        reinitializing the registry.
        """
        self._builders.clear()

    def get_all(self) -> dict[str, AbstractBuilder]:
        """Get all registered builders.

        Returns:
            Dictionary mapping tool names to builder instances
        """
        return dict(self._builders)

    def count(self) -> int:
        """Get the number of registered builders.

        Returns:
            The count of registered builders
        """
        return len(self._builders)
