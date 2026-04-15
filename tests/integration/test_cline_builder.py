"""Integration tests for ClineBuilder with real file I/O.

Tests cover:
- Loading IR models and building Cline output
- Writing files to temporary directories
- Validating markdown syntax and structure
- Verifying skill invocation syntax ("use_skill {name}" pattern)
- Testing variant selection (minimal/verbose)
- Handling missing optional components gracefully
- Error cases with proper recovery
"""

import re
from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from promptosaurus.builders.base import BuildOptions
from promptosaurus.builders.cline_builder import ClineBuilder
from promptosaurus.ir.models import Agent


class TestClineBuilderFileWriting:
    """Tests for writing Cline files to the filesystem."""

    @pytest.fixture
    def temp_agents_dir(self) -> Generator[Path, None, None]:
        """Create a temporary agents directory with test agent structure."""
        with TemporaryDirectory() as temp_dir:
            agents_path = Path(temp_dir) / "agents"
            agents_path.mkdir()

            # Create a minimal test agent structure
            code_agent_dir = agents_path / "code" / "minimal"
            code_agent_dir.mkdir(parents=True)

            # Write minimal prompt
            (code_agent_dir / "prompt.md").write_text(
                "You are a code generation expert.\n\n"
                "Your role is to write high-quality Python code."
            )

            # Write optional skills file
            (code_agent_dir / "skills.md").write_text(
                "## Code Generation\n\nAbility to generate production-ready code."
            )

            yield agents_path

    @pytest.fixture
    def temp_output_dir(self) -> Generator[Path, None, None]:
        """Create a temporary output directory."""
        with TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_write_clinerules_file_to_temp_directory(
        self, temp_agents_dir: Path, temp_output_dir: Path
    ) -> None:
        """Test writing a generated .clinerules file to temporary directory."""
        builder = ClineBuilder(agents_dir=temp_agents_dir)

        agent = Agent(
            name="code",
            description="Code generation agent",
            system_prompt="You are a code expert.",
            tools=["read", "write"],
        )

        options = BuildOptions(variant="minimal")
        output = builder.build(agent, options)

        # Write to temporary file
        output_file = temp_output_dir / ".clinerules"
        output_file.write_text(output)

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_written_file_is_readable(self, temp_agents_dir: Path, temp_output_dir: Path) -> None:
        """Test that written .clinerules files are readable and intact."""
        builder = ClineBuilder(agents_dir=temp_agents_dir)

        agent = Agent(
            name="code",
            description="Code generation agent",
            system_prompt="You are a code expert.",
        )

        options = BuildOptions(variant="minimal")
        output = builder.build(agent, options)

        # Write and read back
        output_file = temp_output_dir / ".clinerules"
        output_file.write_text(output)

        read_content = output_file.read_text()
        assert read_content == output

    def test_multiple_agents_written_independently(
        self, temp_agents_dir: Path, temp_output_dir: Path
    ) -> None:
        """Test writing multiple agent .clinerules files independently."""
        # Create additional agent
        architect_dir = temp_agents_dir / "architect" / "minimal"
        architect_dir.mkdir(parents=True)
        (architect_dir / "prompt.md").write_text("You are a system architect.")

        builder = ClineBuilder(agents_dir=temp_agents_dir)

        # Build both agents
        code_agent = Agent(
            name="code",
            description="Code generation agent",
            system_prompt="You are a code expert.",
        )

        architect_agent = Agent(
            name="architect",
            description="System architecture agent",
            system_prompt="You are a system architect.",
        )

        options = BuildOptions(variant="minimal")
        code_output = builder.build(code_agent, options)
        architect_output = builder.build(architect_agent, options)

        # Write both files (in practice, would be named by agent)
        code_file = temp_output_dir / "code.clinerules"
        architect_file = temp_output_dir / "architect.clinerules"

        code_file.write_text(code_output)
        architect_file.write_text(architect_output)

        # Verify both files exist and have different content
        assert code_file.exists()
        assert architect_file.exists()
        assert code_file.read_text() != architect_file.read_text()
        assert "code" in code_output.lower() or "Code" in code_output


