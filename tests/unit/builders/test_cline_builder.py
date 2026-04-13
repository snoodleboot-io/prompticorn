"""Unit tests for ClineBuilder class.

Tests cover:
- Markdown header generation
- System prompt as prose formatting
- Tools section generation
- Skills section with use_skill invocation pattern
- Workflows section generation
- Subagents section generation
- Agent validation
- Component loading with variants
- Error handling
- Output format verification
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from promptosaurus.builders.base import BuildOptions
from promptosaurus.builders.cline_builder import ClineBuilder
from promptosaurus.ir.models import Agent


class TestClineBuilderInitialization:
    """Tests for ClineBuilder initialization."""

    def test_init_with_default_agents_dir(self) -> None:
        """Test ClineBuilder initializes with default 'agents' directory."""
        builder = ClineBuilder()
        assert builder.agents_dir == "agents"

    def test_init_with_custom_agents_dir(self) -> None:
        """Test ClineBuilder initializes with custom agents directory."""
        builder = ClineBuilder(agents_dir="/custom/agents")
        assert builder.agents_dir == "/custom/agents"

    def test_init_with_path_object(self) -> None:
        """Test ClineBuilder accepts Path object for agents_dir."""
        path = Path("/custom/agents")
        builder = ClineBuilder(agents_dir=path)
        assert builder.agents_dir == path


class TestClineBuilderValidation:
    """Tests for Agent validation."""

    def test_validate_valid_agent(self) -> None:
        """Test validation succeeds for valid agent."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        builder = ClineBuilder()
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
        builder = ClineBuilder()
        errors = builder.validate(agent)
        assert isinstance(errors, list)
        assert len(errors) == 0


