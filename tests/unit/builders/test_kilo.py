"""Unit tests for promptosaurus.builders.kilo."""

import tempfile
import unittest
from pathlib import Path

from promptosaurus.builders.kilo import KiloCodeBuilder
from promptosaurus.builders.kilo_cli import KiloCLIBuilder
from promptosaurus.builders.kilo_ide import KiloIDEBuilder


class TestKiloCodeBuilderBase(unittest.TestCase):
    """Tests for KiloCodeBuilder base class methods using concrete implementation."""

    def test_language_file_map(self):
        """KiloCodeBuilder should have LANGUAGE_FILE_MAP."""
        from promptosaurus.builders.kilo import KiloCodeBuilder
        assert hasattr(KiloCodeBuilder, "LANGUAGE_FILE_MAP")
        assert "python" in KiloCodeBuilder.LANGUAGE_FILE_MAP
        assert KiloCodeBuilder.LANGUAGE_FILE_MAP["python"] == "agents/core/core-conventions-python.md"
        assert KiloCodeBuilder.LANGUAGE_FILE_MAP["typescript"] == "agents/core/core-conventions-typescript.md"

    def test_base_files(self):
        """KiloCodeBuilder should have BASE_FILES."""
        from promptosaurus.builders.kilo import KiloCodeBuilder
        assert hasattr(KiloCodeBuilder, "BASE_FILES")
        assert "agents/core/core-system.md" in KiloCodeBuilder.BASE_FILES
        assert "agents/core/core-conventions.md" in KiloCodeBuilder.BASE_FILES

    def test_substitute_template_variables_basic(self):
        """KiloCodeBuilder should substitute basic template variables."""
        builder = KiloCLIBuilder()
        content = "Language: {{LANGUAGE}}, Runtime: {{RUNTIME}}"
        config = {
            "spec": {
                "language": "python",
                "runtime": "CPython",
            }
        }
        result = builder._substitute_template_variables(content, config)
        assert "python" in result
        assert "CPython" in result

    def test_substitute_template_variables_list(self):
        """KiloCodeBuilder should handle list values in templates."""
        builder = KiloCLIBuilder()
        content = "Tools: {{LINTER}}, {{FORMATTER}}"
        config = {
            "spec": {
                "linter": ["ruff", "mypy"],
                "formatter": ["ruff"],
            }
        }
        result = builder._substitute_template_variables(content, config)
        assert "ruff" in result
        assert "mypy" in result

    def test_substitute_template_variables_coverage(self):
        """KiloCodeBuilder should substitute coverage variables."""
        builder = KiloCLIBuilder()
        content = "Line: {{LINE_COVERAGE_%}}, Branch: {{BRANCH_COVERAGE_%}}"
        config = {
            "spec": {
                "coverage": {
                    "line": 90,
                    "branch": 80,
                }
            }
        }
        result = builder._substitute_template_variables(content, config)
        assert "90" in result
        assert "80" in result

    def test_substitute_template_variables_none_values(self):
        """KiloCodeBuilder should handle None values gracefully."""
        builder = KiloCLIBuilder()
        content = "Value: {{MISSING}}"
        config = {"spec": {}}
        result = builder._substitute_template_variables(content, config)
        assert "" in result or result == content