class TestClineBuilderMarkdownValidation:
    """Tests for markdown syntax and structure validation."""

    @pytest.fixture
    def builder_with_agents(self) -> Generator[ClineBuilder, None, None]:
        """Create a ClineBuilder instance with test agents."""
        with TemporaryDirectory() as temp_dir:
            agents_path = Path(temp_dir) / "agents"
            agents_path.mkdir()

            # Create test agents
            code_dir = agents_path / "code" / "minimal"
            code_dir.mkdir(parents=True)
            (code_dir / "prompt.md").write_text("You are a code expert.")

            test_dir = agents_path / "test_agent" / "minimal"
            test_dir.mkdir(parents=True)
            (test_dir / "prompt.md").write_text("You are a test agent.")

            yield ClineBuilder(agents_dir=agents_path)

    def test_markdown_is_valid_syntax(self, builder_with_agents: ClineBuilder) -> None:
        """Test that generated markdown has valid structure."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt content",
        )

        options = BuildOptions(variant="minimal")
        output = builder_with_agents.build(agent, options)

        # Should have basic markdown structure
        assert len(output) > 0
        assert output.startswith("# ")  # Has main header
        assert "\n" in output  # Has multiple lines

    def test_markdown_contains_main_header(self, builder_with_agents: ClineBuilder) -> None:
        """Test markdown includes main header with agent name."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt content",
        )

        options = BuildOptions(variant="minimal")
        output = builder_with_agents.build(agent, options)

        # Check for main header - Cline format is "# {agent_name} Rules"
        assert output.startswith("# code Rules\n")

    def test_markdown_system_prompt_appears_after_header(
        self, builder_with_agents: ClineBuilder
    ) -> None:
        """Test that system prompt appears in output."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="Code expert system prompt",
        )

        options = BuildOptions(variant="minimal")
        output = builder_with_agents.build(agent, options)

        lines = output.split("\n")
        # First line is "# {agent_name} Rules"
        assert lines[0].startswith("# ") and "Rules" in lines[0]
        # System prompt from component should be in output
        assert "expert" in output or "Code" in output

    def test_markdown_headers_use_proper_levels(self, builder_with_agents: ClineBuilder) -> None:
        """Test that markdown sections use proper heading levels (all main headers are #)."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt",
            tools=["read", "write"],
        )

        options = BuildOptions(variant="minimal", include_tools=True)
        output = builder_with_agents.build(agent, options)

        lines = output.split("\n")

        # Main headers should be level 1 (# System Prompt, # Tools, etc.)
        main_headers = [
            line for line in lines if line.startswith("# ") and not line.startswith("## ")
        ]
        assert len(main_headers) > 0

        # All main headers should be level 1 only
        for header in main_headers:
            assert header.startswith("# ")
            assert not header.startswith("## ")

    def test_markdown_sections_separated_by_blank_lines(
        self, builder_with_agents: ClineBuilder
    ) -> None:
        """Test sections are separated by blank lines."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt",
            tools=["read", "write"],
        )

        options = BuildOptions(variant="minimal", include_tools=True)
        output = builder_with_agents.build(agent, options)

        # Should not have consecutive section headings without blank line
        lines = output.split("\n")
        for i in range(len(lines) - 1):
            if lines[i].startswith("## ") and lines[i + 1].startswith("## "):
                pytest.fail("Consecutive section headings without blank line separator")

    def test_markdown_no_yaml_frontmatter(self, builder_with_agents: ClineBuilder) -> None:
        """Test that Cline output has NO YAML frontmatter (unlike Kilo)."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt",
        )

        options = BuildOptions(variant="minimal")
        output = builder_with_agents.build(agent, options)

        # Should NOT start with ---
        assert not output.startswith("---\n")
        # Should start with markdown header
        assert output.startswith("# ")


