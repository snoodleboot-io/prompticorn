"""Configuration handling module for prompt initialization.

This module provides the ConfigHandler class for reading and writing YAML
configuration files, and helper functions for creating default configurations
with language-specific sensible defaults.

The configuration file (.promptosaurus.yaml) stores project-specific settings
including:
    - Repository type (single-language, multi-language-monorepo, mixed)
    - Language and runtime version
    - Package manager
    - Testing framework
    - Linter and formatter
    - Coverage targets
    - For multi-language-monorepo: list of folder specs

Classes:
    ConfigHandler: Handles reading and writing YAML configuration files.

Functions:
    create_default_config: Create default config with language-specific defaults.
    create_multi_language_config: Create config for multi-language monorepo.
    detect_repository_type: Detect repository type from config.

Example:
    >>> from promptosaurus.config_handler import ConfigHandler, create_default_config
    >>> config = create_default_config('python', repo_type='single-language')
    >>> ConfigHandler.save_config(config)
    >>> loaded = ConfigHandler.load_config()
"""

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from promptosaurus.questions.base.spec_handler import (
    SpecHandler,
)

# Module-level YAML instance with proper indentation for lists
# indent(mapping=2, sequence=4, offset=2) gives us:
# folders:
#   - folder: backend/api
#     language: python
_ruamel_yaml = YAML()
_ruamel_yaml.indent(mapping=2, sequence=4, offset=2)


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
        # Also create sessions directory for session management
        (config_dir / "sessions").mkdir(parents=True, exist_ok=True)
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
            return _ruamel_yaml.load(f) or {}

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
            # Use ruamel.yaml with proper list indentation
            _ruamel_yaml.dump(config, f)

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


# Template for default configuration (single-language)
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

# Template for multi-language-monorepo configuration
DEFAULT_MULTI_LANGUAGE_CONFIG_TEMPLATE = {
    "version": "1.0",
    "repository": {
        "type": "multi-language-monorepo",
        "mappings": {},
    },
    "spec": [],  # List of folder specs for multi-language-monorepo
}


def create_default_config(language: str, **kwargs) -> dict[str, Any]:
    """Create a default configuration with sensible defaults for the language.

    This function uses SpecHandler for cleaner language-specific defaults.

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
    repo_type = kwargs.get("repo_type", "single-language")

    # Use SpecHandler for creating the spec
    handler: SpecHandler = SpecHandler.for_repository_type(repo_type)

    if repo_type == "single-language":
        # For single-language, use the handler to create spec
        config: dict[str, Any] = DEFAULT_CONFIG_TEMPLATE.copy()
        config["repository"]["type"] = repo_type
        config["spec"] = handler.create_spec(language, **kwargs)
        return config
    else:
        # For multi-language-monorepo, create empty config with spec as list
        config = DEFAULT_MULTI_LANGUAGE_CONFIG_TEMPLATE.copy()
        config["repository"]["type"] = repo_type
        config["spec"] = handler.create_spec()
        return config


def create_multi_language_config(
    folder_specs: list[dict[str, Any]],
    **kwargs,
) -> dict[str, Any]:
    """Create a configuration for a multi-language monorepo.

    Args:
        folder_specs: List of folder specifications.
        **kwargs: Optional overrides for config values.

    Returns:
        Configuration dictionary with folder specs.

    Example:
        >>> specs = [
        ...     {"folder": "backend/api", "type": "backend", "subtype": "api", "language": "python"},
        ...     {"folder": "frontend", "type": "frontend", "subtype": "ui", "language": "typescript"}
        ... ]
        >>> config = create_multi_language_config(specs)
        >>> config['repository']['type']
        'multi-language-monorepo'
        >>> len(config['spec'])
        2
    """
    config: dict[str, Any] = DEFAULT_MULTI_LANGUAGE_CONFIG_TEMPLATE.copy()

    # Apply any kwargs to the config
    for key, value in kwargs.items():
        if value:
            if key in config["repository"]:
                config["repository"][key] = value
            else:
                config[key] = value

    config["spec"] = folder_specs
    return config


def detect_repository_type(config: dict[str, Any]) -> str:
    """Detect repository type from configuration.

    This function examines the config structure to determine if it's a
    single-language or multi-language-monorepo configuration.

    Args:
        config: The configuration dictionary.

    Returns:
        Repository type: 'single-language', 'multi-language-monorepo', or 'unknown'.

    Example:
        >>> config = {'repository': {'type': 'single-language'}, 'spec': {}}
        >>> detect_repository_type(config)
        'single-language'
        >>> config2 = {'repository': {'type': 'multi-language-monorepo'}, 'spec': []}
        >>> detect_repository_type(config2)
        'multi-language-monorepo'
    """
    if not config:
        return "unknown"

    repo_info = config.get("repository", {})
    repo_type = repo_info.get("type", "")

    # If explicitly set, use that value
    if repo_type in ("single-language", "multi-language-monorepo", "mixed"):
        return repo_type

    # Otherwise, detect from spec structure
    spec = config.get("spec")

    if spec is None:
        return "unknown"

    if isinstance(spec, list):
        return "multi-language-monorepo"
    elif isinstance(spec, dict):
        return "single-language"

    return "unknown"
