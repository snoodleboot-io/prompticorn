"""Registry discovery for auto-discovering agents from filesystem.

This module provides the RegistryDiscovery class for scanning and auto-discovering
agents and subagents from a directory structure, building Agent IR models.
"""

from pathlib import Path

from prompticorn.agent_registry.errors import RegistryLoadError
from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.bundled_identity import BundledIdentity
from prompticorn.content.content_resolver import ContentResolver
from prompticorn.ir.exceptions import MissingFileError, ParseError
from prompticorn.ir.loaders import ComponentBundle, ComponentLoader
from prompticorn.ir.models import Agent
from prompticorn.text_utils import strip_source_header_comments

# Top-level directories under agents/ that are not agents and must be skipped
# during discovery and structural validation (e.g. shared convention files).
_NON_AGENT_DIRS = frozenset({"subagents", "core"})


class RegistryDiscovery:
    """Auto-discovers agents from filesystem structure.

    Scans a directory structure for agents and subagents, automatically building
    Agent IR models from component files (prompt.md, skills.md, workflow.md).

    The directory structure should follow this pattern:
        agents/
        ├── agent_name/
        │   ├── minimal/
        │   │   ├── prompt.md
        │   │   ├── skills.md (optional)
        │   │   └── workflow.md (optional)
        │   ├── verbose/
        │   │   └── ...
        │   └── subagents/
        │       ├── subagent_name/
        │       │   ├── minimal/
        │       │   └── verbose/
        │       └── ...
        └── ...

    Example:
        >>> discovery = RegistryDiscovery("./agents")
        >>> agents = discovery.discover()
        >>> "code" in agents
        True
        >>> "code/boilerplate" in agents
        True
    """

    def __init__(self, agents_dir: Path | str) -> None:
        """Initialize discovery with agents directory path.

        Args:
            agents_dir: Path to the agents directory to scan.
        """
        self.agents_dir = Path(agents_dir)
        self._component_loader = ComponentLoader()
        self._resolver: ContentResolver | None = None
        self._identity = BundledIdentity()

    @classmethod
    def from_resolver(cls, resolver=None) -> "RegistryDiscovery":
        """Discover agents from resolved content instead of a directory walk.

        The preferred constructor: nothing outside the content package should
        need to know where agent sources live. The directory-taking form remains
        for callers holding a path. (PRO-106)
        """
        from prompticorn.content.content_resolver import default_resolver

        instance = cls.__new__(cls)
        instance.agents_dir = None
        instance._component_loader = ComponentLoader()
        instance._resolver = resolver if resolver is not None else default_resolver()
        # Set here as well as in __init__: this constructor bypasses __init__
        # entirely, so anything it forgets is an AttributeError at first use.
        instance._identity = BundledIdentity()
        return instance

    def _resolved_agent_names(self) -> list[str]:
        """Agent names carried by the resolver, sorted."""
        from prompticorn.content.unit_kind import UnitKind

        assert self._resolver is not None
        return sorted(
            unit.id.segments[0] for unit in self._resolver.units() if unit.kind is UnitKind.AGENT
        )

    def _resolved_subagent_names(self, agent_name: str) -> list[str]:
        """Subagent names under an agent, sorted and de-duplicated across variants."""
        from prompticorn.content.unit_kind import UnitKind

        assert self._resolver is not None
        return sorted(
            {
                unit.id.segments[1]
                for unit in self._resolver.units()
                if unit.kind is UnitKind.SUBAGENT and unit.id.segments[0] == agent_name
            }
        )

    def artifact_id(self, key: str) -> ArtifactId:
        """Artifact identity for a discovered key. (PRO-108)

        Unlike :meth:`Registry.artifact_id` this does not check membership —
        discovery is the thing that decides what exists, so it has no set to
        check against until :meth:`discover` has run.

        Args:
            key: ``"code"`` or ``"code/boilerplate"``.
        """
        return self._identity.for_registry_key(key)

    @staticmethod
    def _read_component(directory: Path, filename: str) -> str:
        """Read a required component document.

        Raises:
            MissingFileError: If it is absent — preserving the semantics the
                loader used to enforce before it became pure. (PRO-105)
        """
        path = directory / filename
        if not path.is_file():
            raise MissingFileError(f"Required file '{filename}' not found in {directory}")
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _read_optional_component(directory: Path, filename: str) -> str | None:
        path = directory / filename
        return path.read_text(encoding="utf-8") if path.is_file() else None

    def discover(self) -> dict[str, Agent]:
        """Scan filesystem and auto-discover all agents.

        Returns:
            Dict[str, Agent] where keys are:
            - Agent: "agent_name"
            - Subagent: "agent_name/subagent_name"

        Raises:
            RegistryLoadError: If discovery fails.
        """
        try:
            if self._resolver is not None:
                return self._discover_via_resolver()

            all_agents: dict[str, Agent] = {}

            # Discover top-level agents
            agents = self.discover_agents()
            all_agents.update(agents)

            # Discover subagents for each agent
            for agent_name in agents.keys():
                subagents = self.discover_subagents(agent_name)
                all_agents.update(subagents)

            return all_agents

        except Exception as e:
            raise RegistryLoadError(f"Failed to discover agents: {str(e)}") from e

    def discover_agents(self) -> dict[str, Agent]:
        """Discover top-level agents (not subagents).

        Returns:
            Dict[str, Agent] where keys are agent names.

        Raises:
            RegistryLoadError: If discovery fails.
        """
        agents: dict[str, Agent] = {}

        if not self.agents_dir.is_dir():
            raise RegistryLoadError(f"Agents directory not found: {self.agents_dir}")

        # Iterate through top-level directories in agents/ (sorted for
        # deterministic, filesystem-independent discovery order — otherwise the
        # order leaks into every generated file that lists agents).
        for agent_dir in sorted(self.agents_dir.iterdir()):
            if not agent_dir.is_dir():
                continue

            # Skip special directories
            if agent_dir.name.startswith(".") or agent_dir.name in _NON_AGENT_DIRS:
                continue

            agent_name = agent_dir.name
            try:
                agent = self._load_agent(agent_name, agent_dir)
                if agent:
                    agents[agent_name] = agent
            except Exception as e:
                # Log error but continue discovering other agents
                print(f"Warning: Failed to load agent '{agent_name}': {str(e)}")

        return agents

    def discover_subagents(self, agent_name: str) -> dict[str, Agent]:
        """Discover subagents for a specific agent.

        Returns:
            Dict[str, Agent] where keys are "agent_name/subagent_name".

        Raises:
            RegistryLoadError: If discovery fails.
        """
        subagents: dict[str, Agent] = {}

        agent_dir = self.agents_dir / agent_name
        subagents_dir = agent_dir / "subagents"

        if not subagents_dir.is_dir():
            return subagents

        # Iterate through subagent directories (sorted for deterministic order).
        for subagent_dir in sorted(subagents_dir.iterdir()):
            if not subagent_dir.is_dir():
                continue

            if subagent_dir.name.startswith("."):
                continue

            subagent_name = subagent_dir.name
            try:
                subagent = self._load_agent(subagent_name, subagent_dir)
                if subagent:
                    key = f"{agent_name}/{subagent_name}"
                    subagents[key] = subagent
            except Exception as e:
                # Log error but continue discovering other subagents
                print(f"Warning: Failed to load subagent '{agent_name}/{subagent_name}': {str(e)}")

        return subagents

    def validate_structure(self) -> list[str]:
        """Validate agents/ directory structure.

        Returns:
            List of issues found (empty if no issues).
        """
        issues: list[str] = []

        if self.agents_dir is None:
            # Structure validation is about the filesystem layout; a
            # resolver-backed discovery has no directory to validate. (PRO-106)
            return issues

        if not self.agents_dir.is_dir():
            issues.append(f"Agents directory not found: {self.agents_dir}")
            return issues

        # Check each agent directory (sorted for deterministic issue order).
        for agent_dir in sorted(self.agents_dir.iterdir()):
            if not agent_dir.is_dir() or agent_dir.name.startswith("."):
                continue
            if agent_dir.name in _NON_AGENT_DIRS:
                continue

            agent_name = agent_dir.name

            # Check if this is a top-level agent (has prompt.md directly)
            # or uses the old variant structure
            direct_prompt = agent_dir / "prompt.md"
            minimal_dir = agent_dir / "minimal"
            verbose_dir = agent_dir / "verbose"

            if direct_prompt.is_file():
                # Top-level agent with direct prompt.md - this is correct
                pass
            elif not minimal_dir.is_dir() and not verbose_dir.is_dir():
                # Neither direct prompt.md nor variants - issue
                issues.append(
                    f"Agent '{agent_name}' has neither prompt.md nor 'minimal'/'verbose' variants"
                )
                continue
            else:
                # Has variants - check for prompt.md in each variant
                for variant_dir in [d for d in [minimal_dir, verbose_dir] if d.is_dir()]:
                    prompt_file = variant_dir / "prompt.md"
                    if not prompt_file.is_file():
                        issues.append(
                            f"Agent '{agent_name}' variant '{variant_dir.name}' missing prompt.md"
                        )

            # Check subagents if they exist
            subagents_dir = agent_dir / "subagents"
            if subagents_dir.is_dir():
                for subagent_dir in sorted(subagents_dir.iterdir()):
                    if not subagent_dir.is_dir() or subagent_dir.name.startswith("."):
                        continue

                    subagent_name = subagent_dir.name

                    # Check for variants in subagent
                    minimal_dir = subagent_dir / "minimal"
                    verbose_dir = subagent_dir / "verbose"

                    if not minimal_dir.is_dir() and not verbose_dir.is_dir():
                        issues.append(
                            f"Subagent '{agent_name}/{subagent_name}' has neither 'minimal' nor 'verbose' variant"
                        )

        return issues

    def _load_agent(self, agent_name: str, agent_dir: Path) -> Agent | None:
        """Load an agent from directory.

        Args:
            agent_name: Name of the agent.
            agent_dir: Path to the agent directory.

        Returns:
            Agent IR model, or None if no variant found.

        Raises:
            Exception: If loading fails.
        """
        # Check if this is a top-level agent (has prompt.md directly)
        # or a subagent (has minimal/verbose variants)
        direct_prompt = agent_dir / "prompt.md"

        if direct_prompt.is_file():
            # Top-level agent: Load from prompt.md directly (no variants)
            return self._load_agent_from_directory(agent_name, agent_dir)

        # Subagent: Try minimal variant first
        minimal_dir = agent_dir / "minimal"
        if minimal_dir.is_dir():
            try:
                return self._load_agent_from_variant(agent_name, minimal_dir)
            except (MissingFileError, ParseError):
                pass

        # Fall back to verbose variant
        verbose_dir = agent_dir / "verbose"
        if verbose_dir.is_dir():
            try:
                return self._load_agent_from_variant(agent_name, verbose_dir)
            except (MissingFileError, ParseError):
                pass

        return None

    def _discover_via_resolver(self) -> dict[str, Agent]:
        """Discover every agent and subagent from resolved content.

        Enumeration order comes from the resolver, which sorts by unit id, so
        discovery no longer depends on filesystem ordering. (PRO-106)
        """
        from prompticorn.content.unit_id import UnitId

        assert self._resolver is not None
        all_agents: dict[str, Agent] = {}

        for agent_name in self._resolved_agent_names():
            prompt_text = self._resolver.read(UnitId.parse(f"agent/{agent_name}"))
            bundle = self._component_loader.parse(prompt_text, source=f"agent/{agent_name}")
            subagent_names = self._resolved_subagent_names(agent_name)
            all_agents[agent_name] = self._build_agent(
                agent_name, bundle, f"agent/{agent_name}", subagent_names
            )

            for subagent_name in subagent_names:
                for variant in ("minimal", "verbose"):
                    unit_id = f"subagent/{agent_name}/{subagent_name}/{variant}"
                    text = self._resolver.read_optional(UnitId.parse(unit_id))
                    if text is None:
                        continue
                    sub_bundle = self._component_loader.parse(text, source=unit_id)
                    all_agents[f"{agent_name}/{subagent_name}"] = self._build_agent(
                        subagent_name, sub_bundle, unit_id, []
                    )
                    break

        return all_agents

    def _load_agent_from_directory(self, agent_name: str, agent_dir: Path) -> Agent:
        """Load a top-level agent from a directory with prompt.md directly.

        Args:
            agent_name: Name of the agent.
            agent_dir: Path to the agent directory (contains prompt.md).

        Returns:
            Agent IR model.

        Raises:
            MissingFileError: If required files are missing.
            ParseError: If parsing fails.
        """
        # Load component bundle (prompt.md only, skills/workflows at subagent level).
        # Bytes are fetched here; the loader only parses. (PRO-105)
        bundle = self._component_loader.parse(
            self._read_component(agent_dir, "prompt.md"),
            skills_text=self._read_optional_component(agent_dir, "skills.md"),
            workflow_text=self._read_optional_component(agent_dir, "workflow.md"),
            source=str(agent_dir),
        )

        # Auto-discover subagents from the filesystem, merged with frontmatter.
        extra_subagents: list[str] = []
        subagents_dir = agent_dir / "subagents"
        if subagents_dir.is_dir():
            extra_subagents = [
                p.name
                for p in sorted(subagents_dir.iterdir())
                if p.is_dir() and not p.name.startswith(".")
            ]

        return self._build_agent(agent_name, bundle, str(agent_dir), extra_subagents)

    def _build_agent(
        self,
        agent_name: str,
        bundle: ComponentBundle,
        source: str,
        extra_subagents: list[str],
    ) -> Agent:
        """Build the Agent model from parsed components.

        Shared by the directory walk and the resolver path so both produce
        identical models — the whole point of the seam. (PRO-106)
        """
        prompt_data = bundle.prompt_content
        if not isinstance(prompt_data, dict):
            raise ParseError(f"Invalid prompt.md format in {source}")

        name = prompt_data.get("name") or agent_name
        description = prompt_data.get("description", "")
        mode = prompt_data.get("mode", "all")
        system_prompt = strip_source_header_comments(prompt_data.get("system_prompt", ""))
        tools = prompt_data.get("tools", [])
        skills = prompt_data.get("skills", [])
        workflows = prompt_data.get("workflows", [])
        subagents = prompt_data.get("subagents", [])
        permissions = prompt_data.get("permissions", None)

        if extra_subagents:
            subagents = sorted(set(subagents) | set(extra_subagents))

        return Agent(
            name=name or agent_name,
            description=description or f"Agent: {agent_name}",
            mode=mode,
            system_prompt=system_prompt or "",
            tools=tools if isinstance(tools, list) else [],
            skills=skills if isinstance(skills, list) else [],
            workflows=workflows if isinstance(workflows, list) else [],
            subagents=subagents if isinstance(subagents, list) else [],
            permissions=permissions if isinstance(permissions, dict) else None,
        )

    def _load_agent_from_variant(self, agent_name: str, variant_dir: Path) -> Agent:
        """Load an agent from a specific variant directory.

        Args:
            agent_name: Name of the agent.
            variant_dir: Path to the variant directory (minimal or verbose).

        Returns:
            Agent IR model.

        Raises:
            MissingFileError: If required files are missing.
            ParseError: If parsing fails.
        """
        # Load component bundle. Bytes here, parsing in the loader. (PRO-105)
        bundle = self._component_loader.parse(
            self._read_component(variant_dir, "prompt.md"),
            skills_text=self._read_optional_component(variant_dir, "skills.md"),
            workflow_text=self._read_optional_component(variant_dir, "workflow.md"),
            source=str(variant_dir),
        )

        # Extract agent fields from prompt content
        prompt_data = bundle.prompt_content
        if not isinstance(prompt_data, dict):
            raise ParseError(f"Invalid prompt.md format in {variant_dir}")

        name = prompt_data.get("name") or agent_name
        description = prompt_data.get("description", "")
        mode = prompt_data.get("mode", "all")
        system_prompt = strip_source_header_comments(prompt_data.get("system_prompt", ""))
        tools = prompt_data.get("tools", [])
        skills = prompt_data.get("skills", [])
        workflows = prompt_data.get("workflows", [])
        subagents = prompt_data.get("subagents", [])

        # Extract permissions
        permissions = prompt_data.get("permissions", None)

        # Create Agent IR model
        agent = Agent(
            name=name or agent_name,
            description=description or f"Agent: {agent_name}",
            mode=mode,
            system_prompt=system_prompt or "",
            tools=tools if isinstance(tools, list) else [],
            skills=skills if isinstance(skills, list) else [],
            workflows=workflows if isinstance(workflows, list) else [],
            subagents=subagents if isinstance(subagents, list) else [],
            permissions=permissions if isinstance(permissions, dict) else None,
        )

        return agent
