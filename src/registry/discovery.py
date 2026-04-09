"""Registry discovery for auto-discovering agents from filesystem.

This module provides the RegistryDiscovery class for scanning and auto-discovering
agents and subagents from a directory structure, building Agent IR models.
"""

from pathlib import Path
from typing import Dict
from collections import defaultdict

from src.ir.models import Agent
from src.ir.loaders import ComponentLoader
from src.ir.exceptions import MissingFileError, ParseError
from src.registry.errors import RegistryLoadError


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

    def discover(self) -> Dict[str, Agent]:
        """Scan filesystem and auto-discover all agents.

        Returns:
            Dict[str, Agent] where keys are:
            - Agent: "agent_name"
            - Subagent: "agent_name/subagent_name"

        Raises:
            RegistryLoadError: If discovery fails.
        """
        try:
            all_agents: Dict[str, Agent] = {}

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

    def discover_agents(self) -> Dict[str, Agent]:
        """Discover top-level agents (not subagents).

        Returns:
            Dict[str, Agent] where keys are agent names.

        Raises:
            RegistryLoadError: If discovery fails.
        """
        agents: Dict[str, Agent] = {}

        if not self.agents_dir.is_dir():
            raise RegistryLoadError(f"Agents directory not found: {self.agents_dir}")

        # Iterate through top-level directories in agents/
        for agent_dir in self.agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            # Skip special directories
            if agent_dir.name.startswith(".") or agent_dir.name == "subagents":
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

    def discover_subagents(self, agent_name: str) -> Dict[str, Agent]:
        """Discover subagents for a specific agent.

        Returns:
            Dict[str, Agent] where keys are "agent_name/subagent_name".

        Raises:
            RegistryLoadError: If discovery fails.
        """
        subagents: Dict[str, Agent] = {}

        agent_dir = self.agents_dir / agent_name
        subagents_dir = agent_dir / "subagents"

        if not subagents_dir.is_dir():
            return subagents

        # Iterate through subagent directories
        for subagent_dir in subagents_dir.iterdir():
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

        if not self.agents_dir.is_dir():
            issues.append(f"Agents directory not found: {self.agents_dir}")
            return issues

        # Check each agent directory
        for agent_dir in self.agents_dir.iterdir():
            if not agent_dir.is_dir() or agent_dir.name.startswith("."):
                continue

            agent_name = agent_dir.name

            # Check for at least minimal or verbose variant
            minimal_dir = agent_dir / "minimal"
            verbose_dir = agent_dir / "verbose"

            if not minimal_dir.is_dir() and not verbose_dir.is_dir():
                issues.append(f"Agent '{agent_name}' has neither 'minimal' nor 'verbose' variant")
                continue

            # Check for prompt.md in each variant
            for variant_dir in [d for d in [minimal_dir, verbose_dir] if d.is_dir()]:
                prompt_file = variant_dir / "prompt.md"
                if not prompt_file.is_file():
                    issues.append(
                        f"Agent '{agent_name}' variant '{variant_dir.name}' missing prompt.md"
                    )

            # Check subagents if they exist
            subagents_dir = agent_dir / "subagents"
            if subagents_dir.is_dir():
                for subagent_dir in subagents_dir.iterdir():
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
        """Load an agent from its directory.

        Tries minimal variant first, then verbose. Returns None if neither found.

        Args:
            agent_name: Name of the agent (directory name).
            agent_dir: Path to the agent directory.

        Returns:
            Agent IR model, or None if no variant found.

        Raises:
            Exception: If loading fails.
        """
        # Try minimal variant first
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
        # Load component bundle
        bundle = self._component_loader.load(str(variant_dir))

        # Extract agent fields from prompt content
        prompt_data = bundle.prompt_content
        if not isinstance(prompt_data, dict):
            raise ParseError(f"Invalid prompt.md format in {variant_dir}")

        name = prompt_data.get("name") or agent_name
        description = prompt_data.get("description", "")
        system_prompt = prompt_data.get("system_prompt", "")
        tools = prompt_data.get("tools", [])
        skills = prompt_data.get("skills", [])
        workflows = prompt_data.get("workflows", [])
        subagents = prompt_data.get("subagents", [])

        # Create Agent IR model
        agent = Agent(
            name=name or agent_name,
            description=description or f"Agent: {agent_name}",
            system_prompt=system_prompt or "",
            tools=tools if isinstance(tools, list) else [],
            skills=skills if isinstance(skills, list) else [],
            workflows=workflows if isinstance(workflows, list) else [],
            subagents=subagents if isinstance(subagents, list) else [],
        )

        return agent
