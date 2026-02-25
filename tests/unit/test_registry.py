"""Unit tests for promptcli.registry."""

import unittest
from pathlib import Path

import pytest


class TestRegistry(unittest.TestCase):
    """Tests for the registry module."""

    def test_prompts_dir_is_path(self):
        """PROMPTS_DIR should be a Path object."""
        from promptcli.registry import PROMPTS_DIR

        assert isinstance(PROMPTS_DIR, Path)

    def test_prompts_dir_exists(self):
        """PROMPTS_DIR should exist."""
        from promptcli.registry import PROMPTS_DIR

        assert PROMPTS_DIR.exists()

    def test_prompts_dir_is_directory(self):
        """PROMPTS_DIR should be a directory."""
        from promptcli.registry import PROMPTS_DIR

        assert PROMPTS_DIR.is_dir()

    def test_always_on_is_list(self):
        """ALWAYS_ON should be a list."""
        from promptcli.registry import ALWAYS_ON

        assert isinstance(ALWAYS_ON, list)

    def test_always_on_contains_strings(self):
        """ALWAYS_ON should contain string filenames."""
        from promptcli.registry import ALWAYS_ON

        assert all(isinstance(f, str) for f in ALWAYS_ON)

    def test_modes_is_dict(self):
        """MODES should be a dictionary."""
        from promptcli.registry import MODES

        assert isinstance(MODES, dict)

    def test_modes_not_empty(self):
        """MODES should not be empty."""
        from promptcli.registry import MODES

        assert len(MODES) > 0

    def test_mode_files_is_dict(self):
        """MODE_FILES should be a dictionary."""
        from promptcli.registry import MODE_FILES

        assert isinstance(MODE_FILES, dict)

    def test_mode_files_not_empty(self):
        """MODE_FILES should not be empty."""
        from promptcli.registry import MODE_FILES

        assert len(MODE_FILES) > 0

    def test_prompt_path_returns_path(self):
        """prompt_path() should return a Path."""
        from promptcli.registry import prompt_path

        result = prompt_path("core-system.md")
        assert isinstance(result, Path)

    def test_prompt_path_includes_filename(self):
        """prompt_path() should include the filename."""
        from promptcli.registry import prompt_path

        result = prompt_path("core-system.md")
        assert result.name == "core-system.md"

    def test_dest_name_strips_prefix(self):
        """dest_name() should strip the mode prefix."""
        from promptcli.registry import dest_name

        result = dest_name("architect", "architect-scaffold.md")
        assert result == "scaffold.md"

    def test_dest_name_with_extension(self):
        """dest_name() should handle custom extensions."""
        from promptcli.registry import dest_name

        result = dest_name("architect", "architect-scaffold.md", ext=".mdc")
        assert result == "scaffold.mdc"

    def test_validate_returns_list(self):
        """validate() should return a list."""
        from promptcli.registry import validate

        result = validate()
        assert isinstance(result, list)

    def test_validate_with_valid_files_returns_empty(self):
        """validate() should return empty list when all files exist."""
        from promptcli.registry import validate

        errors = validate()
        # Filter out orphan warnings - we may have extra files
        missing_errors = [e for e in errors if "MISSING" in e]
        assert len(missing_errors) == 0, f"Missing files: {missing_errors}"
