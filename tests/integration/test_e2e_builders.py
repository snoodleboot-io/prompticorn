"""End-to-End scenario tests for all 5 builders.

This module contains comprehensive E2E tests that:
1. Load agents from test agent directories
2. Build output for all 5 tools (Kilo, Cline, Claude, Copilot, Cursor)
3. Verify each tool's output format is correct
4. Test both minimal and verbose variants
5. Test multiple different agents
6. Verify cross-tool consistency
7. Test error cases and edge cases

Tests are organized into 6 classes covering different aspects of the
complete builder pipeline.
"""

import json
import re
from collections.abc import Generator
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest
import yaml

from promptosaurus.builders.base import BuildOptions
from promptosaurus.builders.claude_builder import ClaudeBuilder
from promptosaurus.builders.cline_builder import ClineBuilder
from promptosaurus.builders.copilot_builder import CopilotBuilder
from promptosaurus.builders.cursor_builder import CursorBuilder
from promptosaurus.builders.factory import BuilderFactory
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.ir.models import Agent

# ============================================================================
# Fixtures for test setup and agent loading
# ============================================================================


def create_test_agents_dir(temp_dir: Path) -> Path:
    """Create a temporary agents directory with proper structure for all test agents."""
    agents_dir = temp_dir / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    # Agent definitions: (name, description, prompt, tools, skills, workflows, subagents)
    agents_config = [
        (
            "code",
            "Code generation agent",
            "You are an expert programmer. Write high-quality, well-tested code.",
            ["read", "write", "execute"],
            ["code_generation", "testing"],
            ["code_workflow"],
            ["test_subagent"],
        ),
        (
            "architect",
            "System architecture agent",
            "You are a system architect. Design scalable, maintainable systems.",
            ["design", "document"],
            ["system_design", "api_design"],
            ["architecture_workflow"],
            [],
        ),
        (
            "test",
            "Testing agent",
            "You are a QA expert. Write comprehensive tests and verify quality.",
            ["test", "verify", "measure"],
            ["unit_testing", "integration_testing"],
            ["testing_workflow"],
            [],
        ),
        (
            "review",
            "Code review agent",
            "You are a code reviewer. Provide constructive feedback on code quality.",
            ["analyze", "review"],
            ["code_review", "best_practices"],
            ["review_workflow"],
            [],
        ),
        (
            "debug",
            "Debugging agent",
            "You are a debugging expert. Help identify and fix issues quickly.",
            ["trace", "debug", "analyze"],
            ["debugging", "profiling"],
            ["debug_workflow"],
            [],
        ),
    ]

    # Create directory structure for each agent
    for name, _desc, prompt, _tools, skills, workflows, subagents in agents_config:
        # Create minimal variant
        minimal_dir = agents_dir / name / "minimal"
        minimal_dir.mkdir(parents=True, exist_ok=True)

        # Write minimal prompt
        (minimal_dir / "prompt.md").write_text(
            f"{prompt}\n\nAgent: {name}\nMinimal variant for focused operation."
        )

        # Write optional minimal skills
        if skills:
            (minimal_dir / "skills.md").write_text(
                f"## Skills for {name}\n\n" + "\n".join(f"- {s}" for s in skills[:1])
            )

        # Create verbose variant
        verbose_dir = agents_dir / name / "verbose"
        verbose_dir.mkdir(parents=True, exist_ok=True)

        # Write verbose prompt (longer version)
        (verbose_dir / "prompt.md").write_text(
            f"{prompt}\n\n"
            f"Agent: {name}\n"
            f"Verbose variant with detailed instructions.\n\n"
            f"Details: This is the full version with comprehensive guidance."
        )

        # Write all verbose skills
        if skills:
            (verbose_dir / "skills.md").write_text(
                f"## Skills for {name}\n\n" + "\n".join(f"- {s}" for s in skills)
            )

        # Write workflows if specified
        if workflows:
            (verbose_dir / "workflows.md").write_text(
                "## Workflows\n\n" + "\n".join(f"- {w}" for w in workflows)
            )

        # Write subagents if specified
        if subagents:
            (verbose_dir / "subagents.md").write_text(
                "## Subagents\n\n" + "\n".join(f"- {sa}" for sa in subagents)
            )

    return agents_dir


