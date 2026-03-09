"""Configuration options management for the prompt update command.

This module provides data structures and functions for managing configuration
options that can be updated interactively via the `prompt update` command.

The module defines:
    - ConfigOption dataclass: Represents a single updateable configuration option
    - CONFIG_OPTIONS: List of all available options
    - Helper functions for loading, getting, and setting nested config values

Constants:
    REPO_TYPE_OPTIONS: Available repository type options
    PACKAGE_MANAGER_OPTIONS: Available package manager options
    TEST_FRAMEWORK_OPTIONS: Available test framework options
    LINTER_OPTIONS: Available linter options
    FORMATTER_OPTIONS: Available formatter options

Classes:
    ConfigOption: Dataclass representing a single configuration option

Functions:
    load_current_values: Load current config values into ConfigOption objects
    get_nested_value: Get value from nested dict using dot notation
    set_nested_value: Set value in nested dict using dot notation

Example:
    >>> from promptosaurus.config_options import CONFIG_OPTIONS, load_current_values
    >>> config = {"spec": {"language": "python"}}
    >>> options = load_current_values(config)
    >>> options[0].current_value
    'python'
"""

from dataclasses import dataclass
from typing import Any

from promptosaurus.questions.language import LANGUAGE_KEYS

# Available options for single-select config fields
REPO_TYPE_OPTIONS = ["single-language", "multi-language-folder", "mixed-collocation"]

PACKAGE_MANAGER_OPTIONS = [
    "poetry",
    "npm",
    "pip",
    "yarn",
    "pnpm",
    "bun",
    "cargo",
    "gradle",
    "maven",
    "dotnet",
]

TEST_FRAMEWORK_OPTIONS = [
    "pytest",
    "vitest",
    "jest",
    "go test",
    "junit",
    "rspec",
    "phpunit",
    "swift testing",
    "kotest",
    "xctest",
]

LINTER_OPTIONS = [
    "ruff",
    "eslint",
    "pylint",
    "golangci-lint",
    "checkstyle",
    "rubocop",
    "phpcs",
    "swiftlint",
    "detekt",
]

FORMATTER_OPTIONS = [
    "ruff",
    "prettier",
    "black",
    "gofmt",
    "dotnet format",
    "rubocop",
    "php-cs-fixer",
]


@dataclass
class ConfigOption:
    """Represents a single configuration option that can be updated interactively.

    This dataclass defines a configuration option that users can modify via the
    `prompt update` command. Each option has a key (used in the config file),
    a display name (shown to users), a type, and available choices if applicable.

    Attributes:
        key: The configuration key in dot notation (e.g., "spec.language").
        display_name: Human-readable name shown in the UI.
        option_type: Type of option - "single-select", "text", or "composite".
        current_value: The current value from the configuration file.
        available_options: List of valid choices for single-select options.

    Example:
        >>> opt = ConfigOption(
        ...     key="spec.language",
        ...     display_name="Language",
        ...     option_type="single-select",
        ...     available_options=["python", "typescript"]
        ... )
        >>> opt.key
        'spec.language'
    """

    key: str
    display_name: str
    option_type: str  # "single-select", "text", "composite"
    current_value: Any = None
    available_options: list[str] | None = None


# Define all updateable options (excluding AI tool which is handled by switch)
CONFIG_OPTIONS: list[ConfigOption] = [
    ConfigOption(
        key="repository.type",
        display_name="Repository Type",
        option_type="single-select",
        available_options=REPO_TYPE_OPTIONS,
    ),
    ConfigOption(
        key="spec.language",
        display_name="Language",
        option_type="single-select",
        available_options=LANGUAGE_KEYS,
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
        available_options=PACKAGE_MANAGER_OPTIONS,
    ),
    ConfigOption(
        key="spec.test_framework",
        display_name="Test Framework",
        option_type="single-select",
        available_options=TEST_FRAMEWORK_OPTIONS,
    ),
    ConfigOption(
        key="spec.linter",
        display_name="Linter",
        option_type="single-select",
        available_options=LINTER_OPTIONS,
    ),
    ConfigOption(
        key="spec.formatter",
        display_name="Formatter",
        option_type="single-select",
        available_options=FORMATTER_OPTIONS,
    ),
    ConfigOption(
        key="spec.coverage",
        display_name="Coverage Targets",
        option_type="composite",
    ),
]


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

    Example:
        >>> config = {"spec": {"language": "python"}}
        >>> options = load_current_values(config)
        >>> options[0].current_value
        'python'
    """
    if options is None:
        options = CONFIG_OPTIONS.copy()

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
