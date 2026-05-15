"""Registry for managing discovered agents.

This module provides the Registry class for holding, caching, and retrieving
discovered agents by name and variant.
"""

from pathlib import Path

from prompticorn.agent_registry.discovery import RegistryDiscovery
from prompticorn.agent_registry.errors import AgentNotFoundError
from prompticorn.ir.models import Agent


class Registry:
    """Registry for managing discovered agents.

    Holds all discovered agents and provides methods to retrieve them by name
    and variant. Supports optional caching for performance.

    Example:
        >>> registry = Registry.from_discovery("./agents")
        >>> agent = registry.get_agent("code", variant="minimal")
        >>> all_agents = registry.get_all_agents()
        >>> agent_names = registry.list_agents()
    """

    def __init__(self, agents: dict[str, Agent], cache: bool = True) -> None:
        """Initialize registry with discovered agents.

        Args:
            agents: Dictionary of agents where keys are "agent_name" or
                   "agent_name/subagent_name" and values are Agent IR models.
            cache: Whether to cache agents in memory (default: True).
        """
        self._agents = agents
        self._cache_enabled = cache
        self._variant_cache: dict[str, dict[str, Agent]] = {}

        # Build variant index if cache is enabled
        if self._cache_enabled:
            self._build_variant_index()

    @classmethod
    def from_discovery(cls, agents_dir: Path | str, cache: bool = True) -> "Registry":
        """Create registry from filesystem discovery.

        Scans the agents directory for agents and subagents, then creates
        and returns a Registry instance.

        Args:
            agents_dir: Path to the agents directory to scan.
            cache: Whether to cache agents in memory (default: True).

        Returns:
            Registry instance with discovered agents.

        Example:
            >>> registry = Registry.from_discovery("./agents")
        """
        discovery = RegistryDiscovery(agents_dir)
        agents = discovery.discover()
        return cls(agents, cache=cache)

    def get_agent(self, name: str, variant: str = "minimal") -> Agent:
        """Get agent by name and variant.

        Retrieves an agent by its name and requested variant. Tries the
        requested variant first, then falls back to other available variants.

        Args:
            name: Agent name (e.g., "code", "architect") or full key
                 (e.g., "code/boilerplate").
            variant: Requested variant ("minimal" or "verbose"). Default: "minimal".

        Returns:
            Agent IR model.

        Raises:
            AgentNotFoundError: If agent not found.
            InvalidVariantError: If variant not available and no fallback.

        Example:
            >>> agent = registry.get_agent("code", variant="minimal")
            >>> subagent = registry.get_agent("code/boilerplate")
        """
        # Check if agent exists
        if name not in self._agents:
            raise AgentNotFoundError(name)

        agent = self._agents[name]

        # For now, we store the agent as-is. Variant selection happens during
        # discovery (minimal takes precedence if available).
        # This could be enhanced to support storing multiple variants.

        return agent

    def get_all_agents(self) -> dict[str, Agent]:
        """Get all agents.

        Returns:
            Dictionary of all agents (both top-level and subagents).

        Example:
            >>> all_agents = registry.get_all_agents()
            >>> for name, agent in all_agents.items():
            ...     print(f"{name}: {agent.description}")
        """
        return self._agents.copy()

    def list_agents(self, include_subagents: bool = False) -> list[str]:
        """List agent names.

        Returns:
            List of agent names. Includes subagents if requested.

        Args:
            include_subagents: Whether to include subagents in the list.
                              Default: False (only top-level agents).

        Example:
            >>> top_agents = registry.list_agents()
            >>> all_agents = registry.list_agents(include_subagents=True)
        """
        if include_subagents:
            return sorted(self._agents.keys())

        # Return only top-level agents (those without "/" in the name)
        return sorted([name for name in self._agents.keys() if "/" not in name])

    def list_subagents(self, agent_name: str) -> list[str]:
        """List subagents for a specific agent.

        Returns:
            List of subagent names for the given agent.

        Args:
            agent_name: Name of the parent agent.

        Example:
            >>> subagents = registry.list_subagents("code")
            >>> for subagent in subagents:
            ...     print(f"code/{subagent}")
        """
        prefix = f"{agent_name}/"
        return sorted(
            [name.replace(prefix, "") for name in self._agents.keys() if name.startswith(prefix)]
        )

    def has_agent(self, name: str) -> bool:
        """Check if agent exists in registry.

        Args:
            name: Agent name to check.

        Returns:
            True if agent exists, False otherwise.

        Example:
            >>> if registry.has_agent("code"):
            ...     agent = registry.get_agent("code")
        """
        return name in self._agents

    def has_subagent(self, agent_name: str, subagent_name: str) -> bool:
        """Check if subagent exists in registry.

        Args:
            agent_name: Name of parent agent.
            subagent_name: Name of subagent.

        Returns:
            True if subagent exists, False otherwise.

        Example:
            >>> if registry.has_subagent("code", "boilerplate"):
            ...     subagent = registry.get_agent("code/boilerplate")
        """
        key = f"{agent_name}/{subagent_name}"
        return key in self._agents

    def _build_variant_index(self) -> None:
        """Build variant index for caching.

        This is called during initialization if caching is enabled.
        It builds an index of agents by their base name for fast lookup.
        """
        # Index agents by base name
        for agent_key, agent in self._agents.items():
            base_name = agent_key.split("/")[0]  # Get "agent" from "agent/subagent"

            if base_name not in self._variant_cache:
                self._variant_cache[base_name] = {}

            self._variant_cache[base_name][agent_key] = agent
