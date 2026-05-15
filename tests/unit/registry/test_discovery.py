"""Comprehensive unit tests for Registry Discovery system.

Tests cover:
- Happy path: Discovering agents and subagents from filesystem
- Edge cases: Empty directories, missing files, mixed structures
- Error handling: Invalid directories, missing component files
"""

import tempfile
from pathlib import Path

import pytest

from prompticorn.agent_registry.discovery import RegistryDiscovery
from prompticorn.agent_registry.errors import RegistryLoadError
from prompticorn.ir.models import Agent

# ============================================================================
# FIXTURES - Test agent directory structures
# ============================================================================


@pytest.fixture
def temp_agents_dir():
    """Create temporary agents directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def single_agent_dir(temp_agents_dir):
    """Create a single agent with minimal variant."""
    agent_dir = temp_agents_dir / "code" / "minimal"
    agent_dir.mkdir(parents=True)

    # Create prompt.md
    (agent_dir / "prompt.md").write_text(
        """---
name: code
description: Code implementation specialist
system_prompt: You are an expert code writer
tools:
  - git
  - python
skills: []
workflows: []
subagents: []
---

# Code Agent

Main prompt content.
""",
        encoding="utf-8",
    )
    return temp_agents_dir


@pytest.fixture
def multi_agent_dir(temp_agents_dir):
    """Create multiple agents with variants."""
    agents = ["code", "architect", "test"]

    for agent_name in agents:
        for variant in ["minimal", "verbose"]:
            variant_dir = temp_agents_dir / agent_name / variant
            variant_dir.mkdir(parents=True)

            (variant_dir / "prompt.md").write_text(
                f"""---
name: {agent_name}
description: {agent_name.capitalize()} agent
system_prompt: You are a {agent_name} specialist
tools: []
skills: []
workflows: []
subagents: []
---

# {agent_name.capitalize()} Agent

{variant} variant content.
""",
                encoding="utf-8",
            )

    return temp_agents_dir


@pytest.fixture
def agent_with_subagents_dir(temp_agents_dir):
    """Create agent with subagents."""
    # Create parent agent
    parent_dir = temp_agents_dir / "code" / "minimal"
    parent_dir.mkdir(parents=True)
    (parent_dir / "prompt.md").write_text(
        """---
name: code
description: Code agent
system_prompt: You are a code specialist
tools: []
skills: []
workflows: []
subagents:
  - formatter
  - documenter
---

# Code Agent
""",
        encoding="utf-8",
    )

    # Create subagents
    subagents = ["formatter", "documenter", "linter"]
    for subagent_name in subagents:
        subagent_dir = temp_agents_dir / "code" / "subagents" / subagent_name / "minimal"
        subagent_dir.mkdir(parents=True)
        (subagent_dir / "prompt.md").write_text(
            f"""---
name: {subagent_name}
description: {subagent_name} subagent
system_prompt: You are a {subagent_name} specialist
tools: []
skills: []
workflows: []
subagents: []
---

# {subagent_name.capitalize()} Subagent
""",
            encoding="utf-8",
        )

    return temp_agents_dir


@pytest.fixture
def agent_with_all_components_dir(temp_agents_dir):
    """Create agent with all component files."""
    agent_dir = temp_agents_dir / "code" / "minimal"
    agent_dir.mkdir(parents=True)

    # Prompt
    (agent_dir / "prompt.md").write_text(
        """---
name: code
description: Code agent
system_prompt: You are a code specialist
tools:
  - git
  - python
skills:
  - refactor
workflows:
  - review
subagents: []
---

# Code Agent
""",
        encoding="utf-8",
    )

    # Skills
    (agent_dir / "skills.md").write_text(
        """---
skills:
  - name: refactor
    description: Improve code
    instructions: Apply SOLID
    tools_needed:
      - python
---

## Refactor Skill
""",
        encoding="utf-8",
    )

    # Workflow
    (agent_dir / "workflow.md").write_text(
        """---
workflows:
  - name: review
    description: Review code
    steps:
      - Analyze
      - Test
      - Approve
---