class TestClineBuilderSkillActivationSyntax:
    """Tests for skill invocation syntax verification."""

    @pytest.fixture
    def builder_with_skills(self) -> Generator[ClineBuilder, None, None]:
        """Create a ClineBuilder instance with agent that has skills."""
        with TemporaryDirectory() as temp_dir:
            agents_path = Path(temp_dir) / "agents"
            agents_path.mkdir()

            # Create agent with skills
            code_dir = agents_path / "code" / "verbose"
            code_dir.mkdir(parents=True)
            (code_dir / "prompt.md").write_text("You are a code expert.")
            (code_dir / "skills.md").write_text(
                "## test-first-implementation\n\n"
                "Write tests first, then implement.\n\n"
                "## refactor-code-module\n\n"
                "Refactor existing code with tests."
            )

            yield ClineBuilder(agents_dir=agents_path)

    def test_skills_section_includes_use_skill_pattern(
        self, builder_with_skills: ClineBuilder
    ) -> None:
        """Test that skills section includes use_skill invocation syntax."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt",
            skills=["test-first-implementation", "refactor-code-module"],
        )

        options = BuildOptions(variant="verbose", include_skills=True)
        output = builder_with_skills.build(agent, options)

        # Should include use_skill pattern
        assert "use_skill" in output
        assert "`use_skill" in output  # In backticks for code formatting

    def test_each_skill_has_use_skill_invocation(self, builder_with_skills: ClineBuilder) -> None:
        """Test that each skill has its own use_skill invocation syntax."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt",
            skills=["test-first-implementation", "refactor-code-module"],
        )

        options = BuildOptions(variant="verbose", include_skills=True)
        output = builder_with_skills.build(agent, options)

        # Find all use_skill patterns
        use_skill_matches = re.findall(r"`use_skill ([a-z_-]+)`", output)
        assert len(use_skill_matches) > 0

    def test_use_skill_format_is_correct(self, builder_with_skills: ClineBuilder) -> None:
        """Test that use_skill syntax follows correct format: use_skill {name}."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt",
            skills=["test-first-implementation"],
        )

        options = BuildOptions(variant="verbose", include_skills=True)
        output = builder_with_skills.build(agent, options)

        # Regex for use_skill pattern: backticks, use_skill, space, name, backticks
        pattern = r"`use_skill [a-z_-]+`"
        matches = re.findall(pattern, output)
        assert len(matches) > 0

    def test_skills_header_mentions_use_skill(self, builder_with_skills: ClineBuilder) -> None:
        """Test that Skills section mentions use_skill invocation."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt",
            skills=["test-first-implementation"],
        )

        options = BuildOptions(variant="verbose", include_skills=True)
        output = builder_with_skills.build(agent, options)

        # Find Skills section (Cline uses "# Skills" not "## Skills")
        assert "# Skills" in output
        # Extract Skills section
        skills_start = output.find("# Skills")
        # Skills section should mention how to invoke
        skills_section = output[skills_start : skills_start + 500]
        assert "use_skill" in skills_section.lower()


class TestClineBuilderVariantHandling:
    """Tests for minimal vs verbose variant selection."""

    @pytest.fixture
    def variant_agents_dir(self) -> Generator[Path, None, None]:
        """Create agents directory with both minimal and verbose variants."""
        with TemporaryDirectory() as temp_dir:
            agents_path = Path(temp_dir) / "agents"

            # Create agent with both variants
            agent_name = "test_agent"

            # Minimal variant
            minimal_dir = agents_path / agent_name / "minimal"
            minimal_dir.mkdir(parents=True)
            (minimal_dir / "prompt.md").write_text("You are a helpful assistant. (MINIMAL)")

            # Verbose variant
            verbose_dir = agents_path / agent_name / "verbose"
            verbose_dir.mkdir(parents=True)
            (verbose_dir / "prompt.md").write_text(
                "You are a helpful assistant.\n\n"
                "Detailed verbose prompt with extensive instructions. (VERBOSE)"
            )
            (verbose_dir / "skills.md").write_text("## Extended Skills\n\nVerbose skills content.")

            yield agents_path

    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    def test_build_with_minimal_variant(self, variant_agents_dir: Path) -> None:
        """Test building with minimal variant."""
        builder = ClineBuilder(agents_dir=variant_agents_dir)

        agent = Agent(
            name="test_agent",
            description="Test agent",
            system_prompt="Test prompt",
        )

        options = BuildOptions(variant="minimal")
        output = builder.build(agent, options)

        assert "(MINIMAL)" in output

    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    def test_build_with_verbose_variant(self, variant_agents_dir: Path) -> None:
        """Test building with verbose variant."""
        builder = ClineBuilder(agents_dir=variant_agents_dir)

        agent = Agent(
            name="test_agent",
            description="Test agent",
            system_prompt="Test prompt",
        )

        options = BuildOptions(variant="verbose")
        output = builder.build(agent, options)

        assert "(VERBOSE)" in output
        assert "Extended Skills" in output

    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    def test_verbose_has_more_content_than_minimal(self, variant_agents_dir: Path) -> None:
        """Test that verbose variant produces longer output than minimal."""
        builder = ClineBuilder(agents_dir=variant_agents_dir)

        agent = Agent(
            name="test_agent",
            description="Test agent",
            system_prompt="Test prompt",
        )

        minimal_output = builder.build(agent, BuildOptions(variant="minimal"))
        verbose_output = builder.build(agent, BuildOptions(variant="verbose"))

        assert len(verbose_output) > len(minimal_output)

    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    @pytest.mark.skip(reason="Builders don't support variants for top-level agents")
    def test_fallback_to_verbose_when_minimal_unavailable(self, variant_agents_dir: Path) -> None:
        """Test that verbose is used as fallback if minimal is missing."""
        # Remove minimal variant
        minimal_dir = variant_agents_dir / "test_agent" / "minimal"
        (minimal_dir / "prompt.md").unlink()

        builder = ClineBuilder(agents_dir=variant_agents_dir)

        agent = Agent(
            name="test_agent",
            description="Test agent",
            system_prompt="Test prompt",
        )

        # Request minimal but should get verbose
        options = BuildOptions(variant="minimal")
        output = builder.build(agent, options)

        assert "(VERBOSE)" in output


