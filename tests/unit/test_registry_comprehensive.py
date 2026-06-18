"""Comprehensive unit tests for prompticorn.registry.

This module provides extensive test coverage for the Registry class,
testing all methods, validators, and edge cases.
"""

import shutil
import tempfile
from pathlib import Path

import pytest

from prompticorn.registry import Registry, _dest_name, _prompt_body_cached


class TestModuleLevelFunctions:
    """Tests for module-level functions."""

    def test_dest_name_removes_mode_prefix(self):
        """Should strip mode prefix from filename."""
        assert _dest_name("code", "code-feature.md") == "feature.md"
        assert _dest_name("test", "test-strategy.md") == "strategy.md"
        assert _dest_name("debug", "debug-root-cause.md") == "root-cause.md"

    def test_dest_name_handles_no_prefix(self):
        """Should return filename unchanged if no mode prefix."""
        assert _dest_name("code", "feature.md") == "feature.md"
        assert _dest_name("test", "something.md") == "something.md"

    def test_dest_name_with_custom_extension(self):
        """Should replace extension when specified."""
        assert _dest_name("code", "code-feature.md", ".txt") == "feature.txt"
        assert _dest_name("test", "test-strategy.md", ".json") == "strategy.json"

    def test_prompt_body_cached_strips_header_comments(self):
        """Should strip header comments from prompt files."""
        # Create a temporary directory and file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            content = """# test.md
# Behavior when testing
Some actual content
More content"""
            test_file.write_text(content)

            # Clear cache first
            _prompt_body_cached.cache_clear()

            result = _prompt_body_cached(Path(tmpdir), "test.md")
            assert result == "Some actual content\nMore content"

    def test_prompt_body_cached_strips_html_comments(self):
        """Should strip HTML comment headers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            content = """<!-- path: some/path.md -->
# Real Content
Body text"""
            test_file.write_text(content)

            _prompt_body_cached.cache_clear()

            result = _prompt_body_cached(Path(tmpdir), "test.md")
            assert result == "# Real Content\nBody text"

    def test_prompt_body_cached_uses_cache(self):
        """Should cache results for performance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.md"
            test_file.write_text("Content")

            _prompt_body_cached.cache_clear()

            # First call
            result1 = _prompt_body_cached(Path(tmpdir), "test.md")

            # Modify file
            test_file.write_text("Modified")

            # Second call should return cached value
            result2 = _prompt_body_cached(Path(tmpdir), "test.md")

            assert result1 == result2 == "Content"


class TestRegistryInitialization:
    """Tests for Registry initialization and basic properties."""

    def test_registry_is_frozen(self):
        """Registry should be frozen (immutable)."""
        from pydantic import ValidationError

        registry = Registry()
        with pytest.raises(ValidationError):  # Pydantic raises validation error for frozen models
            registry.prompts_dir = Path("/tmp")  # Should not be able to modify

    def test_prompts_dir_default_path(self):
        """Should have correct default prompts_dir path."""
        registry = Registry()
        assert registry.prompts_dir.name == "prompts"
        assert registry.prompts_dir.parent.name == "prompticorn"


class TestRegistryValidators:
    """Tests for Registry validators."""

    def test_prompts_dir_must_exist_validation(self):
        """Should validate that prompts_dir exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Valid directory
            registry = Registry(prompts_dir=Path(tmpdir))
            assert registry.prompts_dir == Path(tmpdir)

            # Non-existent directory
            with pytest.raises(ValueError, match="does not exist"):
                Registry(prompts_dir=Path("/nonexistent/path"))

    def test_prompts_dir_must_be_directory(self):
        """Should validate that prompts_dir is a directory."""
        with tempfile.NamedTemporaryFile() as tmpfile:
            with pytest.raises(ValueError, match="is not a directory"):
                Registry(prompts_dir=Path(tmpfile.name))


