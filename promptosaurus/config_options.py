"""Configuration options management for the update command."""

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
    """Represents a single configuration option that can be updated."""

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

    Args:
        config: The configuration dictionary
        options: Optional list of ConfigOption objects. Defaults to CONFIG_OPTIONS.

    Returns:
        List of ConfigOption objects with current values populated
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
