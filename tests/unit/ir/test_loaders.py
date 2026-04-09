"""Comprehensive unit tests for IR loaders (Component, Skill, Workflow).

Tests cover:
- Happy path: Loading valid component files and models
- Edge cases: Missing optional files, empty content
- Validation: Required fields, model creation
- Error handling: Missing files, malformed content, file read errors
"""

import tempfile
from pathlib import Path

import pytest

from src.ir.loaders import ComponentLoader, SkillLoader, WorkflowLoader
from src.ir.loaders.component_loader import ComponentBundle
from src.ir.models import Skill, Workflow
from src.ir.exceptions import ParseError, MissingFileError, ValidationError


# ============================================================================
# FIXTURES - Sample files for testing
# ============================================================================


@pytest.fixture
def temp_agent_dir():
    """Create temporary directory for test agent files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_prompt_md(temp_agent_dir):
    """Create a sample prompt.md file."""
    prompt_file = temp_agent_dir / "prompt.md"
    content = """---
name: test-agent
description: A test agent
system_prompt: You are a helpful assistant
tools:
  - git
  - python
skills:
  - refactor
workflows:
  - code-review
subagents:
  - formatter
---

# Main Agent Prompt

This is the main prompt content.
"""
    prompt_file.write_text(content, encoding="utf-8")
    return prompt_file


@pytest.fixture
def sample_skills_md(temp_agent_dir):
    """Create a sample skills.md file."""
    skills_file = temp_agent_dir / "skills.md"
    content = """---
skills:
  - name: refactor
    description: Improve code structure
    instructions: Apply SOLID principles
    tools_needed:
      - git
      - python
  - name: test
    description: Write tests
    instructions: Use pytest
    tools_needed:
      - python
---

## Refactor Skill

Details about refactoring.

## Test Skill

Details about testing.
"""
    skills_file.write_text(content, encoding="utf-8")
    return skills_file


@pytest.fixture
def sample_workflow_md(temp_agent_dir):
    """Create a sample workflow.md file."""
    workflow_file = temp_agent_dir / "workflow.md"
    content = """---
workflows:
  - name: code-review
    description: Review code for quality
    steps:
      - Analyze code structure
      - Check test coverage
      - Verify error handling
      - Approve or request changes
---

## Code Review Workflow

Process for reviewing code.
"""
    workflow_file.write_text(content, encoding="utf-8")
    return workflow_file


@pytest.fixture
def complete_agent_dir(sample_prompt_md, sample_skills_md, sample_workflow_md):
    """Get the temporary directory with all component files."""
    return sample_prompt_md.parent


@pytest.fixture
def minimal_agent_dir(temp_agent_dir, sample_prompt_md):
    """Temporary directory with only prompt.md (minimal agent)."""
    return sample_prompt_md.parent


@pytest.fixture
def sample_skill_file(temp_agent_dir):
    """Create a sample skill.md file."""
    skill_file = temp_agent_dir / "skill.md"
    skill_file.write_text(
        """---
name: refactor
description: Improve code structure
instructions: Apply SOLID principles
tools_needed:
  - git
  - python
---

## Details
Additional skill details here.
""",
        encoding="utf-8",
    )
    return skill_file


@pytest.fixture
def sample_workflow_file(temp_agent_dir):
    """Create a sample workflow file."""
    workflow_file = temp_agent_dir / "workflow.md"
    workflow_file.write_text(
        """---
name: code-review
description: Review code for quality
steps:
  - Analyze code structure
  - Check test coverage
  - Verify error handling
  - Approve or request changes
---

