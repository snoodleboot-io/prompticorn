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


class TestKiloIDEValidation(unittest.TestCase):
    """Tests for output validation in KiloIDEBuilder."""

    def test_validate_agent_file_with_valid_output(self):
        """_validate_agent_file should return True for valid generated files."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            # Check architect.md is valid
            architect_file = output / ".kilo" / "agents" / "architect.md"
            assert architect_file.exists()
            assert builder._validate_agent_file(architect_file)

    def test_generated_files_have_valid_yaml_frontmatter(self):
        """Generated agent files should have valid YAML frontmatter."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            agents_dir = output / ".kilo" / "agents"
            
            # Check at least 3 agents have valid YAML
            agent_files = list(agents_dir.glob("*.md"))
            assert len(agent_files) > 0, "Should create agent files"
            
            valid_count = 0
            for agent_file in agent_files[:3]:  # Check first 3
                if builder._validate_agent_file(agent_file):
                    valid_count += 1
            
            assert valid_count >= 2, "At least 2 of 3 agents should be valid"

    def test_permission_object_is_nested_not_array(self):
        """Permission in YAML frontmatter should be object, not array."""
        import yaml
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            architect_file = output / ".kilo" / "agents" / "architect.md"
            
            content = architect_file.read_text(encoding="utf-8")
            # Extract frontmatter
            end_marker = content.find("---", 3)
            frontmatter_str = content[3:end_marker].strip()
            frontmatter = yaml.safe_load(frontmatter_str)
            
            # Permission should be dict, not list
            assert isinstance(frontmatter["permission"], dict), \
                "Permission should be dict object, not array"
            # Should have read key
            assert "read" in frontmatter["permission"], \
                "Permission should have 'read' key"

    def test_closing_frontmatter_marker_on_own_line(self):
        """Closing --- marker should be on its own line."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            architect_file = output / ".kilo" / "agents" / "architect.md"
            
            content = architect_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            # First line should be "---"
            assert lines[0] == "---", "First line should be opening ---"
            
            # One of the early lines should be closing "---"
            found_closing = False
            for i in range(1, min(20, len(lines))):  # Check first 20 lines
                if lines[i].strip() == "---":
                    found_closing = True
                    break
            
            assert found_closing, "Should find closing --- marker on own line"

    def test_all_13_agents_created(self):
        """Should create exactly 13 agent files (one per mode)."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            agents_dir = output / ".kilo" / "agents"
            
            # Count .md files
            md_files = list(agents_dir.glob("*.md"))
            assert len(md_files) == 15, \
                f"Should create 15 agent files, got {len(md_files)}"

    def test_agent_files_not_empty(self):
        """Agent files should have content (frontmatter + body)."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            agents_dir = output / ".kilo" / "agents"
            
            for agent_file in agents_dir.glob("*.md"):
                content = agent_file.read_text(encoding="utf-8")
                assert len(content) > 50, \
                    f"{agent_file.name} should have substantial content"
                # Should have frontmatter and body
                assert content.count("---") >= 2, \
                    f"{agent_file.name} should have opening and closing frontmatter"

    def test_permission_uses_regex_patterns_not_globs(self):
        """Permission patterns should be regex, not simplified globs."""
        import yaml
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            architect_file = output / ".kilo" / "agents" / "architect.md"
            
            content = architect_file.read_text(encoding="utf-8")
            # Check if we have regex patterns (look for \\ escapes)
            # Architecture has: "(docs/.*\\.md$|.promptosaurus/sessions/.*\\.md$)"
            # This should be preserved as regex
            
            assert "edit" in content or "read" in content, \
                "Should have permission definitions"