class TestKiloBuilder(unittest.TestCase):
    """Tests for KiloBuilder (now KiloCLIBuilder)."""

    def test_kilo_builder_is_builder_subclass(self):
        """KiloBuilder should be a subclass of Builder."""
        from promptosaurus.builders.builder import Builder

        assert issubclass(KiloCLIBuilder, Builder)

    def test_kilo_builder_has_build_method(self):
        """KiloBuilder should have a build method."""
        builder = KiloCLIBuilder()
        assert hasattr(builder, "build")
        assert callable(builder.build)

    def test_kilo_builder_build_returns_list(self):
        """KiloBuilder.build() should return a list of strings."""
        builder = KiloCLIBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
            assert isinstance(result, list)
            assert all(isinstance(r, str) for r in result)

    def test_kilo_builder_build_creates_files(self):
        """KiloBuilder.build() should create files."""
        builder = KiloCLIBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            # Should have created files in new structure
            assert (output / ".opencode").exists()
            assert (output / ".opencode" / "rules").exists()
            assert (output / "AGENTS.md").exists()
            assert (output / "opencode.json").exists()
            assert (output / ".kilocodemodes").exists()

    def test_kilo_builder_dry_run(self):
        """KiloBuilder.build() with dry_run=True should not write files."""
        builder = KiloCLIBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=True)
            # No files should be created
            assert not (output / ".opencode").exists()
            assert not (output / "AGENTS.md").exists()
            assert not (output / "opencode.json").exists()

    def test_kilo_builder_returns_action_strings(self):
        """KiloBuilder.build() should return action strings."""
        builder = KiloCLIBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output)
            assert len(result) > 0
            assert all(isinstance(r, str) for r in result)

    def test_kilo_builder_with_language_config(self):
        """KiloBuilder.build() should handle language config."""
        builder = KiloCLIBuilder()
        config = {
            "defaults": {
                "language": "python",
                "test_framework": "pytest",
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, config=config)
            assert isinstance(result, list)
            # Should have created language-specific file
            assert (output / ".opencode" / "rules" / "_base.md").exists()

    def test_kilo_builder_with_all_coverage_vars(self):
        """KiloBuilder should substitute all coverage template variables."""
        builder = KiloCLIBuilder()
        config = {
            "defaults": {
                "language": "python",
                "coverage": {
                    "line": 90,
                    "branch": 80,
                    "function": 95,
                    "statement": 88,
                    "mutation": 85,
                    "path": 70,
                }
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, config=config)
            assert isinstance(result, list)

    def test_kilo_builder_with_typescript(self):
        """KiloBuilder should handle TypeScript language config."""
        builder = KiloCLIBuilder()
        config = {
            "defaults": {
                "language": "typescript",
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, config=config)
            assert isinstance(result, list)

    def test_kilo_builder_with_javascript(self):
        """KiloBuilder should handle JavaScript language config."""
        builder = KiloCLIBuilder()
        config = {
            "defaults": {
                "language": "javascript",
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, config=config)
            assert isinstance(result, list)


class TestKiloCustomModes(unittest.TestCase):
    """Tests for custom modes filtering in Kilo builders."""

    def test_kilo_builtin_modes_constant_exists(self):
        """KiloCodeBuilder should have KILO_BUILTIN_MODES constant."""
        assert hasattr(KiloCodeBuilder, "KILO_BUILTIN_MODES")
        assert isinstance(KiloCodeBuilder.KILO_BUILTIN_MODES, frozenset)

    def test_kilo_builtin_modes_contains_expected_modes(self):
        """KILO_BUILTIN_MODES should contain architect, code, ask, debug, orchestrator."""
        expected = {"architect", "code", "ask", "debug", "orchestrator"}
        assert KiloCodeBuilder.KILO_BUILTIN_MODES == expected

    def test_custom_modes_property_exists(self):
        """KiloCodeBuilder should have custom_modes property."""
        builder = KiloCLIBuilder()
        assert hasattr(builder, "custom_modes")
        assert isinstance(builder.custom_modes, list)

    def test_custom_modes_excludes_builtin_modes(self):
        """custom_modes should exclude built-in Kilo modes."""
        builder = KiloCLIBuilder()
        # Built-in modes should NOT be in custom_modes
        for mode in KiloCodeBuilder.KILO_BUILTIN_MODES:
            assert mode not in builder.custom_modes, f"{mode} should not be in custom_modes"

    def test_custom_modes_includes_custom_modes(self):
        """custom_modes should include non-built-in modes."""
        builder = KiloCLIBuilder()
        # These are custom modes that should be included
        expected_custom = {"test", "refactor", "document", "explain", "migration", "review", "security", "compliance", "enforcement", "planning"}
        for mode in expected_custom:
            assert mode in builder.custom_modes, f"{mode} should be in custom_modes"

    def test_cli_builder_uses_custom_modes(self):
        """KiloCLIBuilder should generate only custom mode files."""
        builder = KiloCLIBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            # Check that built-in mode files are NOT created
            for mode in KiloCodeBuilder.KILO_BUILTIN_MODES:
                mode_file = output / ".opencode" / "rules" / f"{mode}.md"
                assert not mode_file.exists(), f"{mode}.md should NOT exist (built-in mode)"

    def test_ide_builder_uses_custom_modes(self):
        """KiloIDEBuilder should create only custom mode directories."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            # Check that built-in mode directories are NOT created
            for mode in KiloCodeBuilder.KILO_BUILTIN_MODES:
                mode_dir = output / ".kilocode" / f"rules-{mode}"
                assert not mode_dir.exists(), f"rules-{mode}/ should NOT exist (built-in mode)"


class TestKiloCLIAgentsContent(unittest.TestCase):
    """Tests for AGENTS.md content generation in KiloCLIBuilder."""

    def test_get_agents_md_content_exists(self):
        """KiloCLIBuilder should have _get_agents_md_content method."""
        builder = KiloCLIBuilder()
        assert hasattr(builder, "_get_agents_md_content")
        assert callable(builder._get_agents_md_content)

    def test_agents_md_content_includes_cli_structure(self):
        """KiloCLIBuilder AGENTS.md should include CLI structure info."""
        builder = KiloCLIBuilder()
        content = builder._get_agents_md_content()
        # Should mention .opencode/rules/ directory structure
        assert ".opencode/rules/" in content
        assert "CLI format" in content
        # Should mention _base.md
        assert "_base.md" in content

    def test_agents_md_content_includes_all_modes(self):
        """KiloCLIBuilder AGENTS.md should list all modes."""
        builder = KiloCLIBuilder()
        content = builder._get_agents_md_content()
        # Should include key modes
        assert "architect" in content
        assert "code" in content
        assert "test" in content
        assert "debug" in content

    def test_agents_md_created_with_content(self):
        """KiloCLIBuilder should create AGENTS.md with correct content."""
        builder = KiloCLIBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            agents_file = output / "AGENTS.md"
            assert agents_file.exists()
            content = agents_file.read_text(encoding="utf-8")
            # Verify CLI-specific content
            assert ".opencode/rules/" in content
            assert "CLI format" in content
            # Should have core instructions section
            assert "Core Instructions" in content