## Review Process
""",
        encoding="utf-8",
    )

    return temp_agents_dir


# ============================================================================
# RegistryDiscovery Tests
# ============================================================================


class TestDiscoveryHappyPath:
    """Test RegistryDiscovery with valid inputs."""

    def test_discover_single_agent(self, single_agent_dir):
        """Test discovering a single agent."""
        discovery = RegistryDiscovery(single_agent_dir)
        agents = discovery.discover()

        assert "code" in agents
        assert len(agents) == 1
        assert agents["code"].name == "code"

    def test_discover_multi_agents(self, multi_agent_dir):
        """Test discovering multiple agents."""
        discovery = RegistryDiscovery(multi_agent_dir)
        agents = discovery.discover()

        assert len(agents) >= 3
        assert "code" in agents
        assert "architect" in agents
        assert "test" in agents

    def test_discover_agents_only(self, single_agent_dir):
        """Test discovering only top-level agents."""
        discovery = RegistryDiscovery(single_agent_dir)
        agents = discovery.discover_agents()

        assert "code" in agents
        assert isinstance(agents["code"], Agent)

    def test_discover_agent_returns_agent_model(self, single_agent_dir):
        """Test discovered agent is an Agent IR model."""
        discovery = RegistryDiscovery(single_agent_dir)
        agents = discovery.discover_agents()

        agent = agents["code"]
        assert isinstance(agent, Agent)
        assert agent.name == "code"
        assert agent.description == "Code implementation specialist"
        assert isinstance(agent.tools, list)

    def test_discover_subagents_exist(self, agent_with_subagents_dir):
        """Test discovering subagents for an agent."""
        discovery = RegistryDiscovery(agent_with_subagents_dir)
        agents = discovery.discover()

        # Should have parent agent and subagents
        assert "code" in agents
        # Subagents are keyed as "agent/subagent"
        keys = list(agents.keys())
        subagent_keys = [k for k in keys if "/" in k]
        assert len(subagent_keys) > 0

    def test_discover_subagents_by_name(self, agent_with_subagents_dir):
        """Test discovering subagents for specific agent."""
        discovery = RegistryDiscovery(agent_with_subagents_dir)
        subagents = discovery.discover_subagents("code")

        # Check subagents are discovered
        assert len(subagents) > 0
        # Keys should be "code/subagent_name"
        for key in subagents.keys():
            assert key.startswith("code/")

    def test_discover_with_all_components(self, agent_with_all_components_dir):
        """Test discovering agent with all component files."""
        discovery = RegistryDiscovery(agent_with_all_components_dir)
        agents = discovery.discover_agents()

        assert "code" in agents
        agent = agents["code"]
        assert agent.tools == ["git", "python"]
        assert agent.skills == ["refactor"]
        assert agent.workflows == ["review"]


class TestDiscoveryEdgeCases:
    """Test RegistryDiscovery edge cases."""

    def test_discover_empty_directory(self, temp_agents_dir):
        """Test discovering from empty directory."""
        discovery = RegistryDiscovery(temp_agents_dir)
        agents = discovery.discover_agents()

        # Should return empty dict, not error
        assert agents == {}

    def test_discover_ignore_hidden_dirs(self, temp_agents_dir):
        """Test hidden directories are ignored."""
        # Create hidden directory (should be ignored)
        (temp_agents_dir / ".hidden" / "minimal").mkdir(parents=True)
        (temp_agents_dir / ".hidden" / "minimal" / "prompt.md").write_text(
            "---\nname: hidden\n---\n", encoding="utf-8"
        )

        # Create real agent
        (temp_agents_dir / "code" / "minimal").mkdir(parents=True)
        (temp_agents_dir / "code" / "minimal" / "prompt.md").write_text(
            """---
name: code
description: Code agent
system_prompt: You are a code specialist
tools: []
skills: []
workflows: []
subagents: []
---
""",
            encoding="utf-8",
        )

        discovery = RegistryDiscovery(temp_agents_dir)
        agents = discovery.discover_agents()

        # Hidden directory should not be discovered
        assert "hidden" not in agents
        assert "code" in agents

    def test_discover_skip_non_directories(self, temp_agents_dir):
        """Test files in agents dir are skipped."""
        # Create a file
        (temp_agents_dir / "readme.txt").write_text("Not an agent", encoding="utf-8")

        # Create real agent
        (temp_agents_dir / "code" / "minimal").mkdir(parents=True)
        (temp_agents_dir / "code" / "minimal" / "prompt.md").write_text(
            """---
