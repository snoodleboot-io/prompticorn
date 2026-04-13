"""Unit tests for ClaudeBuilder class.

Tests cover:
- JSON dictionary structure generation
- System prompt extraction
- Tools list with JSON schemas
- Instructions formatting from all sections
- Agent validation
- Component loading with variants
- Error handling
- JSON serializability verification
"""

from pathlib import Path

from promptosaurus.builders.claude_builder import ClaudeBuilder


class TestClaudeBuilderInitialization:
    """Tests for ClaudeBuilder initialization."""

    def test_init_with_default_agents_dir(self) -> None:
        """Test ClaudeBuilder initializes with default 'agents' directory."""
        builder = ClaudeBuilder()
        assert builder.agents_dir == "agents"

    def test_init_with_custom_agents_dir(self) -> None:
        """Test ClaudeBuilder initializes with custom agents directory."""
        builder = ClaudeBuilder(agents_dir="/custom/agents")
        assert builder.agents_dir == "/custom/agents"

    def test_init_with_path_object(self) -> None:
        """Test ClaudeBuilder accepts Path object for agents_dir."""
        path = Path("/custom/agents")
        builder = ClaudeBuilder(agents_dir=path)
        assert builder.agents_dir == path