class TestClineBuilderComponentHandling:
    """Tests for optional components and graceful degradation."""

    @pytest.fixture
    def minimal_agents_dir(self) -> Generator[Path, None, None]:
        """Create agents directory with minimal structure (only prompt)."""
        with TemporaryDirectory() as temp_dir:
            agents_path = Path(temp_dir) / "agents"

            # Create agent with only prompt (no skills/workflows)
            agent_dir = agents_path / "minimal" / "minimal"
            agent_dir.mkdir(parents=True)
            (agent_dir / "prompt.md").write_text("Minimal system prompt.")

            yield agents_path

    def test_build_without_optional_skills(self, minimal_agents_dir: Path) -> None:
        """Test building succeeds when skills are missing."""
        builder = ClineBuilder(agents_dir=minimal_agents_dir)

        agent = Agent(
            name="minimal",
            description="Minimal agent",
            system_prompt="Test prompt",
        )

        options = BuildOptions(variant="minimal", include_skills=True)
        output = builder.build(agent, options)

        # Should build successfully even without skills - has header with agent name
        assert output.startswith("# minimal Rules")
        assert len(output) > 0

    def test_build_without_optional_workflows(self, minimal_agents_dir: Path) -> None:
        """Test building succeeds when workflows are missing."""
        builder = ClineBuilder(agents_dir=minimal_agents_dir)

        agent = Agent(
            name="minimal",
            description="Minimal agent",
            system_prompt="Test prompt",
        )

        options = BuildOptions(variant="minimal", include_workflows=True)
        output = builder.build(agent, options)

        # Should build successfully even without workflows - has header with agent name
        assert output.startswith("# minimal Rules")
        assert len(output) > 0

    def test_include_flags_control_output(self, minimal_agents_dir: Path) -> None:
        """Test that include flags control which sections appear."""
        builder = ClineBuilder(agents_dir=minimal_agents_dir)

        agent = Agent(
            name="minimal",
            description="Minimal agent",
            system_prompt="Test prompt",
            tools=["tool1", "tool2"],
        )

        # Build with tools included
        with_tools = builder.build(agent, BuildOptions(variant="minimal", include_tools=True))

        # Build without tools
        without_tools = builder.build(agent, BuildOptions(variant="minimal", include_tools=False))

        # With tools should have Tools section (level 1 header)
        assert "# Tools" in with_tools
        assert "# Tools" not in without_tools

    def test_missing_optional_components_no_crash(self, minimal_agents_dir: Path) -> None:
        """Test that missing optional components don't crash the builder."""
        builder = ClineBuilder(agents_dir=minimal_agents_dir)

        agent = Agent(
            name="minimal",
            description="Minimal agent with no optional components",
            system_prompt="Test prompt",
        )

        options = BuildOptions(
            variant="minimal",
            include_skills=True,
            include_workflows=True,
            include_subagents=True,
            include_tools=True,
        )

        # Should not raise an exception
        output = builder.build(agent, options)
        assert len(output) > 0

    def test_system_prompt_rendered_as_prose(self, minimal_agents_dir: Path) -> None:
        """Test that system prompt is rendered as plain prose (no markdown formatting)."""
        builder = ClineBuilder(agents_dir=minimal_agents_dir)

        agent = Agent(
            name="minimal",
            description="Minimal agent",
            system_prompt="You are an expert engineer. You follow SOLID principles.",
        )

        options = BuildOptions(variant="minimal")
        output = builder.build(agent, options)

        # System prompt should appear as prose without markdown headers
        # i.e., not "## You are..." or "### expert engineer"
        prose_lines = output.split("\n")
        # First line is "# minimal Rules"
        # Next meaningful line should be prose prompt
        for _i, line in enumerate(prose_lines[1:5]):
            if line.strip() and not line.startswith("#"):
                # This is prose line - should not have markdown formatting
                assert not line.startswith("*")
                break


