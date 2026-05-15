"""Unit tests for ClaudeBuilder class.

Tests cover:
- Markdown file generation
- Agent file rendering
- Subagent file rendering
- Workflow file rendering
- Real workflow/subagent content loading
- Agent validation
- File path generation
"""

from pathlib import Path

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.ir.models import Agent


class TestClaudeBuilderInitialization:
    """Tests for ClaudeBuilder initialization."""

    def test_init_with_default_agents_dir(self) -> None:
        """Test ClaudeBuilder initializes with default 'agents' directory."""
        builder = ClaudeBuilder()
        assert builder.agents_dir == "agents"

    def test_init_with_custom_agents_dir(self) -> None:
        """Test ClaudeBuilder initializes with custom agents directory."""
        builder = ClaudeBuilder(agents_dir="/custom/agents")
        assert builder.agents_dir == "/custom/agents"

    def test_init_with_path_object(self) -> None:
        """Test ClaudeBuilder accepts Path object for agents_dir."""
        path = Path("/custom/agents")
        builder = ClaudeBuilder(agents_dir=path)
        assert builder.agents_dir == path


class TestClaudeBuilderBuild:
    """Tests for ClaudeBuilder build method."""

    def test_build_returns_dict_of_markdown_files(self) -> None:
        """Test build returns dictionary mapping file paths to Markdown content."""
        builder = ClaudeBuilder()
        agent = Agent(
            name="code",
            description="Write and refactor code",
            system_prompt="You are a senior software engineer.",
            tools=["read", "write"],
            skills=["feature-planning"],
            workflows=["feature"],
            subagents=[],
        )
        options = BuildOptions(
            include_tools=False,
            include_skills=True,
            include_workflows=True,
            include_subagents=True,
            variant="minimal",
        )

        output = builder.build(agent, options)

        # Should return dict[str, str]
        assert isinstance(output, dict)
        assert all(isinstance(k, str) and isinstance(v, str) for k, v in output.items())

    def test_build_creates_agent_file(self) -> None:
        """Test build creates agent file with correct path."""
        builder = ClaudeBuilder()
        agent = Agent(
            name="code",
            description="Write and refactor code",
            system_prompt="You are a senior software engineer.",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )
        options = BuildOptions(
            include_tools=False,
            include_skills=False,
            include_workflows=False,
            include_subagents=False,
            variant="minimal",
        )

        output = builder.build(agent, options)

        # Should have agent file
        assert ".claude/agents/code-agent.md" in output
        agent_content = output[".claude/agents/code-agent.md"]
        assert "# Code" in agent_content
        assert "You are a senior software engineer." in agent_content

    def test_build_creates_workflow_files(self) -> None:
        """Test build creates workflow files when workflows are present."""
        builder = ClaudeBuilder()
        agent = Agent(
            name="code",
            description="Write and refactor code",
            system_prompt="You are a senior software engineer.",
            tools=[],
            skills=[],
            workflows=["feature", "refactor"],
            subagents=[],
        )
        options = BuildOptions(
            include_tools=False,
            include_skills=False,
            include_workflows=True,
            include_subagents=False,
            variant="minimal",
        )

        output = builder.build(agent, options)

        # Should have workflow files
        assert ".claude/workflows/feature.md" in output
        assert ".claude/workflows/refactor.md" in output

    def test_build_creates_subagent_files(self) -> None:
        """Test build creates subagent files when subagents are present."""
        builder = ClaudeBuilder()
        agent = Agent(
            name="debug",
            description="Diagnose and fix bugs",
            system_prompt="You are a debugging expert.",
            tools=[],
            skills=[],
            workflows=[],
            subagents=["debug/rubber-duck", "debug/root-cause"],
        )
        options = BuildOptions(
            include_tools=False,
            include_skills=False,
            include_workflows=False,
            include_subagents=True,
            variant="minimal",
        )

        output = builder.build(agent, options)

        # Should have subagent files
        # Check that subagent files were created (exact names depend on naming logic)
        assert any("rubber-duck" in k for k in output.keys())
        assert any("root-cause" in k for k in output.keys())

    def test_build_includes_skills_in_agent_file(self) -> None:
        """Test build includes skills section in agent file."""
        builder = ClaudeBuilder()
        agent = Agent(
            name="code",
            description="Write and refactor code",
            system_prompt="You are a senior software engineer.",
            tools=[],
            skills=["feature-planning", "post-implementation-checklist"],
            workflows=[],
            subagents=[],
        )
        options = BuildOptions(
            include_tools=False,
            include_skills=True,
            include_workflows=False,
            include_subagents=False,
            variant="minimal",
        )

        output = builder.build(agent, options)

        agent_content = output[".claude/agents/code-agent.md"]
        # Should mention skills
        assert "Skills" in agent_content or "skills" in agent_content.lower()


class TestClaudeBuilderValidation:
    """Tests for ClaudeBuilder validation."""

    def test_validate_accepts_valid_agent(self) -> None:
        """Test validate returns empty list for valid agent."""
        builder = ClaudeBuilder()
        agent = Agent(
            name="code",
            description="Write and refactor code",
            system_prompt="You are a senior software engineer.",
            tools=[],
            skills=[],
            workflows=[],
            subagents=[],
        )

        errors = builder.validate(agent)
        assert errors == []


class TestClaudeBuilderOutputFormat:
    """Tests for ClaudeBuilder output format."""

    def test_get_output_format(self) -> None:
        """Test get_output_format returns correct description."""
        builder = ClaudeBuilder()
        assert "Markdown" in builder.get_output_format()

    def test_get_tool_name(self) -> None:
        """Test get_tool_name returns 'claude'."""
        builder = ClaudeBuilder()
        assert builder.get_tool_name() == "claude"
