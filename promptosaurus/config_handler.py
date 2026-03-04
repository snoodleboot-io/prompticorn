# Configuration handling for prompt init

from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]


class ConfigHandler:
    """Handles reading and writing YAML configuration files."""

    DEFAULT_CONFIG_DIR = Path(".promptosaurus")
    DEFAULT_CONFIG_FILE = "configurations.yaml"

    @classmethod
    def get_config_path(cls, config_dir: Path | None = None) -> Path:
        """Get the path to the configuration file."""
        if config_dir is None:
            config_dir = cls.DEFAULT_CONFIG_DIR
        return config_dir / cls.DEFAULT_CONFIG_FILE

    @classmethod
    def ensure_config_dir(cls, config_dir: Path | None = None) -> Path:
        """Ensure the configuration directory exists."""
        if config_dir is None:
            config_dir = cls.DEFAULT_CONFIG_DIR
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @classmethod
    def load_config(cls, config_path: Path | None = None) -> dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path is None:
            config_path = cls.get_config_path()

        if not config_path.exists():
            return {}

        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    @classmethod
    def save_config(cls, config: dict[str, Any], config_path: Path | None = None) -> None:
        """Save configuration to YAML file."""
        if config_path is None:
            config_path = cls.get_config_path()

        cls.ensure_config_dir(config_path.parent)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)

    @classmethod
    def config_exists(cls, config_path: Path | None = None) -> bool:
        """Check if configuration file exists."""
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
    "defaults": {
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
    """Create a default configuration with sensible defaults for the language."""
    config: dict[str, Any] = DEFAULT_CONFIG_TEMPLATE.copy()
    config["repository"]["type"] = kwargs.get("repo_type", "single-language")
    config["defaults"]["language"] = language

    # Set language-specific defaults
    if language.lower() == "python":
        config["defaults"]["runtime"] = "3.12"
        config["defaults"]["package_manager"] = "poetry"
        config["defaults"]["test_framework"] = "pytest"
        config["defaults"]["linter"] = "ruff"
        config["defaults"]["formatter"] = "ruff"
    elif language.lower() in ("typescript", "javascript"):
        config["defaults"]["runtime"] = "5.4"
        config["defaults"]["package_manager"] = "npm"
        config["defaults"]["test_framework"] = "vitest"
        config["defaults"]["linter"] = "eslint"
        config["defaults"]["formatter"] = "prettier"

    # Override with any provided kwargs
    for key, value in kwargs.items():
        if value:
            config["defaults"][key] = value

    return config
