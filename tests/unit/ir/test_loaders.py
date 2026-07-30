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

from prompticorn.ir.exceptions import MissingFileError, ParseError, ValidationError
from prompticorn.ir.loaders import ComponentLoader, SkillLoader, WorkflowLoader
from prompticorn.ir.loaders.component_loader import ComponentBundle
from prompticorn.ir.models import Skill, Workflow

# ============================================================================
# FIXTURES - Sample files for testing
# ============================================================================


@pytest.fixture
def temp_agent_dir():
    """Create temporary directory for test agent files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_prompt_text():
    """Sample prompt.md text. No file: the loader parses text. (PRO-105)"""
    return """---
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


@pytest.fixture
def sample_skills_text():
    """Sample skills.md text."""
    return """---
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


@pytest.fixture
def sample_workflow_text():
    """Sample workflow.md text."""
    return """---
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


@pytest.fixture
def complete_bundle(sample_prompt_text, sample_skills_text, sample_workflow_text):
    """A bundle parsed from all three documents."""
    return ComponentLoader().parse(
        sample_prompt_text,
        skills_text=sample_skills_text,
        workflow_text=sample_workflow_text,
    )


@pytest.fixture
def minimal_bundle(sample_prompt_text):
    """A bundle parsed from the prompt document alone."""
    return ComponentLoader().parse(sample_prompt_text)


@pytest.fixture
def sample_skill_text():
    """Sample skill document text."""
    return """---
name: refactor
description: Improve code structure
tools_needed:
  - git
  - python
---

## Instructions
Apply SOLID principles to improve code structure. Follow these guidelines:
1. Single Responsibility Principle
2. Open/Closed Principle
3. Liskov Substitution Principle
4. Interface Segregation
5. Dependency Inversion

## Details
Additional skill details here.
"""


@pytest.fixture
def sample_workflow_text_fixture():
    """Sample standalone workflow document text."""
    return """---
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
"""


# ============================================================================
# ComponentLoader Tests
# ============================================================================


class TestComponentLoaderHappyPath:
    """Test ComponentLoader with valid inputs."""

    def test_parse_complete_components(self, complete_bundle):
        """Test parsing all component documents."""
        assert isinstance(complete_bundle, ComponentBundle)
        assert complete_bundle.prompt_content is not None
        assert complete_bundle.skills_content is not None
        assert complete_bundle.workflow_content is not None
        # Verify they're dictionaries
        assert isinstance(complete_bundle.prompt_content, dict)
        assert isinstance(complete_bundle.skills_content, dict)
        assert isinstance(complete_bundle.workflow_content, dict)

    def test_parse_prompt_content(self, complete_bundle):
        """Test prompt content is parsed correctly."""
        assert complete_bundle.prompt_content["name"] == "test-agent"
        assert complete_bundle.prompt_content["description"] == "A test agent"

    def test_parse_skills_content(self, complete_bundle):
        """Test skills content is parsed correctly."""
        assert complete_bundle.skills_content is not None
        assert "skills" in complete_bundle.skills_content
        assert len(complete_bundle.skills_content["skills"]) == 2

    def test_parse_workflow_content(self, complete_bundle):
        """Test workflow content is parsed correctly."""
        assert complete_bundle.workflow_content is not None
        assert "workflows" in complete_bundle.workflow_content
        assert complete_bundle.workflow_content["workflows"][0]["name"] == "code-review"

    def test_parse_minimal_components(self, minimal_bundle):
        """Test parsing only the required prompt document."""
        assert minimal_bundle.prompt_content is not None
        assert minimal_bundle.skills_content is None
        assert minimal_bundle.workflow_content is None

    def test_as_dict_complete(self, complete_bundle):
        """Test as_dict with all components."""
        components = ComponentLoader().as_dict(complete_bundle)

        assert isinstance(components, dict)
        assert "prompt" in components
        assert "skills" in components
        assert "workflow" in components

    def test_as_dict_minimal(self, minimal_bundle):
        """Test as_dict with only the prompt."""
        components = ComponentLoader().as_dict(minimal_bundle)

        assert "prompt" in components
        assert "skills" not in components
        assert "workflow" not in components