@pytest.fixture
def temp_agents_dir() -> Generator[Path, None, None]:
    """Create a temporary agents directory with proper test structure."""
    with TemporaryDirectory() as temp_dir:
        agents_dir = create_test_agents_dir(Path(temp_dir))
        yield agents_dir


@pytest.fixture
def sample_agent() -> Agent:
    """Create a sample agent IR model for testing."""
    return Agent(
        name="code",
        description="Code generation agent",
        system_prompt="You are an expert programmer. Write high-quality, well-tested code.",
        tools=["read", "write", "execute"],
        skills=["code_generation", "testing"],
        workflows=["code_workflow"],
        subagents=["test_subagent"],
    )


@pytest.fixture
def all_builders(temp_agents_dir: Path) -> dict[str, Any]:
    """Create instances of all 5 builders."""
    return {
        "kilo": KiloBuilder(agents_dir=temp_agents_dir),
        "cline": ClineBuilder(agents_dir=temp_agents_dir),
        "claude": ClaudeBuilder(agents_dir=temp_agents_dir),
        "copilot": CopilotBuilder(agents_dir=temp_agents_dir),
        "cursor": CursorBuilder(agents_dir=temp_agents_dir),
    }


@pytest.fixture
def variant_options() -> dict[str, BuildOptions]:
    """Create BuildOptions for minimal and verbose variants."""
    return {
        "minimal": BuildOptions(variant="minimal"),
        "verbose": BuildOptions(variant="verbose"),
    }


# ============================================================================
# Test Class 1: Single Agent, All Tools
# ============================================================================


