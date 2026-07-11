"""Configuration handling module for prompt initialization.

This module provides the ConfigHandler class for reading and writing YAML
configuration files, and helper functions for creating default configurations
with language-specific sensible defaults.

The configuration file (.prompticorn.yaml) stores project-specific settings
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
"""

from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from prompticorn.questions.base.spec_handler import (
    SpecHandler,
)

# Module-level YAML instance with proper indentation for lists


class ConfigHandler:
    """Handles reading and writing YAML configuration files.

    This class provides class methods for managing the .prompticorn.yaml
    configuration file used to store project settings.

    Attributes:
        DEFAULT_CONFIG_DIR: Default directory for config files.
        DEFAULT_CONFIG_FILE: Default filename for config.
    """

    DEFAULT_CONFIG_DIR = Path(".prompticorn")
    DEFAULT_CONFIG_FILE = ".prompticorn.yaml"

    _yaml_instance: YAML | None = None

    @classmethod
    def _get_yaml(cls) -> YAML:
        """Get configured YAML instance for reading and writing config files.

        Uses ruamel.yaml with proper indentation for lists. The instance
        is created once and cached for reuse.

        Returns:
            Configured YAML instance.
        """
        if cls._yaml_instance is None:
            cls._yaml_instance = YAML()
            cls._yaml_instance.indent(mapping=2, sequence=4, offset=2)
        return cls._yaml_instance

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
    def _migrate_from_promptosaurus(cls, config_dir: Path) -> None:
        """Rename .promptosaurus to .prompticorn if the old directory exists.

        TODO: Remove this method once all users have migrated.
        """
        legacy_dir = config_dir.parent / ".promptosaurus"
        if legacy_dir.exists() and not config_dir.exists():
            legacy_dir.rename(config_dir)

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
        cls._migrate_from_promptosaurus(config_dir)
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

        cls._migrate_from_promptosaurus(config_path.parent)

        if not config_path.exists():
            return {}

        with open(config_path, encoding="utf-8") as f:
            config = cls._get_yaml().load(f) or {}

        cls._migrate_old_orm_database_to_fungible(config)
        return config

    @classmethod
    def _migrate_old_orm_database_to_fungible(cls, config: dict[str, Any]) -> None:
        """Normalize legacy scalar project.orm/project.database to the new shape.

        Older configs stored a single ``project.database`` and ``project.orm``
        scalar (plus ``project.layout_style`` / ``project.error_handling``). The
        current model stores ``databases`` and ``data_access`` as per-folder
        multi-select lists on each spec, and ``layout_style`` / ``error_handling``
        per language/folder spec. This one-shot, idempotent migration rewrites old
        configs in place so renderers only ever see the new shape.

        Behavior:
            - Single-language (spec is a dict): seed ``databases`` / ``data_access``
              lists from the old scalars when absent, and carry over
              ``layout_style`` / ``error_handling`` onto the spec.
            - Multi-language-monorepo (spec is a list): seed ``databases`` /
              ``data_access`` on backend/custom folders from the old scalars when
              absent (frontend folders get empty lists); carry over
              ``layout_style`` / ``error_handling`` onto each spec.
            - Drop the migrated keys from ``project``.
            - No-op when the config already uses the new shape (no legacy scalars).

        Args:
            config: Configuration dictionary to migrate in place.
        """
        if not config:
            return

        project = config.get("project")
        if not isinstance(project, dict):
            return

        old_db = project.get("database")
        old_orm = project.get("orm")
        old_layout = project.get("layout_style")
        old_error = project.get("error_handling")

        has_legacy = any(
            key in project for key in ("database", "orm", "layout_style", "error_handling")
        )
        if not has_legacy:
            return

        db_list = [old_db] if old_db else []
        access_list = [old_orm] if old_orm else []

        def _seed_spec(spec: dict[str, Any], *, seed_data_system: bool) -> None:
            """Apply migrated values to a single spec dict in place."""
            if seed_data_system:
                spec.setdefault("databases", list(db_list))
                spec.setdefault("data_access", list(access_list))
            else:
                spec.setdefault("databases", [])
                spec.setdefault("data_access", [])
            if old_layout is not None:
                spec.setdefault("layout_style", old_layout)
            if old_error is not None:
                spec.setdefault("error_handling", old_error)

        spec = config.get("spec")
        if isinstance(spec, dict):
            # Single-language: the lone spec inherits the legacy data-system values.
            _seed_spec(spec, seed_data_system=True)
        elif isinstance(spec, list):
            for folder in spec:
                if not isinstance(folder, dict):
                    continue
                # Frontend folders never carry data-system selections.
                folder_type = folder.get("type", "")
                seed = folder_type != "frontend"
                _seed_spec(folder, seed_data_system=seed)

        # Drop the now-migrated legacy keys from the project section.
        for key in ("database", "orm", "layout_style", "error_handling"):
            project.pop(key, None)

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
            cls._get_yaml().dump(config, f)

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

    @classmethod
    def get_default_single_language_template(cls) -> dict[str, Any]:
        """Get default configuration template for single-language repositories.

        Returns:
            Dictionary with default single-language configuration structure.
        """
        return {
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
                "linters": [],  # List of linters for advanced templating
                "formatter": "",
                "abstract_class_style": "interface",
                "layout_style": "flat",
                "error_handling": "",
                "databases": [],
                "data_access": [],
                "coverage": {
                    "line": 80,
                    "branch": 70,
                    "function": 90,
                    "statement": 85,
                    "mutation": 80,
                    "path": 60,
                },
            },
            "project": cls.get_default_project_settings(),
        }

    @classmethod
    def get_default_project_settings(cls) -> dict[str, str]:
        """Get default project-level settings (language-agnostic).

        These populate the core conventions and are captured during `init`.

        Data-system settings (databases, data_access) and layout_style /
        error_handling are now per-folder/per-language spec values, not
        project-level; they are intentionally absent here.

        Returns:
            Dictionary of project-level settings with empty defaults.
        """
        return {
            "commit_style": "",
            "pr_size": "",
            "deploy_target": "",
        }

    @classmethod
    def get_default_multi_language_template(cls) -> dict[str, Any]:
        """Get default configuration template for multi-language monorepo.

        Returns:
            Dictionary with default multi-language-monorepo configuration structure.
        """
        return {
            "version": "1.0",
            "repository": {
                "type": "multi-language-monorepo",
                "mappings": {},
            },
            "spec": [],  # List of folder specs for multi-language-monorepo
            "project": cls.get_default_project_settings(),
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
    """
    repo_type = kwargs.get("repo_type", "single-language")

    # Use SpecHandler for creating the spec
    handler: SpecHandler = SpecHandler.for_repository_type(repo_type)

    if repo_type == "single-language":
        # For single-language, use the handler to create spec
        config: dict[str, Any] = ConfigHandler.get_default_single_language_template()
        config["repository"]["type"] = repo_type
        config["spec"] = handler.create_spec(language, **kwargs)
        return config
    else:
        # For multi-language-monorepo, create empty config with spec as list
        config = ConfigHandler.get_default_multi_language_template()
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
    """
    config: dict[str, Any] = ConfigHandler.get_default_multi_language_template()

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
