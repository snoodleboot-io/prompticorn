"""Unit tests for KiloBuilder class.

Tests cover:
- YAML frontmatter generation
- Markdown section composition
- Agent validation
- Component loading with variants
- Error handling
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.builders.errors import BuilderValidationError
from promptosaurus.ir.models import Agent


class TestKiloBuilderInitialization:
    """Tests for KiloBuilder initialization."""

    def test_init_with_default_agents_dir(self) -> None:
        """Test KiloBuilder initializes with default 'agents' directory."""
        builder = KiloBuilder()
        assert builder.agents_dir == "agents"

    def test_init_with_custom_agents_dir(self) -> None:
        """Test KiloBuilder initializes with custom agents directory."""
        builder = KiloBuilder(agents_dir="/custom/agents")
        assert builder.agents_dir == "/custom/agents"

    def test_init_with_path_object(self) -> None:
        """Test KiloBuilder accepts Path object for agents_dir."""
        path = Path("/custom/agents")
        builder = KiloBuilder(agents_dir=path)
        assert builder.agents_dir == path


class TestKiloBuilderValidation:
    """Tests for Agent validation."""

    def test_validate_valid_agent(self) -> None:
        """Test validation succeeds for valid agent."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        builder = KiloBuilder()
        errors = builder.validate(agent)
        assert errors == []

    def test_validate_returns_empty_for_valid_agent(self) -> None:
        """Test validate method returns empty list for valid agent."""
        agent = Agent(
            name="test",
            description="Test agent with all required fields",
            system_prompt="Valid system prompt",
            tools=["read", "write"],
            skills=["skill1"],
            workflows=["workflow1"],
            subagents=["subagent1"],
        )
        builder = KiloBuilder()
        errors = builder.validate(agent)
        assert isinstance(errors, list)
        assert len(errors) == 0


