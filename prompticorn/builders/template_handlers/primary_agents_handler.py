"""Template handler for PRIMARY_AGENTS_LIST variable."""

from pathlib import Path
from typing import Any

from prompticorn.builders.template_handlers.template_handler import TemplateHandler


class PrimaryAgentsHandler(TemplateHandler):
    """Handles {{PRIMARY_AGENTS_LIST}} template variable.

    Discovers all primary agents and formats them as a bulleted list
    for inclusion in orchestrator instructions.
    """

    def can_handle(self, variable_name: str) -> bool:
        """Check if this handler can process the variable.

        Args:
            variable_name: The name of the template variable (without braces)

        Returns:
            True if variable is PRIMARY_AGENTS_LIST
        """
        return variable_name == "PRIMARY_AGENTS_LIST"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        """Generate formatted list of all primary agents.

        Args:
            variable_name: The name of the template variable
            config: The configuration dictionary (unused)

        Returns:
            Formatted markdown list of primary agents with descriptions
        """
        from prompticorn.agent_registry.registry import Registry

        # Try multiple possible paths for agents directory
        possible_paths = [
            Path("agents"),  # Relative from CWD
            Path("prompticorn/agents"),  # Relative from project root
            Path(__file__).parent.parent.parent / "agents",  # Relative from this file
        ]

        registry = None
        for agents_dir in possible_paths:
            if agents_dir.exists() and agents_dir.is_dir():
                try:
                    registry = Registry.from_discovery(agents_dir)
                    break
                except Exception:
                    continue

        if registry is None:
            return "*(No agents discovered - agents directory not found)*"

        # Get all agents
        try:
            all_agents_dict = registry.get_all_agents()
        except Exception:
            return "*(No agents discovered - registry error)*"

        # Top-level agents only (keys without "/").
        top_level = [
            agent for agent_name, agent in all_agents_dict.items() if "/" not in agent_name
        ]

        enabled = self._enabled_agent_names(config)
        if enabled is not None:
            # Match the agents actually generated for the active personas, so the
            # orchestrator never references an agent whose file wasn't built.
            primary_agents = [agent for agent in top_level if agent.name in enabled]
        else:
            # No persona filtering: list agents declared as primary.
            primary_agents = [
                agent for agent in top_level if getattr(agent, "mode", None) == "primary"
            ]

        # Sort alphabetically by name
        primary_agents.sort(key=lambda a: a.name)

        # Format as bulleted list with descriptions
        lines = []
        for agent in primary_agents:
            lines.append(f"- **{agent.name}**: {agent.description}")

        return "\n".join(lines) if lines else "*(No primary agents found)*"

    @staticmethod
    def _enabled_agent_names(config: dict[str, Any]) -> set[str] | None:
        """Resolve the set of agent names enabled by the config's active personas.

        Returns:
            Set of enabled agent names, or None when no personas are selected or
            persona data cannot be loaded (caller then falls back to mode-based
            selection).
        """
        active_personas = (config or {}).get("active_personas")
        if not active_personas:
            return None

        try:
            from pathlib import Path

            from prompticorn.personas import PersonaFilter, PersonaRegistry

            personas_yaml = Path(__file__).parent.parent.parent / "personas" / "personas.yaml"
            persona_registry = PersonaRegistry.from_yaml(personas_yaml)
            return PersonaFilter(persona_registry, active_personas).get_enabled_agents()
        except Exception:
            return None
