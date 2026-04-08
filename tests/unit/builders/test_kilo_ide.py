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

    def test_kilo_ide_builder_build_creates_new_format_files(self):
        """KiloIDEBuilder.build() should create new .kilo/agents/ format."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            # Should have created new-format structure
            assert (output / ".kilocode").exists(), ".kilocode/ should exist for core files"
            assert (output / ".kilo").exists(), ".kilo/ should exist for agents"
            assert (output / ".kilo" / "agents").exists(), ".kilo/agents/ should exist"
            assert (output / ".kiloignore").exists(), ".kiloignore should exist"
            # Should also create AGENTS.md
            assert (output / "AGENTS.md").exists(), "AGENTS.md should exist"
            # Should create individual agent files
            agents_dir = output / ".kilo" / "agents"
            agent_files = list(agents_dir.glob("*.md"))
            assert len(agent_files) > 0, "Should create at least one agent file in .kilo/agents/"

    def test_kilo_ide_builder_creates_agent_files(self):
        """KiloIDEBuilder should create individual .kilo/agents/{agent}.md files."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            agents_dir = output / ".kilo" / "agents"
            # Check for specific agents
            architect_file = agents_dir / "architect.md"
            assert architect_file.exists(), "architect.md should exist"
            # Read content to verify frontmatter
            content = architect_file.read_text(encoding="utf-8")
            assert content.startswith("---"), "Agent files should start with YAML frontmatter"
            assert "description:" in content, "Agent files should have description field"
            assert "permission:" in content, "Agent files should have permission field"
            assert "mode:" in content, "Agent files should have mode field"

    def test_kilo_ide_builder_dry_run(self):
        """KiloIDEBuilder.build() with dry_run=True should not write files."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, dry_run=True)
            # No files should be created (only AGENTS.md)
            assert not (output / ".kilo").exists(), ".kilo/ should not exist in dry-run"
            # Result should contain [dry-run] indicators
            dry_run_entries = [r for r in result if "[dry-run]" in r]
            assert len(dry_run_entries) > 0, "Should have dry-run entries"

    def test_kilo_ide_builder_returns_action_strings(self):
        """KiloIDEBuilder.build() should return action strings."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
            assert len(result) > 0
            assert all(isinstance(r, str) for r in result)

    def test_kilo_ide_builder_creates_agent_with_permissions(self):
        """Generated agent files should have proper permission objects."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            architect_file = output / ".kilo" / "agents" / "architect.md"
            content = architect_file.read_text(encoding="utf-8")
            # Check for permission structure
            assert "read:" in content, "Should have read permission"
            assert "allow" in content, "Should have allow keyword in permissions"


class TestKiloIDEPermissionMapping(unittest.TestCase):
    """Tests for permission mapping from old to new format."""

    def test_map_groups_to_permissions_read_only(self):
        """Test mapping of 'read' permission."""
        builder = KiloIDEBuilder()
        groups = ["read"]
        permissions = builder._map_groups_to_permissions(groups)
        assert "read" in permissions
        assert permissions["read"]["*"] == "allow"

    def test_map_groups_to_permissions_edit_unrestricted(self):
        """Test mapping of unrestricted 'edit' permission."""
        builder = KiloIDEBuilder()
        groups = ["read", "edit"]
        permissions = builder._map_groups_to_permissions(groups)
        assert "edit" in permissions
        assert permissions["edit"]["*"] == "allow"

    def test_map_groups_to_permissions_edit_restricted(self):
        """Test mapping of restricted 'edit' permission with file patterns."""
        builder = KiloIDEBuilder()
        groups = [
            "read",
            ["edit", [{"fileRegex": r"docs/.*\.md$"}]]
        ]
        permissions = builder._map_groups_to_permissions(groups)
        assert "edit" in permissions
        # Should have deny-all default
        assert permissions["edit"]["*"] == "deny"
        # Should have allow for pattern
        found_allow = any(v == "allow" for k, v in permissions["edit"].items() if k != "*")
        assert found_allow, "Should have at least one file pattern with allow"

    def test_map_groups_to_permissions_command(self):
        """Test mapping of 'command' permission."""
        builder = KiloIDEBuilder()
        groups = ["read", "command"]
        permissions = builder._map_groups_to_permissions(groups)
        assert "bash" in permissions
        assert permissions["bash"] == "allow"


class TestKiloIDETemplateVariables(unittest.TestCase):
    """Tests for template variable substitution in KiloIDEBuilder."""

    def test_template_substitution_with_config(self):
        """KiloIDEBuilder should substitute template variables."""
        builder = KiloIDEBuilder()
        config = {
            "spec": {
                "language": "python",
                "runtime": "CPython 3.12",
                "package_manager": "uv",
                "linter": ["ruff", "pyright"],
                "formatter": ["ruff"],
                "testing_framework": "pytest",
                "mocking_library": "unittest.mock",
                "coverage_tool": "pytest-cov",
                "mutation_tool": "mutmut",
                "abstract_class_style": "interface",
                "coverage": {
                    "line": 80,
                    "branch": 70,
                    "function": 90,
                    "statement": 85,
                    "mutation": 80,
                    "path": 60,
                },
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
        assert ".kilocode/" in content or ".kilo/" in content
        # Should mention core files location
        assert "system.md" in content or "conventions.md" in content

    def test_agents_md_content_includes_all_modes(self):
        """KiloIDEBuilder AGENTS.md should list all modes."""
        builder = KiloIDEBuilder()
        content = builder._get_agents_md_content()
        # Should include key modes
        assert "architect" in content
        assert "code" in content
        assert "test" in content

    def test_agents_md_created_with_content(self):
        """KiloIDEBuilder should create AGENTS.md with correct content."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            agents_file = output / "AGENTS.md"
            assert agents_file.exists()
            content = agents_file.read_text(encoding="utf-8")
            # Verify the file has content
            assert len(content) > 100