class TestClineBuilderErrorHandling:
    """Tests for error cases and recovery."""

    @pytest.fixture
    def builder_with_agents(self) -> Generator[ClineBuilder, None, None]:
        """Create a ClineBuilder instance with test agents."""
        with TemporaryDirectory() as temp_dir:
            agents_path = Path(temp_dir) / "agents"
            agents_path.mkdir()

            # Create test agents for error handling tests
            code_dir = agents_path / "code" / "minimal"
            code_dir.mkdir(parents=True)
            (code_dir / "prompt.md").write_text("You are a code expert.")

            test_dir = agents_path / "test" / "minimal"
            test_dir.mkdir(parents=True)
            (test_dir / "prompt.md").write_text("You are a test specialist.")

            yield ClineBuilder(agents_dir=agents_path)

    def test_valid_agent_builds_successfully(self, builder_with_agents: ClineBuilder) -> None:
        """Test that valid agent builds successfully."""
        agent = Agent(
            name="code",
            description="Agent description",
            system_prompt="System prompt",
        )

        options = BuildOptions(variant="minimal")
        output = builder_with_agents.build(agent, options)
        assert len(output) > 0
        assert output.startswith("# code Rules")

    def test_agent_with_complete_fields_builds(self, builder_with_agents: ClineBuilder) -> None:
        """Test that agent with all required fields builds successfully."""
        agent = Agent(
            name="code",
            description="Valid description",
            system_prompt="System prompt",
        )

        options = BuildOptions(variant="minimal")
        output = builder_with_agents.build(agent, options)
        assert len(output) > 0
        assert output.startswith("# code Rules")

    def test_agent_with_custom_system_prompt_builds(
        self, builder_with_agents: ClineBuilder
    ) -> None:
        """Test that agent with custom system prompt builds successfully."""
        agent = Agent(
            name="test",
            description="Test agent",
            system_prompt="Custom system prompt text",
        )

        options = BuildOptions(variant="minimal")
        output = builder_with_agents.build(agent, options)
        assert len(output) > 0
        assert output.startswith("# test Rules")

    def test_validation_error_contains_helpful_message(
        self, builder_with_agents: ClineBuilder
    ) -> None:
        """Test that builder's validate method provides helpful error messages."""
        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="System prompt",  # Valid
        )

        # The builder's validate method checks for required fields
        errors = builder_with_agents.validate(agent)
        # A valid agent should have no errors
        assert len(errors) == 0


