"""Persona-based filtering for agents, workflows, and skills.

This package provides persona registry and filtering capabilities to enable
role-based selection of promptosaurus content.

Example usage:
    >>> from promptosaurus.personas import PersonaRegistry, PersonaFilter
    >>> registry = PersonaRegistry.from_yaml("promptosaurus/personas/personas.yaml")
    >>> filter = PersonaFilter(registry, ["software_engineer"])
    >>> enabled_agents = filter.get_enabled_agents()
"""

from promptosaurus.personas.registry import PersonaFilter, PersonaRegistry

__all__ = ["PersonaRegistry", "PersonaFilter"]
