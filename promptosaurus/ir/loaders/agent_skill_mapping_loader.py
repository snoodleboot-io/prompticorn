"""Loader for agent-skill-workflow mappings."""

from pathlib import Path

import yaml


class AgentSkillMappingLoader:
    """Loads agent to skills/workflows mapping from YAML registry.

    Provides resolution of which skills and workflows apply to a given agent.
    Language-agnostic - same skills/workflows apply regardless of language.

    Example:
        >>> loader = AgentSkillMappingLoader()
        >>> skills = loader.get_skills_for_agent("architect")
        >>> isinstance(skills, list)
        True
        >>> workflows = loader.get_workflows_for_agent("code")
        >>> isinstance(workflows, list)
        True
    """

    def __init__(
        self, mapping_file: Path | str = "promptosaurus/configurations/agent_skill_mapping.yaml"
    ):
        """Initialize with path to mapping file.

        Args:
            mapping_file: Path to agent_skill_mapping.yaml

        Raises:
            FileNotFoundError: If mapping file does not exist
        """
        self.mapping_file = Path(mapping_file)
        if not self.mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")
        self._mapping = None

    @property
    def mapping(self) -> dict:
        """Lazy-load mapping YAML.

        Returns:
            Parsed YAML mapping dictionary
        """
        if self._mapping is None:
            with open(self.mapping_file, encoding="utf-8") as f:
                self._mapping = yaml.safe_load(f) or {}
        return self._mapping

    def get_skills_for_agent(self, agent_name: str) -> list[str]:
        """Get skills for an agent.

        Args:
            agent_name: Agent name (e.g., 'code', 'architect')

        Returns:
            List of skill names for this agent

        Example:
            >>> loader = AgentSkillMappingLoader()
            >>> skills = loader.get_skills_for_agent("architect")
            >>> len(skills) > 0
            True
        """
        if agent_name in self.mapping and "skills" in self.mapping[agent_name]:
            return self.mapping[agent_name]["skills"]
        return []

    def get_workflows_for_agent(self, agent_name: str) -> list[str]:
        """Get workflows for an agent.

        Args:
            agent_name: Agent name (e.g., 'code', 'architect')

        Returns:
            List of workflow names for this agent

        Example:
            >>> loader = AgentSkillMappingLoader()
            >>> workflows = loader.get_workflows_for_agent("code")
            >>> isinstance(workflows, list)
            True
        """
        if agent_name in self.mapping and "workflows" in self.mapping[agent_name]:
            return self.mapping[agent_name]["workflows"]
        return []

    def get_all_mappings(self) -> dict:
        """Get the entire mapping dictionary.

        Returns:
            Copy of the complete mapping dictionary

        Example:
            >>> loader = AgentSkillMappingLoader()
            >>> mappings = loader.get_all_mappings()
            >>> isinstance(mappings, dict)
            True
        """
        return self.mapping.copy()

    def has_agent(self, agent_name: str) -> bool:
        """Check if an agent has mappings defined.

        Args:
            agent_name: Agent name

        Returns:
            True if agent has entries in mapping
        """
        return agent_name in self.mapping

    def list_agents(self) -> list[str]:
        """List all agents with mappings.

        Returns:
            Sorted list of agent names

        Example:
            >>> loader = AgentSkillMappingLoader()
            >>> agents = loader.list_agents()
            >>> len(agents) > 0
            True
        """
        return sorted(self.mapping.keys())

    def validate_completeness(self, required_agents: list[str]) -> dict[str, list[str]]:
        """Validate that all required agents have mappings.

        Args:
            required_agents: List of agent names that must have mappings

        Returns:
            Dictionary with 'missing' and 'incomplete' lists

        Example:
            >>> loader = AgentSkillMappingLoader()
            >>> result = loader.validate_completeness(["architect", "code"])
            >>> "missing" in result and "incomplete" in result
            True
        """
        missing = []
        incomplete = []

        for agent in required_agents:
            if agent not in self.mapping:
                missing.append(agent)
            else:
                # Check if agent has both skills and workflows defined
                agent_data = self.mapping[agent]
                has_skills = "skills" in agent_data and len(agent_data["skills"]) > 0
                has_workflows = "workflows" in agent_data and len(agent_data["workflows"]) > 0

                if not has_skills or not has_workflows:
                    incomplete.append({
                        "agent": agent,
                        "has_skills": has_skills,
                        "has_workflows": has_workflows,
                        "skill_count": len(agent_data.get("skills", [])),
                        "workflow_count": len(agent_data.get("workflows", []))
                    })

        return {"missing": missing, "incomplete": incomplete}
