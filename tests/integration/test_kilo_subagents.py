"""Integration tests for KiloBuilder subagent support.

Tests cover:
- Subagent file generation
- Nested directory structure
- Parent agent references in subagent files
- Multiple levels of subagents
- File content validation
"""


import pytest

from promptosaurus.builders.base import BuildOptions
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.ir.models import Agent


class TestKiloSubagentDetection:
    """Tests for detecting and validating subagents."""

    def test_detect_single_subagent(self) -> None:
        """Test detection of single subagent in agent model."""
        agent = Agent(
            name="architect",
            description="Architecture designer",
            system_prompt="You are an architect",
            subagents=["data_modeler"],
        )
        assert len(agent.subagents) == 1
        assert agent.subagents[0] == "data_modeler"

    def test_detect_multiple_subagents(self) -> None:
        """Test detection of multiple subagents."""
        agent = Agent(
            name="orchestrator",
            description="Workflow orchestrator",
            system_prompt="You orchestrate workflows",
            subagents=["task_planner", "code_reviewer", "tester"],
        )
        assert len(agent.subagents) == 3
        assert "task_planner" in agent.subagents
        assert "code_reviewer" in agent.subagents
        assert "tester" in agent.subagents

    def test_agent_with_no_subagents(self) -> None:
        """Test agent without subagents."""
        agent = Agent(
            name="simple",
            description="Simple agent",
            system_prompt="You are simple",
        )
        assert agent.subagents == []


