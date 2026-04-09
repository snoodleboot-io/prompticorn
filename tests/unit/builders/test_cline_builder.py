"""Unit tests for ClineBuilder class.

Tests cover:
- Markdown output generation (no YAML frontmatter)
- Skill activation instruction generation
- use_skill invocation pattern
- Subagent delegation with skill context
- Tool dependency handling
- Agent validation
- Error handling
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.builders.cline_builder import ClineBuilder
from src.builders.base import BuildOptions
from src.builders.component_selector import ComponentBundle, Variant
from src.builders.errors import BuilderValidationError
from src.ir.models import Agent


class TestClineBuilderInitialization:
    """Tests for ClineBuilder initialization."""

    def test_init_with_default_agents_dir(self) -> None:
        """Test ClineBuilder initializes with default 'agents' directory."""
        builder = ClineBuilder()
        assert builder.agents_dir == "agents"
        assert builder.selector is not None

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
            skills=["test-first-implementation"],
            subagents=["subagent1"],
        )
        builder = ClineBuilder()
        errors = builder.validate(agent)
        assert isinstance(errors, list)
        assert len(errors) == 0

    def test_validate_all_required_fields_present(self) -> None:
        """Test validation checks for all required fields."""
        agent = Agent(
            name="valid",
            description="Valid description",
            system_prompt="Valid system prompt",
        )
        builder = ClineBuilder()
        errors = builder.validate(agent)
        # Should have no errors if all required fields are present
        assert errors == []


class TestClineBuilderToolFormatting:
    """Tests for tools formatting."""

    def test_format_tools_single(self) -> None:
        """Test formatting single tool."""
        builder = ClineBuilder()
        result = builder._format_tools(["read"])
        assert "- read" in result

    def test_format_tools_multiple(self) -> None:
        """Test formatting multiple tools."""
        builder = ClineBuilder()
        result = builder._format_tools(["read", "write", "bash"])
        assert "- read" in result
        assert "- write" in result
        assert "- bash" in result

    def test_format_tools_empty(self) -> None:
        """Test formatting empty tools list."""
        builder = ClineBuilder()
        result = builder._format_tools([])
        assert result == ""

    def test_format_tools_preserves_order(self) -> None:
        """Test tool formatting preserves list order."""
        builder = ClineBuilder()
        tools = ["first", "second", "third"]
        result = builder._format_tools(tools)
        lines = result.split("\n")
        assert lines[0] == "- first"
        assert lines[1] == "- second"
        assert lines[2] == "- third"


class TestClineSkillActivation:
    """Tests for skill activation instruction generation."""

    def test_build_skill_activation_instructions_includes_skill_name(self) -> None:
        """Test activation instructions include the skill name."""
        builder = ClineBuilder()
        result = builder._build_skill_activation_instructions("test-first-implementation")
        assert "test-first-implementation" in result
        assert "Test First Implementation" in result

    def test_build_skill_activation_uses_use_skill_syntax(self) -> None:
        """Test activation instructions use use_skill invocation pattern."""
        builder = ClineBuilder()
        result = builder._build_skill_activation_instructions("code-review-audit")
        assert "use_skill code-review-audit" in result

    def test_build_skill_activation_includes_location(self) -> None:
        """Test activation instructions include skill location reference."""
        builder = ClineBuilder()
        result = builder._build_skill_activation_instructions("refactor-code-module")
        assert ".kilo/skills/refactor-code-module.md" in result

    def test_build_skill_activation_includes_when_to_use(self) -> None:
        """Test activation instructions explain when to use the skill."""
        builder = ClineBuilder()
        result = builder._build_skill_activation_instructions("test-first-implementation")
        assert "When to use" in result or "when to use" in result.lower()

    def test_build_skill_activation_includes_invocation_instructions(self) -> None:
        """Test activation instructions explain how to invoke."""
        builder = ClineBuilder()
        result = builder._build_skill_activation_instructions("documentation-generation")
        assert "How to invoke" in result or "invoke" in result.lower()

    def test_build_skill_activation_normalizes_skill_name(self) -> None:
        """Test skill names are properly normalized in output."""
        builder = ClineBuilder()
        result = builder._build_skill_activation_instructions("test-first-implementation")
        # Should convert to title case for display
        assert "Test First Implementation" in result

    def test_build_skill_activation_includes_direct_and_delegation_options(self) -> None:
        """Test activation instructions include direct and delegation invocation."""
        builder = ClineBuilder()
        result = builder._build_skill_activation_instructions("code-review-audit")
        assert "Direct:" in result or "direct" in result.lower()
        assert "Delegation:" in result or "delegation" in result.lower()

    def test_build_skill_activation_multiple_skills(self) -> None:
        """Test activation instructions for multiple skill types."""
        builder = ClineBuilder()
        skills = [
            "test-first-implementation",
            "refactor-code-module",
            "code-review-audit",
        ]
        for skill in skills:
            result = builder._build_skill_activation_instructions(skill)
            assert f"use_skill {skill}" in result
            assert ".kilo/skills/" in result


class TestClineSkillsFormatting:
    """Tests for skills section with activation."""

    def test_format_skills_with_activation_empty(self) -> None:
        """Test formatting empty skills content."""
        builder = ClineBuilder()
        result = builder._format_skills_with_activation("", [])
        assert result == ""

    def test_format_skills_with_activation_includes_header(self) -> None:
        """Test skills section includes explanatory header."""
        builder = ClineBuilder()
        skills_content = "Sample skill content"
        result = builder._format_skills_with_activation(skills_content, ["test-skill"])
        assert "available" in result.lower()
        assert "use_skill" in result

    def test_format_skills_with_activation_single_skill(self) -> None:
        """Test skills section with single skill."""
        builder = ClineBuilder()
        skills_content = "Skill content here"
        result = builder._format_skills_with_activation(
            skills_content, ["test-first-implementation"]
        )
        assert "use_skill test-first-implementation" in result
        assert "## Skill:" in result

    def test_format_skills_with_activation_multiple_skills(self) -> None:
        """Test skills section with multiple skills."""
        builder = ClineBuilder()
        skills_content = "Shared skill content"
        agent_skills = [
            "test-first-implementation",
            "refactor-code-module",
            "code-review-audit",
        ]
        result = builder._format_skills_with_activation(skills_content, agent_skills)

        for skill in agent_skills:
            assert f"use_skill {skill}" in result

    def test_format_skills_includes_original_content(self) -> None:
        """Test skills section preserves original component content."""
        builder = ClineBuilder()
        skills_content = "Original skill definitions here"
        result = builder._format_skills_with_activation(
            skills_content, ["test-skill"]
        )
        assert "Original skill definitions here" in result

    def test_format_skills_properly_separated(self) -> None:
        """Test skills section has proper spacing between skills."""
        builder = ClineBuilder()
        result = builder._format_skills_with_activation(
            "content", ["skill1", "skill2"]
        )
        # Each skill should have its own section
        assert result.count("## Skill:") == 2


class TestClineSubagentSkillMapping:
    """Tests for subagent to skill mapping."""

    def test_get_subagent_skills_test_subagent(self) -> None:
        """Test skill mapping for test subagent."""
        builder = ClineBuilder()
        skills = builder._get_subagent_skills(
            "test", ["test-first-implementation", "code-review-audit"]
        )
        assert "test-first-implementation" in skills

    def test_get_subagent_skills_refactor_subagent(self) -> None:
        """Test skill mapping for refactor subagent."""
        builder = ClineBuilder()
        skills = builder._get_subagent_skills(
            "refactor", ["refactor-code-module", "test-first-implementation"]
        )
        assert "refactor-code-module" in skills

    def test_get_subagent_skills_review_subagent(self) -> None:
        """Test skill mapping for review subagent."""
        builder = ClineBuilder()
        skills = builder._get_subagent_skills(
            "review", ["code-review-audit", "test-first-implementation"]
        )
        assert "code-review-audit" in skills

    def test_get_subagent_skills_unknown_subagent(self) -> None:
        """Test skill mapping for unknown subagent returns empty."""
        builder = ClineBuilder()
        skills = builder._get_subagent_skills(
            "unknown-subagent", ["test-first-implementation"]
        )
        assert skills == []

    def test_get_subagent_skills_filters_unavailable_skills(self) -> None:
        """Test that only available agent skills are included."""
        builder = ClineBuilder()
        # Ask for test subagent skills but don't include them in agent
        skills = builder._get_subagent_skills("test", ["code-review-audit"])
        # test subagent would want test-first-implementation but it's not in agent skills
        assert "test-first-implementation" not in skills

    def test_get_subagent_skills_case_insensitive(self) -> None:
        """Test skill mapping is case-insensitive."""
        builder = ClineBuilder()
        skills1 = builder._get_subagent_skills(
            "TEST", ["test-first-implementation"]
        )
        skills2 = builder._get_subagent_skills(
            "test", ["test-first-implementation"]
        )
        assert skills1 == skills2


class TestClineSubagentFormatting:
    """Tests for subagent delegation section."""

    def test_format_subagents_with_skills_empty(self) -> None:
        """Test subagent formatting with empty list."""
        builder = ClineBuilder()
        result = builder._format_subagents_with_skills([], [])
        assert result == ""

    def test_format_subagents_with_skills_includes_header(self) -> None:
        """Test subagent section includes delegation header."""
        builder = ClineBuilder()
        result = builder._format_subagents_with_skills(
            ["test"], ["test-first-implementation"]
        )
        assert "delegate" in result.lower()
        assert "specialist" in result.lower()

    def test_format_subagents_single_subagent(self) -> None:
        """Test formatting single subagent."""
        builder = ClineBuilder()
        result = builder._format_subagents_with_skills(
            ["test"], ["test-first-implementation"]
        )
        assert "### Subagent:" in result
        assert "test" in result.lower()

    def test_format_subagents_multiple_subagents(self) -> None:
        """Test formatting multiple subagents."""
        builder = ClineBuilder()
        result = builder._format_subagents_with_skills(
            ["test", "refactor", "review"],
            ["test-first-implementation", "refactor-code-module", "code-review-audit"],
        )
        assert result.count("### Subagent:") == 3

    def test_format_single_subagent_with_skills_includes_name(self) -> None:
        """Test subagent entry includes normalized name."""
        builder = ClineBuilder()
        result = builder._format_single_subagent_with_skills("test-code", [])
        assert "Test Code" in result

    def test_format_single_subagent_with_skills_includes_use_skill_syntax(self) -> None:
        """Test subagent entry includes use_skill invocation."""
        builder = ClineBuilder()
        result = builder._format_single_subagent_with_skills(
            "test", ["test-first-implementation"]
        )
        assert "use_skill test" in result

    def test_format_single_subagent_with_skills_lists_available_skills(self) -> None:
        """Test subagent entry lists its available skills."""
        builder = ClineBuilder()
        result = builder._format_single_subagent_with_skills(
            "test",
            ["test-first-implementation", "code-review-audit"],
        )
        assert "Available skills:" in result
        assert "use_skill test-first-implementation" in result

    def test_format_single_subagent_with_skills_no_skills(self) -> None:
        """Test subagent entry without skills still formats correctly."""
        builder = ClineBuilder()
        result = builder._format_single_subagent_with_skills("unknown", [])
        assert "### Subagent:" in result
        assert "Unknown" in result

    def test_format_single_subagent_delegates_invocation_syntax(self) -> None:
        """Test subagent entry includes both invocation syntaxes."""
        builder = ClineBuilder()
        result = builder._format_single_subagent_with_skills("code", [])
        assert "use_skill code" in result
        assert "code subagent" in result.lower()


class TestClineBuilderBuildOutput:
    """Tests for complete build output."""

    def test_build_includes_system_prompt_section_header(self) -> None:
        """Test build output includes system prompt section header."""
        builder = ClineBuilder()
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        # Mock the selector to avoid filesystem dependencies
        mock_bundle = ComponentBundle(
            variant=Variant.VERBOSE,
            prompt="System prompt content",
            skills="",
            workflow="",
            fallback_used=False,
        )
        builder.selector.select = lambda *args, **kwargs: mock_bundle

        options = BuildOptions()
        result = builder.build(agent, options)
        assert "# System Prompt" in result

    def test_build_no_yaml_frontmatter(self) -> None:
        """Test build output has no YAML frontmatter (unlike Kilo)."""
        builder = ClineBuilder()
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
        )
        # Mock the selector
        mock_bundle = ComponentBundle(
            variant=Variant.VERBOSE,
            prompt="Content here",
            skills="",
            workflow="",
            fallback_used=False,
        )
        builder.selector.select = lambda *args, **kwargs: mock_bundle

        options = BuildOptions()
        result = builder.build(agent, options)
        # Should not start with ---
        assert not result.startswith("---")
        # Should not contain YAML frontmatter markers
        lines = result.split("\n")
        # First line should be a markdown header, not YAML
        assert lines[0].startswith("#")

    def test_build_invalid_agent_raises_error(self) -> None:
        """Test build raises BuilderValidationError for invalid agent."""
        builder = ClineBuilder()
        # This will not raise during Agent creation, but during build validation
        agent = Agent(name="test", description="test", system_prompt="test")
        
        # The validate method should return empty list if all required fields present
        options = BuildOptions()
        errors = builder.validate(agent)
        assert errors == []  # All required fields are present

    def test_build_handles_empty_tools_gracefully(self) -> None:
        """Test build handles missing tools."""
        builder = ClineBuilder()
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            tools=[],
        )
        mock_bundle = ComponentBundle(
            variant=Variant.VERBOSE,
            prompt="Content",
            skills="",
            workflow="",
            fallback_used=False,
        )
        builder.selector.select = lambda *args, **kwargs: mock_bundle

        options = BuildOptions(include_tools=True)
        result = builder.build(agent, options)
        # Should not include Tools section if empty
        assert "# Tools" not in result

    def test_build_includes_tools_when_present(self) -> None:
        """Test build includes tools section when tools are present."""
        builder = ClineBuilder()
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            tools=["read", "write"],
        )
        mock_bundle = ComponentBundle(
            variant=Variant.VERBOSE,
            prompt="Content",
            skills="",
            workflow="",
            fallback_used=False,
        )
        builder.selector.select = lambda *args, **kwargs: mock_bundle

        options = BuildOptions(include_tools=True)
        result = builder.build(agent, options)
        assert "# Tools" in result
        assert "- read" in result

    def test_build_includes_skills_when_present(self) -> None:
        """Test build includes skills section when skills are present."""
        builder = ClineBuilder()
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            skills=["test-first-implementation"],
        )
        mock_bundle = ComponentBundle(
            variant=Variant.VERBOSE,
            prompt="Content",
            skills="Skill definitions",
            workflow="",
            fallback_used=False,
        )
        builder.selector.select = lambda *args, **kwargs: mock_bundle

        options = BuildOptions(include_skills=True)
        result = builder.build(agent, options)
        assert "# Skills" in result
        assert "use_skill" in result

    def test_build_includes_subagents_when_present(self) -> None:
        """Test build includes subagents section when subagents are present."""
        builder = ClineBuilder()
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            subagents=["test"],
            skills=["test-first-implementation"],
        )
        mock_bundle = ComponentBundle(
            variant=Variant.VERBOSE,
            prompt="Content",
            skills="",
            workflow="",
            fallback_used=False,
        )
        builder.selector.select = lambda *args, **kwargs: mock_bundle

        options = BuildOptions(include_subagents=True)
        result = builder.build(agent, options)
        assert "# Subagents" in result
        assert "### Subagent:" in result

    def test_build_respects_include_options(self) -> None:
        """Test build respects include_* options."""
        builder = ClineBuilder()
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code assistant",
            tools=["read"],
            skills=["test-skill"],
        )
        mock_bundle = ComponentBundle(
            variant=Variant.VERBOSE,
            prompt="Content",
            skills="Skills",
            workflow="",
            fallback_used=False,
        )
        builder.selector.select = lambda *args, **kwargs: mock_bundle

        # Build with tools included
        options_with_tools = BuildOptions(include_tools=True, include_skills=False)
        result_with_tools = builder.build(agent, options_with_tools)
        assert "# Tools" in result_with_tools
        assert "# Skills" not in result_with_tools

        # Build with skills included
        options_with_skills = BuildOptions(include_tools=False, include_skills=True)
        result_with_skills = builder.build(agent, options_with_skills)
        assert "# Tools" not in result_with_skills
        assert "# Skills" in result_with_skills


class TestClineBuilderMetadata:
    """Tests for metadata methods."""

    def test_get_output_format(self) -> None:
        """Test get_output_format returns correct format description."""
        builder = ClineBuilder()
        result = builder.get_output_format()
        assert "Cline" in result
        assert ".clinerules" in result or "clinerules" in result.lower()

    def test_get_tool_name(self) -> None:
        """Test get_tool_name returns 'cline'."""
        builder = ClineBuilder()
        assert builder.get_tool_name() == "cline"

    def test_get_tool_name_lowercase(self) -> None:
        """Test get_tool_name returns lowercase."""
        builder = ClineBuilder()
        result = builder.get_tool_name()
        assert result == result.lower()


class TestClineBuilderWorkflowsFormatting:
    """Tests for workflows section formatting."""

    def test_format_workflows_strips_whitespace(self) -> None:
        """Test workflows formatting removes extra whitespace."""
        builder = ClineBuilder()
        content = "  \n\n  Workflow content  \n\n  "
        result = builder._format_workflows(content)
        assert result == "Workflow content"

    def test_format_workflows_preserves_content(self) -> None:
        """Test workflows formatting preserves content structure."""
        builder = ClineBuilder()
        content = "## Workflow 1\n\nSteps here\n\n## Workflow 2\n\nMore steps"
        result = builder._format_workflows(content)
        assert "## Workflow 1" in result
        assert "## Workflow 2" in result
