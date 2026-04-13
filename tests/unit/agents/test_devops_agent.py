"""Unit tests for DevOps Agent."""

import pytest


@pytest.mark.unit
class TestDevOpsAgent:
    """Test suite for devops agent."""

    @pytest.fixture
    def agent_file(self, agents_dir):
        """Get devops agent file."""
        return agents_dir / "devops" / "prompt.md"

    def test_agent_exists(self, agent_file):
        """Test that agent file exists."""
        assert agent_file.exists(), "devops/prompt.md not found"


@pytest.mark.unit
class TestDevOpsAgentSubagents:
    """Test suite for devops agent subagents."""

    @pytest.fixture
    def subagents_dir(self, agents_dir):
        """Get devops subagents directory."""
        return agents_dir / "devops" / "subagents"

    @pytest.mark.parametrize(
        "subagent_name", ["docker", "kubernetes", "aws", "terraform-deployment", "gitops"]
    )
    def test_subagent_exists(self, subagents_dir, subagent_name):
        """Test that subagent exists."""
        subagent_dir = subagents_dir / subagent_name
        assert subagent_dir.exists(), f"Subagent dir not found: {subagent_name}"

    @pytest.mark.parametrize("variant", ["minimal", "verbose"])
    @pytest.mark.parametrize(
        "subagent_name", ["docker", "kubernetes", "aws", "terraform-deployment", "gitops"]
    )
    def test_subagent_variant_exists(self, subagents_dir, subagent_name, variant):
        """Test that subagent variants exist."""
        file_path = subagents_dir / subagent_name / variant / "prompt.md"
        assert file_path.exists(), f"Missing {variant} variant for {subagent_name}"