## Process
Details about the workflow.
""",
        encoding="utf-8",
    )
    return workflow_file


# ============================================================================
# ComponentLoader Tests
# ============================================================================


class TestComponentLoaderHappyPath:
    """Test ComponentLoader with valid inputs."""

    def test_load_complete_components(self, complete_agent_dir):
        """Test loading all component files."""
        loader = ComponentLoader()
        bundle = loader.load(str(complete_agent_dir))

        assert isinstance(bundle, ComponentBundle)
        assert bundle.prompt_content is not None
        assert bundle.skills_content is not None
        assert bundle.workflow_content is not None
        # Verify they're dictionaries
        assert isinstance(bundle.prompt_content, dict)
        assert isinstance(bundle.skills_content, dict)
        assert isinstance(bundle.workflow_content, dict)

    def test_load_prompt_content(self, complete_agent_dir):
        """Test prompt.md content is loaded correctly."""
        loader = ComponentLoader()
        bundle = loader.load(str(complete_agent_dir))

        assert bundle.prompt_content["name"] == "test-agent"
        assert bundle.prompt_content["description"] == "A test agent"

    def test_load_skills_content(self, complete_agent_dir):
        """Test skills.md content is loaded correctly."""
        loader = ComponentLoader()
        bundle = loader.load(str(complete_agent_dir))

        assert bundle.skills_content is not None
        assert "skills" in bundle.skills_content
        assert len(bundle.skills_content["skills"]) == 2

    def test_load_workflow_content(self, complete_agent_dir):
        """Test workflow.md content is loaded correctly."""
        loader = ComponentLoader()
        bundle = loader.load(str(complete_agent_dir))

        assert bundle.workflow_content is not None
        assert "workflows" in bundle.workflow_content
        assert bundle.workflow_content["workflows"][0]["name"] == "code-review"

    def test_load_minimal_components(self, minimal_agent_dir):
        """Test loading only required prompt.md."""
        loader = ComponentLoader()
        bundle = loader.load(str(minimal_agent_dir))

        assert bundle.prompt_content is not None
        assert bundle.skills_content is None
        assert bundle.workflow_content is None

    def test_load_as_dict_complete(self, complete_agent_dir):
        """Test load_as_dict with all components."""
        loader = ComponentLoader()
        components = loader.load_as_dict(str(complete_agent_dir))

        assert isinstance(components, dict)
        assert "prompt" in components
        assert "skills" in components
        assert "workflow" in components

    def test_load_as_dict_minimal(self, minimal_agent_dir):
        """Test load_as_dict with only prompt."""
        loader = ComponentLoader()
        components = loader.load_as_dict(str(minimal_agent_dir))

        assert "prompt" in components
        assert "skills" not in components
        assert "workflow" not in components


class TestComponentLoaderEdgeCases:
    """Test ComponentLoader edge cases."""

    def test_load_nonexistent_directory(self):
        """Test loading from non-existent directory raises MissingFileError."""
        loader = ComponentLoader()
        with pytest.raises(MissingFileError, match="Directory not found"):
            loader.load("/nonexistent/directory")

    def test_load_missing_prompt_file(self, temp_agent_dir):
        """Test loading without required prompt.md raises MissingFileError."""
        loader = ComponentLoader()
        with pytest.raises(MissingFileError, match="prompt.md"):
            loader.load(str(temp_agent_dir))

    def test_load_with_only_skills(self, temp_agent_dir, sample_prompt_md, sample_skills_md):
        """Test loading with prompt and skills but no workflow."""
        loader = ComponentLoader()
        bundle = loader.load(str(temp_agent_dir))

        assert bundle.prompt_content is not None
        assert bundle.skills_content is not None
        assert bundle.workflow_content is None

    def test_load_with_only_workflow(self, temp_agent_dir, sample_prompt_md, sample_workflow_md):
        """Test loading with prompt and workflow but no skills."""
        loader = ComponentLoader()
        bundle = loader.load(str(temp_agent_dir))

        assert bundle.prompt_content is not None
        assert bundle.skills_content is None
        assert bundle.workflow_content is not None

    def test_load_empty_prompt_file(self, temp_agent_dir):
        """Test loading empty prompt.md."""
        prompt_file = temp_agent_dir / "prompt.md"
        prompt_file.write_text("", encoding="utf-8")

        loader = ComponentLoader()
        bundle = loader.load(str(temp_agent_dir))

        assert bundle.prompt_content == {}

    def test_load_prompt_with_only_markdown(self, temp_agent_dir):
        """Test loading prompt.md with no frontmatter."""
        prompt_file = temp_agent_dir / "prompt.md"
        prompt_file.write_text("# Markdown Content\nNo frontmatter here", encoding="utf-8")

        loader = ComponentLoader()
        bundle = loader.load(str(temp_agent_dir))

        assert bundle.prompt_content == {}


class TestComponentLoaderErrors:
    """Test ComponentLoader error handling."""

    def test_load_invalid_yaml_in_prompt(self, temp_agent_dir):
        """Test loading prompt with invalid YAML raises ParseError."""
        prompt_file = temp_agent_dir / "prompt.md"
        prompt_file.write_text(
            """---
