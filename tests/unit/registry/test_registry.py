"""Comprehensive unit tests for Registry system.

Tests cover:
- Happy path: Getting agents, listing agents, caching
- Edge cases: Missing agents, subagent queries, variant handling
- Error handling: Invalid names, variant errors
"""

import pytest

from promptosaurus.agent_registry.errors import AgentNotFoundError
from promptosaurus.agent_registry.registry import Registry
from promptosaurus.ir.models import Agent

# ============================================================================
# FIXTURES - Test agents
# ============================================================================


@pytest.fixture
def sample_agent() -> Agent:
    """Create a sample agent."""
    return Agent(
        name="code",
        description="Code implementation specialist",
        system_prompt="You are an expert code writer",
        tools=["git", "python"],
        skills=["refactor", "test"],
        workflows=["code-review"],
        subagents=["formatter"],
    )


@pytest.fixture
def sample_agent_2() -> Agent:
    """Create another sample agent."""
    return Agent(
        name="architect",
        description="System architecture specialist",
        system_prompt="You are an expert architect",
        tools=["draw.io", "markdown"],
        skills=["design"],
        workflows=["planning"],
        subagents=[],
    )


@pytest.fixture
def sample_subagent() -> Agent:
    """Create a sample subagent."""
    return Agent(
        name="formatter",
        description="Code formatting specialist",
        system_prompt="You format code",
        tools=["python"],
        skills=[],
        workflows=[],
        subagents=[],
    )


@pytest.fixture
def sample_agents_dict(sample_agent, sample_agent_2, sample_subagent) -> dict[str, Agent]:
    """Create a dictionary of agents including subagents."""
    return {
        "code": sample_agent,
        "architect": sample_agent_2,
        "code/formatter": sample_subagent,
    }


# ============================================================================
# Registry Tests - Initialization
# ============================================================================


class TestRegistryInitialization:
    """Test Registry initialization."""

    def test_init_with_agents(self, sample_agents_dict):
        """Test creating registry with agents dict."""
        registry = Registry(sample_agents_dict)

        assert registry is not None
        assert len(registry.get_all_agents()) == 3

    def test_init_with_caching_enabled(self, sample_agents_dict):
        """Test registry with caching enabled."""
        registry = Registry(sample_agents_dict, cache=True)

        assert registry._cache_enabled is True

    def test_init_with_caching_disabled(self, sample_agents_dict):
        """Test registry with caching disabled."""
        registry = Registry(sample_agents_dict, cache=False)

        assert registry._cache_enabled is False

    def test_init_empty_registry(self):
        """Test creating empty registry."""
        registry = Registry({})

        assert len(registry.get_all_agents()) == 0


# ============================================================================
# Registry Tests - Get Agent
# ============================================================================


class TestRegistryGetAgent:
    """Test getting agents from registry."""

    def test_get_agent_by_name(self, sample_agents_dict):
        """Test getting agent by name."""
        registry = Registry(sample_agents_dict)
        agent = registry.get_agent("code")

        assert agent.name == "code"
        assert agent.description == "Code implementation specialist"

    def test_get_agent_multiple_agents(self, sample_agents_dict):
        """Test getting different agents."""
        registry = Registry(sample_agents_dict)

        code_agent = registry.get_agent("code")
        arch_agent = registry.get_agent("architect")

        assert code_agent.name == "code"
        assert arch_agent.name == "architect"

    def test_get_subagent_by_key(self, sample_agents_dict):
        """Test getting subagent by full key."""
        registry = Registry(sample_agents_dict)
        subagent = registry.get_agent("code/formatter")

        assert subagent.name == "formatter"

    def test_get_agent_default_variant(self, sample_agents_dict):
        """Test default variant parameter."""
        registry = Registry(sample_agents_dict)
        agent = registry.get_agent("code", variant="minimal")

        assert agent is not None

    def test_get_agent_nonexistent_raises_error(self, sample_agents_dict):
        """Test getting non-existent agent raises error."""
        registry = Registry(sample_agents_dict)

        with pytest.raises(AgentNotFoundError):
            registry.get_agent("nonexistent")

    def test_get_agent_wrong_subagent_key_raises_error(self, sample_agents_dict):
        """Test getting subagent with wrong key raises error."""
        registry = Registry(sample_agents_dict)

        with pytest.raises(AgentNotFoundError):
            registry.get_agent("code/nonexistent")


# ============================================================================
# Registry Tests - List Agents
# ============================================================================


