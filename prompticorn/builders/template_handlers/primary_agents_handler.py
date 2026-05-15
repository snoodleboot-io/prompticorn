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

        # Filter to primary agents only
        primary_agents = []
        for _agent_name, agent in all_agents_dict.items():
            # Include agents that have mode='primary'
            # Exclude subagents and special modes
            if hasattr(agent, "mode") and agent.mode == "primary":
                primary_agents.append(agent)
            # Also include agents without explicit mode if they're top-level
            elif not hasattr(agent, "mode") and not hasattr(agent, "parent_agent"):
                primary_agents.append(agent)

        # Sort alphabetically by name
        primary_agents.sort(key=lambda a: a.name)

        # Format as bulleted list with descriptions
        lines = []
        for agent in primary_agents:
            lines.append(f"- **{agent.name}**: {agent.description}")

        return "\n".join(lines) if lines else "*(No primary agents found)*"