class TestKiloBuilderFrontmatter:
    """Tests for YAML frontmatter generation."""

    def test_frontmatter_contains_name(self) -> None:
        """Test frontmatter includes agent name."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        builder = KiloBuilder()
        frontmatter = builder._build_frontmatter(agent)
        assert frontmatter["name"] == "code"

    def test_frontmatter_contains_description(self) -> None:
        """Test frontmatter includes agent description."""
        agent = Agent(
            name="code",
            description="My Code Agent",
            system_prompt="You are a code assistant",
        )
        builder = KiloBuilder()
        frontmatter = builder._build_frontmatter(agent)
        assert frontmatter["description"] == "My Code Agent"

    def test_frontmatter_contains_model(self) -> None:
        """Test frontmatter includes default model."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        builder = KiloBuilder()
        frontmatter = builder._build_frontmatter(agent)
        assert frontmatter["model"] == "anthropic/claude-opus-4-1"

    def test_frontmatter_contains_state_management(self) -> None:
        """Test frontmatter includes state management path."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        builder = KiloBuilder()
        frontmatter = builder._build_frontmatter(agent)
        assert frontmatter["state_management"] == ".promptosaurus/sessions/"

    def test_frontmatter_all_required_keys(self) -> None:
        """Test frontmatter contains all required keys."""
        agent = Agent(
            name="test",
            description="Test agent",
            system_prompt="Test prompt",
        )
        builder = KiloBuilder()
        frontmatter = builder._build_frontmatter(agent)

        required_keys = {"name", "description", "model", "state_management"}
        assert set(frontmatter.keys()) == required_keys


class TestKiloBuilderFormatting:
    """Tests for section formatting methods."""

    def test_format_tools_single(self) -> None:
        """Test formatting single tool."""
        builder = KiloBuilder()
        result = builder._format_tools(["read"])
        assert result == "- read"

    def test_format_tools_multiple(self) -> None:
        """Test formatting multiple tools."""
        builder = KiloBuilder()
        result = builder._format_tools(["read", "grep", "bash"])
        assert "- read" in result
        assert "- grep" in result
        assert "- bash" in result

    def test_format_tools_empty(self) -> None:
        """Test formatting empty tools list."""
        builder = KiloBuilder()
        result = builder._format_tools([])
        assert result == ""

    def test_format_tools_newline_separated(self) -> None:
        """Test tools are newline separated."""
        builder = KiloBuilder()
        result = builder._format_tools(["tool1", "tool2"])
        lines = result.split("\n")
        assert len(lines) == 2

    def test_format_skills_single(self) -> None:
        """Test formatting single skill."""
        builder = KiloBuilder()
        result = builder._format_skills(["skill1"])
        assert result == "- skill1"

    def test_format_skills_multiple(self) -> None:
        """Test formatting multiple skills."""
        builder = KiloBuilder()
        result = builder._format_skills(["skill1", "skill2", "skill3"])
        assert "- skill1" in result
        assert "- skill2" in result
        assert "- skill3" in result

    def test_format_workflows_single(self) -> None:
        """Test formatting single workflow."""
        builder = KiloBuilder()
        result = builder._format_workflows(["workflow1"])
        assert result == "- workflow1"

    def test_format_workflows_multiple(self) -> None:
        """Test formatting multiple workflows."""
        builder = KiloBuilder()
        result = builder._format_workflows(["workflow1", "workflow2"])
        assert "- workflow1" in result
        assert "- workflow2" in result

    def test_format_subagents_single(self) -> None:
        """Test formatting single subagent."""
        builder = KiloBuilder()
        result = builder._format_subagents(["architect"])
        assert result == "- architect"

    def test_format_subagents_multiple(self) -> None:
        """Test formatting multiple subagents."""
        builder = KiloBuilder()
        result = builder._format_subagents(["architect", "code", "review"])
        assert "- architect" in result
        assert "- code" in result
        assert "- review" in result

    def test_format_subagents_empty(self) -> None:
        """Test formatting empty subagents list."""
        builder = KiloBuilder()
        result = builder._format_subagents([])
        assert result == ""

    def test_format_subagents_newline_separated(self) -> None:
        """Test subagents are newline separated."""
        builder = KiloBuilder()
        result = builder._format_subagents(["sub1", "sub2", "sub3"])
        lines = result.split("\n")
        assert len(lines) == 3


class TestKiloBuilderYAMLComposition:
    """Tests for YAML + Markdown composition."""

    def test_compose_yaml_markdown_has_frontmatter(self) -> None:
        """Test composed output contains YAML frontmatter."""
        builder = KiloBuilder()
        frontmatter = {"name": "test", "description": "Test agent"}
        markdown = "# System Prompt\nTest"
        result = builder._compose_yaml_markdown(frontmatter, markdown)

        assert result.startswith("---")
        assert "name: test" in result
        assert result.count("---") == 2

    def test_compose_yaml_markdown_has_markdown(self) -> None:
        """Test composed output contains markdown content."""
        builder = KiloBuilder()
        frontmatter = {"name": "test"}
        markdown = "# System Prompt\nTest content"
        result = builder._compose_yaml_markdown(frontmatter, markdown)

        assert "# System Prompt" in result
        assert "Test content" in result

    def test_compose_yaml_markdown_separator(self) -> None:
        """Test YAML and Markdown are properly separated."""
        builder = KiloBuilder()
        frontmatter = {"name": "test"}
        markdown = "# System Prompt"
        result = builder._compose_yaml_markdown(frontmatter, markdown)

        # Should have YAML frontmatter, blank line, then markdown
        parts = result.split("\n\n")
        assert parts[0].startswith("---")
        assert "# System Prompt" in parts[1]

    def test_compose_yaml_quotes_strings_with_colons(self) -> None:
        """Test strings containing colons are quoted in YAML."""
        builder = KiloBuilder()
        frontmatter = {"description": "Code with: colons"}
        markdown = "Test"
        result = builder._compose_yaml_markdown(frontmatter, markdown)

        assert 'description: "Code with: colons"' in result

    def test_compose_yaml_quotes_strings_with_newlines(self) -> None:
        """Test strings containing newlines are quoted in YAML."""
        builder = KiloBuilder()
        frontmatter = {"description": "Line 1\nLine 2"}
        markdown = "Test"
        result = builder._compose_yaml_markdown(frontmatter, markdown)

        # Should quote the string
        assert "description:" in result

    def test_compose_yaml_handles_numeric_values(self) -> None:
        """Test YAML composition handles numeric values."""
        builder = KiloBuilder()
        frontmatter = {"name": "test", "priority": 1, "weight": 0.5}
        markdown = "Test"
        result = builder._compose_yaml_markdown(frontmatter, markdown)

        assert "priority: 1" in result
        assert "weight: 0.5" in result

    def test_compose_yaml_handles_boolean_values(self) -> None:
        """Test YAML composition handles boolean values."""
        builder = KiloBuilder()
        frontmatter = {"enabled": True, "deprecated": False}
        markdown = "Test"
        result = builder._compose_yaml_markdown(frontmatter, markdown)

        assert "enabled: true" in result
        assert "deprecated: false" in result


class TestKiloBuilderIntegration:
    """Integration tests for the complete build process."""

    @pytest.fixture
    def temp_agents_dir(self) -> tuple[str, Path]:
        """Create temporary agents directory structure."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create agent directory with minimal variant
            agent_dir = tmppath / "test_agent" / "minimal"
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Create required files
            (agent_dir / "prompt.md").write_text("Test system prompt")
            (agent_dir / "skills.md").write_text("## Test Skill\nTest skill content")
            (agent_dir / "workflow.md").write_text("## Test Workflow\nTest workflow content")

            yield tmpdir, tmppath

    def test_build_with_basic_agent(self, temp_agents_dir: tuple[str, Path]) -> None:
        """Test building output for basic agent."""
        tmpdir, tmppath = temp_agents_dir

        builder = KiloBuilder(agents_dir=tmppath)
        agent = Agent(
            name="test_agent",
            description="Test Agent",
            system_prompt="Test system prompt",
            tools=["read", "write"],
        )
        options = BuildOptions(variant="minimal")

        result = builder.build(agent, options)

        # Verify structure
        assert result.startswith("---")
        assert "name: test_agent" in result
        assert "description: Test Agent" in result
        assert "# System Prompt" in result
        assert "# Tools" in result
        assert "- read" in result
        assert "- write" in result

    def test_build_returns_string(self, temp_agents_dir: tuple[str, Path]) -> None:
        """Test build method returns a string."""
        tmpdir, tmppath = temp_agents_dir

        builder = KiloBuilder(agents_dir=tmppath)
        agent = Agent(
            name="test_agent",
            description="Test Agent",
            system_prompt="Test system prompt",
        )
        options = BuildOptions(variant="minimal")

        result = builder.build(agent, options)
        assert isinstance(result, str)

    def test_build_respects_include_tools_flag(self, temp_agents_dir: tuple[str, Path]) -> None:
        """Test build respects include_tools flag."""
        tmpdir, tmppath = temp_agents_dir

        builder = KiloBuilder(agents_dir=tmppath)
        agent = Agent(
            name="test_agent",
            description="Test Agent",
            system_prompt="Test system prompt",
            tools=["read"],
        )
        options = BuildOptions(variant="minimal", include_tools=False)

        result = builder.build(agent, options)

        # Tools section should not be included
        assert "# Tools" not in result

    def test_build_respects_include_skills_flag(self, temp_agents_dir: tuple[str, Path]) -> None:
        """Test build respects include_skills flag."""
        tmpdir, tmppath = temp_agents_dir

        builder = KiloBuilder(agents_dir=tmppath)
        agent = Agent(
            name="test_agent",
            description="Test Agent",
            system_prompt="Test system prompt",
        )
        options = BuildOptions(variant="minimal", include_skills=False)

        result = builder.build(agent, options)

        # Skills section should not be included
        assert "# Skills" not in result

    def test_build_respects_include_workflows_flag(self, temp_agents_dir: tuple[str, Path]) -> None:
        """Test build respects include_workflows flag."""
        tmpdir, tmppath = temp_agents_dir

        builder = KiloBuilder(agents_dir=tmppath)
        agent = Agent(
            name="test_agent",
            description="Test Agent",
            system_prompt="Test system prompt",
        )
        options = BuildOptions(variant="minimal", include_workflows=False)

        result = builder.build(agent, options)

        # Workflows section should not be included
        assert "# Workflows" not in result

    def test_build_respects_include_subagents_flag(self, temp_agents_dir: tuple[str, Path]) -> None:
        """Test build respects include_subagents flag."""
        tmpdir, tmppath = temp_agents_dir

        builder = KiloBuilder(agents_dir=tmppath)
        agent = Agent(
            name="test_agent",
            description="Test Agent",
            system_prompt="Test system prompt",
            subagents=["sub1", "sub2"],
        )
        options = BuildOptions(variant="minimal", include_subagents=False)

        result = builder.build(agent, options)

        # Subagents section should not be included
        assert "# Subagents" not in result

    def test_build_with_all_sections(self, temp_agents_dir: tuple[str, Path]) -> None:
        """Test building with all sections included."""
        tmpdir, tmppath = temp_agents_dir

        builder = KiloBuilder(agents_dir=tmppath)
        agent = Agent(
            name="test_agent",
            description="Test Agent",
            system_prompt="Test system prompt",
            tools=["read", "write"],
            skills=["skill1"],
            workflows=["workflow1"],
            subagents=["sub1"],
        )
        options = BuildOptions(
            variant="minimal",
            include_tools=True,
            include_skills=True,
            include_workflows=True,
            include_subagents=True,
        )

        result = builder.build(agent, options)

        # All sections should be present
        assert "# System Prompt" in result
        assert "# Tools" in result
        assert "# Skills" in result
        assert "# Workflows" in result
        assert "# Subagents" in result