name: code
description: Code agent
system_prompt: You are a code specialist
tools: []
skills: []
workflows: []
subagents: []
---
""",
            encoding="utf-8",
        )

        discovery = RegistryDiscovery(temp_agents_dir)
        agents = discovery.discover_agents()

        assert "code" in agents
        # File should not be discovered as agent

    def test_discover_no_subagents(self, single_agent_dir):
        """Test agent without subagents directory."""
        discovery = RegistryDiscovery(single_agent_dir)
        subagents = discovery.discover_subagents("code")

        # Should return empty dict
        assert subagents == {}

    def test_discover_handles_missing_optional_components(self, temp_agents_dir):
        """Test discovering agent with only prompt.md (no skills/workflow)."""
        agent_dir = temp_agents_dir / "code" / "minimal"
        agent_dir.mkdir(parents=True)
        (agent_dir / "prompt.md").write_text(
            """---
name: code
description: Code agent
system_prompt: You are a code specialist
tools: []
skills: []
workflows: []
subagents: []
---
""",
            encoding="utf-8",
        )

        discovery = RegistryDiscovery(temp_agents_dir)
        agents = discovery.discover_agents()

        assert "code" in agents
        # Should still create agent even without optional files


class TestDiscoveryErrors:
    """Test RegistryDiscovery error handling."""

    def test_discover_nonexistent_directory(self):
        """Test discovering from non-existent directory."""
        discovery = RegistryDiscovery("/nonexistent/path")
        with pytest.raises(RegistryLoadError, match="not found"):
            discovery.discover_agents()

    def test_discover_invalid_agent_fails_gracefully(self, temp_agents_dir):
        """Test invalid agent doesn't stop discovery of other agents."""
        # Create invalid agent (no prompt.md)
        (temp_agents_dir / "invalid").mkdir(parents=True)

        # Create valid agent
        (temp_agents_dir / "code" / "minimal").mkdir(parents=True)
        (temp_agents_dir / "code" / "minimal" / "prompt.md").write_text(
            """---
name: code
description: Code agent
system_prompt: You are a code specialist
tools: []
skills: []
workflows: []
subagents: []
---
""",
            encoding="utf-8",
        )

        discovery = RegistryDiscovery(temp_agents_dir)
        agents = discovery.discover_agents()

        # Valid agent should be discovered despite invalid one
        assert "code" in agents

    def test_discover_malformed_yaml_fails(self, temp_agents_dir):
        """Test agent with malformed YAML is handled."""
        agent_dir = temp_agents_dir / "bad" / "minimal"
        agent_dir.mkdir(parents=True)
        (agent_dir / "prompt.md").write_text(
            """---
invalid: yaml: content
  bad indent
---
""",
            encoding="utf-8",
        )

        discovery = RegistryDiscovery(temp_agents_dir)
        agents = discovery.discover_agents()

        # Bad agent should not be discovered
        assert "bad" not in agents


class TestDiscoveryIntegration:
    """Test RegistryDiscovery integration scenarios."""

    def test_discover_full_structure(self, agent_with_subagents_dir):
        """Test discovering complete structure with parent and subagents."""
        discovery = RegistryDiscovery(agent_with_subagents_dir)
        all_agents = discovery.discover()

        # Should have parent agent
        assert "code" in all_agents

        # Should have subagents
        subagent_keys = [k for k in all_agents.keys() if "/" in k]
        assert len(subagent_keys) >= 3

    def test_discover_preserves_agent_data(self, agent_with_all_components_dir):
        """Test discovered agent preserves all metadata."""
        discovery = RegistryDiscovery(agent_with_all_components_dir)
        agents = discovery.discover_agents()

        agent = agents["code"]
        assert agent.name == "code"
        assert agent.description == "Code agent"
        assert agent.system_prompt == "You are a code specialist"
        assert "git" in agent.tools
        assert "python" in agent.tools