class TestClineBuilderFormatting:
    """Tests for section formatting methods."""

    def test_format_header(self) -> None:
        """Test markdown header generation."""
        builder = ClineBuilder()
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        header = builder._format_header(agent)
        assert header == "# code Rules"

    def test_format_header_with_special_characters(self) -> None:
        """Test header generation with special characters in name."""
        builder = ClineBuilder()
        agent = Agent(
            name="test-agent-name",
            description="Test agent",
            system_prompt="You are a test assistant",
        )
        header = builder._format_header(agent)
        assert header == "# test-agent-name Rules"

    def test_format_system_prompt_prose(self) -> None:
        """Test system prompt formatting as prose."""
        builder = ClineBuilder()
        prompt = "You are an expert code assistant."
        result = builder._format_system_prompt_prose(prompt)
        assert result == "You are an expert code assistant."

    def test_format_system_prompt_prose_strips_whitespace(self) -> None:
        """Test system prompt formatting strips leading/trailing whitespace."""
        builder = ClineBuilder()
        prompt = "  \n  You are an expert code assistant.  \n  "
        result = builder._format_system_prompt_prose(prompt)
        assert result == "You are an expert code assistant."

    def test_format_system_prompt_prose_preserves_internal_whitespace(self) -> None:
        """Test system prompt formatting preserves internal content."""
        builder = ClineBuilder()
        prompt = "You are an expert code assistant.\n\nYour responsibilities:\n- Code\n- Tests"
        result = builder._format_system_prompt_prose(prompt)
        assert "Your responsibilities:" in result
        assert "- Code" in result

    def test_format_tools_section_single_tool(self) -> None:
        """Test formatting single tool."""
        builder = ClineBuilder()
        result = builder._format_tools_section(["read"])
        assert "## Tools" in result
        assert "- **read**:" in result

    def test_format_tools_section_multiple_tools(self) -> None:
        """Test formatting multiple tools."""
        builder = ClineBuilder()
        result = builder._format_tools_section(["read", "grep", "bash"])
        assert "## Tools" in result
        assert "- **read**:" in result
        assert "- **grep**:" in result
        assert "- **bash**:" in result

    def test_format_tools_section_empty(self) -> None:
        """Test formatting with empty tools list."""
        builder = ClineBuilder()
        result = builder._format_tools_section([])
        assert "## Tools" in result

    def test_format_skills_section(self) -> None:
        """Test skills section formatting."""
        builder = ClineBuilder()
        skill_names = ["test-implementation", "code-review"]
        result = builder._format_skills_section(skill_names)
        assert "## Skills" in result
        assert "use_skill" in result

    def test_format_skills_section_use_skill_invocation(self) -> None:
        """Test skills section includes use_skill invocation pattern."""
        builder = ClineBuilder()
        skill_names = ["my-skill"]
        result = builder._format_skills_section(skill_names)
        assert "use_skill" in result

    def test_format_skills_section_empty_names(self) -> None:
        """Test skills section with empty skill names."""
        builder = ClineBuilder()
        skill_names = []
        result = builder._format_skills_section(skill_names)
        assert "## Skills" in result

    def test_format_workflows_section(self) -> None:
        """Test workflows section formatting."""
        builder = ClineBuilder()
        workflow_names = ["feature-implementation", "code-review"]
        result = builder._format_workflows_section(workflow_names)
        assert "## Workflows" in result
        assert "feature-implementation" in result
        assert "code-review" in result

    def test_format_workflows_section_single(self) -> None:
        """Test workflows section with single workflow."""
        builder = ClineBuilder()
        workflow_names = ["my"]
        result = builder._format_workflows_section(workflow_names)
        assert result.startswith("## Workflows")
        assert "my" in result

    def test_format_subagents_section_single(self) -> None:
        """Test formatting single subagent."""
        builder = ClineBuilder()
        result = builder._format_subagents_section(["code-test"])
        assert "## Subagents" in result
        assert "code-test" in result
        assert "use_skill" in result

    def test_format_subagents_section_multiple(self) -> None:
        """Test formatting multiple subagents."""
        builder = ClineBuilder()
        result = builder._format_subagents_section(["code-test", "code-review", "code-refactor"])
        assert "## Subagents" in result
        assert "code-test" in result
        assert "code-review" in result
        assert "code-refactor" in result

    def test_format_subagents_section_invocation(self) -> None:
        """Test subagents section includes invocation instructions."""
        builder = ClineBuilder()
        result = builder._format_subagents_section(["test-agent"])
        assert "use_skill" in result

    def test_format_subagents_section_empty(self) -> None:
        """Test formatting with empty subagents list."""
        builder = ClineBuilder()
        result = builder._format_subagents_section([])
        assert "## Subagents" in result


