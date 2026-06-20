"""Unit tests for prompticorn.registry."""

import unittest
from pathlib import Path


class TestRegistry(unittest.TestCase):
    """Tests for the registry module."""

    def test_prompts_dir_is_path(self):
        """prompts_dir should be a Path object."""
        from prompticorn.registry import registry

        assert isinstance(registry.prompts_dir, Path)

    def test_prompts_dir_exists(self):
        """prompts_dir should exist."""
        from prompticorn.registry import registry

        assert registry.prompts_dir.exists()

    def test_prompts_dir_is_directory(self):
        """prompts_dir should be a directory."""
        from prompticorn.registry import registry

        assert registry.prompts_dir.is_dir()

    def test_prompt_path_returns_path(self):
        """prompt_path() should return a Path."""
        from prompticorn.registry import registry

        result = registry.prompt_path("core-system.md")
        assert isinstance(result, Path)

    def test_prompt_path_includes_filename(self):
        """prompt_path() should include the filename."""
        from prompticorn.registry import registry

        result = registry.prompt_path("core-system.md")
        assert result.name == "core-system.md"

    def test_dest_name_strips_prefix(self):
        """dest_name() should strip the mode prefix."""
        from prompticorn.registry import registry

        result = registry.dest_name("architect", "architect-scaffold.md")
        assert result == "scaffold.md"

    def test_dest_name_with_extension(self):
        """dest_name() should handle custom extensions."""
        from prompticorn.registry import registry

        result = registry.dest_name("architect", "architect-scaffold.md", ext=".mdc")
        assert result == "scaffold.mdc"
