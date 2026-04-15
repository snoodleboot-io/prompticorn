"""Factory pattern for creating and managing builder instances.

This module provides the BuilderFactory class, which implements the factory
pattern for builder creation and retrieval. It maintains a registry of
available builders and provides a clean API for getting builder instances.
"""

from typing import Any

from promptosaurus.builders.base import Builder
from promptosaurus.builders.errors import BuilderNotFoundError


class BuilderFactory:
    """Factory for creating and retrieving builder instances.

    The factory maintains a registry of builder classes indexed by tool name.
    Builders are instantiated on-demand when requested.

    Example:
        # Register a custom builder
        BuilderFactory.register('kilo', KiloBuilder)

        # Get a builder instance
        builder = BuilderFactory.get_builder('kilo')

        # List available builders
        tools = BuilderFactory.list_builders()
    """

    _builders: dict[str, type[Builder]] = {}

    @classmethod
    def register(cls, tool_name: str, builder_class: type[Builder]) -> None:
        """Register a builder class for a tool.

        Args:
            tool_name: The name of the tool (e.g., 'kilo', 'claude', 'cline')
            builder_class: The builder class to register. Must be a subclass of Builder.

        Raises:
            TypeError: If builder_class is not a subclass of Builder
            ValueError: If tool_name is empty
        """
        if not tool_name or not tool_name.strip():
            raise ValueError("tool_name cannot be empty")

        if not issubclass(builder_class, Builder):
            raise TypeError(
                f"builder_class must be a subclass of Builder, got {builder_class.__name__}"
            )

        tool_key = tool_name.lower().strip()
        cls._builders[tool_key] = builder_class

    @classmethod
    def get_builder(cls, tool_name: str) -> Builder:
        """Get a builder instance for the specified tool.

        Args:
            tool_name: The name of the tool (e.g., 'kilo', 'claude', 'cline')

        Returns:
            An instance of the registered builder for the tool

        Raises:
            BuilderNotFoundError: If no builder is registered for the tool
        """
        if not tool_name or not tool_name.strip():
            raise ValueError("tool_name cannot be empty")

        tool_key = tool_name.lower().strip()

        if tool_key not in cls._builders:
            raise BuilderNotFoundError(tool_name)

        builder_class = cls._builders[tool_key]
        return builder_class()

    @classmethod
    def list_builders(cls) -> list[str]:
        """List all registered tool names.

        Returns:
            List of registered tool names, sorted alphabetically
        """
        return sorted(cls._builders.keys())

    @classmethod
    def has_builder(cls, tool_name: str) -> bool:
        """Check if a builder is registered for a tool.

        Args:
            tool_name: The tool name to check

        Returns:
            True if a builder is registered, False otherwise
        """
        if not tool_name or not tool_name.strip():
            return False
        return tool_name.lower().strip() in cls._builders

    @classmethod
    def clear(cls) -> None:
        """Clear all registered builders.

        This method is primarily useful for testing. In production,
        it should rarely be called.
        """
        cls._builders.clear()

    @classmethod
    def get_builder_info(cls, tool_name: str) -> dict[str, Any]:
        """Get metadata about a registered builder.

        Args:
            tool_name: The tool name to get info for

        Returns:
            Dictionary containing builder metadata:
              - tool_name: The tool name
              - class_name: The builder class name
              - output_format: The output format (requires instantiation)

        Raises:
            BuilderNotFoundError: If no builder is registered for the tool
        """
        if not cls.has_builder(tool_name):
            raise BuilderNotFoundError(tool_name)

        builder = cls.get_builder(tool_name)
        return {
            "tool_name": tool_name.lower(),
            "class_name": builder.__class__.__name__,
            "output_format": builder.get_output_format(),
        }
