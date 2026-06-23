"""Coverage-focused unit tests for ComponentComposer.

Exercises every public composition method (markdown, YAML+markdown, JSON)
plus the private section formatters, covering default ordering, section
inclusion/exclusion, empty inputs, fallback flags, and frontmatter typing
branches.
"""

import pytest

from prompticorn.builders.component_composer import ComponentComposer
from prompticorn.builders.component_selector import ComponentBundle, Variant
from prompticorn.ir.models import Agent


@pytest.fixture
def agent_full():
    """Agent populated with tools and subagents."""
    return Agent(
        name="test-agent",
        description="A fully populated test agent",
        system_prompt="You are a test",
        tools=["read", "write"],
        skills=["skill-a"],
        workflows=["wf-a"],
        subagents=["sub-a", "sub-b"],
    )


@pytest.fixture
def agent_empty():
    """Agent with no tools, skills, workflows, or subagents."""
    return Agent(
        name="bare-agent",
        description="An agent with empty lists",
        system_prompt="You are bare",
        tools=[],
        skills=[],
        workflows=[],
        subagents=[],
    )


@pytest.fixture
def bundle_full():
    """Bundle with prompt, skills, and workflow content."""
    return ComponentBundle(
        variant=Variant.MINIMAL,
        prompt="The system prompt body",
        skills="  Skill content with surrounding space  ",
        workflow="  Workflow content with space  ",
        fallback_used=False,
    )


@pytest.fixture
def bundle_minimal():
    """Bundle with only a prompt and no optional content."""
    return ComponentBundle(
        variant=Variant.VERBOSE,
        prompt="Prompt only",
        skills=None,
        workflow=None,
        fallback_used=True,
    )


class TestComposeMarkdown:
    """Tests for ComponentComposer.compose_markdown."""

    def test_default_includes_all_sections(self, bundle_full, agent_full):
        # Arrange / Act
        result = ComponentComposer.compose_markdown(bundle_full, agent_full)

        # Assert
        assert "# System Prompt" in result
        assert "The system prompt body" in result
        assert "# Tools" in result
        assert "- read" in result
        assert "- write" in result
        assert "# Skills" in result
        assert "Skill content with surrounding space" in result
        assert "# Workflows" in result
        assert "Workflow content with space" in result
        assert "# Subagents" in result
        assert "- sub-a" in result
        assert "- sub-b" in result

    def test_section_ordering(self, bundle_full, agent_full):
        # Arrange / Act
        result = ComponentComposer.compose_markdown(bundle_full, agent_full)

        # Assert order: prompt < tools < skills < workflows < subagents
        positions = [
            result.index("# System Prompt"),
            result.index("# Tools"),
            result.index("# Skills"),
            result.index("# Workflows"),
            result.index("# Subagents"),
        ]
        assert positions == sorted(positions)

    def test_skills_and_workflow_are_stripped(self, bundle_full, agent_full):
        # Act
        result = ComponentComposer.compose_markdown(bundle_full, agent_full)

        # Assert leading/trailing whitespace removed by formatters
        assert "  Skill content" not in result
        assert "  Workflow content" not in result

    def test_include_sections_subset(self, bundle_full, agent_full):
        # Act: only request the prompt section
        result = ComponentComposer.compose_markdown(
            bundle_full, agent_full, include_sections=["prompt"]
        )

        # Assert
        assert "# System Prompt" in result
        assert "# Tools" not in result
        assert "# Skills" not in result
        assert "# Workflows" not in result
        assert "# Subagents" not in result

    def test_include_sections_empty_list(self, bundle_full, agent_full):
        # Act: empty list excludes everything
        result = ComponentComposer.compose_markdown(bundle_full, agent_full, include_sections=[])

        # Assert
        assert result == ""

    def test_empty_agent_and_bundle_only_prompt(self, bundle_minimal, agent_empty):
        # Act: empty lists / None optional content suppress non-prompt sections
        result = ComponentComposer.compose_markdown(bundle_minimal, agent_empty)

        # Assert
        assert "# System Prompt" in result
        assert "Prompt only" in result
        assert "# Tools" not in result
        assert "# Skills" not in result
        assert "# Workflows" not in result
        assert "# Subagents" not in result

    def test_requested_section_skipped_when_data_absent(self, bundle_minimal, agent_empty):
        # Act: request all sections but the data is absent
        result = ComponentComposer.compose_markdown(
            bundle_minimal,
            agent_empty,
            include_sections=["prompt", "tools", "skills", "workflows", "subagents"],
        )

        # Assert only the prompt heading appears
        assert result.count("#") == result.count("# System Prompt")


