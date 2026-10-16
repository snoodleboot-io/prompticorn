"""Template handler for PRIMARY_AGENTS_LIST variable."""

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

        Agents come from the content resolver, so the list names the agents this
        build actually resolved — including any supplied by a project layer. It
        used to try three filesystem paths in turn, the first two relative to the
        current working directory and the third the installed package, which
        meant the token was resolved from the bundled tree no matter which layers
        the rest of the build read from. (PRO-165, PRO-166)

        Args:
            variable_name: The name of the template variable
            config: The configuration dictionary

        Returns:
            Formatted markdown list of primary agents with descriptions
        """
        from prompticorn.agent_registry.registry import Registry

        registry = Registry.from_resolver()
        all_agents_dict = registry.get_all_agents()

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

        Personas are resolved rather than read from
        ``prompticorn/personas/personas.yaml`` on disk, so a project overriding
        that file gets an orchestrator whose agent list agrees with the agents
        the build emitted. (PRO-165)

        Returns:
            Set of enabled agent names, or None when no personas are selected or
            a selected persona does not exist (caller then falls back to
            mode-based selection).

        Raises:
            MalformedConfigurationError: If the persona data is present and
                unusable. Narrowed from a bare `except Exception` (PRO-165):
                an unknown persona name is tolerated here because
                ``PromptBuilder.build`` tolerates exactly the same thing and
                built every agent, so falling back to the mode-based list keeps
                the two in step. A malformed document is not tolerated in either
                place.
        """
        active_personas = (config or {}).get("active_personas")
        if not active_personas:
            return None

        from prompticorn.personas import PersonaFilter, PersonaRegistry

        try:
            from prompticorn.personas import PersonaFilter, PersonaRegistry
            from prompticorn.personas.registry import config_file_naming

            # Through the resolver, not Path(__file__) (PRO-166) — so a project
            # layer's personas.yaml is the one this list is computed from.
            # Deprecated aliases resolve inside PersonaFilter, and `source` lets
            # the warning name the config file they came from. (PRO-159)
            registry = PersonaRegistry.from_resolver()
            return PersonaFilter(
                registry,
                active_personas,
                source=config_file_naming(active_personas),
            ).get_enabled_agents()
        except KeyError:
            return None