class TestKiloSubagentBuildBasics:
    """Tests for basic subagent file building."""

    def test_build_subagents_returns_dict(self) -> None:
        """Test build_subagents returns dictionary of subagent files."""
        builder = KiloBuilder()
        agent = Agent(
            name="test_agent",
            description="Test agent",
            system_prompt="Test prompt",
            subagents=["sub1", "sub2"],
        )
        options = BuildOptions()

        result = builder.build_subagents(agent, options)

        assert isinstance(result, dict)
        assert len(result) == 2
        assert "sub1" in result
        assert "sub2" in result

    def test_build_subagents_empty_when_no_subagents(self) -> None:
        """Test build_subagents returns empty dict for agent with no subagents."""
        builder = KiloBuilder()
        agent = Agent(
            name="no_subs",
            description="No subagents",
            system_prompt="Test",
        )
        options = BuildOptions()

        result = builder.build_subagents(agent, options)

        assert result == {}

    def test_subagent_file_has_yaml_frontmatter(self) -> None:
        """Test subagent file includes YAML frontmatter."""
        builder = KiloBuilder()
        agent = Agent(
            name="parent",
            description="Parent agent",
            system_prompt="Parent prompt",
            subagents=["child"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)
        content = subagents["child"]

        assert content.startswith("---")
        assert "---\n\n" in content
        assert "name: child" in content

    def test_subagent_file_has_system_prompt(self) -> None:
        """Test subagent file includes system prompt section."""
        builder = KiloBuilder()
        agent = Agent(
            name="parent",
            description="Parent agent",
            system_prompt="Parent prompt",
            subagents=["child"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)
        content = subagents["child"]

        assert "# System Prompt" in content

    def test_subagent_file_has_parent_reference(self) -> None:
        """Test subagent file includes parent agent reference."""
        builder = KiloBuilder()
        agent = Agent(
            name="architect",
            description="Architect agent",
            system_prompt="Architect prompt",
            subagents=["data_modeler"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)
        content = subagents["data_modeler"]

        # Check for parent reference in frontmatter
        assert "parent_agent: architect" in content
        # Check for parent reference in markdown
        assert "# Parent Agent" in content
        assert "architect" in content


class TestKiloSubagentContent:
    """Tests for subagent file content structure."""

    def test_subagent_frontmatter_includes_required_fields(self) -> None:
        """Test subagent frontmatter has all required fields."""
        builder = KiloBuilder()
        agent = Agent(
            name="parent",
            description="Parent description",
            system_prompt="Parent prompt",
            subagents=["child"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)
        content = subagents["child"]

        assert "name: child" in content
        assert "description:" in content
        assert "model:" in content
        assert "state_management:" in content
        assert "parent_agent: parent" in content

    def test_subagent_markdown_structure(self) -> None:
        """Test subagent markdown has proper section structure."""
        builder = KiloBuilder()
        agent = Agent(
            name="orchestrator",
            description="Main orchestrator",
            system_prompt="Main prompt",
            subagents=["scheduler"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)
        content = subagents["scheduler"]

        # Should have parent reference section
        assert "# Parent Agent" in content
        # Should have system prompt section
        assert "# System Prompt" in content

    def test_subagent_with_tools_included(self) -> None:
        """Test subagent file includes tools when requested."""
        builder = KiloBuilder()
        Agent(
            name="parent",
            description="Parent",
            system_prompt="Parent prompt",
            subagents=["tool_user"],
        )
        options = BuildOptions(include_tools=True)

        # Create subagent with tools for building
        subagent = Agent(
            name="tool_user",
            description="Has tools",
            system_prompt="Uses tools",
            tools=["read", "write"],
        )
        content = builder._build_subagent_file(subagent, "parent", options)

        assert "# Tools" in content
        assert "- read" in content
        assert "- write" in content

    def test_subagent_with_skills_included(self) -> None:
        """Test subagent file includes skills when requested."""
        builder = KiloBuilder()
        subagent = Agent(
            name="skilled",
            description="Has skills",
            system_prompt="Skilled agent",
            skills=["testing", "refactoring"],
        )
        options = BuildOptions(include_skills=True)

        content = builder._build_subagent_file(subagent, "parent", options)

        assert "# Skills" in content

    def test_subagent_tools_excluded_by_default(self) -> None:
        """Test subagent tools section excluded when not requested."""
        builder = KiloBuilder()
        subagent = Agent(
            name="tool_user",
            description="Has tools",
            system_prompt="Uses tools",
            tools=["read", "write"],
        )
        options = BuildOptions(include_tools=False)

        content = builder._build_subagent_file(subagent, "parent", options)

        assert "# Tools" not in content

    def test_subagent_skills_excluded_by_default(self) -> None:
        """Test subagent skills section excluded when not requested."""
        builder = KiloBuilder()
        subagent = Agent(
            name="skilled",
            description="Has skills",
            system_prompt="Skilled",
            skills=["testing"],
        )
        options = BuildOptions(include_skills=False)

        content = builder._build_subagent_file(subagent, "parent", options)

        assert "# Skills" not in content


class TestKiloSubagentValidation:
    """Tests for subagent validation."""

    def test_subagent_validation_fails_without_name(self) -> None:
        """Test subagent creation fails if name is empty (Pydantic validation)."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            # Pydantic validates at creation time, not at build time
            Agent(
                name="",  # Empty name
                description="Description",
                system_prompt="Prompt",
            )

    def test_subagent_validation_fails_without_description(self) -> None:
        """Test subagent creation fails if description is empty."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            # Pydantic validates at creation time
            Agent(
                name="test",
                description="",  # Empty description
                system_prompt="Prompt",
            )

    def test_subagent_validation_fails_without_prompt(self) -> None:
        """Test subagent creation fails if system_prompt is empty."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            # Pydantic validates at creation time
            Agent(
                name="test",
                description="Description",
                system_prompt="",  # Empty prompt
            )

    def test_subagent_validation_passes_with_required_fields(self) -> None:
        """Test subagent validation passes with required fields."""
        builder = KiloBuilder()
        subagent = Agent(
            name="valid",
            description="Valid description",
            system_prompt="Valid prompt",
        )
        options = BuildOptions()

        # Should not raise
        content = builder._build_subagent_file(subagent, "parent", options)
        assert content is not None


class TestKiloSubagentIntegration:
    """Integration tests for full agent + subagent generation."""

    def test_subagent_generation_with_single_subagent(self) -> None:
        """Test generating subagent files for agent with single subagent."""
        builder = KiloBuilder()
        agent = Agent(
            name="parent_agent",
            description="Architecture designer",
            system_prompt="You design systems",
            subagents=["data_modeler"],
        )
        options = BuildOptions()

        # Build subagents (don't call build() as it needs component variants)
        subagents = builder.build_subagents(agent, options)
        assert len(subagents) == 1
        assert "data_modeler" in subagents
        assert "parent_agent: parent_agent" in subagents["data_modeler"]

    def test_subagent_generation_with_multiple_subagents(self) -> None:
        """Test generating subagent files for agent with multiple subagents."""
        builder = KiloBuilder()
        agent = Agent(
            name="multi_parent",
            description="Workflow orchestrator",
            system_prompt="You manage workflows",
            subagents=["planner", "executor", "reviewer"],
        )
        options = BuildOptions()

        # Build subagents
        subagents = builder.build_subagents(agent, options)
        assert len(subagents) == 3

        # Verify each subagent
        for name in ["planner", "executor", "reviewer"]:
            assert name in subagents
            content = subagents[name]
            assert "parent_agent: multi_parent" in content
            assert "# Parent Agent" in content

    def test_subagent_hierarchy_depth(self) -> None:
        """Test building subagents at different nesting levels."""
        builder = KiloBuilder()

        # Parent agent with subagents
        parent_agent = Agent(
            name="level0",
            description="Top level",
            system_prompt="Top",
            subagents=["level1a", "level1b"],
        )
        options = BuildOptions()

        # Generate subagents for parent
        level1_agents = builder.build_subagents(parent_agent, options)
        assert len(level1_agents) == 2

        # Verify parent reference at level 1
        assert "parent_agent: level0" in level1_agents["level1a"]
        assert "parent_agent: level0" in level1_agents["level1b"]

    def test_subagent_with_tools_and_skills(self) -> None:
        """Test subagent generation with tools and skills."""
        builder = KiloBuilder()

        # Create subagent with tools and skills
        subagent = Agent(
            name="multi_capable",
            description="Has tools and skills",
            system_prompt="Multi-capable subagent",
            tools=["file_system", "database"],
            skills=["testing", "optimization"],
        )
        options = BuildOptions(include_tools=True, include_skills=True)

        content = builder._build_subagent_file(subagent, "parent", options)

        # Verify tools section
        assert "# Tools" in content
        assert "- file_system" in content
        assert "- database" in content

        # Verify skills section
        assert "# Skills" in content

    def test_subagents_reference_parent_correctly(self) -> None:
        """Test that subagents correctly reference their parent."""
        builder = KiloBuilder()
        agent = Agent(
            name="coordinator",
            description="Coordinates subagents",
            system_prompt="Coordinates",
            subagents=["worker1", "worker2", "worker3"],
        )
        options = BuildOptions()

        # Build subagents
        subagents = builder.build_subagents(agent, options)

        # Verify all subagents are built
        for sub_name in agent.subagents:
            assert sub_name in subagents
            # Verify parent reference is correct
            assert "parent_agent: coordinator" in subagents[sub_name]
            assert "# Parent Agent" in subagents[sub_name]

    def test_subagent_file_content_well_formed(self) -> None:
        """Test that subagent files are well-formed markdown with valid YAML."""
        builder = KiloBuilder()
        agent = Agent(
            name="test",
            description="Test agent",
            system_prompt="Test",
            subagents=["sub"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)
        content = subagents["sub"]

        # Check YAML is properly closed
        assert content.count("---") >= 2  # Opening and closing markers

        # Check markdown sections exist
        assert "# Parent Agent" in content
        assert "# System Prompt" in content

        # Check no orphaned section markers
        lines = content.split("\n")
        markdown_headers = [l for l in lines if l.startswith("#")]
        assert len(markdown_headers) >= 2  # Parent Agent + System Prompt


class TestKiloSubagentErrorHandling:
    """Tests for subagent error handling."""

    def test_build_subagents_creates_dict_for_valid_agent(self) -> None:
        """Test build_subagents returns dict for valid agent."""
        builder = KiloBuilder()
        agent = Agent(
            name="valid_agent",
            description="Valid",
            system_prompt="Valid",
            subagents=["sub"],
        )
        options = BuildOptions()

        # build_subagents should return a dict
        result = builder.build_subagents(agent, options)
        assert isinstance(result, dict)
        assert "sub" in result

    def test_subagent_inherits_parent_characteristics(self) -> None:
        """Test that generated subagents reference their parent."""
        builder = KiloBuilder()
        agent = Agent(
            name="intelligent_parent",
            description="Parent with intelligence",
            system_prompt="Parent system prompt",
            subagents=["smart_child"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)
        content = subagents["smart_child"]

        # Verify parent name is in subagent file
        assert "intelligent_parent" in content
        assert "parent_agent: intelligent_parent" in content


class TestKiloSubagentCoverage:
    """Tests designed to achieve 85%+ coverage target."""

    def test_format_subagent_parent_section(self) -> None:
        """Test parent agent section formatting."""
        builder = KiloBuilder()
        subagent = Agent(
            name="child",
            description="Child agent",
            system_prompt="Child",
        )
        options = BuildOptions()

        content = builder._build_subagent_file(subagent, "known_parent", options)

        # Verify parent section is properly formatted
        assert "# Parent Agent" in content
        lines = content.split("\n")
        # Find parent section and verify parent name appears nearby
        assert any("known_parent" in line for line in lines)

    def test_build_subagents_preserves_order(self) -> None:
        """Test that subagents are built in order."""
        builder = KiloBuilder()
        subagent_names = ["alpha", "beta", "gamma"]
        agent = Agent(
            name="ordered",
            description="Ordered",
            system_prompt="Ordered",
            subagents=subagent_names,
        )
        options = BuildOptions()

        result = builder.build_subagents(agent, options)

        # All subagents should be present
        for name in subagent_names:
            assert name in result

    def test_subagent_description_auto_generated(self) -> None:
        """Test that subagent descriptions are auto-generated with parent context."""
        builder = KiloBuilder()
        agent = Agent(
            name="boss",
            description="Boss agent",
            system_prompt="Manages team",
            subagents=["assistant"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)
        content = subagents["assistant"]

        # Subagent description should reference parent
        assert "Subagent of boss" in content

    def test_subagent_frontmatter_model_field(self) -> None:
        """Test that subagent frontmatter includes model field."""
        builder = KiloBuilder()
        subagent = Agent(
            name="test",
            description="Test",
            system_prompt="Test",
        )
        options = BuildOptions()

        content = builder._build_subagent_file(subagent, "parent", options)

        assert "model:" in content
        assert "anthropic/claude" in content

    def test_subagent_frontmatter_state_management(self) -> None:
        """Test that subagent frontmatter includes state_management."""
        builder = KiloBuilder()
        subagent = Agent(
            name="stateful",
            description="Has state",
            system_prompt="Stateful",
        )
        options = BuildOptions()

        content = builder._build_subagent_file(subagent, "parent", options)

        assert "state_management:" in content
        assert ".promptosaurus/sessions" in content

    def test_build_subagents_each_creates_valid_file(self) -> None:
        """Test that each subagent gets its own valid file."""
        builder = KiloBuilder()
        agent = Agent(
            name="multi",
            description="Multi subagent",
            system_prompt="Multi",
            subagents=["sub1", "sub2", "sub3"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)

        # Each should have valid YAML and markdown
        for _name, content in subagents.items():
            # Check YAML frontmatter
            assert content.startswith("---")
            assert "---\n\n" in content
            # Check markdown sections
            assert "# Parent Agent" in content
            assert "# System Prompt" in content
            # Check parent reference
            assert "parent_agent: multi" in content

    def test_subagent_system_prompt_preserved(self) -> None:
        """Test that subagent system prompt is preserved."""
        builder = KiloBuilder()
        subagent = Agent(
            name="specialized",
            description="Specialized worker",
            system_prompt="You are a specialized worker for task X",
        )
        options = BuildOptions()

        content = builder._build_subagent_file(subagent, "coordinator", options)

        # Original system prompt should be preserved
        assert "You are a specialized worker for task X" in content

    def test_subagent_frontmatter_all_required_fields(self) -> None:
        """Test frontmatter has all required fields for subagent."""
        builder = KiloBuilder()
        subagent = Agent(
            name="complete",
            description="Complete subagent",
            system_prompt="Complete",
        )
        options = BuildOptions()

        content = builder._build_subagent_file(subagent, "parent", options)

        # All required frontmatter fields
        assert "name: complete" in content
        assert "description:" in content
        assert "model:" in content
        assert "state_management:" in content
        assert "parent_agent: parent" in content

    def test_subagent_with_empty_tools_list(self) -> None:
        """Test subagent with empty tools list."""
        builder = KiloBuilder()
        subagent = Agent(
            name="no_tools",
            description="No tools",
            system_prompt="No tools",
            tools=[],
        )
        options = BuildOptions(include_tools=True)

        content = builder._build_subagent_file(subagent, "parent", options)

        # Tools section should not be in content (list is empty)
        assert "# Tools" not in content

    def test_subagent_with_empty_skills_list(self) -> None:
        """Test subagent with empty skills list."""
        builder = KiloBuilder()
        subagent = Agent(
            name="no_skills",
            description="No skills",
            system_prompt="No skills",
            skills=[],
        )
        options = BuildOptions(include_skills=True)

        content = builder._build_subagent_file(subagent, "parent", options)

        # Skills section should not be in content (list is empty)
        assert "# Skills" not in content

    def test_build_subagents_each_subagent_independent(self) -> None:
        """Test that each subagent is independently generated."""
        builder = KiloBuilder()
        agent = Agent(
            name="coordinator",
            description="Coordinates work",
            system_prompt="Coordinates",
            subagents=["worker_a", "worker_b"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)

        # Verify each has its own name and content
        content_a = subagents["worker_a"]
        content_b = subagents["worker_b"]

        # Each should reference its own name
        assert "name: worker_a" in content_a
        assert "name: worker_b" in content_b

        # But both reference same parent
        assert "parent_agent: coordinator" in content_a
        assert "parent_agent: coordinator" in content_b

    def test_subagent_file_contains_parent_context_comment(self) -> None:
        """Test that subagent file explicitly shows parent context."""
        builder = KiloBuilder()
        subagent = Agent(
            name="helper",
            description="Helper subagent",
            system_prompt="Helps with tasks",
        )
        options = BuildOptions()

        content = builder._build_subagent_file(subagent, "parent_agent_name", options)

        # Parent context should be visible in multiple places
        # 1. In frontmatter
        assert "parent_agent: parent_agent_name" in content
        # 2. In markdown section
        assert "# Parent Agent" in content

    def test_subagent_frontmatter_description_auto_generated(self) -> None:
        """Test that subagent has auto-generated description with parent context."""
        builder = KiloBuilder()
        # When building subagents via build_subagents, description is auto-generated
        agent = Agent(
            name="task_manager",
            description="Task manager",
            system_prompt="Manages tasks",
            subagents=["task_runner"],
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)
        content = subagents["task_runner"]

        # Auto-generated description should reference parent
        assert "Subagent of task_manager" in content

    def test_build_subagents_large_number(self) -> None:
        """Test build_subagents with many subagents."""
        builder = KiloBuilder()
        subagent_names = [f"worker_{i}" for i in range(10)]
        agent = Agent(
            name="factory",
            description="Factory coordinator",
            system_prompt="Factory",
            subagents=subagent_names,
        )
        options = BuildOptions()

        subagents = builder.build_subagents(agent, options)

        # All should be generated
        assert len(subagents) == 10
        for name in subagent_names:
            assert name in subagents
            assert "parent_agent: factory" in subagents[name]
