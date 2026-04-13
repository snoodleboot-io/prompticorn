"""Custom exceptions for the registry layer.

This module defines custom exceptions for agent discovery, registration,
and retrieval operations.
"""


class RegistryException(Exception):
    """Base exception for all registry errors."""

    pass


class AgentNotFoundError(RegistryException):
    """Raised when an agent cannot be found by name."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Agent not found: {name}")


class InvalidVariantError(RegistryException):
    """Raised when an invalid variant is requested for an agent."""

    def __init__(self, agent_name: str, variant: str, available: list[str]) -> None:
        self.agent_name = agent_name
        self.variant = variant
        self.available = available
        available_str = ", ".join(available) if available else "none"
        super().__init__(
            f"Invalid variant '{variant}' for agent '{agent_name}'. "
            f"Available variants: {available_str}"
        )


class RegistryLoadError(RegistryException):
    """Raised when registry discovery or loading fails."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
