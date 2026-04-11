"""Unit tests for Incident Agent subagents."""

import pytest
from pathlib import Path


@pytest.mark.unit
class TestIncidentTriageSubagent:
    """Test suite for triage subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "incident" / "subagents" / "triage"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for triage"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_has_purpose(self, subagent_dir, variant, read_file):
        """Test subagent has purpose."""
        file_path = subagent_dir / variant / "prompt.md"
        content = read_file(file_path)
        assert "purpose" in content.lower(), f"{variant}: Missing purpose"


@pytest.mark.unit
class TestIncidentPostmortemSubagent:
    """Test suite for postmortem subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "incident" / "subagents" / "postmortem"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for postmortem"


@pytest.mark.unit
class TestIncidentRunbookSubagent:
    """Test suite for runbook subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "incident" / "subagents" / "runbook"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for runbook"


@pytest.mark.unit
class TestIncidentOncallSubagent:
    """Test suite for oncall subagent."""

    @pytest.fixture
    def subagent_dir(self, agents_dir):
        """Get subagent directory."""
        return agents_dir / "incident" / "subagents" / "oncall"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    def test_subagent_variant_exists(self, subagent_dir, variant):
        """Test that variant exists."""
        file_path = subagent_dir / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for oncall"
