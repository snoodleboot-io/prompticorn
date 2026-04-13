"""Unit tests for Phase 2 Week 3 Workflows."""

import pytest


@pytest.mark.unit
class TestBackendArchitectureWorkflows:
    """Test suite for backend architecture workflows."""

    @pytest.fixture
    def workflows_dir(self, workflows_dir):
        """Get workflows directory."""
        return workflows_dir

    @pytest.mark.parametrize(
        "workflow_name",
        [
            "api-design",
            "microservices-architecture",
            "caching-strategy",
            "database-selection",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_backend_workflow_exists(self, workflows_dir, workflow_name, variant):
        """Test that backend architecture workflows exist."""
        file_path = workflows_dir / workflow_name / variant / "workflow.md"
        assert file_path.exists(), f"Missing {workflow_name}/{variant}"


@pytest.mark.unit
class TestFrontendWorkflows:
    """Test suite for frontend workflows."""

    @pytest.fixture
    def workflows_dir(self, workflows_dir):
        """Get workflows directory."""
        return workflows_dir

    @pytest.mark.parametrize(
        "workflow_name",
        [
            "component-architecture",
            "state-management",
            "frontend-performance",
            "responsive-design",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_frontend_workflow_exists(self, workflows_dir, workflow_name, variant):
        """Test that frontend workflows exist."""
        file_path = workflows_dir / workflow_name / variant / "workflow.md"
        assert file_path.exists(), f"Missing {workflow_name}/{variant}"


@pytest.mark.unit
class TestDevOpsWorkflows:
    """Test suite for DevOps workflows."""

    @pytest.fixture
    def workflows_dir(self, workflows_dir):
        """Get workflows directory."""
        return workflows_dir

    @pytest.mark.parametrize(
        "workflow_name",
        [
            "cicd-pipeline",
            "container-orchestration",
            "infrastructure-as-code",
            "disaster-recovery",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_devops_workflow_exists(self, workflows_dir, workflow_name, variant):
        """Test that DevOps workflows exist."""
        file_path = workflows_dir / workflow_name / variant / "workflow.md"
        assert file_path.exists(), f"Missing {workflow_name}/{variant}"


@pytest.mark.unit
class TestTestingWorkflows:
    """Test suite for testing/QA workflows."""

    @pytest.fixture
    def workflows_dir(self, workflows_dir):
        """Get workflows directory."""
        return workflows_dir

    @pytest.mark.parametrize(
        "workflow_name",
        [
            "testing-strategy",
            "automated-testing",
            "performance-testing",
            "security-testing",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_testing_workflow_exists(self, workflows_dir, workflow_name, variant):
        """Test that testing workflows exist."""
        file_path = workflows_dir / workflow_name / variant / "workflow.md"
        assert file_path.exists(), f"Missing {workflow_name}/{variant}"


@pytest.mark.unit
class TestSecurityWorkflows:
    """Test suite for security workflows."""

    @pytest.fixture
    def workflows_dir(self, workflows_dir):
        """Get workflows directory."""
        return workflows_dir

    @pytest.mark.parametrize(
        "workflow_name",
        [
            "authentication-authorization",
            "data-encryption",
            "vulnerability-assessment",
            "compliance-audit",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_security_workflow_exists(self, workflows_dir, workflow_name, variant):
        """Test that security workflows exist."""
        file_path = workflows_dir / workflow_name / variant / "workflow.md"
        assert file_path.exists(), f"Missing {workflow_name}/{variant}"


@pytest.mark.unit
class TestWorkflowContent:
    """Test workflow content quality."""

    @pytest.mark.parametrize(
        "workflow_name",
        [
            "api-design",
            "microservices-architecture",
            "component-architecture",
            "cicd-pipeline",
            "testing-strategy",
            "authentication-authorization",
        ],
    )
    def test_workflow_has_minimal_variant(self, workflows_dir, workflow_name, read_file):
        """Test workflows have content in minimal variant."""
        file_path = workflows_dir / workflow_name / "minimal" / "prompt.md"
        if file_path.exists():
            content = read_file(file_path)
            assert len(content.strip()) > 50, f"{workflow_name} minimal too short"

    @pytest.mark.parametrize(
        "workflow_name",
        [
            "api-design",
            "component-architecture",
            "cicd-pipeline",
        ],
    )
    def test_workflow_has_verbose_variant(self, workflows_dir, workflow_name, read_file):
        """Test workflows have comprehensive verbose variant."""
        file_path = workflows_dir / workflow_name / "verbose" / "prompt.md"
        if file_path.exists():
            content = read_file(file_path)
            assert len(content.strip()) > 500, f"{workflow_name} verbose should be comprehensive"
            assert "Phase" in content or "step" in content.lower(), (
                f"{workflow_name} verbose should have structured phases"
            )
