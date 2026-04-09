"""Unit tests for CursorBuilder class.

Tests cover:
- Markdown header generation
- System prompt as prose formatting
- Constraints section generation
- Tools section generation
- Workflows section generation
- Subagents section generation
- Agent validation
- Component loading with variants
- Error handling
- Output format verification
"""

import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from promptosaurus.builders.cursor_builder import CursorBuilder
from promptosaurus.builders.base import BuildOptions
from promptosaurus.builders.errors import BuilderValidationError
from promptosaurus.ir.models import Agent


class TestCursorBuilderInitialization:
    """Tests for CursorBuilder initialization."""

    def test_init_with_default_agents_dir(self) -> None:
        """Test CursorBuilder initializes with default 'agents' directory."""
        builder = CursorBuilder()
        assert builder.agents_dir == "agents"

    def test_init_with_custom_agents_dir(self) -> None:
        """Test CursorBuilder initializes with custom agents directory."""
        builder = CursorBuilder(agents_dir="/custom/agents")
        assert builder.agents_dir == "/custom/agents"

    def test_init_with_path_object(self) -> None:
        """Test CursorBuilder accepts Path object for agents_dir."""
        path = Path("/custom/agents")
        builder = CursorBuilder(agents_dir=path)
        assert builder.agents_dir == path