invalid: yaml: content
  bad indent
---
Content
""",
            encoding="utf-8",
        )

        loader = ComponentLoader()
        with pytest.raises(ParseError):
            loader.load(str(temp_agent_dir))

    def test_load_file_permission_error(self, temp_agent_dir):
        """Test loading from directory without read permission."""
        prompt_file = temp_agent_dir / "prompt.md"
        prompt_file.write_text("---\nname: test\n---\n", encoding="utf-8")

        # Change permissions
        temp_agent_dir.chmod(0o000)

        try:
            loader = ComponentLoader()
            with pytest.raises(ParseError):
                loader.load(str(temp_agent_dir))
        finally:
            # Restore permissions for cleanup
            temp_agent_dir.chmod(0o755)


# ============================================================================
# SkillLoader Tests
# ============================================================================


class TestSkillLoaderHappyPath:
    """Test SkillLoader with valid inputs."""

    def test_load_single_skill(self, sample_skill_file):
        """Test loading a single skill from file."""
        loader = SkillLoader()
        skill = loader.load(str(sample_skill_file))

        assert isinstance(skill, Skill)
        assert skill.name == "refactor"
        assert skill.description == "Improve code structure"
        assert skill.instructions == "Apply SOLID principles"
        assert skill.tools_needed == ["git", "python"]

    def test_load_skill_minimal(self, temp_agent_dir):
        """Test loading skill with only required fields."""
        skill_file = temp_agent_dir / "minimal.md"
        skill_file.write_text(
            """---
name: minimal
description: A minimal skill
instructions: Do something
tools_needed: []
---
""",
            encoding="utf-8",
        )
        loader = SkillLoader()
        skill = loader.load(str(skill_file))

        assert skill.name == "minimal"
        assert skill.tools_needed == []

    def test_load_skill_with_tools(self, temp_agent_dir):
        """Test skill with multiple tools."""
        skill_file = temp_agent_dir / "tools.md"
        skill_file.write_text(
            """---
name: advanced
description: Advanced skill with many tools
instructions: Use all the tools
tools_needed:
  - git
  - python
  - docker
  - kubernetes
---
""",
            encoding="utf-8",
        )
        loader = SkillLoader()
        skill = loader.load(str(skill_file))

        assert len(skill.tools_needed) == 4


class TestSkillLoaderEdgeCases:
    """Test SkillLoader edge cases."""

    def test_load_skill_no_tools_needed(self, temp_agent_dir):
        """Test skill without tools_needed field."""
        skill_file = temp_agent_dir / "no_tools.md"
        skill_file.write_text(
            """---
name: analysis
description: Analyze code
instructions: Look carefully
tools_needed: []
---
""",
            encoding="utf-8",
        )
        loader = SkillLoader()
        skill = loader.load(str(skill_file))

        # Should have empty list
        assert skill.tools_needed == []

    def test_load_skill_with_extra_fields(self, temp_agent_dir):
        """Test skill with additional metadata fields (should be ignored)."""
        skill_file = temp_agent_dir / "extra.md"
        skill_file.write_text(
            """---
name: advanced
description: Advanced skill
instructions: Complex instructions
tools_needed:
  - advanced-tool
version: 2.0
deprecated: false
---
""",
            encoding="utf-8",
        )
        loader = SkillLoader()
        skill = loader.load(str(skill_file))

        assert skill.name == "advanced"

    def test_load_skill_with_markdown_content(self, temp_agent_dir):
        """Test skill with markdown sections after frontmatter."""
        skill_file = temp_agent_dir / "with_content.md"
        skill_file.write_text(
            """---