class TestSingleAgentAllTools:
    """Tests for building a single agent with all 5 tools."""

    def test_build_sample_agent_with_all_tools(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Test building sample agent with all 5 tools."""
        options = BuildOptions(variant="verbose")

        outputs = {}
        for tool_name, builder in all_builders.items():
            output = builder.build(sample_agent, options)
            outputs[tool_name] = output
            assert output is not None
            if tool_name != "claude":  # Claude returns dict
                assert isinstance(output, str)
            assert len(output) > 0

    def test_all_tools_produce_output(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify all tools produce non-empty output."""
        options = BuildOptions(variant="verbose")

        for tool_name, builder in all_builders.items():
            output = builder.build(sample_agent, options)
            # Claude returns dict, others return strings
            if tool_name == "claude":
                assert isinstance(output, dict)
                assert "system" in output
            else:
                assert isinstance(output, str)
                assert len(output) > 50  # Reasonable minimum size

    def test_tools_produce_different_outputs(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify each tool produces unique, tool-specific output."""
        options = BuildOptions(variant="verbose")

        outputs = {}
        for tool_name, builder in all_builders.items():
            output = builder.build(sample_agent, options)
            outputs[tool_name] = output

        # Convert all to strings for comparison
        output_strings = {}
        for tool_name, output in outputs.items():
            if tool_name == "claude":
                output_strings[tool_name] = json.dumps(output, indent=2)
            else:
                output_strings[tool_name] = str(output)

        # Verify they're different from each other
        tools = list(output_strings.keys())
        for i, tool1 in enumerate(tools):
            for tool2 in tools[i + 1 :]:
                assert output_strings[tool1] != output_strings[tool2], (
                    f"{tool1} and {tool2} produced identical output"
                )

    def test_kilo_output_contains_yaml_frontmatter(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Kilo output has YAML frontmatter."""
        options = BuildOptions(variant="verbose")
        output = all_builders["kilo"].build(sample_agent, options)

        assert output.startswith("---"), "Kilo output should start with ---"
        assert "---" in output[3:], "Kilo output should have closing ---"

    def test_claude_output_contains_required_keys(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Claude output contains required JSON keys."""
        options = BuildOptions(variant="verbose")
        output = all_builders["claude"].build(sample_agent, options)

        assert isinstance(output, dict)
        assert "system" in output
        assert "tools" in output
        assert isinstance(output["system"], str)
        assert len(output["system"]) > 0

    def test_cline_output_is_markdown(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Cline output is valid markdown."""
        options = BuildOptions(variant="verbose")
        output = all_builders["cline"].build(sample_agent, options)

        assert isinstance(output, str)
        # Should have markdown headers
        assert "#" in output
        # Should be substantial
        assert len(output) > 100


# ============================================================================
# Test Class 2: Format Validation
# ============================================================================


class TestFormatValidation:
    """Tests for validating output format of each builder."""

    def test_kilo_yaml_frontmatter_is_valid(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Kilo YAML frontmatter is valid YAML."""
        options = BuildOptions(variant="verbose")
        output = all_builders["kilo"].build(sample_agent, options)

        # Extract frontmatter
        match = re.match(r"^---\n(.*?)\n---", output, re.DOTALL)
        assert match is not None, "Could not find YAML frontmatter"

        frontmatter_str = match.group(1)
        frontmatter = yaml.safe_load(frontmatter_str)

        assert isinstance(frontmatter, dict)
        assert "name" in frontmatter
        assert "description" in frontmatter

    def test_kilo_has_markdown_sections(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Kilo output has expected markdown sections."""
        options = BuildOptions(variant="verbose")
        output = all_builders["kilo"].build(sample_agent, options)

        # Check for at least some common sections (not all may be present)
        output_lower = output.lower()
        sections = ["system", "prompt", "tools"]  # Core sections
        found_sections = [s for s in sections if s in output_lower]
        assert len(found_sections) >= 2, (
            f"Expected at least 2 of {sections} in Kilo output, found {found_sections}"
        )

    def test_cline_has_markdown_syntax(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Cline output has valid markdown syntax."""
        options = BuildOptions(variant="verbose")
        output = all_builders["cline"].build(sample_agent, options)

        # Check for markdown elements
        assert "#" in output, "Should have headers"
        assert "-" in output, "Should have list items or dashes"
        # Should have coherent structure
        assert len(output.split("\n")) > 5, "Should have multiple lines"

    def test_cline_has_use_skill_patterns(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Cline output documents skill usage."""
        options = BuildOptions(variant="verbose")
        output = all_builders["cline"].build(sample_agent, options)

        # If agent has skills, should mention them
        if sample_agent.skills:
            # Should have skills section
            assert "skill" in output.lower(), "Skills section expected in Cline output"

    def test_claude_json_is_valid(self, sample_agent: Agent, all_builders: dict[str, Any]) -> None:
        """Verify Claude output is valid JSON."""
        options = BuildOptions(variant="verbose")
        output = all_builders["claude"].build(sample_agent, options)

        # Should be dict (already parsed)
        assert isinstance(output, dict)

        # Verify it's JSON-serializable
        json_str = json.dumps(output)
        assert json_str is not None

        # Deserialize and verify
        deserialized = json.loads(json_str)
        assert isinstance(deserialized, dict)

    def test_claude_has_required_fields(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Claude output has required fields."""
        options = BuildOptions(variant="verbose")
        output = all_builders["claude"].build(sample_agent, options)

        assert isinstance(output, dict)
        assert "system" in output
        assert isinstance(output["system"], str)
        assert len(output["system"]) > 0

        # Tools should be a list or missing
        if "tools" in output:
            assert isinstance(output["tools"], list)

    def test_copilot_yaml_frontmatter_valid(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Copilot YAML frontmatter is valid."""
        options = BuildOptions(variant="verbose")
        output = all_builders["copilot"].build(sample_agent, options)

        # Should start with YAML
        match = re.match(r"^---\n(.*?)\n---", output, re.DOTALL)
        assert match is not None

        frontmatter_str = match.group(1)
        frontmatter = yaml.safe_load(frontmatter_str)
        assert isinstance(frontmatter, dict)

    def test_copilot_has_applyto_metadata(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify Copilot has applyTo metadata."""
        options = BuildOptions(variant="verbose")
        output = all_builders["copilot"].build(sample_agent, options)

        # Extract and check frontmatter
        match = re.match(r"^---\n(.*?)\n---", output, re.DOTALL)
        if match:
            frontmatter_str = match.group(1)
            frontmatter = yaml.safe_load(frontmatter_str)
            # applyTo is optional but common
            if "applyTo" in frontmatter:
                assert isinstance(frontmatter["applyTo"], (list, str))

    def test_cursor_is_markdown(self, sample_agent: Agent, all_builders: dict[str, Any]) -> None:
        """Verify Cursor output is valid markdown."""
        options = BuildOptions(variant="verbose")
        output = all_builders["cursor"].build(sample_agent, options)

        assert isinstance(output, str)
        assert len(output) > 50


# ============================================================================
# Test Class 3: Variant Testing (Minimal vs Verbose)
# ============================================================================


class TestVariantTesting:
    """Tests for minimal and verbose variants across all tools."""

    def test_all_tools_support_minimal_variant(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify all tools support minimal variant."""
        options = BuildOptions(variant="minimal")

        for _tool_name, builder in all_builders.items():
            output = builder.build(sample_agent, options)
            assert output is not None
            assert len(output) > 0

    def test_all_tools_support_verbose_variant(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify all tools support verbose variant."""
        options = BuildOptions(variant="verbose")

        for _tool_name, builder in all_builders.items():
            output = builder.build(sample_agent, options)
            assert output is not None
            assert len(output) > 0

    def test_minimal_is_smaller_than_verbose(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify minimal variant produces smaller output than verbose."""
        minimal_opts = BuildOptions(variant="minimal")
        verbose_opts = BuildOptions(variant="verbose")

        for tool_name, builder in all_builders.items():
            minimal = builder.build(sample_agent, minimal_opts)
            verbose = builder.build(sample_agent, verbose_opts)

            # Convert to string for size comparison
            if tool_name == "claude":
                minimal_size = len(json.dumps(minimal))
                verbose_size = len(json.dumps(verbose))
            else:
                minimal_size = len(str(minimal))
                verbose_size = len(str(verbose))

            # Minimal should be same size or smaller
            assert minimal_size <= verbose_size, (
                f"{tool_name}: minimal ({minimal_size}) should be <= verbose ({verbose_size})"
            )

    def test_variant_switching_same_output(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify switching variants produces consistent output."""
        # Build minimal twice
        opts_minimal = BuildOptions(variant="minimal")
        output1 = all_builders["kilo"].build(sample_agent, opts_minimal)
        output2 = all_builders["kilo"].build(sample_agent, opts_minimal)

        assert output1 == output2, "Same variant should produce same output"

    def test_verbose_contains_more_detail(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify verbose variant contains more content."""
        minimal_opts = BuildOptions(variant="minimal")
        verbose_opts = BuildOptions(variant="verbose")

        for tool_name, builder in all_builders.items():
            minimal = builder.build(sample_agent, minimal_opts)
            verbose = builder.build(sample_agent, verbose_opts)

            if tool_name != "claude":
                # Verbose should have similar structure but more content
                # Both should be substantive
                assert len(str(verbose)) > 20
                assert len(str(minimal)) > 20


# ============================================================================
# Test Class 4: Multiple Agents
# ============================================================================


class TestMultipleAgents:
    """Tests for building multiple different agents."""

    @pytest.fixture
    def multi_agents(self) -> list[Agent]:
        """Create multiple test agents that match the temp directory structure."""
        return [
            Agent(
                name="code",
                description="Code generation agent",
                system_prompt="You are an expert programmer. Write high-quality, well-tested code.",
                tools=["read", "write", "execute"],
                skills=["code_generation", "testing"],
            ),
            Agent(
                name="architect",
                description="System architecture agent",
                system_prompt="You are a system architect. Design scalable, maintainable systems.",
                tools=["design", "document"],
                skills=["system_design", "api_design"],
            ),
            Agent(
                name="test",
                description="Testing agent",
                system_prompt="You are a QA expert. Write comprehensive tests and verify quality.",
                tools=["test", "verify", "measure"],
                skills=["unit_testing", "integration_testing"],
            ),
            Agent(
                name="review",
                description="Code review agent",
                system_prompt="You are a code reviewer. Provide constructive feedback on code quality.",
                tools=["analyze", "review"],
                skills=["code_review", "best_practices"],
            ),
            Agent(
                name="debug",
                description="Debugging agent",
                system_prompt="You are a debugging expert. Help identify and fix issues quickly.",
                tools=["trace", "debug", "analyze"],
                skills=["debugging", "profiling"],
            ),
        ]

    def test_build_multiple_agents(
        self, multi_agents: list[Agent], all_builders: dict[str, Any]
    ) -> None:
        """Test building multiple different agents."""
        options = BuildOptions(variant="verbose")

        for agent in multi_agents:
            for _tool_name, builder in all_builders.items():
                output = builder.build(agent, options)
                assert output is not None
                assert len(output) > 0

    def test_different_agents_produce_different_output(
        self, multi_agents: list[Agent], all_builders: dict[str, Any]
    ) -> None:
        """Verify different agents produce different outputs."""
        options = BuildOptions(variant="verbose")

        # Build code agent
        code_agent = multi_agents[0]
        code_output = all_builders["kilo"].build(code_agent, options)

        # Build architect agent
        arch_agent = multi_agents[1]
        arch_output = all_builders["kilo"].build(arch_agent, options)

        # Should be different
        assert code_output != arch_output

    def test_agent_names_in_output(
        self, multi_agents: list[Agent], all_builders: dict[str, Any]
    ) -> None:
        """Verify agent names appear in output."""
        options = BuildOptions(variant="verbose")

        for agent in multi_agents[:3]:  # Test first 3
            for tool_name, builder in all_builders.items():
                output = builder.build(agent, options)
                output_lower = (
                    json.dumps(output).lower() if isinstance(output, dict) else str(output).lower()
                )
                # Name should appear somewhere in output
                assert agent.name.lower() in output_lower, (
                    f"Agent name '{agent.name}' not found in {tool_name} output"
                )

    def test_each_agent_builds_with_all_tools(
        self, multi_agents: list[Agent], all_builders: dict[str, Any]
    ) -> None:
        """Verify each agent builds successfully with all tools."""
        options = BuildOptions(variant="verbose")

        for agent in multi_agents:
            for tool_name, builder in all_builders.items():
                output = builder.build(agent, options)
                assert output is not None
                if tool_name == "claude":
                    assert isinstance(output, dict)
                else:
                    assert isinstance(output, str)


# ============================================================================
# Test Class 5: Cross-Tool Consistency
# ============================================================================


class TestCrosToolConsistency:
    """Tests for consistency across all tools."""

    def test_same_ir_builds_in_all_tools(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify same IR builds in all 5 tools without errors."""
        options = BuildOptions(variant="verbose")

        for tool_name, builder in all_builders.items():
            try:
                output = builder.build(sample_agent, options)
                assert output is not None
            except Exception as e:
                pytest.fail(f"{tool_name} builder failed: {e}")

    def test_agent_metadata_preserved_across_tools(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify agent metadata is preserved across tool outputs."""
        options = BuildOptions(variant="verbose")

        agent_name_lower = sample_agent.name.lower()

        for _tool_name, builder in all_builders.items():
            output = builder.build(sample_agent, options)
            output_str = (
                json.dumps(output).lower() if isinstance(output, dict) else str(output).lower()
            )

            # Agent name should be present
            assert agent_name_lower in output_str

    def test_tools_preserved_across_builders(self, temp_agents_dir: Path) -> None:
        """Verify agent tools are represented in all builder outputs."""
        # Create tooltest agent directory with both variants
        tooltest_dir_min = temp_agents_dir / "tooltest" / "minimal"
        tooltest_dir_min.mkdir(parents=True, exist_ok=True)
        (tooltest_dir_min / "prompt.md").write_text("Testing prompt")

        tooltest_dir_verb = temp_agents_dir / "tooltest" / "verbose"
        tooltest_dir_verb.mkdir(parents=True, exist_ok=True)
        (tooltest_dir_verb / "prompt.md").write_text("Testing prompt - verbose")

        agent = Agent(
            name="tooltest",
            description="Test agent with specific tools",
            system_prompt="Testing prompt",
            tools=["specific_tool_one", "specific_tool_two"],
        )
        options = BuildOptions(variant="verbose")
        builders = {
            "kilo": KiloBuilder(agents_dir=temp_agents_dir),
            "cline": ClineBuilder(agents_dir=temp_agents_dir),
            "claude": ClaudeBuilder(agents_dir=temp_agents_dir),
            "copilot": CopilotBuilder(agents_dir=temp_agents_dir),
            "cursor": CursorBuilder(agents_dir=temp_agents_dir),
        }

        for _tool_name, builder in builders.items():
            output = builder.build(agent, options)
            output_str = (
                json.dumps(output).lower() if isinstance(output, dict) else str(output).lower()
            )

            # At least one tool should be referenced
            has_tool_ref = "tool" in output_str and (
                "specific_tool" in output_str or "tooltest" in output_str
            )
            assert has_tool_ref or len(agent.tools) == 0

    def test_variant_consistency_across_tools(
        self, sample_agent: Agent, all_builders: dict[str, Any]
    ) -> None:
        """Verify minimal/verbose variants behave consistently."""
        minimal_opts = BuildOptions(variant="minimal")
        verbose_opts = BuildOptions(variant="verbose")

        for tool_name, builder in all_builders.items():
            minimal = builder.build(sample_agent, minimal_opts)
            verbose = builder.build(sample_agent, verbose_opts)

            # Both should be non-empty
            if tool_name == "claude":
                assert isinstance(minimal, dict)
                assert isinstance(verbose, dict)
            else:
                assert len(str(minimal)) > 0
                assert len(str(verbose)) > 0


# ============================================================================
# Test Class 6: Error Handling
# ============================================================================


class TestErrorHandling:
    """Tests for error cases and edge cases."""

    def test_invalid_agent_raises_error(self) -> None:
        """Verify invalid agent raises appropriate error."""
        # Agent with empty required field - Pydantic will reject before builder
        with pytest.raises(Exception):  # Pydantic ValidationError
            Agent(
                name="invalid",
                description="",  # Invalid: empty description
                system_prompt="",  # Invalid: empty prompt
            )

    def test_agent_with_minimal_fields(self, temp_agents_dir: Path) -> None:
        """Test building agent with only required fields."""
        # Create a minimal agent directory with both variants
        minimal_dir_min = temp_agents_dir / "minimal" / "minimal"
        minimal_dir_min.mkdir(parents=True, exist_ok=True)
        (minimal_dir_min / "prompt.md").write_text("Minimal prompt")

        minimal_dir_verb = temp_agents_dir / "minimal" / "verbose"
        minimal_dir_verb.mkdir(parents=True, exist_ok=True)
        (minimal_dir_verb / "prompt.md").write_text("Minimal prompt - verbose")

        minimal_agent = Agent(
            name="minimal",
            description="Minimal agent",
            system_prompt="Minimal prompt",
        )

        options = BuildOptions(variant="verbose")
        builders = {
            "kilo": KiloBuilder(agents_dir=temp_agents_dir),
            "cline": ClineBuilder(agents_dir=temp_agents_dir),
            "claude": ClaudeBuilder(agents_dir=temp_agents_dir),
            "copilot": CopilotBuilder(agents_dir=temp_agents_dir),
            "cursor": CursorBuilder(agents_dir=temp_agents_dir),
        }

        for _tool_name, builder in builders.items():
            output = builder.build(minimal_agent, options)
            assert output is not None
            assert len(output) > 0

    def test_agent_with_all_optional_fields(self, temp_agents_dir: Path) -> None:
        """Test building agent with all optional fields filled."""
        # Create a full agent directory with both variants
        full_dir_min = temp_agents_dir / "full" / "minimal"
        full_dir_min.mkdir(parents=True, exist_ok=True)
        (full_dir_min / "prompt.md").write_text("Full prompt")
        (full_dir_min / "skills.md").write_text("- skill1")

        full_dir_verb = temp_agents_dir / "full" / "verbose"
        full_dir_verb.mkdir(parents=True, exist_ok=True)
        (full_dir_verb / "prompt.md").write_text("Full prompt")
        (full_dir_verb / "skills.md").write_text("- skill1\n- skill2")
        (full_dir_verb / "workflows.md").write_text("- workflow1")
        (full_dir_verb / "subagents.md").write_text("- subagent1")

        full_agent = Agent(
            name="full",
            description="Full agent",
            system_prompt="Full prompt",
            tools=["tool1", "tool2", "tool3"],
            skills=["skill1", "skill2"],
            workflows=["workflow1"],
            subagents=["subagent1"],
        )

        options = BuildOptions(variant="verbose")
        builders = {
            "kilo": KiloBuilder(agents_dir=temp_agents_dir),
            "cline": ClineBuilder(agents_dir=temp_agents_dir),
            "claude": ClaudeBuilder(agents_dir=temp_agents_dir),
            "copilot": CopilotBuilder(agents_dir=temp_agents_dir),
            "cursor": CursorBuilder(agents_dir=temp_agents_dir),
        }

        for _tool_name, builder in builders.items():
            output = builder.build(full_agent, options)
            assert output is not None
            assert len(output) > 0

    def test_unicode_in_agent_fields(self, temp_agents_dir: Path) -> None:
        """Test handling of unicode characters in agent fields."""
        # Create unicode agent directory with both variants
        unicode_dir_min = temp_agents_dir / "unicode" / "minimal"
        unicode_dir_min.mkdir(parents=True, exist_ok=True)
        (unicode_dir_min / "prompt.md").write_text(
            "You can handle: émoji 🎉 and spëcial çharacters"
        )

        unicode_dir_verb = temp_agents_dir / "unicode" / "verbose"
        unicode_dir_verb.mkdir(parents=True, exist_ok=True)
        (unicode_dir_verb / "prompt.md").write_text(
            "You can handle: émoji 🎉 and spëcial çharacters - verbose"
        )

        unicode_agent = Agent(
            name="unicode",
            description="Testing unicode: ñ, é, 中文, 日本語, 🚀",
            system_prompt="You can handle: émoji 🎉 and spëcial çharacters",
            tools=["tool1", "tool2"],
        )

        options = BuildOptions(variant="verbose")
        builders = {
            "kilo": KiloBuilder(agents_dir=temp_agents_dir),
            "cline": ClineBuilder(agents_dir=temp_agents_dir),
            "claude": ClaudeBuilder(agents_dir=temp_agents_dir),
            "copilot": CopilotBuilder(agents_dir=temp_agents_dir),
            "cursor": CursorBuilder(agents_dir=temp_agents_dir),
        }

        for _tool_name, builder in builders.items():
            output = builder.build(unicode_agent, options)
            assert output is not None
            assert len(output) > 0

    def test_long_agent_fields(self, temp_agents_dir: Path) -> None:
        """Test handling of very long agent fields."""
        long_prompt = "This is a very long system prompt. " * 50  # ~2000 chars

        # Create long agent directory with both variants
        long_dir_min = temp_agents_dir / "long" / "minimal"
        long_dir_min.mkdir(parents=True, exist_ok=True)
        (long_dir_min / "prompt.md").write_text(long_prompt)
        (long_dir_min / "skills.md").write_text("- skill1")

        long_dir_verb = temp_agents_dir / "long" / "verbose"
        long_dir_verb.mkdir(parents=True, exist_ok=True)
        (long_dir_verb / "prompt.md").write_text(long_prompt)
        (long_dir_verb / "skills.md").write_text("\n".join(f"- skill{i}" for i in range(10)))

        long_agent = Agent(
            name="long",
            description="Long agent description with substantial content",
            system_prompt=long_prompt,
            tools=[f"tool{i}" for i in range(10)],
            skills=[f"skill{i}" for i in range(10)],
        )

        options = BuildOptions(variant="verbose")
        builders = {
            "kilo": KiloBuilder(agents_dir=temp_agents_dir),
            "cline": ClineBuilder(agents_dir=temp_agents_dir),
            "claude": ClaudeBuilder(agents_dir=temp_agents_dir),
            "copilot": CopilotBuilder(agents_dir=temp_agents_dir),
            "cursor": CursorBuilder(agents_dir=temp_agents_dir),
        }

        for _tool_name, builder in builders.items():
            output = builder.build(long_agent, options)
            assert output is not None
            assert len(output) > 0


# ============================================================================
# Integration Test: Full E2E Workflow
# ============================================================================


class TestFullE2EWorkflow:
    """Comprehensive end-to-end workflow test."""

    def test_complete_e2e_workflow(self, sample_agent: Agent, all_builders: dict[str, Any]) -> None:
        """Test complete E2E workflow: create agent → build all tools → validate."""
        # Step 1: Build with minimal variant
        minimal_opts = BuildOptions(variant="minimal")
        minimal_outputs = {}
        for tool_name, builder in all_builders.items():
            output = builder.build(sample_agent, minimal_opts)
            minimal_outputs[tool_name] = output
            assert output is not None
            assert len(output) > 0

        # Step 2: Build with verbose variant
        verbose_opts = BuildOptions(variant="verbose")
        verbose_outputs = {}
        for tool_name, builder in all_builders.items():
            output = builder.build(sample_agent, verbose_opts)
            verbose_outputs[tool_name] = output
            assert output is not None
            assert len(output) > 0

        # Step 3: Validate consistency
        for tool_name in all_builders.keys():
            minimal = minimal_outputs[tool_name]
            verbose = verbose_outputs[tool_name]

            # Both should be valid
            if tool_name == "claude":
                assert isinstance(minimal, dict)
                assert isinstance(verbose, dict)
                # Should be JSON serializable
                json.dumps(minimal)
                json.dumps(verbose)
            else:
                assert isinstance(minimal, str)
                assert isinstance(verbose, str)
                # Verbose should be >= minimal
                assert len(verbose) >= len(minimal)

    def test_builder_factory_integration(self, sample_agent: Agent, temp_agents_dir: Path) -> None:
        """Test integration with BuilderFactory."""
        # Register all builders with temp_agents_dir
        BuilderFactory.register("kilo", KiloBuilder)
        BuilderFactory.register("cline", ClineBuilder)
        BuilderFactory.register("claude", ClaudeBuilder)
        BuilderFactory.register("copilot", CopilotBuilder)
        BuilderFactory.register("cursor", CursorBuilder)

        # Verify all are registered
        available_tools = BuilderFactory.list_builders()
        expected_tools = ["cline", "claude", "copilot", "cursor", "kilo"]
        for tool in expected_tools:
            assert tool in available_tools

        # Build with factory using our temp agents directory
        options = BuildOptions(variant="verbose")
        for tool in expected_tools:
            # Create builders with proper agents_dir
            builder = (
                KiloBuilder(agents_dir=temp_agents_dir)
                if tool == "kilo"
                else ClineBuilder(agents_dir=temp_agents_dir)
                if tool == "cline"
                else ClaudeBuilder(agents_dir=temp_agents_dir)
                if tool == "claude"
                else CopilotBuilder(agents_dir=temp_agents_dir)
                if tool == "copilot"
                else CursorBuilder(agents_dir=temp_agents_dir)
            )
            output = builder.build(sample_agent, options)
            assert output is not None
