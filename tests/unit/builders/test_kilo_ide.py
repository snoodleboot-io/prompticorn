"""Unit tests for promptosaurus.builders.kilo_ide."""

import tempfile
import unittest
from pathlib import Path

from promptosaurus.builders.kilo.kilo_ide import KiloIDEBuilder


class TestKiloIDEBuilder(unittest.TestCase):
    """Tests for KiloIDEBuilder."""

    def test_kilo_ide_builder_is_builder_subclass(self):
        """KiloIDEBuilder should be a subclass of Builder."""
        from promptosaurus.builders.builder import Builder

        assert issubclass(KiloIDEBuilder, Builder)

    def test_kilo_ide_builder_has_build_method(self):
        """KiloIDEBuilder should have a build method."""
        builder = KiloIDEBuilder()
        assert hasattr(builder, "build")
        assert callable(builder.build)

    def test_kilo_ide_builder_build_returns_list(self):
        """KiloIDEBuilder.build() should return a list of strings."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
            assert isinstance(result, list)
            assert all(isinstance(r, str) for r in result)

    def test_kilo_ide_builder_build_creates_files(self):
        """KiloIDEBuilder.build() should create IDE-style files."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            # Should have created IDE-style structure
            assert (output / ".kilocode").exists()
            assert (output / ".kilocodemodes").exists()
            assert (output / ".kiloignore").exists()
            # Should also create AGENTS.md
            assert (output / "AGENTS.md").exists()

    def test_kilo_ide_builder_dry_run(self):
        """KiloIDEBuilder.build() with dry_run=True should not write files."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=True)
            # No files should be created
            assert not (output / ".kilocode").exists()
            assert not (output / ".kilocodemodes").exists()

    def test_kilo_ide_builder_returns_action_strings(self):
        """KiloIDEBuilder.build() should return action strings."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
            assert len(result) > 0
            assert all(isinstance(r, str) for r in result)

    def test_kilo_ide_builder_creates_mode_directories(self):
        """KiloIDEBuilder should create per-mode directories."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            # Should have created mode directories
            kilo_dir = output / ".kilocode"
            # Check for at least one rules-{mode} directory
            has_mode_dir = any(
                d.is_dir() and d.name.startswith("rules-")
                for d in kilo_dir.iterdir()
                if d.name != "rules"
            )
            self.assertTrue(has_mode_dir, "Expected at least one rules-{mode} directory")


class TestKiloIDETemplateVariables(unittest.TestCase):
    """Tests for template variable substitution in KiloIDEBuilder."""

    def test_template_substitution_with_config(self):
        """KiloIDEBuilder should substitute template variables."""
        builder = KiloIDEBuilder()
        config = {
            "spec": {
                "language": "python",
                "test_framework": "pytest",
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            # This should not raise an error
            result = builder.build(output, config=config, dry_run=False)
            assert isinstance(result, list)


class TestKiloIDEAgentsContent(unittest.TestCase):
    """Tests for AGENTS.md content generation in KiloIDEBuilder."""

    def test_get_agents_md_content_exists(self):
        """KiloIDEBuilder should have _get_agents_md_content method."""
        builder = KiloIDEBuilder()
        assert hasattr(builder, "_get_agents_md_content")
        assert callable(builder._get_agents_md_content)

    def test_agents_md_content_includes_ide_structure(self):
        """KiloIDEBuilder AGENTS.md should include IDE structure info."""
        builder = KiloIDEBuilder()
        content = builder._get_agents_md_content()
        # Should mention .kilocode/ directory structure
        assert ".kilocode/" in content
        assert "IDE format" in content
        # Should mention core files location
        assert "system.md" in content
        assert "conventions.md" in content

    def test_agents_md_content_includes_all_modes(self):
        """KiloIDEBuilder AGENTS.md should list all modes."""
        builder = KiloIDEBuilder()
        content = builder._get_agents_md_content()
        # Should include key modes
        assert "architect" in content
        assert "code" in content
        assert "test" in content
        assert "debug" in content

    def test_agents_md_created_with_content(self):
        """KiloIDEBuilder should create AGENTS.md with correct content."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            agents_file = output / "AGENTS.md"
            assert agents_file.exists()
            content = agents_file.read_text(encoding="utf-8")
            # Verify IDE-specific content
            assert ".kilocode/" in content
            assert "IDE format" in content
