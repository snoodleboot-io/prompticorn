"""Unit tests for promptcli.builders.kilo."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from promptcli.builders.kilo import KiloBuilder


class TestKiloBuilder(unittest.TestCase):
    """Tests for the KiloBuilder class."""

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
        with patch("promptcli.builders.kilo.ALWAYS_ON", []):
            with patch("promptcli.builders.kilo.MODE_FILES", {}):
                result = builder.build(Path("/tmp/output"), dry_run=True)
        assert isinstance(result, list)
        assert all(isinstance(item, str) for item in result)

    def test_kilo_builder_dry_run_does_not_write_files(self):
        """KiloBuilder.build() with dry_run=True should not write files."""
        builder = KiloBuilder()
        with patch("promptcli.builders.kilo.ALWAYS_ON", []):
            with patch("promptcli.builders.kilo.MODE_FILES", {}):
                with patch("shutil.copy2") as mock_copy:
                    result = builder.build(Path("/tmp/output"), dry_run=True)
                    mock_copy.assert_not_called()

    def test_kilo_builder_build_creates_files_when_not_dry_run(self):
        """KiloBuilder.build() should create files when dry_run=False."""
        builder = KiloBuilder()
        with patch("promptcli.builders.kilo.ALWAYS_ON", ["core-system.md"]):
            with patch("promptcli.builders.kilo.MODE_FILES", {}):
                with patch(
                    "promptcli.builders.kilo.prompt_path"
                ) as mock_prompt_path:
                    with patch("shutil.copy2") as mock_copy:
                        mock_prompt_path.return_value = Path(
                            "/fake/prompts/core-system.md"
                        )
                        result = builder.build(Path("/tmp/output"), dry_run=False)
                        mock_copy.assert_called()

    def test_kilo_builder_returns_action_strings(self):
        """KiloBuilder.build() should return action strings."""
        builder = KiloBuilder()
        with patch("promptcli.builders.kilo.ALWAYS_ON", ["core-system.md"]):
            with patch("promptcli.builders.kilo.MODE_FILES", {}):
                with patch(
                    "promptcli.builders.kilo.prompt_path"
                ) as mock_prompt_path:
                    mock_prompt_path.return_value = Path(
                        "/fake/prompts/core-system.md"
                    )
                    result = builder.build(Path("/tmp/output"), dry_run=True)
                    # Should contain either ✓ or [dry-run] prefix
                    assert len(result) > 0
                    assert any(
                        "core-system.md" in item for item in result
                    )
