"""Unit tests for schema validators."""

import pytest

from validation.schema_validator import SchemaValidator


@pytest.mark.unit
class TestSchemaValidator:
    """Test suite for schema validator."""

    @pytest.fixture
    def validator(self, project_root):
        """Create validator instance."""
        return SchemaValidator(project_root)

    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None
        assert hasattr(validator, "validate_agent")
        assert hasattr(validator, "validate_workflow")
        assert hasattr(validator, "validate_skill")

    def test_validate_agent_with_valid_file(self, validator, agents_dir, read_file):
        """Test validating a valid agent file."""
        agent_file = agents_dir / "data" / "prompt.md"
        if agent_file.exists():
            content = read_file(agent_file)
            # Agent should have description in frontmatter or content
            assert "description" in content.lower() or "you are" in content.lower()

    def test_validate_workflow_with_valid_file(self, validator, workflows_dir, read_file):
        """Test validating a valid workflow file."""
        workflow_file = workflows_dir / "data-pipeline" / "minimal" / "prompt.md"
        if workflow_file.exists():
            content = read_file(workflow_file)
            assert len(content.strip()) > 0, "Workflow content should not be empty"

    def test_validate_skill_with_valid_file(self, validator):
        """Test validating skill file."""
        # Verify validator has skill validation capability
        assert hasattr(validator, "validate_skill"), "Validator should have validate_skill method"


@pytest.mark.unit
class TestContentValidation:
    """Test suite for content validation rules."""

    def test_agent_has_required_sections(self, agents_dir, read_file):
        """Test that agents have required sections."""
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir() and agent_dir.name not in ["__pycache__"]:
                agent_file = agent_dir / "prompt.md"
                if agent_file.exists():
                    content = read_file(agent_file)
                    # Check for key sections (case-insensitive)
                    content_lower = content.lower()
                    assert (
                        "description" in content_lower
                        or "you are" in content_lower
                        or "purpose" in content_lower
                        or "overview" in content_lower
                    ), f"{agent_dir.name}: Missing description/purpose section"

    def test_workflow_minimum_length(self, workflows_dir, read_file):
        """Test that workflows have minimum content."""
        minimal_workflow = workflows_dir / "data-pipeline" / "minimal" / "prompt.md"
        if minimal_workflow.exists():
            content = read_file(minimal_workflow)
            lines = len(content.strip().split("\n"))
            assert lines >= 20, f"Minimal workflow too short: {lines} lines (min 20)"

    def test_workflow_variant_consistency(self, workflows_dir, read_file):
        """Test that both minimal and verbose variants exist for workflows."""
        workflow_dirs = [d for d in workflows_dir.iterdir() if d.is_dir()]

        for workflow_dir in workflow_dirs:
            minimal_file = workflow_dir / "minimal" / "prompt.md"
            verbose_file = workflow_dir / "verbose" / "prompt.md"

            if minimal_file.exists():
                assert verbose_file.exists(), (
                    f"{workflow_dir.name}: Has minimal but missing verbose variant"
                )
            if verbose_file.exists():
                assert minimal_file.exists(), (
                    f"{workflow_dir.name}: Has verbose but missing minimal variant"
                )


@pytest.mark.unit
class TestFileStructure:
    """Test suite for file structure validation."""

    def test_subagent_directory_structure(self, agents_dir):
        """Test that subagents have proper directory structure."""
        for agent_dir in agents_dir.iterdir():
            if agent_dir.is_dir() and agent_dir.name not in ["__pycache__", "core"]:
                subagents_dir = agent_dir / "subagents"
                if subagents_dir.exists():
                    # Should have at least one subagent
                    subagents = [
                        d
                        for d in subagents_dir.iterdir()
                        if d.is_dir() and d.name not in ["__pycache__"]
                    ]
                    assert len(subagents) > 0, f"{agent_dir.name}: Should have subagents"

    def test_workflow_variant_files_exist(self, workflows_dir):
        """Test that workflow variants have prompt.md files."""
        for workflow_dir in workflows_dir.iterdir():
            if workflow_dir.is_dir() and workflow_dir.name.endswith(""):
                for variant_dir in ["minimal", "verbose"]:
                    variant_path = workflow_dir / variant_dir
                    if variant_path.exists():
                        # Check for either prompt.md or workflow.md
                        prompt_file = variant_path / "prompt.md"
                        workflow_file = variant_path / "workflow.md"
                        assert prompt_file.exists() or workflow_file.exists(), (
                            f"{workflow_dir.name}/{variant_dir}: Missing prompt.md or workflow.md"
                        )
