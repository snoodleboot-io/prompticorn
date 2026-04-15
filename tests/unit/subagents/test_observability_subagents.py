"""Unit tests for Observability Agent subagents."""

import pytest


@pytest.mark.unit
class TestObservabilityMetricsSubagent:
    """Test suite for metrics subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "observability" / "subagents" / "metrics"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for metrics"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_has_purpose(self, subagent_dir, variant, read_file):
        """Test subagent has purpose."""
        file_path = subagent_dir / variant / "prompt.md"
        content = read_file(file_path)
        assert "focus" in content.lower() or "purpose" in content.lower(), (
            f"{variant}: Missing focus/purpose"
        )


@pytest.mark.unit
class TestObservabilityLoggingSubagent:
    """Test suite for logging subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "observability" / "subagents" / "logging"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for logging"


@pytest.mark.unit
class TestObservabilityTracingSubagent:
    """Test suite for tracing subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "observability" / "subagents" / "tracing"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for tracing"


@pytest.mark.unit
class TestObservabilityAlertingSubagent:
    """Test suite for alerting subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "observability" / "subagents" / "alerting"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for alerting"


@pytest.mark.unit
class TestObservabilityDashboardsSubagent:
    """Test suite for dashboards subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "observability" / "subagents" / "dashboards"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for dashboards"