class TestComponentLoaderEdgeCases:
    """Test ComponentLoader edge cases.

    These no longer build temp directory trees: the loader parses text, so the
    inputs are strings. (PRO-105)
    """

    def test_parse_with_only_skills(self, sample_prompt_text, sample_skills_text):
        """Prompt and skills, no workflow."""
        bundle = ComponentLoader().parse(sample_prompt_text, skills_text=sample_skills_text)

        assert bundle.prompt_content is not None
        assert bundle.skills_content is not None
        assert bundle.workflow_content is None

    def test_parse_with_only_workflow(self, sample_prompt_text, sample_workflow_text):
        """Prompt and workflow, no skills."""
        bundle = ComponentLoader().parse(sample_prompt_text, workflow_text=sample_workflow_text)

        assert bundle.prompt_content is not None
        assert bundle.skills_content is None
        assert bundle.workflow_content is not None

    def test_parse_empty_prompt(self):
        """Empty documents parse to an empty content mapping."""
        bundle = ComponentLoader().parse("")

        assert bundle.prompt_content == {"content": ""}

    def test_parse_prompt_with_only_markdown(self):
        """A document with no frontmatter keeps its body under 'content'."""
        bundle = ComponentLoader().parse("# Markdown Content\nNo frontmatter here")

        assert "content" in bundle.prompt_content
        assert bundle.prompt_content["content"] == "# Markdown Content\nNo frontmatter here"


class TestComponentLoaderErrors:
    """Test ComponentLoader error handling."""

    def test_parse_invalid_yaml_raises_parse_error(self):
        """Invalid frontmatter surfaces as ParseError."""
        loader = ComponentLoader()
        with pytest.raises(ParseError):
            loader.parse(
                """---
invalid: yaml: content
  bad indent
---
Content
"""
            )

    def test_parse_error_names_the_source(self):
        """The error must say which unit failed, not merely that one did."""
        loader = ComponentLoader()
        with pytest.raises(ParseError, match="agent/broken"):
            loader.parse("---\ninvalid: yaml: content\n  bad\n---\n", source="agent/broken")


class TestComponentLoaderIsPure:
    """The loader must not reach for the filesystem (PRO-105)."""

    def test_module_imports_nothing_filesystem_related(self):
        import ast
        from pathlib import Path as _Path

        import prompticorn.ir.loaders.component_loader as module

        tree = ast.parse(_Path(module.__file__).read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])

        assert not (imported & {"os", "pathlib", "shutil", "glob", "io", "tempfile"})


# ============================================================================
# SkillLoader Tests
# ============================================================================


class TestSkillLoaderHappyPath:
    """Test SkillLoader with valid inputs."""

    def test_load_single_skill(self, sample_skill_text):
        """Test loading a single skill from file."""
        loader = SkillLoader()
        skill = loader.parse(sample_skill_text)

        assert isinstance(skill, Skill)
        assert skill.name == "refactor"
        assert skill.description == "Improve code structure"
        assert "Apply SOLID principles" in skill.instructions
        assert skill.tools_needed == ["git", "python"]

    def test_load_skill_minimal(self, temp_agent_dir):
        """Test loading skill with only required fields."""
        skill_text = """---
name: minimal
description: A minimal skill
tools_needed: []
---

## Instructions
Do something useful.
"""
        loader = SkillLoader()
        skill = loader.parse(skill_text)

        assert skill.name == "minimal"
        assert skill.tools_needed == []
        assert skill.instructions is not None

    def test_load_skill_with_tools(self, temp_agent_dir):
        """Test skill with multiple tools."""
        skill_text = """---
name: advanced
description: Advanced skill with many tools
tools_needed:
  - git
  - python
  - docker
  - kubernetes
---

## Instructions
Use all the tools to accomplish the task.
"""
        loader = SkillLoader()
        skill = loader.parse(skill_text)

        assert len(skill.tools_needed) == 4


