"""Tests for config module."""

import pytest
import tempfile
from pathlib import Path

from promptcli.config import (
    ConfigHandler,
    DEFAULT_CONFIG_TEMPLATE,
    create_default_config,
)


class TestConfigHandler:
    """Tests for ConfigHandler class."""

    def test_get_default_config_path(self):
        """Should return default config path."""
        path = ConfigHandler.get_config_path()

        assert path == Path(".prompty") / "configurations.yaml"

    def test_get_custom_config_path_uses_default_filename(self):
        """Should return custom config path with default filename when directory provided."""
        custom = Path(".custom")
        path = ConfigHandler.get_config_path(custom)

        # When a directory is provided, it should append the default filename
        assert path == custom / "configurations.yaml"

    def test_ensure_config_dir_creates_directory(self):
        """Should create config directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".prompty"
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
            test_config = {"version": "1.0", "defaults": {"language": "python"}}

            ConfigHandler.save_config(test_config, config_path)

            loaded = ConfigHandler.load_config(config_path)
            assert loaded == test_config

    def test_load_nonexistent_returns_empty_dict(self):
        """Should return empty dict for non-existent config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"

            loaded = ConfigHandler.load_config(config_path)

            assert loaded == {}


class TestDefaultConfigTemplate:
    """Tests for DEFAULT_CONFIG_TEMPLATE."""

    def test_template_has_version(self):
        """Template should have version key."""
        assert "version" in DEFAULT_CONFIG_TEMPLATE

    def test_template_has_repository(self):
        """Template should have repository key."""
        assert "repository" in DEFAULT_CONFIG_TEMPLATE

    def test_template_has_defaults(self):
        """Template should have defaults key."""
        assert "defaults" in DEFAULT_CONFIG_TEMPLATE

    def test_template_has_coverage(self):
        """Template should have coverage in defaults."""
        assert "coverage" in DEFAULT_CONFIG_TEMPLATE["defaults"]


class TestCreateDefaultConfig:
    """Tests for create_default_config function."""

    def test_creates_python_config(self):
        """Should create config with Python defaults."""
        config = create_default_config("python")

        assert config["defaults"]["language"] == "python"
        assert config["defaults"]["runtime"] == "3.12"
        assert config["defaults"]["package_manager"] == "poetry"
        assert config["defaults"]["test_framework"] == "pytest"
        assert config["defaults"]["linter"] == "ruff"
        assert config["defaults"]["formatter"] == "ruff"

    def test_creates_typescript_config(self):
        """Should create config with TypeScript defaults."""
        config = create_default_config("typescript")

        assert config["defaults"]["language"] == "typescript"
        assert config["defaults"]["runtime"] == "5.4"
        assert config["defaults"]["package_manager"] == "npm"
        assert config["defaults"]["test_framework"] == "vitest"

    def test_creates_javascript_config(self):
        """Should create config with JavaScript defaults."""
        config = create_default_config("javascript")

        assert config["defaults"]["language"] == "javascript"
        assert config["defaults"]["package_manager"] == "npm"

    def test_sets_repo_type(self):
        """Should set repository type."""
        config = create_default_config("python", repo_type="multi-language-folder")

        assert config["repository"]["type"] == "multi-language-folder"

    def test_overrides_with_kwargs(self):
        """Should override defaults with provided kwargs."""
        config = create_default_config(
            "python",
            runtime="3.11",
            package_manager="pip",
        )

        assert config["defaults"]["runtime"] == "3.11"
        assert config["defaults"]["package_manager"] == "pip"

    def test_ignores_empty_kwargs(self):
        """Should ignore empty kwargs."""
        config = create_default_config("python", runtime="", package_manager=None)

        # Should still have defaults
        assert config["defaults"]["runtime"] == "3.12"
        assert config["defaults"]["package_manager"] == "poetry"

    def test_unknown_language_keeps_defaults(self):
        """Unknown language should still have defaults from first match."""
        config = create_default_config("unknown_lang")

        # Should not crash, but may have empty values
        assert config["defaults"]["language"] == "unknown_lang"
