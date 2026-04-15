"""Unit tests for Data Agent subagents."""

import pytest


@pytest.mark.unit
class TestDataPipelineSubagent:
    """Test suite for data pipeline subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "data" / "subagents" / "pipeline"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for pipeline"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_has_purpose(self, subagent_dir, variant, read_file):
        """Test subagent has purpose."""
        file_path = subagent_dir / variant / "prompt.md"
        content = read_file(file_path)
        assert "focus" in content.lower() or "purpose" in content.lower(), (
            f"{variant}: Missing focus/purpose"
        )

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_has_examples(self, subagent_dir, variant, read_file):
        """Test subagent has examples."""
        file_path = subagent_dir / variant / "prompt.md"
        content = read_file(file_path)
        assert (
            "example" in content.lower()
            or "pattern" in content.lower()
            or "question" in content.lower()
        ), f"{variant}: Missing examples/patterns"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_minimum_length(self, subagent_dir, variant, read_file):
        """Test subagent meets length requirements."""
        file_path = subagent_dir / variant / "prompt.md"
        content = read_file(file_path)
        lines = len(content.strip().split("\n"))
        min_lines = 30 if variant == "minimal" else 100
        assert lines > min_lines, f"{variant}: Too short ({lines} lines, min {min_lines})"


@pytest.mark.unit
class TestDataWarehouseSubagent:
    """Test suite for data warehouse subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "data" / "subagents" / "warehouse"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for warehouse"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_has_purpose(self, subagent_dir, variant, read_file):
        """Test subagent has purpose."""
        file_path = subagent_dir / variant / "prompt.md"
        content = read_file(file_path)
        assert "focus" in content.lower() or "purpose" in content.lower(), (
            f"{variant}: Missing focus/purpose"
        )


@pytest.mark.unit
class TestDataQualitySubagent:
    """Test suite for data quality subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "data" / "subagents" / "quality"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for quality"


@pytest.mark.unit
class TestDataGovernanceSubagent:
    """Test suite for data governance subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "data" / "subagents" / "governance"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for governance"


@pytest.mark.unit
class TestDataStreamingSubagent:
    """Test suite for data streaming subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "data" / "subagents" / "streaming"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for streaming"