class TestSkillLoaderEdgeCases:
    """Test SkillLoader edge cases."""

    def test_load_skill_no_tools_needed(self, temp_agent_dir):
        """Test skill without tools_needed field."""
        skill_text = """---
name: analysis
description: Analyze code
tools_needed: []
---

## Instructions
Look carefully at the code and analyze it.
"""
        loader = SkillLoader()
        skill = loader.parse(skill_text)

        # Should have empty list
        assert skill.tools_needed == []

    def test_load_skill_with_extra_fields(self, temp_agent_dir):
        """Test skill with additional metadata fields (should be ignored)."""
        skill_text = """---
name: advanced
description: Advanced skill
tools_needed:
  - advanced-tool
version: 2.0
deprecated: false
---

## Instructions
Complex instructions for this skill.
"""
        loader = SkillLoader()
        skill = loader.parse(skill_text)

        assert skill.name == "advanced"

    def test_load_skill_with_markdown_content(self, temp_agent_dir):
        """Test skill with markdown sections after frontmatter."""
        skill_text = """---
name: documented
description: Well documented skill
tools_needed:
  - tool1
---

## Instructions
Follow the steps carefully:
Step 1: Do this
Step 2: Then that
Step 3: Finally this

## Examples

Example code here.
"""
        loader = SkillLoader()
        skill = loader.parse(skill_text)

        assert skill.name == "documented"


class TestSkillLoaderErrors:
    """Test SkillLoader error handling."""

    def test_load_skill_missing_name(self, temp_agent_dir):
        """Test skill without required name field."""
        skill_text = """---
description: No name skill
instructions: Do something
tools_needed: []
---
"""
        loader = SkillLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.parse(skill_text)

    def test_load_skill_missing_description(self, temp_agent_dir):
        """Test skill without required description field."""
        skill_text = """---
name: no-desc
instructions: Do something
tools_needed: []
---
"""
        loader = SkillLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.parse(skill_text)

    def test_load_skill_invalid_yaml(self, temp_agent_dir):
        """Test skill with invalid YAML raises ParseError."""
        skill_text = """---
invalid: yaml: content
  bad indent
---
"""
        loader = SkillLoader()
        with pytest.raises(ParseError):
            loader.parse(skill_text)

    def test_loader_has_no_file_loading_api(self):
        """Missing-content is the source's concern now; the loader only parses.
        (PRO-105)"""
        assert not hasattr(SkillLoader(), "load")


# ============================================================================
# WorkflowLoader Tests
# ============================================================================


class TestWorkflowLoaderHappyPath:
    """Test WorkflowLoader with valid inputs."""

    def test_parse_single_workflow(self, sample_workflow_text_fixture):
        """Test parsing a single workflow document."""
        loader = WorkflowLoader()
        workflow = loader.parse(sample_workflow_text_fixture)

        assert isinstance(workflow, Workflow)
        assert workflow.name == "code-review"
        assert workflow.description == "Review code for quality"
        assert len(workflow.steps) == 4

    def test_load_workflow_minimal(self, temp_agent_dir):
        """Test loading workflow with only required fields."""
        workflow_text = """---
name: minimal
description: A minimal workflow
steps:
  - Step 1
---
"""
        loader = WorkflowLoader()
        workflow = loader.parse(workflow_text)

        assert workflow.name == "minimal"
        assert workflow.steps == ["Step 1"]

    def test_load_workflow_many_steps(self, temp_agent_dir):
        """Test loading workflow with many steps."""
        workflow_text = """---
name: complex
description: Complex workflow
steps:
  - Step 1
  - Step 2
  - Step 3
  - Step 4
  - Step 5
---
"""
        loader = WorkflowLoader()
        workflow = loader.parse(workflow_text)

        assert len(workflow.steps) == 5


