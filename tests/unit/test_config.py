"""Tests for config module."""

import tempfile
from pathlib import Path

from prompticorn.config_handler import (
    ConfigHandler,
    create_default_config,
)


class TestConfigHandler:
    """Tests for ConfigHandler class."""

    def test_get_default_config_path(self):
        """Should return default config path."""
        path = ConfigHandler.get_config_path()

        assert path == Path(".prompticorn") / ".prompticorn.yaml"

    def test_get_custom_config_path_uses_default_filename(self):
        """Should return custom config path with default filename when directory provided."""
        custom = Path(".custom")
        path = ConfigHandler.get_config_path(custom)

        # When a directory is provided, it should append the default filename
        assert path == custom / ".prompticorn.yaml"

    def test_ensure_config_dir_creates_directory(self):
        """Should create config directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".prompticorn"
            assert not config_dir.exists()

            ConfigHandler.ensure_config_dir(config_dir)

            assert config_dir.exists()
            assert config_dir.is_dir()

    def test_config_exists_returns_false_for_nonexistent(self):
        """Should return False for non-existent config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            assert not ConfigHandler.config_exists(config_path)

    def test_config_exists_returns_true_for_existing(self):
        """Should return True for existing config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("version: 1.0")

            assert ConfigHandler.config_exists(config_path)

    def test_save_and_load_config(self):
        """Should save and load config correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            test_config = {"version": "1.0", "spec": {"language": "python"}}

            ConfigHandler.save_config(test_config, config_path)

            loaded = ConfigHandler.load_config(config_path)
            assert loaded == test_config

    def test_save_config_yaml_formatting(self):
        """YAML should use proper 2-space indentation for lists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            # Config with list (like multi-language monorepo spec)
            test_config = {
                "version": "1.0",
                "spec": [
                    {
                        "folder": "backend/api",
                        "type": "backend",
                        "language": "python",
                        "python_linter": ["ruff"],
                    }
                ],
            }

            ConfigHandler.save_config(test_config, config_path)

            # Read the raw YAML text
            yaml_text = config_path.read_text()

            # Check proper indentation:
            # - "spec:" should be at indent 0
            # - "- folder:" should be at indent 2 (dash at indent 2)
            # - "type:" should be at indent 4
            lines = yaml_text.split("\n")
            for line in lines:
                if line.startswith("spec:"):
                    # spec: should have no leading spaces
                    assert not line.startswith(" "), (
                        f"spec: should have no leading spaces: {line!r}"
                    )
                elif line.startswith("- folder:"):
                    # List item should start with exactly 2 spaces then dash
                    assert line.startswith("  -"), f"List item should have 2-space indent: {line!r}"
                elif line.startswith("  type:") or line.startswith("  language:"):
                    # Properties should have 2-space indent
                    assert line.startswith("  "), f"Property should have 2-space indent: {line!r}"
                elif line.startswith("    - ruff"):
                    # Nested list item should have 4-space indent
                    assert line.startswith("    -"), (
                        f"Nested list should have 4-space indent: {line!r}"
                    )

    def test_load_nonexistent_returns_empty_dict(self):
        """Should return empty dict for non-existent config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"

            loaded = ConfigHandler.load_config(config_path)

            assert loaded == {}


class TestDefaultConfigTemplate:
    """Tests for ConfigHandler default template methods."""

    def test_template_has_version(self):
        """Template should have version key."""
        assert "version" in ConfigHandler.get_default_single_language_template()

    def test_template_has_repository(self):
        """Template should have repository key."""
        assert "repository" in ConfigHandler.get_default_single_language_template()

    def test_template_has_defaults(self):
        """Template should have defaults key."""
        assert "spec" in ConfigHandler.get_default_single_language_template()

    def test_template_has_coverage(self):
        """Template should have coverage in defaults."""
        assert "coverage" in ConfigHandler.get_default_single_language_template()["spec"]


class TestCreateDefaultConfig:
    """Tests for create_default_config function."""

    def test_creates_python_config(self):
        """Should create config with Python defaults."""
        config = create_default_config("python")

        assert config["spec"]["language"] == "python"
        assert config["spec"]["runtime"] == "3.14"
        assert config["spec"]["package_manager"] == "uv"
        assert config["spec"]["test_framework"] == "pytest"
        assert config["spec"]["linter"] == "ruff"
        assert config["spec"]["formatter"] == "ruff"

    def test_creates_typescript_config(self):
        """Should create config with TypeScript defaults."""
        config = create_default_config("typescript")

        assert config["spec"]["language"] == "typescript"
        assert config["spec"]["runtime"] == "v6.0"
        assert config["spec"]["package_manager"] == "pnpm"
        assert config["spec"]["test_framework"] == "vitest"

    def test_creates_javascript_config(self):
        """Should create config with JavaScript defaults."""
        config = create_default_config("javascript")

        assert config["spec"]["language"] == "javascript"
        assert config["spec"]["package_manager"] == "pnpm"

    def test_sets_repo_type(self):
        """Should set repository type."""
        config = create_default_config("python", repo_type="multi-language-monorepo")

        assert config["repository"]["type"] == "multi-language-monorepo"

    def test_overrides_with_kwargs(self):
        """Should override defaults with provided kwargs."""
        config = create_default_config(
            "python",
            runtime="3.11",
            package_manager="pip",
        )

        assert config["spec"]["runtime"] == "3.11"
        assert config["spec"]["package_manager"] == "pip"

    def test_ignores_empty_kwargs(self):
        """Should ignore empty kwargs."""
        config = create_default_config("python", runtime="", package_manager=None)

        # Should still have defaults
        assert config["spec"]["runtime"] == "3.14"
        assert config["spec"]["package_manager"] == "uv"

    def test_unknown_language_keeps_defaults(self):
        """Unknown language should still have defaults from first match."""
        config = create_default_config("unknown_lang")

        # Should not crash, but may have empty values
        assert config["spec"]["language"] == "unknown_lang"