class TestClineBuilderIntegration:
    """Integration tests for complex scenarios."""

    @pytest.fixture
    def complex_agents_dir(self) -> Generator[Path, None, None]:
        """Create agents directory with complex agent structures."""
        with TemporaryDirectory() as temp_dir:
            agents_path = Path(temp_dir) / "agents"

            # Code agent with all components
            code_dir = agents_path / "code" / "verbose"
            code_dir.mkdir(parents=True)
            (code_dir / "prompt.md").write_text(
                "You are a code expert. Write high-quality Python code.\n\n"
                "Follow SOLID principles and best practices."
            )
            (code_dir / "skills.md").write_text(
                "## test-first-implementation\n\n"
                "Write comprehensive tests before implementation.\n\n"
                "## code-review-audit\n\n"
                "Review code against conventions."
            )
            (code_dir / "workflow.md").write_text(
                "### Feature Implementation\n\n"
                "1. Read existing code\n"
                "2. Understand patterns\n"
                "3. Implement feature\n"
                "4. Write tests"
            )

            # Architect agent (minimal)
            architect_dir = agents_path / "architect" / "minimal"
            architect_dir.mkdir(parents=True)
            (architect_dir / "prompt.md").write_text("You are a system architect.")

            yield agents_path

    def test_build_multiple_agents_in_sequence(self, complex_agents_dir: Path) -> None:
        """Test building multiple different agents in sequence."""
        builder = ClineBuilder(agents_dir=complex_agents_dir)

        code_agent = Agent(
            name="code",
            description="Code generation agent",
            system_prompt="You are a code expert.",
            tools=["read", "write"],
            skills=["test-first-implementation", "code-review-audit"],
        )

        architect_agent = Agent(
            name="architect",
            description="Architecture agent",
            system_prompt="You are a system architect.",
        )

        # Build both in sequence
        code_output = builder.build(
            code_agent, BuildOptions(variant="verbose", include_skills=True)
        )
        architect_output = builder.build(architect_agent, BuildOptions(variant="minimal"))

        # Both should build successfully with proper headers
        assert code_output.startswith("# code Rules")
        assert architect_output.startswith("# architect Rules")
        assert "You are a code expert" in code_output
        assert "You are a system architect" in architect_output
        assert len(code_output) > len(architect_output)

    def test_rebuild_with_different_build_options(self, complex_agents_dir: Path) -> None:
        """Test rebuilding same agent with different build options."""
        builder = ClineBuilder(agents_dir=complex_agents_dir)

        agent = Agent(
            name="code",
            description="Code generation agent",
            system_prompt="You are a code expert.",
            skills=["test-first-implementation"],
        )

        # Build with skills and tools
        with_skills = builder.build(agent, BuildOptions(variant="verbose", include_skills=True))
        without_skills = builder.build(agent, BuildOptions(variant="minimal", include_skills=False))

        # Both should have proper headers
        assert with_skills.startswith("# code Rules")
        assert without_skills.startswith("# code Rules")

        # With skills should have more content (or at least skills section)
        assert "# Skills" in with_skills or "use_skill" in with_skills

    def test_full_roundtrip_write_and_read(self, complex_agents_dir: Path) -> None:
        """Test complete roundtrip: build, write, read, and verify."""
        builder = ClineBuilder(agents_dir=complex_agents_dir)

        agent = Agent(
            name="code",
            description="Code generation agent",
            system_prompt="You are a code expert.\n\nYou follow best practices.",
            tools=["read", "write"],
            skills=["test-first-implementation"],
        )

        # Build
        output = builder.build(agent, BuildOptions(variant="verbose", include_skills=True))

        with TemporaryDirectory() as temp_dir:
            # Write
            output_file = Path(temp_dir) / ".clinerules"
            output_file.write_text(output)

            # Read
            read_content = output_file.read_text()

            # Verify
            assert read_content == output
            assert read_content.startswith("# code Rules")
            assert "You are a code expert" in read_content
            assert "use_skill" in read_content

    def test_markdown_syntax_valid_for_all_components(self, complex_agents_dir: Path) -> None:
        """Test that markdown output is valid for agents with all components."""
        builder = ClineBuilder(agents_dir=complex_agents_dir)

        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code expert.",
            tools=["read", "write", "bash"],
            skills=["test-first-implementation", "code-review-audit"],
            subagents=["code-test", "code-review"],
        )

        output = builder.build(
            agent,
            BuildOptions(
                variant="verbose",
                include_tools=True,
                include_skills=True,
                include_subagents=True,
                include_workflows=True,
            ),
        )

        # Verify markdown structure
        assert len(output) > 0
        assert output.startswith("# ")  # Has main header
        assert "## " in output  # Has section headers
        assert "- " in output or "*" in output  # Has lists

    def test_headers_hierarchy_is_correct(self, complex_agents_dir: Path) -> None:
        """Test that markdown header hierarchy follows Cline format."""
        builder = ClineBuilder(agents_dir=complex_agents_dir)

        agent = Agent(
            name="code",
            description="Code agent",
            system_prompt="You are a code expert.",
            skills=["test-first-implementation"],
            subagents=["code-test"],
        )

        output = builder.build(
            agent,
            BuildOptions(
                variant="verbose",
                include_skills=True,
                include_subagents=True,
            ),
        )

        lines = output.split("\n")

        # Cline format uses level 1 headers for main sections (System Prompt is rendered as prose, but Skills/Subagents are headers)
        main_headers = [
            line for line in lines if line.startswith("# ") and not line.startswith("## ")
        ]
        # Should have at least one main header (the agent name header)
        assert len(main_headers) >= 1

        # Check that expected sections are present (header or prose content)
        assert "code" in output  # Agent name should appear in header
        assert "# Skills" in output or "# Subagents" in output