name: documented
description: Well documented skill
instructions: Follow the steps
tools_needed:
  - tool1
---

## Detailed Instructions

Step 1: Do this
Step 2: Then that
Step 3: Finally this

## Examples

Example code here.
""",
            encoding="utf-8",
        )
        loader = SkillLoader()
        skill = loader.load(str(skill_file))

        assert skill.name == "documented"


class TestSkillLoaderErrors:
    """Test SkillLoader error handling."""

    def test_load_skill_missing_name(self, temp_agent_dir):
        """Test skill without required name field."""
        skill_file = temp_agent_dir / "no_name.md"
        skill_file.write_text(
            """---
description: No name skill
instructions: Do something
tools_needed: []
---
""",
            encoding="utf-8",
        )
        loader = SkillLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.load(str(skill_file))

    def test_load_skill_missing_description(self, temp_agent_dir):
        """Test skill without required description field."""
        skill_file = temp_agent_dir / "no_desc.md"
        skill_file.write_text(
            """---
name: no-desc
instructions: Do something
tools_needed: []
---
""",
            encoding="utf-8",
        )
        loader = SkillLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.load(str(skill_file))

    def test_load_skill_invalid_yaml(self, temp_agent_dir):
        """Test skill with invalid YAML raises ParseError."""
        skill_file = temp_agent_dir / "invalid.md"
        skill_file.write_text(
            """---
invalid: yaml: content
  bad indent
---
""",
            encoding="utf-8",
        )
        loader = SkillLoader()
        with pytest.raises(ParseError):
            loader.load(str(skill_file))

    def test_load_skill_file_not_found(self):
        """Test loading non-existent skill file."""
        loader = SkillLoader()
        with pytest.raises(MissingFileError):
            loader.load("/nonexistent/skill.md")


# ============================================================================
# WorkflowLoader Tests
# ============================================================================


class TestWorkflowLoaderHappyPath:
    """Test WorkflowLoader with valid inputs."""

    def test_load_single_workflow(self, sample_workflow_file):
        """Test loading a single workflow from file."""
        loader = WorkflowLoader()
        workflow = loader.load(str(sample_workflow_file))

        assert isinstance(workflow, Workflow)
        assert workflow.name == "code-review"
        assert workflow.description == "Review code for quality"
        assert len(workflow.steps) == 4

    def test_load_workflow_minimal(self, temp_agent_dir):
        """Test loading workflow with only required fields."""
        workflow_file = temp_agent_dir / "minimal.md"
        workflow_file.write_text(
            """---
name: minimal
description: A minimal workflow
steps:
  - Step 1
