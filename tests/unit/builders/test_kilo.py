"""Unit tests for promptcli.builders.kilo."""

import tempfile
import unittest
from pathlib import Path

from promptcli.builders.kilo import KiloBuilder


class TestKiloBuilder(unittest.TestCase):
    """Tests for KiloBuilder."""

    def test_kilo_builder_is_builder_subclass(self):
        """KiloBuilder should be a subclass of Builder."""
        from promptcli.builders.builder import Builder

        assert issubclass(KiloBuilder, Builder)

    def test_kilo_builder_has_build_method(self):
        """KiloBuilder should have a build method."""
        builder = KiloBuilder()
        assert hasattr(builder, "build")
        assert callable(builder.build)

    def test_kilo_builder_build_returns_list(self):
        """KiloBuilder.build() should return a list of strings."""
        builder = KiloBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
            assert isinstance(result, list)
            assert all(isinstance(r, str) for r in result)

    def test_kilo_builder_build_creates_files(self):
        """KiloBuilder.build() should create files."""
        builder = KiloBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, dry_run=False)
            # Should have created files
            assert (output / ".kilo").exists()

    def test_kilo_builder_dry_run(self):
        """KiloBuilder.build() with dry_run=True should not write files."""
        builder = KiloBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, dry_run=True)
            # No files should be created
            assert not (output / ".kilo").exists()

    def test_kilo_builder_returns_action_strings(self):
        """KiloBuilder.build() should return action strings."""
        builder = KiloBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
            assert len(result) > 0
            assert all(isinstance(r, str) for r in result)
