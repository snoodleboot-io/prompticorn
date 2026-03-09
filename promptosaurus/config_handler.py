"""Configuration handling module for prompt initialization.

This module provides the ConfigHandler class for reading and writing YAML
configuration files, and helper functions for creating default configurations
with language-specific sensible defaults.

The configuration file (.promptosaurus.yaml) stores project-specific settings
including:
    - Repository type (single-language, multi-language-folder, mixed)
    - Language and runtime version
    - Package manager
    - Testing framework
    - Linter and formatter
    - Coverage targets

Classes:
    ConfigHandler: Handles reading and writing YAML configuration files.

Functions:
    create_default_config: Create default config with language-specific defaults.

Example:
    >>> from promptosaurus.config_handler import ConfigHandler, create_default_config
    >>> config = create_default_config('python', repo_type='single-language')
    >>> ConfigHandler.save_config(config)
    >>> loaded = ConfigHandler.load_config()
"""

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


class ConfigHandler:
    """Handles reading and writing YAML configuration files.

    This class provides class methods for managing the .promptosaurus.yaml
    configuration file used to store project settings.

    Attributes:
        DEFAULT_CONFIG_DIR: Default directory for config files.
        DEFAULT_CONFIG_FILE: Default filename for config.
    """

    DEFAULT_CONFIG_DIR = Path(".promptosaurus")
    DEFAULT_CONFIG_FILE = ".promptosaurus.yaml"

    @classmethod
    def get_config_path(cls, config_dir: Path | None = None) -> Path:
        """Get the path to the configuration file.

        Args:
            config_dir: Optional custom config directory. Defaults to DEFAULT_CONFIG_DIR.

        Returns:
            Path to the configuration file.
        """
        if config_dir is None:
            config_dir = cls.DEFAULT_CONFIG_DIR
        return config_dir / cls.DEFAULT_CONFIG_FILE

    @classmethod
    def ensure_config_dir(cls, config_dir: Path | None = None) -> Path:
        """Ensure the configuration directory exists.

        Args:
            config_dir: Optional custom config directory. Defaults to DEFAULT_CONFIG_DIR.

        Returns:
            Path to the config directory.

        Raises:
            OSError: If directory creation fails.
        """
        if config_dir is None:
            config_dir = cls.DEFAULT_CONFIG_DIR
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @classmethod
    def load_config(cls, config_path: Path | None = None) -> dict[str, Any]:
        """Load configuration from YAML file.

        Args:
            config_path: Optional custom path to config file. Defaults to standard location.

        Returns:
            Configuration dictionary, empty dict if file doesn't exist.

        Raises:
            yaml.YAMLError: If YAML parsing fails.
        """
        if config_path is None:
            config_path = cls.get_config_path()

        if not config_path.exists():
            return {}

        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @classmethod
    def save_config(cls, config: dict[str, Any], config_path: Path | None = None) -> None:
        """Save configuration to YAML file.

        Args:
            config: Configuration dictionary to save.
            config_path: Optional custom path to save to. Defaults to standard location.

        Raises:
            OSError: If file write fails.
            yaml.YAMLError: If YAML dumping fails.
        """
        if config_path is None:
            config_path = cls.get_config_path()

        cls.ensure_config_dir(config_path.parent)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def config_exists(cls, config_path: Path | None = None) -> bool:
        """Check if configuration file exists.

        Args:
            config_path: Optional custom path to check. Defaults to standard location.

        Returns:
            True if config file exists, False otherwise.
        """
        if config_path is None:
            config_path = cls.get_config_path()
        return config_path.exists()


# Template for default configuration
DEFAULT_CONFIG_TEMPLATE = {
    "version": "1.0",
    "repository": {
        "type": "single-language",
        "mappings": {},
    },
    "spec": {
        "language": "",
        "runtime": "",
        "package_manager": "",
        "test_framework": "",
        "linter": "",
        "formatter": "",
        "coverage": {
            "line": 80,
            "branch": 70,
            "function": 90,
            "statement": 85,
            "mutation": 80,
            "path": 60,
        },
    },
}


def create_default_config(language: str, **kwargs) -> dict[str, Any]:
    """Create a default configuration with sensible defaults for the language.

    Args:
        language: Programming language (e.g., 'python', 'typescript').
        **kwargs: Optional overrides for config values. Supports:
            - repo_type: Repository type override
            - runtime: Runtime version override
            - package_manager: Package manager override
            - test_framework: Test framework override
            - linter: Linter override
            - formatter: Formatter override

    Returns:
        Configuration dictionary with defaults applied.

    Example:
        >>> config = create_default_config('python', package_manager='pip')
        >>> config['spec']['package_manager']
        'pip'
    """
    config: dict[str, Any] = DEFAULT_CONFIG_TEMPLATE.copy()
    config["repository"]["type"] = kwargs.get("repo_type", "single-language")
    config["spec"]["language"] = language

    # Set language-specific defaults
    if language.lower() == "python":
        config["spec"]["runtime"] = "3.12"
        config["spec"]["package_manager"] = "poetry"
        config["spec"]["test_framework"] = "pytest"
        config["spec"]["linter"] = "ruff"
        config["spec"]["formatter"] = "ruff"
    elif language.lower() in ("typescript", "javascript"):
        config["spec"]["runtime"] = "5.4"
        config["spec"]["package_manager"] = "npm"
        config["spec"]["test_framework"] = "vitest"
        config["spec"]["linter"] = "eslint"
        config["spec"]["formatter"] = "prettier"

    # Override with any provided kwargs (except repo_type - it's already in repository.type)
    for key, value in kwargs.items():
        if value and key != "repo_type":
            config["spec"][key] = value

    return config