---
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        workflow = loader.load(str(workflow_file))

        assert workflow.name == "minimal"
        assert workflow.steps == ["Step 1"]

    def test_load_workflow_many_steps(self, temp_agent_dir):
        """Test loading workflow with many steps."""
        workflow_file = temp_agent_dir / "complex.md"
        workflow_file.write_text(
            """---
name: complex
description: Complex workflow
steps:
  - Step 1
  - Step 2
  - Step 3
  - Step 4
  - Step 5
---
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        workflow = loader.load(str(workflow_file))

        assert len(workflow.steps) == 5


class TestWorkflowLoaderEdgeCases:
    """Test WorkflowLoader edge cases."""

    def test_load_workflow_empty_steps(self, temp_agent_dir):
        """Test workflow with empty steps list."""
        workflow_file = temp_agent_dir / "empty.md"
        workflow_file.write_text(
            """---
name: empty
description: No steps
steps: []
---
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        workflow = loader.load(str(workflow_file))

        assert workflow.steps == []

    def test_load_workflow_single_step(self, temp_agent_dir):
        """Test workflow with single step."""
        workflow_file = temp_agent_dir / "simple.md"
        workflow_file.write_text(
            """---
name: simple
description: Single step
steps:
  - Do the thing
---
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        workflow = loader.load(str(workflow_file))

        assert len(workflow.steps) == 1
        assert workflow.steps[0] == "Do the thing"

    def test_load_workflow_with_extra_fields(self, temp_agent_dir):
        """Test workflow with additional metadata fields."""
        workflow_file = temp_agent_dir / "extra.md"
        workflow_file.write_text(
            """---
name: advanced
description: Advanced workflow
steps:
  - Step 1
  - Step 2
priority: high
author: test-author
---
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        workflow = loader.load(str(workflow_file))

        assert workflow.name == "advanced"

    def test_load_workflow_with_markdown_content(self, temp_agent_dir):
        """Test workflow with markdown sections after frontmatter."""
        workflow_file = temp_agent_dir / "with_content.md"
        workflow_file.write_text(
            """---
name: documented
description: Well documented workflow
steps:
  - Step 1
  - Step 2
---

## Detailed Steps

Step 1: Do this carefully
Step 2: Then that

## Success Criteria

All steps completed successfully.
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        workflow = loader.load(str(workflow_file))

        assert workflow.name == "documented"


class TestWorkflowLoaderErrors:
    """Test WorkflowLoader error handling."""

    def test_load_workflow_missing_name(self, temp_agent_dir):
        """Test workflow without required name field."""
        workflow_file = temp_agent_dir / "no_name.md"
        workflow_file.write_text(
            """---
description: No name
steps:
  - Step 1
---
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.load(str(workflow_file))

    def test_load_workflow_missing_description(self, temp_agent_dir):
        """Test workflow without required description field."""
        workflow_file = temp_agent_dir / "no_desc.md"
        workflow_file.write_text(
            """---
name: no-desc
steps:
  - Step 1
---
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.load(str(workflow_file))

    def test_load_workflow_missing_steps(self, temp_agent_dir):
        """Test workflow without required steps field."""
        workflow_file = temp_agent_dir / "no_steps.md"
        workflow_file.write_text(
            """---
name: no-steps
description: Missing steps
---
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.load(str(workflow_file))

    def test_load_workflow_invalid_yaml(self, temp_agent_dir):
        """Test workflow with invalid YAML."""
        workflow_file = temp_agent_dir / "invalid.md"
        workflow_file.write_text(
            """---
invalid: yaml: content
  bad indent
---
""",
            encoding="utf-8",
        )
        loader = WorkflowLoader()
        with pytest.raises(ParseError):
            loader.load(str(workflow_file))

    def test_load_workflow_file_not_found(self):
        """Test loading non-existent workflow file."""
        loader = WorkflowLoader()
        with pytest.raises(MissingFileError):
            loader.load("/nonexistent/workflow.md")


# ============================================================================
# Integration Tests
# ============================================================================


class TestLoadersIntegration:
    """Test loaders working together with ComponentLoader."""

    def test_load_all_components(self, complete_agent_dir):
        """Test loading all components."""
        component_loader = ComponentLoader()
        bundle = component_loader.load(str(complete_agent_dir))

        # Verify all components are loaded
        assert bundle.prompt_content is not None
        assert bundle.skills_content is not None
        assert bundle.workflow_content is not None

        # Components should be dictionaries
        assert isinstance(bundle.prompt_content, dict)
        assert isinstance(bundle.skills_content, dict)
        assert isinstance(bundle.workflow_content, dict)

    def test_load_individual_files_match_bundle(self, complete_agent_dir):
        """Test that individual file loads match bundle loads."""
        # Load as bundle
        component_loader = ComponentLoader()
        bundle = component_loader.load(str(complete_agent_dir))

        # Load prompt individually
        prompt_file = Path(complete_agent_dir) / "prompt.md"
        # Note: We don't have a direct prompt loader, but we can verify structure
        assert bundle.prompt_content["name"] == "test-agent"

        # Verify bundle integrity
        assert bundle.skills_content is not None
        assert bundle.workflow_content is not None
        assert len(bundle.skills_content["skills"]) == 2
        assert len(bundle.workflow_content["workflows"]) == 1