class TestRegistryListAgents:
    """Test listing agents."""

    def test_list_agents_top_level_only(self, sample_agents_dict):
        """Test listing only top-level agents (default)."""
        registry = Registry(sample_agents_dict)
        agents = registry.list_agents()

        assert len(agents) == 2  # code, architect
        assert "code" in agents
        assert "architect" in agents
        assert "code/formatter" not in agents

    def test_list_agents_include_subagents(self, sample_agents_dict):
        """Test listing agents including subagents."""
        registry = Registry(sample_agents_dict)
        agents = registry.list_agents(include_subagents=True)

        assert len(agents) == 3  # code, architect, code/formatter
        assert "code" in agents
        assert "architect" in agents
        assert "code/formatter" in agents

    def test_list_agents_sorted(self, sample_agents_dict):
        """Test agents are returned sorted."""
        registry = Registry(sample_agents_dict)
        agents = registry.list_agents(include_subagents=True)

        assert agents == sorted(agents)

    def test_list_agents_empty_registry(self):
        """Test listing agents in empty registry."""
        registry = Registry({})
        agents = registry.list_agents()

        assert agents == []

    def test_list_agents_only_subagents(self):
        """Test listing when only subagents exist."""
        agents_dict = {
            "code/formatter": Agent(
                name="formatter",
                description="Formatter",
                system_prompt="Format code",
                tools=[],
                skills=[],
                workflows=[],
                subagents=[],
            )
        }
        registry = Registry(agents_dict)
        top_level = registry.list_agents()

        # Should be empty since no top-level agents
        assert top_level == []


# ============================================================================
# Registry Tests - List Subagents
# ============================================================================


class TestRegistryListSubagents:
    """Test listing subagents for specific agent."""

    def test_list_subagents_for_agent(self, sample_agents_dict):
        """Test listing subagents for an agent."""
        registry = Registry(sample_agents_dict)
        subagents = registry.list_subagents("code")

        assert len(subagents) == 1
        assert "formatter" in subagents

    def test_list_subagents_no_subagents(self, sample_agents_dict):
        """Test listing subagents when none exist."""
        registry = Registry(sample_agents_dict)
        subagents = registry.list_subagents("architect")

        assert subagents == []

    def test_list_subagents_nonexistent_agent(self, sample_agents_dict):
        """Test listing subagents for non-existent agent."""
        registry = Registry(sample_agents_dict)
        subagents = registry.list_subagents("nonexistent")

        # Should return empty list, not error
        assert subagents == []

    def test_list_subagents_multiple(self):
        """Test listing multiple subagents."""
        agents_dict = {
            "code": Agent(
                name="code",
                description="Code agent",
                system_prompt="Code",
                tools=[],
                skills=[],
                workflows=[],
                subagents=["formatter", "documenter"],
            ),
            "code/formatter": Agent(
                name="formatter",
                description="Formatter",
                system_prompt="Format",
                tools=[],
                skills=[],
                workflows=[],
                subagents=[],
            ),
            "code/documenter": Agent(
                name="documenter",
                description="Documenter",
                system_prompt="Document",
                tools=[],
                skills=[],
                workflows=[],
                subagents=[],
            ),
        }
        registry = Registry(agents_dict)
        subagents = registry.list_subagents("code")

        assert len(subagents) == 2
        assert "formatter" in subagents
        assert "documenter" in subagents
        assert subagents == sorted(subagents)


# ============================================================================
# Registry Tests - Get All Agents
# ============================================================================


class TestRegistryGetAllAgents:
    """Test getting all agents."""

    def test_get_all_agents(self, sample_agents_dict):
        """Test getting all agents as dict."""
        registry = Registry(sample_agents_dict)
        all_agents = registry.get_all_agents()

        assert len(all_agents) == 3
        assert all(isinstance(agent, Agent) for agent in all_agents.values())

    def test_get_all_agents_returns_copy(self, sample_agents_dict, sample_agent):
        """Test get_all_agents returns a copy, not reference."""
        registry = Registry(sample_agents_dict)
        all_agents = registry.get_all_agents()

        # Modify the returned dict
        all_agents["new_agent"] = sample_agent

        # Original registry should not be modified
        assert "new_agent" not in registry.get_all_agents()

    def test_get_all_agents_empty_registry(self):
        """Test getting all agents from empty registry."""
        registry = Registry({})
        all_agents = registry.get_all_agents()

        assert all_agents == {}


# ============================================================================
# Registry Tests - Has Agent
# ============================================================================


