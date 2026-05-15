"""Persona-based filtering for agents, workflows, and skills.

This package provides persona registry and filtering capabilities to enable
role-based selection of prompticorn content.

Example usage:
    >>> from prompticorn.personas import PersonaRegistry, PersonaFilter
    >>> registry = PersonaRegistry.from_yaml("prompticorn/personas/personas.yaml")
    >>> filter = PersonaFilter(registry, ["software_engineer"])
    >>> enabled_agents = filter.get_enabled_agents()
"""

from prompticorn.personas.registry import PersonaFilter, PersonaRegistry

__all__ = ["PersonaRegistry", "PersonaFilter"]
