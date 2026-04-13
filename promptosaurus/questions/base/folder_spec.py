"""Folder specification for multi-language monorepo configuration."""

from dataclasses import dataclass, field
from typing import Any

# Language-specific defaults
LANGUAGE_DEFAULTS: dict[str, dict[str, str]] = {
    "python": {
        "runtime": "3.14",
        "package_manager": "uv",
        "test_framework": "pytest",
        "linter": "ruff",
        "formatter": "ruff",
    },
    "typescript": {
        "runtime": "6.0",
        "package_manager": "pnpm",
        "test_framework": "vitest",
        "linter": "eslint",
        "formatter": "prettier",
    },
    "javascript": {
        "runtime": "6.0",
        "package_manager": "pnpm",
        "test_framework": "vitest",
        "linter": "eslint",
        "formatter": "prettier",
    },
    "go": {
        "runtime": "1.21",
        "package_manager": "go mod",
        "test_framework": "go test",
        "linter": "golangci-lint",
        "formatter": "gofmt",
    },
    "java": {
        "runtime": "21",
        "package_manager": "maven",
        "test_framework": "junit",
        "linter": "checkstyle",
        "formatter": "google-java-format",
    },
    "rust": {
        "runtime": "1.75",
        "package_manager": "cargo",
        "test_framework": "cargo test",
        "linter": "clippy",
        "formatter": "rustfmt",
    },
    "csharp": {
        "runtime": "8.0",
        "package_manager": "nuget",
        "test_framework": "xunit",
        "linter": "roslynator",
        "formatter": "dotnet format",
    },
}


# Default coverage targets
DEFAULT_COVERAGE = {
    "line": 80,
    "branch": 70,
    "function": 90,
    "statement": 85,
    "mutation": 80,
    "path": 60,
}


@dataclass
class FolderSpec:
    """Represents configuration for a single folder in a multi-language monorepo.

    Attributes:
        folder: The folder path (e.g., "frontend", "backend", "services/auth/api")
        type: The folder type - "backend" or "frontend"
        subtype: The folder subtype:
            - backend: api, library, worker, cli
            - frontend: ui, library, e2e
        language: The programming language for this folder
        runtime: The runtime version
        package_manager: The package manager
        test_framework: The testing framework
        linter: The linter tool (single string for backwards compatibility)
        linters: List of linter tools for advanced templating
        formatter: The formatter tool
        coverage: Coverage targets
    """

    folder: str
    type: str  # "backend" or "frontend"
    subtype: str  # "api", "library", "worker", "cli" or "ui", "library", "e2e"
    language: str = ""  # Can be empty - will be derived from preset if type/subtype provided
    runtime: str = ""
    package_manager: str = ""
    test_framework: str = ""
    linter: str = ""
    linters: list[str] = field(default_factory=list)  # List of linters for advanced templating
    formatter: str = ""
    coverage: dict[str, int] = field(default_factory=lambda: DEFAULT_COVERAGE.copy())

    def __post_init__(self) -> None:
        """Apply language-specific defaults after initialization."""
        # If language is not provided, try to derive from preset
        if not self.language and self.type and self.subtype:
            preset_defaults = get_preset_defaults(self.type, self.subtype)
            if preset_defaults and "language" in preset_defaults:
                self.language = preset_defaults["language"]

        # If still no language, use python as fallback
        if not self.language:
            self.language = "python"

        lang_key = self.language.lower()

        # Get defaults for this language
        defaults: dict[str, str] = (
            LANGUAGE_DEFAULTS.get(lang_key) or LANGUAGE_DEFAULTS.get("python") or {}
        )

        # Apply defaults if not specified
        if not self.runtime and "runtime" in defaults:
            self.runtime = defaults["runtime"]
        if not self.package_manager:
            self.package_manager = defaults.get("package_manager", "")
        if not self.test_framework:
            self.test_framework = defaults.get("test_framework", "")
        if not self.linter:
            self.linter = defaults.get("linter", "")
        if not self.linters and self.linter:
            self.linters = [self.linter]  # Initialize linters list from linter
        if not self.formatter:
            self.formatter = defaults.get("formatter", "")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of the folder spec.
        """
        return {
            "folder": self.folder,
            "type": self.type,
            "subtype": self.subtype,
            "language": self.language,
            "runtime": self.runtime,
            "package_manager": self.package_manager,
            "test_framework": self.test_framework,
            "linter": self.linter,
            "linters": self.linters.copy(),  # List of linters for advanced templating
            "formatter": self.formatter,
            "coverage": self.coverage.copy(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FolderSpec":
        """Create from dictionary.

        Args:
            data: Dictionary containing folder spec data.

        Returns:
            FolderSpec instance.
        """
        # Extract coverage if present
        coverage = data.pop("coverage", None)

        # Create instance
        instance = cls(**data)

        # Apply coverage if provided
        if coverage:
            instance.coverage = coverage

        return instance


# Standard folder type presets
FOLDER_TYPE_PRESETS = {
    "backend": {
        "api": {"language": "python", "subtype": "api"},
        "library": {"language": "python", "subtype": "library"},
        "worker": {"language": "python", "subtype": "worker"},
        "cli": {"language": "python", "subtype": "cli"},
    },
    "frontend": {
        "ui": {"language": "typescript", "subtype": "ui"},
        "library": {"language": "typescript", "subtype": "library"},
        "e2e": {"language": "typescript", "subtype": "e2e"},
    },
}


def get_preset_defaults(folder_type: str, subtype: str) -> dict[str, str]:
    """Get default values for a preset.

    Args:
        folder_type: The folder type ("backend" or "frontend")
        subtype: The folder subtype

    Returns:
        Dictionary with default values for the preset
    """
    return FOLDER_TYPE_PRESETS.get(folder_type, {}).get(subtype, {})