class TestRegistryMethods:
    """Tests for Registry methods."""

    @pytest.fixture
    def test_registry(self):
        """Create a test registry with temporary directory."""
        tmpdir = tempfile.mkdtemp()

        # Create some test files
        prompts_dir = Path(tmpdir) / "prompts"
        prompts_dir.mkdir()

        # Create test files
        (prompts_dir / "test1.md").write_text("# test1.md\nContent 1")
        (prompts_dir / "test2.md").write_text("<!-- header -->\nContent 2")

        registry = Registry(prompts_dir=prompts_dir)

        yield registry

        # Cleanup
        shutil.rmtree(tmpdir)

    def test_prompt_path_returns_absolute_path(self, test_registry):
        """Should return absolute path to prompt file."""
        path = test_registry.prompt_path("test1.md")
        assert path.is_absolute()
        assert path.name == "test1.md"
        assert path.exists()

    def test_prompt_body_reads_and_strips_header(self, test_registry):
        """Should read prompt file and strip header."""
        _prompt_body_cached.cache_clear()

        body = test_registry.prompt_body("test1.md")
        assert body == "Content 1"

        body2 = test_registry.prompt_body("test2.md")
        assert body2 == "Content 2"

    def test_dest_name_method(self, test_registry):
        """Should strip mode prefix using dest_name method."""
        assert test_registry.dest_name("test", "test-file.md") == "file.md"
        assert test_registry.dest_name("code", "code-feature.md", ".txt") == "feature.txt"


class TestRegistryIgnoreFileGeneration:
    """Tests for ignore file generation methods."""

    def test_generate_gitignore(self):
        """Should generate proper .gitignore content."""
        registry = Registry()
        content = registry.generate_gitignore()

        assert "# Auto-generated by prompt CLI" in content
        assert "__pycache__/" in content
        assert "node_modules/" in content
        assert ".env" in content
        assert ".DS_Store" in content
        assert content.endswith("\n")

    def test_generate_clineignore(self):
        """Should generate proper .clineignore content."""
        registry = Registry()
        content = registry.generate_clineignore()

        assert "# Auto-generated by prompt CLI" in content
        assert "# Files and directories to ignore in Cline" in content
        assert "__pycache__/" in content
        assert content.endswith("\n")

    def test_generate_cursorignore(self):
        """Should generate proper .cursorignore content."""
        registry = Registry()
        content = registry.generate_cursorignore()

        assert "# Auto-generated by prompt CLI" in content
        assert "# Files and directories to ignore in Cursor" in content
        assert "__pycache__/" in content
        assert content.endswith("\n")

    def test_generate_kiloignore(self):
        """Should generate proper .kiloignore content."""
        registry = Registry()
        content = registry.generate_kiloignore()

        assert "# Auto-generated by prompt CLI" in content
        assert "# Files and directories to ignore in Kilo Code" in content
        assert "__pycache__/" in content
        assert content.endswith("\n")

    def test_generate_copilotignore(self):
        """Should generate proper .copilotignore content."""
        registry = Registry()
        content = registry.generate_copilotignore()

        assert "# Auto-generated by prompt CLI" in content
        assert "# Files and directories to ignore in GitHub Copilot" in content
        assert "__pycache__/" in content
        assert content.endswith("\n")


class TestRegistryEdgeCases:
    """Tests for edge cases and error handling."""

    def test_copilot_apply_patterns(self):
        """Should have valid copilot apply patterns."""
        registry = Registry()

        assert "**" in registry.copilot_apply["architect"]
        assert "**/*.test.*" in registry.copilot_apply["test"]
        assert "**/*.yml" in registry.copilot_apply["orchestrator"]

    def test_default_ignore_patterns_comprehensive(self):
        """Should have comprehensive default ignore patterns."""
        registry = Registry()
        patterns = registry.default_ignore_patterns

        # Python patterns
        assert "__pycache__/" in patterns
        assert "*.py[cod]" in patterns

        # Dependencies
        assert "node_modules/" in patterns
        assert ".venv/" in patterns

        # Build outputs
        assert "dist/" in patterns
        assert "build/" in patterns

        # IDE
        assert ".idea/" in patterns
        assert ".vscode/" in patterns

        # Secrets
        assert ".env" in patterns
        assert "*.pem" in patterns

        # OS
        assert ".DS_Store" in patterns
        assert "Thumbs.db" in patterns


class TestRegistrySingleton:
    """Tests for the singleton registry instance."""

    def test_singleton_instance_exists(self):
        """Should have a singleton registry instance."""
        from prompticorn.registry import registry

        assert registry is not None
        assert isinstance(registry, Registry)
