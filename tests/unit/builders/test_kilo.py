"""Unit tests for promptosaurus.builders.kilo."""

import tempfile
import unittest
from pathlib import Path

from promptosaurus.builders.kilo.kilo_cli import KiloCLIBuilder
from promptosaurus.builders.kilo.kilo_code_builder import KiloCodeBuilder
from promptosaurus.builders.kilo.kilo_ide import KiloIDEBuilder

PYTHON_CONFIG = {
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

TYPESCRIPT_CONFIG = {
    "spec": {
        "language": "typescript",
        "runtime": "Node 20",
        "package_manager": "pnpm",
        "linter": ["eslint"],
        "formatter": ["prettier"],
        "testing_framework": "vitest",
        "mocking_library": "vitest/mock",
        "coverage_tool": "v8",
        "e2e_tool": "playwright",
        "mutation_tool": "stryker-mutator",
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

JAVASCRIPT_CONFIG = {
    "spec": {
        "language": "javascript",
        "runtime": "Node 20",
        "package_manager": "npm",
        "linter": ["eslint"],
        "formatter": ["prettier"],
        "testing_framework": "jest",
        "mocking_library": "jest.mock",
        "coverage_tool": "istanbul",
        "e2e_tool": "playwright",
        "mutation_tool": "stryker-mutator",
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


class TestKiloCodeBuilderBase(unittest.TestCase):
    """Tests for KiloCodeBuilder base class methods using concrete implementation."""

    def test_language_file_map(self):
        """KiloCodeBuilder should have language_file_map property loaded from YAML."""

        # Test via instance to ensure YAML is loaded
        builder = KiloCLIBuilder()
        assert hasattr(KiloCodeBuilder, "language_file_map")
        assert "python" in builder.language_file_map
        assert builder.language_file_map["python"] == "agents/core/core-conventions-python.md"
        assert (
            builder.language_file_map["typescript"] == "agents/core/core-conventions-typescript.md"
        )

    def test_substitute_template_variables_basic(self):
        """KiloCodeBuilder should substitute basic template variables."""
        builder = KiloCLIBuilder()
        content = "Language: {{config.language}}, Runtime: {{config.runtime}}"
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
        content = "Tools: {{config.linter}}, {{config.formatter}}"
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
        content = "Line: {{config.coverage.line}}, Branch: {{config.coverage.branch}}"
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
        content = "Value: {{config.missing | default('')}}"
        config = {"spec": {}}
        result = builder._substitute_template_variables(content, config)
        assert "Value: " in result


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
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, config=PYTHON_CONFIG)
            assert isinstance(result, list)
            # Should have created language-specific file
            assert (output / ".opencode" / "rules" / "_base.md").exists()

    def test_kilo_builder_with_all_coverage_vars(self):
        """KiloBuilder should substitute all coverage template variables."""
        builder = KiloCLIBuilder()
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
                    "line": 90,
                    "branch": 80,
                    "function": 95,
                    "statement": 88,
                    "mutation": 85,
                    "path": 70,
                },
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, config=config)
            assert isinstance(result, list)

    def test_kilo_builder_with_typescript(self):
        """KiloBuilder should handle TypeScript language config."""
        builder = KiloCLIBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, config=TYPESCRIPT_CONFIG)
            assert isinstance(result, list)

    def test_kilo_builder_with_javascript(self):
        """KiloBuilder should handle JavaScript language config."""
        builder = KiloCLIBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            result = builder.build(output, config=JAVASCRIPT_CONFIG)
            assert isinstance(result, list)


class TestKiloCustomModes(unittest.TestCase):
    """Tests for custom modes filtering in Kilo builders."""

    def test_custom_modes_property_exists(self):
        """KiloCodeBuilder should have custom_modes property."""
        builder = KiloCLIBuilder()
        assert hasattr(builder, "custom_modes")
        assert isinstance(builder.custom_modes, list)

    def test_custom_modes_excludes_builtin_modes(self):
        """custom_modes should exclude built-in Kilo modes."""
        builder = KiloCLIBuilder()
        # Built-in modes should NOT be in custom_modes
        for mode in builder._kilo_builtin_modes:
            assert mode not in builder.custom_modes, f"{mode} should not be in custom_modes"

    def test_custom_modes_includes_custom_modes(self):
        """custom_modes should include non-built-in modes."""
        builder = KiloCLIBuilder()
        # These are custom modes that should be included
        expected_custom = {
            "test",
            "refactor",
            "document",
            "explain",
            "migration",
            "review",
            "security",
            "compliance",
            "enforcement",
            "planning",
        }
        for mode in expected_custom:
            assert mode in builder.custom_modes, f"{mode} should be in custom_modes"

    def test_cli_builder_uses_custom_modes(self):
        """KiloCLIBuilder should generate only custom mode files."""
        builder = KiloCLIBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            # Check that built-in mode files are NOT created
            for mode in builder._kilo_builtin_modes:
                mode_file = output / ".opencode" / "rules" / f"{mode}.md"
                assert not mode_file.exists(), f"{mode}.md should NOT exist (built-in mode)"

    def test_ide_builder_uses_custom_modes(self):
        """KiloIDEBuilder should create mode directories for ALL 15 modes (not just custom modes)."""
        builder = KiloIDEBuilder()
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir)
            builder.build(output, dry_run=False)
            # IDE should create directories for ALL 15 modes
            for mode in builder.kilo_modes.keys():
                mode_dir = output / ".kilocode" / f"rules-{mode}"
                assert mode_dir.exists(), f"rules-{mode}/ should exist for IDE"


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
