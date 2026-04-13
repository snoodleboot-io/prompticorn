"""Unit tests for Backend Agent."""

import pytest


@pytest.mark.unit
class TestBackendAgent:
    """Test suite for backend agent."""

    @pytest.fixture
    def agent_file(self, agents_dir):
        """Get backend agent file."""
        return agents_dir / "backend" / "prompt.md"

    @pytest.fixture
    def agent_content(self, agent_file, read_file):
        """Read agent file content."""
        assert agent_file.exists(), f"Agent file not found: {agent_file}"
        return read_file(agent_file)

    def test_agent_exists(self, agent_file):
        """Test that agent file exists."""
        assert agent_file.exists(), "backend/prompt.md not found"

    def test_agent_has_content(self, agent_content):
        """Test that agent has meaningful content."""
        assert len(agent_content.strip()) > 50, "Agent content should be meaningful"

    def test_agent_is_valid_file(self, agent_file):
        """Test that agent file exists and is readable."""
        assert agent_file.exists(), "Agent file should exist"
        assert agent_file.stat().st_size > 0, "Agent file should not be empty"


@pytest.mark.unit
class TestBackendAgentSubagents:
    """Test suite for backend agent subagents."""

    @pytest.fixture
    def subagents_dir(self, agents_dir):
        """Get backend subagents directory."""
        return agents_dir / "backend" / "subagents"

    @pytest.mark.parametrize("subagent_name", ["api-design", "microservices", "caching", "storage"])
    def test_subagent_exists(self, subagents_dir, subagent_name):
        """Test that subagent exists."""
        subagent_dir = subagents_dir / subagent_name
        assert subagent_dir.exists(), f"Subagent dir not found: {subagent_name}"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    @pytest.mark.parametrize("subagent_name", ["api-design", "microservices", "caching", "storage"])
    def test_subagent_variant_exists(self, subagents_dir, subagent_name, variant, read_file):
        """Test that subagent variants exist."""
        file_path = subagents_dir / subagent_name / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for {subagent_name}"

        content = read_file(file_path)
        assert len(content.strip()) > 20, f"{subagent_name}/{variant} too short: content missing"
