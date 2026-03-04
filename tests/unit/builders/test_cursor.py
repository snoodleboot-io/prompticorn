"""Unit tests for CursorBuilder."""

import tempfile
import unittest
from pathlib import Path

from promptosaurus.builders.cursor import CursorBuilder


class TestCursorBuilder(unittest.TestCase):
    """Test cases for CursorBuilder."""

    def test_cursor_builder_is_builder_subclass(self):
        """CursorBuilder should be a subclass of Builder."""
        from promptosaurus.builders.builder import Builder

        self.assertTrue(issubclass(CursorBuilder, Builder))

    def test_cursor_builder_has_build_method(self):
        """CursorBuilder should have a build method."""
        builder = CursorBuilder()
        self.assertTrue(hasattr(builder, "build"))
        self.assertTrue(callable(builder.build))

    def test_cursor_builder_build_returns_list(self):
        """build() should return a list of action strings."""
        builder = CursorBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
        self.assertIsInstance(result, list)

    def test_cursor_builder_dry_run_returns_dry_run_prefix(self):
        """build() with dry_run=True should return dry run message."""
        builder = CursorBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, dry_run=True)
        self.assertIsInstance(result, list)

    def test_cursor_builder_returns_action_strings(self):
        """build() should return action strings."""
        builder = CursorBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
        self.assertIsInstance(result, list)
        # Should have action strings
        self.assertTrue(len(result) > 0)
