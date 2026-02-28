"""Unit tests for promptcli.registry."""

import unittest
from pathlib import Path


class TestRegistry(unittest.TestCase):
    """Tests for the registry module."""

    def test_prompts_dir_is_path(self):
        """prompts_dir should be a Path object."""
        from promptcli.registry import registry

        assert isinstance(registry.prompts_dir, Path)

    def test_prompts_dir_exists(self):
        """prompts_dir should exist."""
        from promptcli.registry import registry

        assert registry.prompts_dir.exists()

    def test_prompts_dir_is_directory(self):
        """prompts_dir should be a directory."""
        from promptcli.registry import registry

        assert registry.prompts_dir.is_dir()

    def test_always_on_is_list(self):
        """always_on should be a list."""
        from promptcli.registry import registry

        assert isinstance(registry.always_on, list)

    def test_always_on_contains_strings(self):
        """always_on should contain string filenames."""
        from promptcli.registry import registry

        assert all(isinstance(f, str) for f in registry.always_on)

    def test_modes_is_dict(self):
        """modes should be a dictionary."""
        from promptcli.registry import registry

        assert isinstance(registry.modes, dict)

    def test_modes_not_empty(self):
        """modes should not be empty."""
        from promptcli.registry import registry

        assert len(registry.modes) > 0

    def test_mode_files_is_dict(self):
        """mode_files should be a dictionary."""
        from promptcli.registry import registry

        assert isinstance(registry.mode_files, dict)

    def test_mode_files_not_empty(self):
        """mode_files should not be empty."""
        from promptcli.registry import registry

        assert len(registry.mode_files) > 0

    def test_prompt_path_returns_path(self):
        """prompt_path() should return a Path."""
        from promptcli.registry import registry

        result = registry.prompt_path("core-system.md")
        assert isinstance(result, Path)

    def test_prompt_path_includes_filename(self):
        """prompt_path() should include the filename."""
        from promptcli.registry import registry

        result = registry.prompt_path("core-system.md")
        assert result.name == "core-system.md"

    def test_dest_name_strips_prefix(self):
        """dest_name() should strip the mode prefix."""
        from promptcli.registry import registry

        result = registry.dest_name("architect", "architect-scaffold.md")
        assert result == "scaffold.md"

    def test_dest_name_with_extension(self):
        """dest_name() should handle custom extensions."""
        from promptcli.registry import registry

        result = registry.dest_name("architect", "architect-scaffold.md", ext=".mdc")
        assert result == "scaffold.mdc"

    def test_validate_returns_list(self):
        """validate() should return a list."""
        from promptcli.registry import registry

        result = registry.validate()
        assert isinstance(result, list)

    def test_validate_with_valid_files_returns_empty(self):
        """validate() should return empty list when all files exist."""
        from promptcli.registry import registry

        errors = registry.validate()
        # Filter out orphan warnings - we may have extra files
        missing_errors = [e for e in errors if "MISSING" in e]
        assert len(missing_errors) == 0, f"Missing files: {missing_errors}"
