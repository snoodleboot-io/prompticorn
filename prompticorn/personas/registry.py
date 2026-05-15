"""Persona registry and filtering for role-based agent selection.

This module provides the PersonaRegistry and PersonaFilter classes for managing
persona-based filtering of agents, workflows, and skills.

Reference: planning/current/adrs/ADR-001-persona-based-filtering.md
"""

from pathlib import Path

import yaml


class PersonaRegistry:
    """Registry for managing persona definitions and mappings.

    Loads persona definitions from personas.yaml and provides methods to query
    persona information, agent mappings, workflow mappings, and skill mappings.

    Example:
        >>> registry = PersonaRegistry.from_yaml("prompticorn/personas/personas.yaml")
        >>> personas = registry.list_personas()
        >>> agents = registry.get_agents_for_persona("software_engineer")
    """

    def __init__(self, personas_data: dict) -> None:
        """Initialize registry with persona data.

        Args:
            personas_data: Dictionary loaded from personas.yaml containing
                          persona definitions and universal agents.
        """
        self._raw_data = personas_data
        self._personas = personas_data.get("personas", {})
        self._universal_agents = personas_data.get("universal_agents", [])
        self._version = personas_data.get("version", "unknown")

    @classmethod
    def from_yaml(cls, yaml_path: Path | str) -> "PersonaRegistry":
        """Create registry from personas.yaml file.

        Args:
            yaml_path: Path to personas.yaml file.

        Returns:
            PersonaRegistry instance.

        Raises:
            FileNotFoundError: If yaml file doesn't exist.
            yaml.YAMLError: If yaml is malformed.
        """
        yaml_path = Path(yaml_path)
        if not yaml_path.exists():
            msg = f"Personas file not found: {yaml_path}"
            raise FileNotFoundError(msg)

        with yaml_path.open("r") as f:
            personas_data = yaml.safe_load(f)

        return cls(personas_data)

    def list_personas(self) -> list[str]:
        """Get list of all persona identifiers.

        Returns:
            List of persona keys (e.g., ['software_engineer', 'architect', ...])
        """
        return list(self._personas.keys())

    def get_persona_info(self, persona_name: str) -> dict:
        """Get full persona definition.

        Args:
            persona_name: Persona identifier (e.g., 'software_engineer').

        Returns:
            Dictionary with persona definition including display_name, description,
            focus, primary_agents, secondary_agents, workflows, skills.

        Raises:
            KeyError: If persona doesn't exist.
        """
        if persona_name not in self._personas:
            msg = f"Persona '{persona_name}' not found. Available: {self.list_personas()}"
            raise KeyError(msg)

        return self._personas[persona_name]

    def get_agents_for_persona(self, persona_name: str) -> list[str]:
        """Get all agents (primary + secondary) for a persona.

        Args:
            persona_name: Persona identifier.

        Returns:
            List of agent names for this persona.
        """
        persona = self.get_persona_info(persona_name)
        primary = persona.get("primary_agents", [])
        secondary = persona.get("secondary_agents", [])
        return primary + secondary

    def get_workflows_for_persona(self, persona_name: str) -> list[str]:
        """Get workflows mapped to a persona.

        Args:
            persona_name: Persona identifier.

        Returns:
            List of workflow names.
        """
        persona = self.get_persona_info(persona_name)
        return persona.get("workflows", [])

    def get_skills_for_persona(self, persona_name: str) -> list[str]:
        """Get skills mapped to a persona.

        Args:
            persona_name: Persona identifier.

        Returns:
            List of skill names.
        """
        persona = self.get_persona_info(persona_name)
        return persona.get("skills", [])

    def get_universal_agents(self) -> list[str]:
        """Get list of universal agents (always enabled).

        Returns:
            List of universal agent names.
        """
        return self._universal_agents

    def get_display_name(self, persona_name: str) -> str:
        """Get user-friendly display name for persona.

        Args:
            persona_name: Persona identifier.

        Returns:
            Display name (e.g., 'Software Engineer').
        """
        persona = self.get_persona_info(persona_name)
        return persona.get("display_name", persona_name)

    def get_description(self, persona_name: str) -> str:
        """Get persona description.

        Args:
            persona_name: Persona identifier.

        Returns:
            Persona description string.
        """
        persona = self.get_persona_info(persona_name)
        return persona.get("description", "")