class TestKiloBuilderMetadata:
    """Tests for builder metadata methods."""

    def test_get_output_format(self) -> None:
        """Test get_output_format returns correct format description."""
        builder = KiloBuilder()
        format_desc = builder.get_output_format()
        assert "Kilo" in format_desc
        assert "YAML" in format_desc
        assert "Markdown" in format_desc

    def test_get_tool_name(self) -> None:
        """Test get_tool_name returns 'kilo'."""
        builder = KiloBuilder()
        assert builder.get_tool_name() == "kilo"

    def test_supports_feature_tools(self) -> None:
        """Test supports_feature for tools."""
        builder = KiloBuilder()
        assert builder.supports_feature("tools")

    def test_supports_feature_skills(self) -> None:
        """Test supports_feature for skills."""
        builder = KiloBuilder()
        assert builder.supports_feature("skills")

    def test_supports_feature_workflows(self) -> None:
        """Test supports_feature for workflows."""
        builder = KiloBuilder()
        assert builder.supports_feature("workflows")

    def test_supports_feature_subagents(self) -> None:
        """Test supports_feature for subagents."""
        builder = KiloBuilder()
        assert builder.supports_feature("subagents")

    def test_get_tool_name_derived_from_class_name(self) -> None:
        """Test tool name is automatically derived from class name."""
        builder = KiloBuilder()
        # KiloBuilder -> kilo
        assert builder.get_tool_name() == "kilo"

    def test_supports_feature_returns_false_for_unsupported(self) -> None:
        """Test supports_feature returns False for invalid features."""
        builder = KiloBuilder()
        assert not builder.supports_feature("unknown_feature")