class TestWorkflowLoaderEdgeCases:
    """Test WorkflowLoader edge cases."""

    def test_load_workflow_empty_steps(self, temp_agent_dir):
        """Test workflow with empty steps list raises validation error."""
        workflow_text = """---
name: empty
description: No steps
steps: []
---
"""
        loader = WorkflowLoader()
        # Workflows require at least one step
        with pytest.raises((ParseError, ValidationError)):
            loader.parse(workflow_text)

    def test_load_workflow_single_step(self, temp_agent_dir):
        """Test workflow with single step."""
        workflow_text = """---
name: simple
description: Single step
steps:
  - Do the thing
---
"""
        loader = WorkflowLoader()
        workflow = loader.parse(workflow_text)

        assert len(workflow.steps) == 1
        assert workflow.steps[0] == "Do the thing"

    def test_load_workflow_with_extra_fields(self, temp_agent_dir):
        """Test workflow with additional metadata fields."""
        workflow_text = """---
name: advanced
description: Advanced workflow
steps:
  - Step 1
  - Step 2
priority: high
author: test-author
---
"""
        loader = WorkflowLoader()
        workflow = loader.parse(workflow_text)

        assert workflow.name == "advanced"

    def test_load_workflow_with_markdown_content(self, temp_agent_dir):
        """Test workflow with markdown sections after frontmatter."""
        workflow_text = """---
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
"""
        loader = WorkflowLoader()
        workflow = loader.parse(workflow_text)

        assert workflow.name == "documented"


class TestWorkflowLoaderErrors:
    """Test WorkflowLoader error handling."""

    def test_load_workflow_missing_name(self, temp_agent_dir):
        """Test workflow without required name field."""
        workflow_text = """---
description: No name
steps:
  - Step 1
---
"""
        loader = WorkflowLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.parse(workflow_text)

    def test_load_workflow_missing_description(self, temp_agent_dir):
        """Test workflow without required description field."""
        workflow_text = """---
name: no-desc
steps:
  - Step 1
---
"""
        loader = WorkflowLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.parse(workflow_text)

    def test_load_workflow_missing_steps(self, temp_agent_dir):
        """Test workflow without required steps field."""
        workflow_text = """---
name: no-steps
description: Missing steps
---
"""
        loader = WorkflowLoader()
        with pytest.raises((ParseError, ValidationError)):
            loader.parse(workflow_text)

    def test_load_workflow_invalid_yaml(self, temp_agent_dir):
        """Test workflow with invalid YAML."""
        workflow_text = """---
invalid: yaml: content
  bad indent
---
"""
        loader = WorkflowLoader()
        with pytest.raises(ParseError):
            loader.parse(workflow_text)

    def test_loader_has_no_file_loading_api(self):
        """Missing-content is the source's concern now; the loader only parses.
        (PRO-105)"""
        assert not hasattr(WorkflowLoader(), "load")


# ============================================================================
# Integration Tests
# ============================================================================


class TestLoadersIntegration:
    """Test loaders working together with ComponentLoader."""

    def test_parse_all_components(self, complete_bundle):
        """Test parsing all components together."""
        bundle = complete_bundle

        # Verify all components are loaded
        assert bundle.prompt_content is not None
        assert bundle.skills_content is not None
        assert bundle.workflow_content is not None

        # Components should be dictionaries
        assert isinstance(bundle.prompt_content, dict)
        assert isinstance(bundle.skills_content, dict)
        assert isinstance(bundle.workflow_content, dict)

    def test_parsed_bundle_exposes_each_document(self, complete_bundle):
        """Each document is reachable from the bundle it was parsed into."""
        bundle = complete_bundle

        assert bundle.prompt_content["name"] == "test-agent"

        # Verify bundle integrity
        assert bundle.skills_content is not None
        assert bundle.workflow_content is not None
        assert len(bundle.skills_content["skills"]) == 2
        assert len(bundle.workflow_content["workflows"]) == 1


# ============================================================================
# AGENT SKILL MAPPING LOADER TESTS
# ============================================================================


