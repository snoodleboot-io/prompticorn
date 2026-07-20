"""Unit tests for Phase 2 Week 4 Skills."""

import pytest


@pytest.mark.unit
class TestBackendSkills:
    """Test suite for backend skills."""

    @pytest.fixture
    def skills_dir(self, skills_dir):
        """Get skills directory."""
        return skills_dir

    @pytest.mark.parametrize(
        "skill_name",
        [
            "api-versioning-strategy",
            "microservices-communication-patterns",
            "distributed-caching-design",
            "nosql-database-selection",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_backend_skill_exists(self, skills_dir, skill_name, variant):
        """Test that backend skills exist."""
        file_path = skills_dir / skill_name / variant / "SKILL.md"
        assert file_path.exists(), f"Missing {skill_name}/{variant}"


@pytest.mark.unit
class TestFrontendSkills:
    """Test suite for frontend skills."""

    @pytest.fixture
    def skills_dir(self, skills_dir):
        """Get skills directory."""
        return skills_dir

    @pytest.mark.parametrize(
        "skill_name",
        [
            "component-design-systems",
            "state-management-architecture",
            "css-performance-optimization",
            "responsive-design-patterns",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_frontend_skill_exists(self, skills_dir, skill_name, variant):
        """Test that frontend skills exist."""
        file_path = skills_dir / skill_name / variant / "SKILL.md"
        assert file_path.exists(), f"Missing {skill_name}/{variant}"


@pytest.mark.unit
class TestDevOpsSkills:
    """Test suite for DevOps skills."""

    @pytest.fixture
    def skills_dir(self, skills_dir):
        """Get skills directory."""
        return skills_dir

    @pytest.mark.parametrize(
        "skill_name",
        [
            "container-security-hardening",
            "kubernetes-resource-management",
            "infrastructure-drift-detection",
            "deployment-rollback-strategies",
            "iac-best-practices",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_devops_skill_exists(self, skills_dir, skill_name, variant):
        """Test that DevOps skills exist."""
        file_path = skills_dir / skill_name / variant / "SKILL.md"
        assert file_path.exists(), f"Missing {skill_name}/{variant}"


@pytest.mark.unit
class TestTestingSkills:
    """Test suite for testing skills."""

    @pytest.fixture
    def skills_dir(self, skills_dir):
        """Get skills directory."""
        return skills_dir

    @pytest.mark.parametrize(
        "skill_name",
        [
            "test-data-strategies",
            "flaky-test-remediation",
            "mutation-testing",
            "load-testing",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_testing_skill_exists(self, skills_dir, skill_name, variant):
        """Test that testing skills exist."""
        file_path = skills_dir / skill_name / variant / "SKILL.md"
        assert file_path.exists(), f"Missing {skill_name}/{variant}"


@pytest.mark.unit
class TestMLAISkills:
    """Test suite for ML/AI skills."""

    @pytest.fixture
    def skills_dir(self, skills_dir):
        """Get skills directory."""
        return skills_dir

    @pytest.mark.parametrize(
        "skill_name",
        [
            "feature-engineering",
            "model-evaluation",
            "ml-deployment",
            "model-monitoring",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_mlai_skill_exists(self, skills_dir, skill_name, variant):
        """Test that ML/AI skills exist."""
        file_path = skills_dir / skill_name / variant / "SKILL.md"
        assert file_path.exists(), f"Missing {skill_name}/{variant}"


@pytest.mark.unit
class TestSecuritySkills:
    """Test suite for security skills."""

    @pytest.fixture
    def skills_dir(self, skills_dir):
        """Get skills directory."""
        return skills_dir

    @pytest.mark.parametrize(
        "skill_name",
        [
            "threat-modeling",
            "key-management",
            "compliance-automation",
            "incident-automation",
            "api-security",
        ],
    )
    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_security_skill_exists(self, skills_dir, skill_name, variant):
        """Test that security skills exist."""
        file_path = skills_dir / skill_name / variant / "SKILL.md"
        assert file_path.exists(), f"Missing {skill_name}/{variant}"


@pytest.mark.unit
class TestSkillContent:
    """Test skill content quality."""

    @pytest.mark.parametrize(
        "skill_name",
        [
            "api-versioning-strategy",
            "component-design-systems",
            "container-security-hardening",
            "feature-engineering",
            "threat-modeling",
        ],
    )
    def test_skill_has_minimal_variant(self, skills_dir, skill_name, read_file):
        """Test skills have content in minimal variant."""
        file_path = skills_dir / skill_name / "minimal" / "SKILL.md"
        assert file_path.exists(), f"Missing {skill_name}/minimal"
        content = read_file(file_path)
        assert len(content.strip()) > 50, f"{skill_name} minimal too short"

    @pytest.mark.parametrize(
        "skill_name",
        [
            "api-versioning-strategy",
            "feature-engineering",
            "threat-modeling",
        ],
    )
    def test_skill_has_verbose_variant(self, skills_dir, skill_name, read_file):
        """Test skills have comprehensive verbose variant."""
        file_path = skills_dir / skill_name / "verbose" / "SKILL.md"
        assert file_path.exists(), f"Missing {skill_name}/verbose"
        content = read_file(file_path)
        assert len(content.strip()) > 300, f"{skill_name} verbose should be comprehensive"
        assert "Learning Path" in content or "Purpose" in content, (
            f"{skill_name} verbose should have structured content"
        )


@pytest.mark.unit
class TestSkillFilenameCasing:
    """Guard the canonical ``SKILL.md`` spelling (PRO-89).

    The loader (``prompt_builder._write_skill_files``) and the emitter
    (``skill_emitter``) only ever resolve uppercase ``SKILL.md``. A lowercase
    ``skill.md`` on disk is therefore invisible to every builder on a
    case-sensitive filesystem, and the miss is silent. These tests fail loudly
    instead of letting a dead skill ship.
    """

    def test_no_lowercase_skill_files(self, skills_dir):
        """No skill may use the lowercase spelling the builders cannot read."""
        offenders = sorted(
            str(path.relative_to(skills_dir)) for path in skills_dir.rglob("skill.md")
        )
        assert not offenders, (
            "These files are invisible to the builders — rename to SKILL.md: "
            f"{offenders}"
        )

    def test_every_skill_variant_has_a_skill_file(self, skills_dir):
        """Every skill directory must carry both variants as SKILL.md."""
        missing = sorted(
            f"{skill.name}/{variant}"
            for skill in skills_dir.iterdir()
            if skill.is_dir()
            for variant in ("minimal", "verbose")
            if not (skill / variant / "SKILL.md").is_file()
        )
        assert not missing, f"Skill variants with no SKILL.md: {missing}"
