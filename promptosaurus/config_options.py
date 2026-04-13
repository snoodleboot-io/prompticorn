"""Configuration options management for the promptosaurus update command.

This module provides data structures and functions for managing configuration
options that can be updated interactively via the `promptosaurus update` command.

The module defines:
    - ConfigOption dataclass: Represents a single updateable configuration option
    - CONFIG_OPTIONS: List of all available options
    - Helper functions for loading, getting, and setting nested config values

Configuration is loaded from YAML files in promptosaurus/configurations/
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from promptosaurus.questions.language import LanguageRegistry


class ConfigOptionsRegistry:
    """Registry for loading configuration options from YAML files.

    Loads configuration options once and caches them for reuse.
    Configuration is loaded from promptosaurus/configurations/config_options.yaml
    """

    _config: dict[str, list[str]] | None = None

    @classmethod
    def _load_config(cls) -> dict[str, list[str]]:
        """Load configuration options from YAML file.

        Returns:
            Dictionary with option lists for repo_type, package_manager, etc.
        """
        if cls._config is None:
            config_file = Path(__file__).parent / "configurations" / "config_options.yaml"
            with open(config_file, encoding="utf-8") as f:
                cls._config = yaml.safe_load(f)
        assert cls._config is not None
        return cls._config

    @classmethod
    def get_repo_type_options(cls) -> list[str]:
        """Get available repository type options.

        Returns:
            List of valid repository type strings.
        """
        config = cls._load_config()
        return config["repo_type_options"].copy()

    @classmethod
    def get_package_manager_options(cls) -> list[str]:
        """Get available package manager options.

        Returns:
            List of valid package manager strings.
        """
        config = cls._load_config()
        return config["package_manager_options"].copy()

    @classmethod
    def get_test_framework_options(cls) -> list[str]:
        """Get available test framework options.

        Returns:
            List of valid test framework strings.
        """
        config = cls._load_config()
        return config["test_framework_options"].copy()

    @classmethod
    def get_linter_options(cls) -> list[str]:
        """Get available linter options.

        Returns:
            List of valid linter strings.
        """
        config = cls._load_config()
        return config["linter_options"].copy()

    @classmethod
    def get_formatter_options(cls) -> list[str]:
        """Get available formatter options.

        Returns:
            List of valid formatter strings.
        """
        config = cls._load_config()
        return config["formatter_options"].copy()


@dataclass
class ConfigOption:
    """Represents a single configuration option that can be updated interactively.

    This dataclass defines a configuration option that users can modify via the
    `promptosaurus update` command. Each option has a key (used in the config file),
    a display name (shown to users), a type, and available choices if applicable.

    Attributes:
        key: The configuration key in dot notation (e.g., "spec.language").
        display_name: Human-readable name shown in the UI.
        option_type: Type of option - "single-select", "text", or "composite".
        current_value: The current value from the configuration file.
        available_options: List of valid choices for single-select options.
    """

    key: str
    display_name: str
    option_type: str  # "single-select", "text", "composite"
    current_value: Any = None
    available_options: list[str] | None = None


def _get_config_options() -> list[ConfigOption]:
    """Get the list of all updateable configuration options.

    Options are loaded dynamically from the ConfigOptionsRegistry.

    Returns:
        List of ConfigOption instances.
    """
    return [
        ConfigOption(
            key="repository.type",
            display_name="Repository Type",
            option_type="single-select",
            available_options=ConfigOptionsRegistry.get_repo_type_options(),
        ),
        ConfigOption(
            key="spec.language",
            display_name="Language",
            option_type="single-select",
            available_options=LanguageRegistry.get_supported_languages(),
        ),
        ConfigOption(
            key="spec.runtime",
            display_name="Runtime",
            option_type="text",
        ),
        ConfigOption(
            key="spec.package_manager",
            display_name="Package Manager",
            option_type="single-select",
            available_options=ConfigOptionsRegistry.get_package_manager_options(),
        ),
        ConfigOption(
            key="spec.test_framework",
            display_name="Test Framework",
            option_type="single-select",
            available_options=ConfigOptionsRegistry.get_test_framework_options(),
        ),
        ConfigOption(
            key="spec.linter",
            display_name="Linter",
            option_type="single-select",
            available_options=ConfigOptionsRegistry.get_linter_options(),
        ),
        ConfigOption(
            key="spec.formatter",
            display_name="Formatter",
            option_type="single-select",
            available_options=ConfigOptionsRegistry.get_formatter_options(),
        ),
        ConfigOption(
            key="spec.coverage",
            display_name="Coverage Targets",
            option_type="composite",
        ),
    ]


# Define all updateable options (excluding AI tool which is handled by switch)
# This is a function call now, not a module-level constant
CONFIG_OPTIONS = _get_config_options()


def load_current_values(
    config: dict[str, Any], options: list[ConfigOption] | None = None
) -> list[ConfigOption]:
    """Load current values from config into ConfigOption objects.

    This function populates the `current_value` attribute of each ConfigOption
    by looking up values in the nested configuration dictionary using dot notation.

    Args:
        config: The configuration dictionary loaded from YAML.
        options: Optional list of ConfigOption objects. Defaults to CONFIG_OPTIONS.

    Returns:
        List of ConfigOption objects with current values populated.
    """
    if options is None:
        options = _get_config_options()

    for opt in options:
        # Get value from nested config using dot notation
        value: Any = config
        for key in opt.key.split("."):
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = None
                break
        opt.current_value = value

    return options


def get_nested_value(config: dict[str, Any], key: str) -> Any:
    """Get a value from nested dict using dot notation.

    Args:
        config: The configuration dictionary
        key: Dot-separated key path (e.g., "spec.language")

    Returns:
        The value at the key path, or None if not found
    """
    value: Any = config
    for part in key.split("."):
        if isinstance(value, dict):
            value = value.get(part)
        else:
            return None
    return value


def set_nested_value(config: dict[str, Any], key: str, value: Any) -> None:
    """Set a value in nested dict using dot notation (mutates in place).

    Args:
        config: The configuration dictionary (mutated in place)
        key: Dot-separated key path (e.g., "spec.language")
        value: The value to set
    """
    parts = key.split(".")
    current = config

    # Navigate to the parent of the target key
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]

    # Set the final value
    current[parts[-1]] = value