class TestComposeYamlMarkdown:
    """Tests for ComponentComposer.compose_yaml_markdown."""

    def test_default_frontmatter_fields(self, bundle_minimal, agent_empty):
        # Act
        result = ComponentComposer.compose_yaml_markdown(bundle_minimal, agent_empty)

        # Assert structure and default-derived fields
        assert result.startswith("---\n")
        assert "name: bare-agent" in result
        assert "variant: verbose" in result
        assert "fallback_used: true" in result
        assert "\n---\n\n# System Prompt" in result

    def test_fallback_used_false_renders_lowercase_bool(self, bundle_full, agent_full):
        # Act
        result = ComponentComposer.compose_yaml_markdown(bundle_full, agent_full)

        # Assert bool branch lowercases the value
        assert "fallback_used: false" in result

    def test_custom_frontmatter_preserved(self, bundle_full, agent_full):
        # Arrange
        frontmatter = {"name": "override", "custom": "value"}

        # Act
        result = ComponentComposer.compose_yaml_markdown(
            bundle_full, agent_full, frontmatter=frontmatter
        )

        # Assert custom name kept and defaults still filled in
        assert "name: override" in result
        assert "custom: value" in result
        assert "variant: minimal" in result

    def test_string_with_special_chars_is_quoted(self, bundle_full, agent_full):
        # Arrange: value containing a colon triggers the quoting branch
        frontmatter = {"title": "a: special"}

        # Act
        result = ComponentComposer.compose_yaml_markdown(
            bundle_full, agent_full, frontmatter=frontmatter
        )

        # Assert
        assert 'title: "a: special"' in result

    def test_numeric_values(self, bundle_full, agent_full):
        # Arrange: int and float exercise the numeric branch
        frontmatter = {"count": 3, "ratio": 1.5}

        # Act
        result = ComponentComposer.compose_yaml_markdown(
            bundle_full, agent_full, frontmatter=frontmatter
        )

        # Assert
        assert "count: 3" in result
        assert "ratio: 1.5" in result

    def test_list_value_rendered_as_block(self, bundle_full, agent_full):
        # Arrange
        frontmatter = {"tags": ["one", "two"]}

        # Act
        result = ComponentComposer.compose_yaml_markdown(
            bundle_full, agent_full, frontmatter=frontmatter
        )

        # Assert list branch renders block style
        assert "tags:" in result
        assert "  - one" in result
        assert "  - two" in result

    def test_fallback_else_branch_for_unknown_type(self, bundle_full, agent_full):
        # Arrange: a dict value falls through to the generic else branch
        frontmatter = {"meta": {"k": "v"}}

        # Act
        result = ComponentComposer.compose_yaml_markdown(
            bundle_full, agent_full, frontmatter=frontmatter
        )

        # Assert generic str() rendering
        assert "meta: {'k': 'v'}" in result


class TestComposeJson:
    """Tests for ComponentComposer.compose_json."""

    def test_structure_and_values(self, bundle_full, agent_full):
        # Act
        result = ComponentComposer.compose_json(bundle_full, agent_full)

        # Assert agent block
        assert result["agent"]["name"] == "test-agent"
        assert result["agent"]["description"] == "A fully populated test agent"
        assert result["agent"]["tools"] == ["read", "write"]
        assert result["agent"]["skills"] == ["skill-a"]
        assert result["agent"]["workflows"] == ["wf-a"]
        assert result["agent"]["subagents"] == ["sub-a", "sub-b"]

        # Assert components block
        assert result["components"]["variant"] == "minimal"
        assert result["components"]["fallback_used"] is False
        assert result["components"]["prompt"] == "The system prompt body"
        assert result["components"]["skills"] == "  Skill content with surrounding space  "
        assert result["components"]["workflow"] == "  Workflow content with space  "

    def test_json_with_none_optionals(self, bundle_minimal, agent_empty):
        # Act
        result = ComponentComposer.compose_json(bundle_minimal, agent_empty)

        # Assert
        assert result["components"]["variant"] == "verbose"
        assert result["components"]["fallback_used"] is True
        assert result["components"]["skills"] is None
        assert result["components"]["workflow"] is None
        assert result["agent"]["tools"] == []


class TestFormatters:
    """Tests for the section-formatting helpers."""

    def test_format_tools_section_with_items(self):
        # Act
        result = ComponentComposer._format_tools_section(["a", "b"])

        # Assert
        assert result == "- a\n- b"

    def test_format_tools_section_empty(self):
        # Act / Assert
        assert ComponentComposer._format_tools_section([]) == ""

    def test_format_subagents_section_with_items(self):
        # Act
        result = ComponentComposer._format_subagents_section(["x", "y"])

        # Assert
        assert result == "- x\n- y"

    def test_format_subagents_section_empty(self):
        # Act / Assert
        assert ComponentComposer._format_subagents_section([]) == ""

    def test_format_skills_section_strips(self):
        # Act / Assert
        assert ComponentComposer._format_skills_section("  hello  ") == "hello"

    def test_format_workflows_section_strips(self):
        # Act / Assert
        assert ComponentComposer._format_workflows_section("  flow  ") == "flow"
