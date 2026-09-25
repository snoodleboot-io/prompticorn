"""Persona registry and filtering for role-based agent selection.

This module provides the PersonaRegistry and PersonaFilter classes for managing
persona-based filtering of agents. A persona selects agents; the agents'
skill and workflow mappings live in agent_skill_mapping.yaml.

Reference: planning/current/adrs/ADR-001-persona-based-filtering.md
"""

import warnings
from pathlib import Path

import yaml

from prompticorn.content.configuration_document import ConfigurationDocument

# The configuration unit personas.yaml is addressed as, and the keys the document
# is required to have the right shape for.
PERSONAS_CONFIGURATION = "personas"
PERSONAS_KEY = "personas"
UNIVERSAL_AGENTS_KEY = "universal_agents"


class DeprecatedPersonaWarning(UserWarning):
    """A configuration named a persona id that is now only an alias.

    ``UserWarning`` rather than ``DeprecationWarning``, deliberately. Python
    hides ``DeprecationWarning`` unless it is triggered from ``__main__``, and
    the only reader who can act on this is the person running ``prompticorn``
    against their own config — exactly the reader who would never see it.
    """


def config_file_naming(persona_ids: list[str] | None) -> Path | None:
    """The project config file that genuinely lists one of ``persona_ids``.

    Provenance the registry cannot recover on its own: ``active_personas``
    reaches the builders as a bare list, so by the time an alias is resolved,
    where it was written down is gone. The project's own config is the
    overwhelmingly likely answer but not the only one — profiles, test fixtures
    and programmatic callers all pass configurations that file knows nothing
    about — so this reads it and names it only when it really carries the id.
    Naming the wrong file is worse than naming none: it sends the reader to edit
    something that is already correct. (PRO-159)
    """
    if not persona_ids:
        return None

    from prompticorn.config_handler import ConfigHandler

    try:
        path = ConfigHandler.get_config_path()
        if not path.is_file():
            return None
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return None

    listed = data.get("active_personas") or []
    return path if set(persona_ids) & set(listed) else None