class TestClineBuilderBuild:
    """Tests for full build process."""

    @pytest.fixture
    def temp_agents_dir(self):
        """Create temporary agents directory structure."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create agent directory with minimal variant
            agent_dir = tmppath / "code" / "minimal"
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Create required files
            (agent_dir / "prompt.md").write_text("You are an expert code assistant")
            (agent_dir / "skills.md").write_text("## Test Skill\nTest skill content")
            (agent_dir / "workflow.md").write_text("## Test Workflow\nTest workflow content")

            yield tmpdir, tmppath

    def test_build_returns_string(self, temp_agents_dir) -> None:
        """Test build method returns string."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        assert isinstance(result, str)

    def test_build_includes_header(self, temp_agents_dir) -> None:
        """Test build output includes agent name header."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        assert "# code Rules" in result

    def test_build_includes_system_prompt(self, temp_agents_dir) -> None:
        """Test build output includes system prompt."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are an expert code assistant",
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        assert "You are an expert code assistant" in result

    def test_build_with_tools(self, temp_agents_dir) -> None:
        """Test build includes tools section when requested."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            tools=["read", "write"],
        )
        options = BuildOptions(variant="minimal", include_tools=True)
        result = builder.build(agent, options)
        assert "## Tools" in result
        assert "read" in result
        assert "write" in result

    def test_build_without_tools(self, temp_agents_dir) -> None:
        """Test build excludes tools section when not requested."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            tools=["read", "write"],
        )
        options = BuildOptions(variant="minimal", include_tools=False)
        result = builder.build(agent, options)
        assert "## Tools" not in result

    def test_build_with_subagents(self, temp_agents_dir) -> None:
        """Test build includes subagents section when requested."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            subagents=["code-test"],
        )
        options = BuildOptions(variant="minimal", include_subagents=True)
        result = builder.build(agent, options)
        assert "## Subagents" in result

    def test_build_without_subagents(self, temp_agents_dir) -> None:
        """Test build excludes subagents section when not requested."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            subagents=["code-test"],
        )
        options = BuildOptions(variant="minimal", include_subagents=False)
        result = builder.build(agent, options)
        assert "## Subagents" not in result

    def test_build_minimal_variant(self, temp_agents_dir) -> None:
        """Test build with minimal variant."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_verbose_variant(self, temp_agents_dir) -> None:
        """Test build with verbose variant."""
        tmpdir, tmppath = temp_agents_dir
        # Add verbose variant directory
        verbose_dir = tmppath / "code" / "verbose"
        verbose_dir.mkdir(parents=True, exist_ok=True)
        (verbose_dir / "prompt.md").write_text("You are an expert code assistant")
        (verbose_dir / "skills.md").write_text("## Test Skill\nTest skill content")
        (verbose_dir / "workflow.md").write_text("## Test Workflow\nTest workflow content")

        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        options = BuildOptions(variant="verbose")
        result = builder.build(agent, options)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_build_no_yaml_frontmatter(self, temp_agents_dir) -> None:
        """Test that build output does NOT include YAML frontmatter."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        # Should not start with --- (YAML frontmatter)
        assert not result.strip().startswith("---")

    def test_build_is_pure_markdown(self, temp_agents_dir) -> None:
        """Test that build output is pure markdown."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        # Should start with markdown header
        assert result.strip().startswith("#")
        # Should contain content
        assert len(result) > 0


class TestClineBuilderMetadata:
    """Tests for builder metadata methods."""

    def test_get_output_format(self) -> None:
        """Test get_output_format method."""
        builder = ClineBuilder()
        format_desc = builder.get_output_format()
        assert isinstance(format_desc, str)
        assert "Markdown" in format_desc
        assert "Cline" in format_desc

    def test_get_tool_name(self) -> None:
        """Test get_tool_name method."""
        builder = ClineBuilder()
        tool_name = builder.get_tool_name()
        assert tool_name == "cline"

    def test_supports_features(self) -> None:
        """Test supports_feature method."""
        builder = ClineBuilder()
        assert builder.supports_feature("skills")
        assert builder.supports_feature("workflows")
        assert builder.supports_feature("subagents")
        assert builder.supports_feature("tools")


class TestClineBuilderEdgeCases:
    """Tests for edge cases and error conditions."""

    @pytest.fixture
    def temp_agents_dir(self):
        """Create temporary agents directory structure."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create agent directory with minimal variant
            agent_dir = tmppath / "code" / "minimal"
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Create required files
            (agent_dir / "prompt.md").write_text("You are an expert code assistant")
            (agent_dir / "skills.md").write_text("## Test Skill\nTest skill content")
            (agent_dir / "workflow.md").write_text("## Test Workflow\nTest workflow content")

            yield tmpdir, tmppath

    def test_build_with_empty_tools_list(self, temp_agents_dir) -> None:
        """Test build with empty tools list."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            tools=[],
        )
        options = BuildOptions(variant="minimal", include_tools=True)
        result = builder.build(agent, options)
        # Tools section should not be included if list is empty
        assert "## Tools" not in result

    def test_build_with_empty_subagents_list(self, temp_agents_dir) -> None:
        """Test build with empty subagents list."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            subagents=[],
        )
        options = BuildOptions(variant="minimal", include_subagents=True)
        result = builder.build(agent, options)
        # Subagents section should not be included if list is empty
        assert "## Subagents" not in result

    def test_build_with_special_characters_in_agent_name(self, temp_agents_dir) -> None:
        """Test build with special characters in agent name."""
        tmpdir, tmppath = temp_agents_dir
        # Create directory for agent with special characters
        agent_dir = tmppath / "code-test-agent" / "minimal"
        agent_dir.mkdir(parents=True, exist_ok=True)
        (agent_dir / "prompt.md").write_text("You are a test assistant")
        (agent_dir / "skills.md").write_text("## Test Skill\nTest skill content")
        (agent_dir / "workflow.md").write_text("## Test Workflow\nTest workflow content")

        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code-test-agent",
            description="Code testing agent",
            system_prompt="You are a test assistant",
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        assert "code-test-agent" in result

    def test_build_with_multiline_prompt(self, temp_agents_dir) -> None:
        """Test build with multiline system prompt."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        prompt = """You are an expert code assistant.

