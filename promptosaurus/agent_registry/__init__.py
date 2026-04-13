"""Registry layer for managing discovered agents.

This module provides the registry system for auto-discovering agents from
the filesystem and managing them at runtime.

Components:
- RegistryDiscovery: Auto-discovers agents from filesystem
- Registry: Manages and retrieves discovered agents
- Exceptions: AgentNotFoundError, InvalidVariantError, RegistryLoadError
"""

from promptosaurus.agent_registry.discovery import RegistryDiscovery
from promptosaurus.agent_registry.errors import (
    AgentNotFoundError,
    InvalidVariantError,
    RegistryException,
    RegistryLoadError,
)
from promptosaurus.agent_registry.registry import Registry

__all__ = [
    "RegistryDiscovery",
    "Registry",
    "RegistryException",
    "AgentNotFoundError",
    "InvalidVariantError",
    "RegistryLoadError",
]
