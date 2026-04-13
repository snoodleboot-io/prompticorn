"""Unit tests for Performance Agent."""

import pytest


@pytest.mark.unit
class TestPerformanceAgent:
    """Test suite for performance agent."""

    @pytest.fixture
    def agent_file(self, agents_dir):
        """Get performance agent file."""
        return agents_dir / "performance" / "prompt.md"

    def test_agent_exists(self, agent_file):
        """Test that agent file exists."""
        assert agent_file.exists(), "performance/prompt.md not found"


@pytest.mark.unit
class TestPerformanceAgentSubagents:
    """Test suite for performance agent subagents."""

    @pytest.fixture
    def subagents_dir(self, agents_dir):
        """Get performance subagents directory."""
        return agents_dir / "performance" / "subagents"

    @pytest.mark.parametrize(
        "subagent_name",
        ["profiling", "bottleneck-analysis", "optimization-strategies", "benchmarking"],
    )
    def test_subagent_exists(self, subagents_dir, subagent_name):
        """Test that subagent exists."""
        subagent_dir = subagents_dir / subagent_name
        assert subagent_dir.exists(), f"Subagent dir not found: {subagent_name}"