class PersonaRegistry:
    """Registry for managing persona definitions and mappings.

    Loads persona definitions from personas.yaml and provides methods to query
    persona information and agent mappings.

    Example:
        >>> registry = PersonaRegistry.from_yaml("prompticorn/personas/personas.yaml")
        >>> personas = registry.list_personas()
        >>> agents = registry.get_agents_for_persona("fullstack_software_engineer")
    """

    def __init__(self, personas_data: dict) -> None:
        """Initialize registry with persona data.

        Args:
            personas_data: Dictionary loaded from personas.yaml containing
                          persona definitions, universal agents and any
                          deprecated aliases.
        """
        self._raw_data = personas_data
        self._personas = personas_data.get("personas", {})
        self._universal_agents = personas_data.get("universal_agents", [])
        self._version = personas_data.get("version", "unknown")
        self._aliases = self._read_aliases(personas_data)
        # Resolution happens on every lookup, so without this the same
        # deprecation would be reported once per get_* call — dozens of times in
        # one build. One registry, one telling.
        self._warned_aliases: set[str] = set()

    @staticmethod
    def _read_aliases(personas_data: dict) -> dict[str, str]:
        """Build the alias -> canonical map declared by ``deprecated_aliases``.

        An alias naming a persona that does not exist is dropped rather than
        obeyed. Honouring it would resolve a selection to nothing, which filters
        nothing: a typo in this map would make a working persona unreachable
        while every assertion about the personas themselves still passed.
        """
        personas = personas_data.get("personas", {})
        declared = personas_data.get("deprecated_aliases") or {}
        return {
            alias: target
            for alias, target in declared.items()
            if alias != target and target in personas
        }

    @classmethod
    def from_resolver(cls) -> "PersonaRegistry":
        """Create a registry from resolved content rather than a path.

        The preferred constructor: consumers should not need to know where
        personas.yaml lives. ``from_yaml`` remains for callers holding an
        explicit path. (PRO-106)

        **Validated, not merely parsed** (PRO-165). This used to be a bare
        ``yaml.safe_load``, which was defensible while the only possible source
        was the bundled file. Since PRO-117 a project layer can supply
        ``personas/personas.yaml``, and a wrong-shaped document does not fail
        here — it loads as a registry that knows no personas, filters nothing,
        and produces a build emitting all 26 agents where 15 were asked for. So
        the shape is checked, and a document that fails the check is rejected
        with a message naming the file and the layer that supplied it.

        Raises:
            MalformedConfigurationError: If the document is not usable persona
                data. Not a ContentError, deliberately: consumers tolerate an
                absent configuration by catching that, and a present-and-wrong
                one must not take the same path.
        """
        document = ConfigurationDocument.load(PERSONAS_CONFIGURATION)
        # personas: the sections that make the document mean anything. An empty
        # mapping is rejected rather than accepted as "no personas", because a
        # selection against it fails and the failure path builds everything.
        document.require_mapping(PERSONAS_KEY)
        document.require_mapping_values(PERSONAS_KEY)
        # universal_agents is optional — a file may define none — but if it is
        # there it is read as a list of names and must be one.
        document.require_string_list(UNIVERSAL_AGENTS_KEY)
        return cls(document.data)

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

        with yaml_path.open("r", encoding="utf-8") as f:
            personas_data = yaml.safe_load(f)

        return cls(personas_data)

    def resolve_persona(self, persona_name: str, *, source: Path | str | None = None) -> str:
        """Map a configured persona id onto the persona it stands for.

        Deprecated ids keep resolving so a config written against an older
        release still builds the set it always built. The alternative — letting
        the id fail — is not a loud failure anywhere it matters: ``PersonaFilter``
        raises ``KeyError``, but ``prompt_builder`` catches broadly around persona
        filtering and falls back to building *every* agent. A dropped id would
        quietly emit the whole library instead of the role's slice. (PRO-159)

        Args:
            persona_name: Persona identifier as a configuration spelled it.
            source: Config file the value came from, when the caller knows it.
                ``active_personas`` reaches here as a bare list, so provenance
                can only come from above; callers holding a synthetic config
                pass nothing rather than naming a file that has nothing to do
                with the value.

        Returns:
            The canonical persona identifier, or ``persona_name`` unchanged when
            it is not a deprecated alias.
        """
        target = self._aliases.get(persona_name)
        if target is None:
            return persona_name

        if persona_name not in self._warned_aliases:
            self._warned_aliases.add(persona_name)
            location = f" in {source}" if source else ""
            warnings.warn(
                f"Persona '{persona_name}'{location} is a deprecated alias for "
                f"'{target}' and will be removed in a future release. Update "
                f"active_personas to '{target}'.",
                DeprecatedPersonaWarning,
                stacklevel=3,
            )
        return target

    def list_personas(self) -> list[str]:
        """Get the persona identifiers offered for selection.

        Deprecated aliases are excluded: this list feeds the ``init`` and
        ``swap`` pickers, where an alias is a duplicate entry competing with the
        persona it points at — and the duplicate wins, because it was listed
        first under the friendlier name. Use
        :meth:`list_resolvable_personas` where the question is what a config may
        legally say rather than what a user may choose.

        Returns:
            List of selectable persona keys
            (e.g., ['fullstack_software_engineer', 'architect', ...])
        """
        return [name for name in self._personas if name not in self._aliases]

    def list_resolvable_personas(self) -> list[str]:
        """Get every persona identifier a configuration may legally name.

        That is the selectable personas plus the deprecated aliases. Aliases are
        listed even once their duplicate definition is deleted, since resolution
        is what keeps the stale config building.

        Returns:
            List of accepted persona keys, selectable ones first.
        """
        return self.list_personas() + list(self._aliases)

    def get_persona_info(self, persona_name: str) -> dict:
        """Get full persona definition.

        Args:
            persona_name: Persona identifier (e.g., 'fullstack_software_engineer'),
                          or a deprecated alias for one.

        Returns:
            Dictionary with persona definition including display_name, description,
            focus, primary_agents, secondary_agents.

            A deprecated alias returns the definition of the persona it resolves
            to, so every derived value — the agent list, and the display name the
            CLAUDE.md header is stamped with — describes the persona actually
            being built rather than the id that asked for it.

        Raises:
            KeyError: If persona doesn't exist.
        """
        resolved = self.resolve_persona(persona_name)
        if resolved not in self._personas:
            msg = f"Persona '{persona_name}' not found. Available: {self.list_personas()}"
            raise KeyError(msg)

        return self._personas[resolved]

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
    """Filters agents based on selected personas.

    Implements the dynamic agent enabling/disabling mechanism described in ADR-001.
    Agents are enabled if present in ANY selected persona, disabled otherwise.

    Example:
        >>> registry = PersonaRegistry.from_yaml("personas.yaml")
        >>> filter = PersonaFilter(registry, ["fullstack_software_engineer", "qa_tester"])
        >>> enabled_agents = filter.get_enabled_agents()
    """

    def __init__(
        self,
        registry: PersonaRegistry,
        selected_personas: list[str],
        *,
        source: Path | str | None = None,
    ) -> None:
        """Initialize filter with registry and selected personas.

        Deprecated aliases are resolved up front, so the rest of the filter —
        and everything downstream that asks it what was selected — only ever
        sees canonical ids. Selecting an alias alongside the persona it points at
        is one selection, not two.

        Args:
            registry: PersonaRegistry instance.
            selected_personas: List of persona identifiers to enable, as the
                configuration spelled them.
            source: Config file the selection came from, when the caller knows
                it, so a deprecation warning can name the file to edit.

        Raises:
            KeyError: If any selected persona neither exists nor resolves.
        """
        self._registry = registry

        # Validate personas exist, naming the id the config used rather than
        # what it resolved to — the reader has to find it in their own file.
        available = registry.list_personas()
        resolved: list[str] = []
        for persona in selected_personas:
            canonical = registry.resolve_persona(persona, source=source)
            if canonical not in available:
                msg = f"Invalid persona: '{persona}'. Available: {available}"
                raise KeyError(msg)
            if canonical not in resolved:
                resolved.append(canonical)

        self._selected_personas = resolved

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

    def is_agent_enabled(self, agent_name: str) -> bool:
        """Check if a specific agent should be enabled.

        Args:
            agent_name: Agent identifier.

        Returns:
            True if agent should be enabled, False otherwise.
        """
        return agent_name in self.get_enabled_agents()

    def get_selected_personas(self) -> list[str]:
        """Get list of currently selected personas.

        Returns:
            List of canonical persona identifiers: deprecated aliases have been
            resolved and duplicates collapsed, so this is what is being built
            rather than what the configuration asked for verbatim.
        """
        return self._selected_personas
