"""Unit tests for promptosaurus.builders.cline."""

import unittest
from pathlib import Path
from unittest.mock import patch

from promptosaurus.builders.cline import ClineBuilder


class TestClineBuilder(unittest.TestCase):
    """Tests for the ClineBuilder class."""

    def test_cline_builder_is_builder_subclass(self):
        """ClineBuilder should be a subclass of Builder."""
        from promptosaurus.builders.builder import Builder

        assert issubclass(ClineBuilder, Builder)

    def test_cline_builder_has_build_method(self):
        """ClineBuilder should have a build method."""
        builder = ClineBuilder()
        assert hasattr(builder, "build")
        assert callable(builder.build)

    def test_cline_builder_build_returns_list(self):
        """ClineBuilder.build() should return a list of strings."""
        builder = ClineBuilder()
        with patch("promptosaurus.builders.builder.Builder._build_concatenated") as mock_concat:
            mock_concat.return_value = "# .clinerules\n"
            result = builder.build(Path("/tmp/output"), dry_run=True)
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_cline_builder_dry_run_returns_dry_run_prefix(self):
        """ClineBuilder.build() with dry_run=True should return action with [dry-run]."""
        builder = ClineBuilder()
        with patch("promptosaurus.builders.builder.Builder._build_concatenated") as mock_concat:
            mock_concat.return_value = "# .clinerules\nline1\nline2\n"
            result = builder.build(Path("/tmp/output"), dry_run=True)
            assert any("[dry-run]" in item for item in result)

    def test_cline_builder_returns_action_string_with_line_count(self):
        """ClineBuilder.build() should return action string with line count."""
        builder = ClineBuilder()
        with patch("promptosaurus.builders.builder.Builder._build_concatenated") as mock_concat:
            mock_concat.return_value = "# .clinerules\nline1\nline2\n"
            result = builder.build(Path("/tmp/output"), dry_run=True)
            assert any("lines" in item for item in result)
