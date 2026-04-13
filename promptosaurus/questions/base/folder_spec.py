"""Folder specification for multi-language monorepo configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class FolderSpecRegistry:
    """Registry for folder specification defaults and presets.
    
    Loads language defaults, coverage targets, and folder type presets
    from YAML configuration file.
    """
    _config: dict[str, Any] | None = None
    
    @classmethod
    def _load_config(cls) -> dict[str, Any]:
        """Load folder spec configuration from YAML file.
        
        Returns:
            Dictionary with language_defaults, default_coverage, and folder_type_presets.
        """
        if cls._config is None:
            config_file = Path(__file__).parent.parent / "configurations" / "language_defaults.yaml"
            with open(config_file, encoding="utf-8") as f:
                cls._config = yaml.safe_load(f)
        return cls._config
    
    @classmethod
    def get_language_defaults(cls) -> dict[str, dict[str, str]]:
        """Get language-specific defaults.
        
        Returns:
            Dictionary mapping language keys to their default configurations.
        """
        config = cls._load_config()
        # Return all keys except default_coverage and folder_type_presets
        return {
            k: v for k, v in config.items() 
            if k not in ("default_coverage", "folder_type_presets")
        }
    
    @classmethod
    def get_default_coverage(cls) -> dict[str, int]:
        """Get default coverage targets.
        
        Returns:
            Dictionary with coverage target percentages.
        """
        config = cls._load_config()
        return config["default_coverage"].copy()
    
    @classmethod
    def get_folder_type_presets(cls) -> dict[str, dict[str, dict[str, str]]]:
        """Get folder type presets.
        
        Returns:
            Dictionary mapping folder types to their preset configurations.
        """
        config = cls._load_config()
        return config["folder_type_presets"]
    
    @classmethod
    def get_preset_defaults(cls, folder_type: str, subtype: str) -> dict[str, str]:
        """Get default values for a specific preset.
        
        Args:
            folder_type: The folder type ("backend" or "frontend")
            subtype: The folder subtype
            
        Returns:
            Dictionary with default values for the preset.
        """
        presets = cls.get_folder_type_presets()
        return presets.get(folder_type, {}).get(subtype, {})


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
    coverage: dict[str, int] = field(default_factory=lambda: FolderSpecRegistry.get_default_coverage())

    def __post_init__(self) -> None:
        """Apply language-specific defaults after initialization."""
        # If language is not provided, try to derive from preset
        if not self.language and self.type and self.subtype:
            preset_defaults = FolderSpecRegistry.get_preset_defaults(self.type, self.subtype)
            if preset_defaults and "language" in preset_defaults:
                self.language = preset_defaults["language"]

        # If still no language, use python as fallback
        if not self.language:
            self.language = "python"

        lang_key = self.language.lower()

        # Get defaults for this language
        all_language_defaults = FolderSpecRegistry.get_language_defaults()
        defaults: dict[str, str] = (
            all_language_defaults.get(lang_key) or all_language_defaults.get("python") or {}
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


def get_preset_defaults(folder_type: str, subtype: str) -> dict[str, str]:
    """Get default values for a preset.

    Args:
        folder_type: The folder type ("backend" or "frontend")
        subtype: The folder subtype

    Returns:
        Dictionary with default values for the preset
    """
    return FolderSpecRegistry.get_preset_defaults(folder_type, subtype)