Your core responsibilities:
- Implement features
- Write tests
- Review code

You follow core conventions."""
        # The component prompt file contains the multiline prompt
        agent_dir = tmppath / "code" / "minimal"
        (agent_dir / "prompt.md").write_text(prompt)

        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt=prompt,
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        assert "Your core responsibilities:" in result
        assert "Implement features" in result

    def test_build_preserves_markdown_in_prompt(self, temp_agents_dir) -> None:
        """Test build preserves markdown formatting in system prompt."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        prompt = "You are an expert. **Key**: Always read code first."
        # Update the component prompt file to include markdown
        agent_dir = tmppath / "code" / "minimal"
        (agent_dir / "prompt.md").write_text(prompt)

        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt=prompt,
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        assert "**Key**" in result

    def test_skill_name_normalization(self) -> None:
        """Test skill names are normalized for use_skill invocation."""
        builder = ClineBuilder()
        result = builder._format_skills_section(["Test First Implementation", "Code Review"])
        # Should contain normalized versions
        assert "use_skill" in result
        # Either snake_case or hyphenated forms
        assert "test" in result.lower()
        assert "code" in result.lower()

    def test_subagent_name_normalization(self) -> None:
        """Test subagent names are normalized for use_skill invocation."""
        builder = ClineBuilder()
        result = builder._format_subagents_section(["Code Review Audit"])
        assert "Code Review Audit" in result
        assert "use_skill" in result


class TestClineBuilderComparison:
    """Tests comparing Cline format with Kilo format."""

    @pytest.fixture
    def temp_agents_dir(self):
        """Create temporary agents directory structure."""
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create agent directory with minimal variant
            agent_dir = tmppath / "code" / "minimal"
            agent_dir.mkdir(parents=True, exist_ok=True)

            # Create required files
            (agent_dir / "prompt.md").write_text("You are an expert code assistant")
            (agent_dir / "skills.md").write_text("## Test Skill\nTest skill content")
            (agent_dir / "workflow.md").write_text("## Test Workflow\nTest workflow content")

            yield tmpdir, tmppath

    def test_cline_no_yaml_frontmatter_unlike_kilo(self, temp_agents_dir) -> None:
        """Test Cline output has no YAML frontmatter (unlike Kilo)."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        # Cline format is pure markdown, no YAML
        assert not result.startswith("---")

    def test_cline_system_prompt_as_prose(self, temp_agents_dir) -> None:
        """Test Cline system prompt is prose (no separate heading)."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        prompt = "You are an expert code assistant with SOLID expertise."
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt=prompt,
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        # In Cline, prompt is prose (no "# System Prompt" heading)
        assert "# code Rules" in result
        assert "You are an expert" in result

    def test_cline_single_file_output(self, temp_agents_dir) -> None:
        """Test Cline build returns single file content (not dict)."""
        tmpdir, tmppath = temp_agents_dir
        builder = ClineBuilder(agents_dir=tmppath)
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        options = BuildOptions(variant="minimal")
        result = builder.build(agent, options)
        # Should return string, not dict (single .clinerules file)
        assert isinstance(result, str)

    def test_cline_skills_with_use_skill_invocation(self) -> None:
        """Test Cline skills include use_skill invocation pattern."""
        builder = ClineBuilder()
        result = builder._format_skills_section(["test-implementation"])
        assert "use_skill" in result
        # This is Cline-specific pattern
        assert "Invoke by: `use_skill" in result
