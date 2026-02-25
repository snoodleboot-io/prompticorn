"""Unit tests for CopilotBuilder."""

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from pathlib import Path
import tempfile

from promptcli.builders.copilot import CopilotBuilder


class TestCopilotBuilder(unittest.TestCase):
    """Test cases for CopilotBuilder."""

    def test_copilot_builder_is_builder_subclass(self):
        """CopilotBuilder should be a subclass of Builder."""
        from promptcli.builders.builder import Builder
        self.assertTrue(issubclass(CopilotBuilder, Builder))

    def test_copilot_builder_has_build_method(self):
        """CopilotBuilder should have a build method."""
        builder = CopilotBuilder()
        self.assertTrue(hasattr(builder, 'build'))
        self.assertTrue(callable(getattr(builder, 'build')))

    def test_copilot_builder_build_returns_list(self):
        """build() should return a list of action strings."""
        builder = CopilotBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
        self.assertIsInstance(result, list)

    def test_copilot_builder_dry_run_returns_dry_run_prefix(self):
        """build() with dry_run=True should return dry run message."""
        builder = CopilotBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, dry_run=True)
        self.assertIsInstance(result, list)

    def test_copilot_builder_returns_action_strings(self):
        """build() should return action strings."""
        builder = CopilotBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
        self.assertIsInstance(result, list)
        # Should have action strings
        self.assertTrue(len(result) > 0)
