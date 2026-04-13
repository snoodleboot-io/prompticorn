"""Unit tests for Observability Agent."""

import pytest


@pytest.mark.unit
class TestObservabilityAgent:
    """Test suite for observability agent."""

    @pytest.fixture
    def agent_file(self, agents_dir):
        """Get observability agent file."""
        return agents_dir / "observability" / "prompt.md"

    @pytest.fixture
    def agent_content(self, agent_file, read_file):
        """Read agent file content."""
        assert agent_file.exists(), f"Agent file not found: {agent_file}"
        return read_file(agent_file)

    def test_agent_exists(self, agent_file):
        """Test that agent file exists."""
        assert agent_file.exists(), "observability/prompt.md not found"

    def test_agent_has_content(self, agent_content):
        """Test that agent has meaningful content."""
        assert len(agent_content.strip()) > 50, "Agent content should be meaningful"

    def test_agent_subagents_exist(self, agents_dir):
        """Test that all observability subagents exist."""
        expected = ["metrics", "logging", "tracing", "alerting", "dashboards"]
        for subagent in expected:
            subagent_dir = agents_dir / "observability" / "subagents" / subagent
            assert subagent_dir.exists(), f"Missing observability subagent: {subagent}"


@pytest.mark.unit
class TestObservabilitySubagents:
    """Test suite for observability subagents."""

    @pytest.fixture
    def subagents_dir(self, agents_dir):
        """Get observability subagents directory."""
        return agents_dir / "observability" / "subagents"

    @pytest.mark.parametrize(
        "subagent_name", ["metrics", "logging", "tracing", "alerting", "dashboards"]
    )
    def test_subagent_exists(self, subagents_dir, subagent_name):
        """Test that subagent exists."""
        subagent_dir = subagents_dir / subagent_name
        assert subagent_dir.exists(), f"Subagent dir not found: {subagent_name}"