class PersonaFilter:
    """Filters agents, workflows, and skills based on selected personas.

    Implements the dynamic agent enabling/disabling mechanism described in ADR-001.
    Agents are enabled if present in ANY selected persona, disabled otherwise.

    Example:
        >>> registry = PersonaRegistry.from_yaml("personas.yaml")
        >>> filter = PersonaFilter(registry, ["software_engineer", "qa_tester"])
        >>> enabled_agents = filter.get_enabled_agents()
        >>> enabled_workflows = filter.get_enabled_workflows()
    """

    def __init__(self, registry: PersonaRegistry, selected_personas: list[str]) -> None:
        """Initialize filter with registry and selected personas.

        Args:
            registry: PersonaRegistry instance.
            selected_personas: List of persona identifiers to enable.

        Raises:
            KeyError: If any selected persona doesn't exist.
        """
        self._registry = registry
        self._selected_personas = selected_personas

        # Validate personas exist
        available = registry.list_personas()
        for persona in selected_personas:
            if persona not in available:
                msg = f"Invalid persona: '{persona}'. Available: {available}"
                raise KeyError(msg)

    def get_enabled_agents(self) -> set[str]:
        """Get all agents that should be enabled for selected personas.

        Implements the dynamic enabling/disabling algorithm from ADR-001:
        - Collect agents from all selected personas
        - Enable if present in ANY selected persona
        - Always include universal agents

        Returns:
            Set of agent names to enable.

        Example:
            >>> filter = PersonaFilter(registry, ["qa_tester"])
            >>> enabled = filter.get_enabled_agents()
            >>> "code" in enabled  # False - QA/Tester doesn't have code
            >>> "test" in enabled  # True - QA/Tester has test
            >>> "ask" in enabled   # True - ask is universal
        """
        enabled_agents: set[str] = set()

        # Add universal agents (always enabled)
        enabled_agents.update(self._registry.get_universal_agents())

        # Add agents from each selected persona
        for persona_name in self._selected_personas:
            persona_agents = self._registry.get_agents_for_persona(persona_name)
            enabled_agents.update(persona_agents)

        return enabled_agents

    def get_enabled_workflows(self) -> set[str]:
        """Get all workflows that should be enabled for selected personas.

        Returns:
            Set of workflow names to enable.
        """
        enabled_workflows: set[str] = set()

        for persona_name in self._selected_personas:
            persona_workflows = self._registry.get_workflows_for_persona(persona_name)
            enabled_workflows.update(persona_workflows)

        return enabled_workflows

    def get_enabled_skills(self) -> set[str]:
        """Get all skills that should be enabled for selected personas.

        Returns:
            Set of skill names to enable.
        """
        enabled_skills: set[str] = set()

        for persona_name in self._selected_personas:
            persona_skills = self._registry.get_skills_for_persona(persona_name)
            enabled_skills.update(persona_skills)

        return enabled_skills

    def is_agent_enabled(self, agent_name: str) -> bool:
        """Check if a specific agent should be enabled.

        Args:
            agent_name: Agent identifier.

        Returns:
            True if agent should be enabled, False otherwise.
        """
        return agent_name in self.get_enabled_agents()

    def is_workflow_enabled(self, workflow_name: str) -> bool:
        """Check if a specific workflow should be enabled.

        Args:
            workflow_name: Workflow identifier.

        Returns:
            True if workflow should be enabled, False otherwise.
        """
        return workflow_name in self.get_enabled_workflows()

    def is_skill_enabled(self, skill_name: str) -> bool:
        """Check if a specific skill should be enabled.

        Args:
            skill_name: Skill identifier.

        Returns:
            True if skill should be enabled, False otherwise.
        """
        return skill_name in self.get_enabled_skills()

    def get_selected_personas(self) -> list[str]:
        """Get list of currently selected personas.

        Returns:
            List of persona identifiers.
        """
        return self._selected_personas