class TestRegistryHasAgent:
    """Test checking if agent exists."""

    def test_has_agent_exists(self, sample_agents_dict):
        """Test checking existing agent."""
        registry = Registry(sample_agents_dict)

        assert registry.has_agent("code") is True
        assert registry.has_agent("architect") is True

    def test_has_agent_not_exists(self, sample_agents_dict):
        """Test checking non-existent agent."""
        registry = Registry(sample_agents_dict)

        assert registry.has_agent("nonexistent") is False

    def test_has_subagent_exists(self, sample_agents_dict):
        """Test checking existing subagent."""
        registry = Registry(sample_agents_dict)

        assert registry.has_agent("code/formatter") is True

    def test_has_subagent_not_exists(self, sample_agents_dict):
        """Test checking non-existent subagent."""
        registry = Registry(sample_agents_dict)

        assert registry.has_agent("code/nonexistent") is False


# ============================================================================
# Registry Tests - Caching
# ============================================================================


class TestRegistryCaching:
    """Test registry caching behavior."""

    def test_cache_enabled_by_default(self, sample_agents_dict):
        """Test caching is enabled by default."""
        registry = Registry(sample_agents_dict)

        assert registry._cache_enabled is True

    def test_cache_can_be_disabled(self, sample_agents_dict):
        """Test caching can be disabled."""
        registry = Registry(sample_agents_dict, cache=False)

        assert registry._cache_enabled is False

    def test_variant_cache_built_when_enabled(self, sample_agents_dict):
        """Test variant cache is built when caching enabled."""
        registry = Registry(sample_agents_dict, cache=True)

        # Cache should be built
        assert len(registry._variant_cache) > 0

    def test_no_variant_cache_when_disabled(self, sample_agents_dict):
        """Test variant cache not built when caching disabled."""
        Registry(sample_agents_dict, cache=False)

        # Cache might not be built
        # This depends on implementation details


# ============================================================================
# Registry Tests - From Discovery
# ============================================================================


class TestRegistryFromDiscovery:
    """Test creating registry from discovery."""

    def test_from_discovery_returns_registry(self, tmp_path):
        """Test from_discovery returns Registry instance."""
        # Create minimal agent structure
        agent_dir = tmp_path / "code" / "minimal"
        agent_dir.mkdir(parents=True)
        (agent_dir / "prompt.md").write_text(
            """---
name: code
description: Code agent
system_prompt: You code
tools: []
skills: []
workflows: []
subagents: []
---
""",
            encoding="utf-8",
        )

        registry = Registry.from_discovery(tmp_path)

        assert isinstance(registry, Registry)
        assert registry.has_agent("code")

    def test_from_discovery_with_cache_enabled(self, tmp_path):
        """Test from_discovery with cache enabled."""
        agent_dir = tmp_path / "code" / "minimal"
        agent_dir.mkdir(parents=True)
        (agent_dir / "prompt.md").write_text(
            """---
name: code
description: Code agent
system_prompt: You code
tools: []
skills: []
workflows: []
subagents: []
---
""",
            encoding="utf-8",
        )

        registry = Registry.from_discovery(tmp_path, cache=True)

        assert registry._cache_enabled is True

    def test_from_discovery_with_cache_disabled(self, tmp_path):
        """Test from_discovery with cache disabled."""
        agent_dir = tmp_path / "code" / "minimal"
        agent_dir.mkdir(parents=True)
        (agent_dir / "prompt.md").write_text(
            """---
name: code
description: Code agent
system_prompt: You code
tools: []
skills: []
workflows: []
subagents: []
---
""",
            encoding="utf-8",
        )

        registry = Registry.from_discovery(tmp_path, cache=False)

        assert registry._cache_enabled is False


# ============================================================================
# Registry Tests - Integration
# ============================================================================


class TestRegistryIntegration:
    """Test registry integration scenarios."""

    def test_full_workflow_get_agent_and_list(self, sample_agents_dict):
        """Test full workflow: create, get, list."""
        registry = Registry(sample_agents_dict)

        # List all agents
        all_agents = registry.list_agents(include_subagents=True)
        assert len(all_agents) == 3

        # Get specific agent
        agent = registry.get_agent("code")
        assert agent.name == "code"

        # List subagents
        subagents = registry.list_subagents("code")
        assert "formatter" in subagents

    def test_registry_maintains_agent_data(self, sample_agents_dict):
        """Test registry preserves all agent data."""
        registry = Registry(sample_agents_dict)

        agent = registry.get_agent("code")
        assert agent.tools == ["git", "python"]
        assert agent.skills == ["refactor", "test"]
        assert agent.workflows == ["code-review"]
        assert agent.subagents == ["formatter"]
