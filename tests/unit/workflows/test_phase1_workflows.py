"""Unit tests for Phase 1 workflows (data, observability, incident)."""

import pytest
from pathlib import Path


@pytest.mark.unit
class TestDataPipelineWorkflow:
    """Test suite for data pipeline workflow."""

    @pytest.fixture
    def workflow_dir(self, workflows_dir):
        """Get workflow directory."""
        return workflows_dir / "data-pipeline-workflow"

    def test_workflow_dir_exists(self, workflow_dir):
        """Test that workflow directory exists."""
        assert workflow_dir.exists(), "data-pipeline-workflow directory not found"

    def test_workflow_has_content(self, workflow_dir):
        """Test that workflow has some content."""
        # Check if any variant exists
        has_content = False
        for variant in ["minimal", "verbose", "prompt.md"]:
            file_path = (
                workflow_dir / variant
                if variant.endswith(".md")
                else workflow_dir / variant / "prompt.md"
            )
            if file_path.exists():
                has_content = True
                break
        assert has_content, "workflow should have content in some form"


@pytest.mark.unit
class TestDataQualityWorkflow:
    """Test suite for data quality workflow."""

    @pytest.fixture
    def workflow_dir(self, workflows_dir):
        """Get workflow directory."""
        return workflows_dir / "data-quality-workflow"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_workflow_variant_exists(self, workflow_dir, variant):
        """Test that workflow variant exists."""
        file_path = workflow_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for data-quality-workflow"


@pytest.mark.unit
class TestSchemaMigrationWorkflow:
    """Test suite for schema migration workflow."""

    @pytest.fixture
    def workflow_dir(self, workflows_dir):
        """Get workflow directory."""
        return workflows_dir / "schema-migration-workflow"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_workflow_variant_exists(self, workflow_dir, variant):
        """Test that workflow variant exists."""
        file_path = workflow_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for schema-migration-workflow"


@pytest.mark.unit
class TestObservabilityWorkflow:
    """Test suite for observability workflow."""

    @pytest.fixture
    def workflow_dir(self, workflows_dir):
        """Get workflow directory."""
        return workflows_dir / "observability-workflow"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_workflow_variant_exists(self, workflow_dir, variant):
        """Test that workflow variant exists."""
        file_path = workflow_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for observability-workflow"


@pytest.mark.unit
class TestSLOSLIWorkflow:
    """Test suite for SLO/SLI workflow."""

    @pytest.fixture
    def workflow_dir(self, workflows_dir):
        """Get workflow directory."""
        return workflows_dir / "slo-sli-workflow"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_workflow_variant_exists(self, workflow_dir, variant):
        """Test that workflow variant exists."""
        file_path = workflow_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for slo-sli-workflow"


@pytest.mark.unit
class TestCapacityPlanningWorkflow:
    """Test suite for capacity planning workflow."""

    @pytest.fixture
    def workflow_dir(self, workflows_dir):
        """Get workflow directory."""
        return workflows_dir / "capacity-planning-workflow"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_workflow_variant_exists(self, workflow_dir, variant):
        """Test that workflow variant exists."""
        file_path = workflow_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for capacity-planning-workflow"


@pytest.mark.unit
class TestIncidentResponseWorkflow:
    """Test suite for incident response workflow."""

    @pytest.fixture
    def workflow_dir(self, workflows_dir):
        """Get workflow directory."""
        return workflows_dir / "incident-response-workflow"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_workflow_variant_exists(self, workflow_dir, variant):
        """Test that workflow variant exists."""
        file_path = workflow_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for incident-response-workflow"


@pytest.mark.unit
class TestPostmortemWorkflow:
    """Test suite for postmortem workflow."""

    @pytest.fixture
    def workflow_dir(self, workflows_dir):
        """Get workflow directory."""
        return workflows_dir / "postmortem-workflow"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_workflow_variant_exists(self, workflow_dir, variant):
        """Test that workflow variant exists."""
        file_path = workflow_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for postmortem-workflow"
