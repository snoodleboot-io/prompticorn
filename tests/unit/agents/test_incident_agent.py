"""Unit tests for Incident Agent."""

import pytest


@pytest.mark.unit
class TestIncidentAgent:
    """Test suite for incident agent."""

    @pytest.fixture
    def agent_file(self, agents_dir):
        """Get incident agent file."""
        return agents_dir / "incident" / "prompt.md"

    @pytest.fixture
    def agent_content(self, agent_file, read_file):
        """Read agent file content."""
        assert agent_file.exists(), f"Agent file not found: {agent_file}"
        return read_file(agent_file)

    def test_agent_exists(self, agent_file):
        """Test that agent file exists."""
        assert agent_file.exists(), "incident/prompt.md not found"

    def test_agent_has_content(self, agent_content):
        """Test that agent has meaningful content."""
        assert len(agent_content.strip()) > 50, "Agent content should be meaningful"

    def test_agent_subagents_exist(self, agents_dir):
        """Test that all incident subagents exist."""
        expected = ["triage", "postmortem", "runbook", "oncall"]
        for subagent in expected:
            subagent_dir = agents_dir / "incident" / "subagents" / subagent
            assert subagent_dir.exists(), f"Missing incident subagent: {subagent}"
