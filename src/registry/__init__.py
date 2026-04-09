"""Registry layer for managing discovered agents.

This module provides the registry system for auto-discovering agents from
the filesystem and managing them at runtime.

Components:
- RegistryDiscovery: Auto-discovers agents from filesystem
- Registry: Manages and retrieves discovered agents
- Exceptions: AgentNotFoundError, InvalidVariantError, RegistryLoadError
"""

from src.registry.discovery import RegistryDiscovery
from src.registry.registry import Registry
from src.registry.errors import (
    RegistryException,
    AgentNotFoundError,
    InvalidVariantError,
    RegistryLoadError,
)

__all__ = [
    "RegistryDiscovery",
    "Registry",
    "RegistryException",
    "AgentNotFoundError",
    "InvalidVariantError",
    "RegistryLoadError",
]