class TestAgentSkillMappingLoader:
    """Tests for AgentSkillMappingLoader - language-agnostic agent mappings."""

    @pytest.fixture
    def temp_mapping_file(self, tmp_path):
        """Create temporary agent_skill_mapping.yaml file."""
        mapping_file = tmp_path / "agent_skill_mapping.yaml"
        content = """# Agent skill/workflow mapping
architect:
  skills:
    - architecture-documentation
    - data-model-discovery
    - mermaid-erd-creation
  workflows:
    - scaffold
    - data-model
    - task-breakdown

code:
  skills:
    - feature-planning
    - incremental-implementation
  workflows:
    - code
    - feature

test:
  skills:
    - test-coverage-categories
  workflows:
    - testing

empty-agent:
  skills: []
  workflows: []

partial-agent:
  skills:
    - some-skill
"""
        mapping_file.write_text(content, encoding="utf-8")
        return mapping_file

    def test_init_success(self, temp_mapping_file):
        """Test successful initialization with valid mapping file."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        assert loader.mapping_file == temp_mapping_file
        assert loader._mapping is None  # Lazy loading

    def test_init_file_not_found(self, tmp_path):
        """Test initialization with non-existent file raises error."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        non_existent = tmp_path / "does_not_exist.yaml"

        with pytest.raises(FileNotFoundError, match="Mapping file not found"):
            AgentSkillMappingLoader(non_existent)

    def test_mapping_lazy_load(self, temp_mapping_file):
        """Test that mapping is lazy-loaded on first access."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        assert loader._mapping is None

        # Access mapping property
        mapping = loader.mapping
        assert loader._mapping is not None
        assert isinstance(mapping, dict)
        assert "architect" in mapping
        assert "code" in mapping

    def test_get_skills_for_agent_success(self, temp_mapping_file):
        """Test getting skills for an agent."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)

        # Test architect skills
        skills = loader.get_skills_for_agent("architect")
        assert isinstance(skills, list)
        assert len(skills) == 3
        assert "architecture-documentation" in skills
        assert "data-model-discovery" in skills
        assert "mermaid-erd-creation" in skills

        # Test code skills
        skills = loader.get_skills_for_agent("code")
        assert len(skills) == 2
        assert "feature-planning" in skills
        assert "incremental-implementation" in skills

    def test_get_skills_for_nonexistent_agent(self, temp_mapping_file):
        """Test getting skills for non-existent agent returns empty list."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        skills = loader.get_skills_for_agent("nonexistent")
        assert skills == []

    def test_get_skills_for_empty_agent(self, temp_mapping_file):
        """Test getting skills for agent with empty skills list."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        skills = loader.get_skills_for_agent("empty-agent")
        assert skills == []

    def test_get_workflows_for_agent_success(self, temp_mapping_file):
        """Test getting workflows for an agent."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)

        # Test architect workflows
        workflows = loader.get_workflows_for_agent("architect")
        assert isinstance(workflows, list)
        assert len(workflows) == 3
        assert "scaffold" in workflows
        assert "data-model" in workflows
        assert "task-breakdown" in workflows

        # Test code workflows
        workflows = loader.get_workflows_for_agent("code")
        assert len(workflows) == 2
        assert "code" in workflows
        assert "feature" in workflows

    def test_get_workflows_for_nonexistent_agent(self, temp_mapping_file):
        """Test getting workflows for non-existent agent returns empty list."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        workflows = loader.get_workflows_for_agent("nonexistent")
        assert workflows == []

    def test_get_workflows_for_empty_agent(self, temp_mapping_file):
        """Test getting workflows for agent with empty workflows list."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        workflows = loader.get_workflows_for_agent("empty-agent")
        assert workflows == []

    def test_get_all_mappings(self, temp_mapping_file):
        """Test getting all mappings."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        mappings = loader.get_all_mappings()

        assert isinstance(mappings, dict)
        assert "architect" in mappings
        assert "code" in mappings
        assert "test" in mappings
        assert "empty-agent" in mappings

        # Verify it's a copy (not reference)
        mappings["new-key"] = "new-value"
        assert "new-key" not in loader.mapping

    def test_has_agent(self, temp_mapping_file):
        """Test checking if agent has mappings."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)

        assert loader.has_agent("architect") is True
        assert loader.has_agent("code") is True
        assert loader.has_agent("nonexistent") is False

    def test_list_agents(self, temp_mapping_file):
        """Test listing all agents."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        agents = loader.list_agents()

        assert isinstance(agents, list)
        assert len(agents) == 5  # architect, code, test, empty-agent, partial-agent
        assert agents == sorted(agents)  # Should be sorted
        assert "architect" in agents
        assert "code" in agents
        assert "test" in agents

    def test_validate_completeness_all_complete(self, temp_mapping_file):
        """Test validation when all required agents are complete."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        result = loader.validate_completeness(["architect", "code", "test"])

        assert result["missing"] == []
        assert result["incomplete"] == []

    def test_validate_completeness_missing_agents(self, temp_mapping_file):
        """Test validation detects missing agents."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        result = loader.validate_completeness(["architect", "missing1", "missing2"])

        assert "missing1" in result["missing"]
        assert "missing2" in result["missing"]
        assert len(result["missing"]) == 2

    def test_validate_completeness_incomplete_agents(self, temp_mapping_file):
        """Test validation detects incomplete agents (missing skills or workflows)."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        result = loader.validate_completeness(["architect", "empty-agent", "partial-agent"])

        # empty-agent has empty skills and workflows
        # partial-agent has skills but missing workflows
        incomplete_agents = [item["agent"] for item in result["incomplete"]]
        assert "empty-agent" in incomplete_agents
        assert "partial-agent" in incomplete_agents

    def test_validate_completeness_mixed(self, temp_mapping_file):
        """Test validation with mix of complete, incomplete, and missing agents."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)
        result = loader.validate_completeness(
            [
                "architect",  # complete
                "empty-agent",  # incomplete (empty lists)
                "nonexistent",  # missing
            ]
        )

        assert len(result["missing"]) == 1
        assert "nonexistent" in result["missing"]

        incomplete_agents = [item["agent"] for item in result["incomplete"]]
        assert "empty-agent" in incomplete_agents

    def test_malformed_yaml(self, tmp_path):
        """Test handling of malformed YAML file."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("architect:\n  skills: [unclosed list", encoding="utf-8")

        loader = AgentSkillMappingLoader(bad_file)

        # Should raise error when accessing mapping
        import yaml

        with pytest.raises(yaml.YAMLError):  # yaml.YAMLError or similar
            _ = loader.mapping

    def test_empty_yaml_file(self, tmp_path):
        """Test handling of empty YAML file."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("", encoding="utf-8")

        loader = AgentSkillMappingLoader(empty_file)
        mapping = loader.mapping

        assert mapping == {}
        assert loader.get_skills_for_agent("anything") == []
        assert loader.get_workflows_for_agent("anything") == []

    def test_caching(self, temp_mapping_file):
        """Test that mapping is cached after first load."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        loader = AgentSkillMappingLoader(temp_mapping_file)

        # First access loads and caches
        mapping1 = loader.mapping
        assert loader._mapping is not None

        # Second access returns cached version
        mapping2 = loader.mapping
        assert mapping1 is mapping2  # Same object reference

    def test_agent_with_no_skills_field(self, tmp_path):
        """Test agent entry that has workflows but no skills field."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        mapping_file = tmp_path / "test.yaml"
        content = """agent-no-skills:
  workflows:
    - some-workflow
"""
        mapping_file.write_text(content, encoding="utf-8")

        loader = AgentSkillMappingLoader(mapping_file)
        skills = loader.get_skills_for_agent("agent-no-skills")

        assert skills == []

    def test_agent_with_no_workflows_field(self, tmp_path):
        """Test agent entry that has skills but no workflows field."""
        from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader

        mapping_file = tmp_path / "test.yaml"
        content = """agent-no-workflows:
  skills:
    - some-skill
"""
        mapping_file.write_text(content, encoding="utf-8")

        loader = AgentSkillMappingLoader(mapping_file)
        workflows = loader.get_workflows_for_agent("agent-no-workflows")

        assert workflows == []
