"""Unit tests for ML/AI Agent."""

import pytest


@pytest.mark.unit
class TestMLAIAgent:
    """Test suite for ML/AI agent."""

    @pytest.fixture
    def agent_file(self, agents_dir):
        """Get ML/AI agent file."""
        return agents_dir / "mlai" / "prompt.md"

    def test_agent_exists(self, agent_file):
        """Test that agent file exists."""
        assert agent_file.exists(), "mlai/prompt.md not found"


@pytest.mark.unit
class TestMLAIAgentSubagents:
    """Test suite for ML/AI agent subagents."""

    @pytest.fixture
    def subagents_dir(self, agents_dir):
        """Get ML/AI subagents directory."""
        return agents_dir / "mlai" / "subagents"

    @pytest.mark.parametrize(
        "subagent_name", ["data-preparation", "model-training", "deployment", "monitoring"]
    )
    def test_subagent_exists(self, subagents_dir, subagent_name):
        """Test that subagent exists."""
        subagent_dir = subagents_dir / subagent_name
        assert subagent_dir.exists(), f"Subagent dir not found: {subagent_name}"
