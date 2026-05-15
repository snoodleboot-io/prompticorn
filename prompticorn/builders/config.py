"""Configuration loader for Kilo builder settings.

This module provides the KiloConfig class that loads and manages configuration
for the Kilo builder, including custom modes and language file mappings.

The configuration is loaded from YAML files:
- kilo_modes.yaml: Custom mode definitions
- kilo_language_file_map.yaml: Language to conventions file mappings

Classes:
    KiloConfig: Configuration loader for Kilo builder settings.
"""

from pathlib import Path
from typing import Any

import yaml


class KiloConfig:
    """Configuration loader for Kilo builder settings.

    This class loads configuration from YAML files and provides
    typed access to settings. It uses lazy loading to defer
    file I/O until the properties are first accessed.

    Attributes:
        kilo_modes: Dictionary of mode slug to mode configuration.
        language_file_map: Dictionary of language name to conventions file.
        base_files: Frozenset of core file paths needed for .kilocode/rules/.

    Methods:
        _load_modes: Load custom modes from YAML file.
        _load_language_map: Load language file map from YAML file.

    Args:
        modes_path: Optional custom path to kilo_modes.yaml
        language_map_path: Optional custom path to kilo_language_file_map.yaml
    """

    def __init__(
        self,
        modes_path: Path | None = None,
        language_map_path: Path | None = None,
    ) -> None:
        """Initialize config with optional custom paths.

        Args:
            modes_path: Optional custom path to kilo_modes.yaml.
            language_map_path: Optional custom path to kilo_language_file_map.yaml.
        """
        self._modes_path = modes_path or self._default_modes_path()
        self._language_map_path = language_map_path or self._default_language_map_path()
        self._kilo_modes: dict[str, Any] | None = None
        self._language_file_map: dict[str, str] | None = None
        # Internal class variable for core files (not a constant)
        self._base_files = frozenset(
            [
                "agents/core/core-system.md",
                "agents/core/core-conventions.md",
                "agents/core/core-session.md",
            ]
        )

    @staticmethod
    def _default_modes_path() -> Path:
        """Get the default path to kilo_modes.yaml.

        Returns:
            Path to the default kilo_modes.yaml file in the kilo directory.
        """
        return Path(__file__).parent / "kilo" / "kilo_modes.yaml"

    @staticmethod
    def _default_language_map_path() -> Path:
        """Get the default path to kilo_language_file_map.yaml.

        Returns:
            Path to the default kilo_language_file_map.yaml file in the kilo directory.
        """
        return Path(__file__).parent / "kilo" / "kilo_language_file_map.yaml"

    @property
    def kilo_modes(self) -> dict[str, Any]:
        """Lazy-load and return kilo modes from YAML.

        Loads the custom mode definitions from the modes YAML file.
        The file is only read once on first access, then cached.

        Returns:
            Dictionary of mode slug to mode configuration.

        Raises:
            FileNotFoundError: If the modes YAML file doesn't exist.
            yaml.YAMLError: If the YAML file is malformed.
        """
        if self._kilo_modes is None:
            self._kilo_modes = self._load_modes()
        return self._kilo_modes

    @property
    def language_file_map(self) -> dict[str, str]:
        """Lazy-load and return language file map from YAML.

        Loads the language to conventions file mappings from the YAML file.
        The file is only read once on first access, then cached.

        Returns:
            Dictionary mapping language name to conventions file path.

        Raises:
            FileNotFoundError: If the language map YAML file doesn't exist.
            yaml.YAMLError: If the YAML file is malformed.
        """
        if self._language_file_map is None:
            self._language_file_map = self._load_language_map()
        return self._language_file_map

    @property
    def base_files(self) -> frozenset[str]:
        """Return set of core base files needed for .kilocode/rules/.

        These are the always-on prompt files that are included in
        every build regardless of mode.

        Returns:
            Frozenset of core file paths.
        """
        return self._base_files

    def _load_modes(self) -> dict[str, Any]:
        """Load custom modes from YAML file.

        Reads and parses the kilo_modes.yaml file, extracting the
        customModes array into a dictionary keyed by mode slug.

        Returns:
            Dictionary mapping mode slug to mode configuration.

        Raises:
            FileNotFoundError: If the modes YAML file doesn't exist.
            yaml.YAMLError: If the YAML file is malformed.
        """
        with self._modes_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        modes_list = data.get("customModes", [])
        return {mode["slug"]: mode for mode in modes_list if isinstance(mode, dict)}

    def _load_language_map(self) -> dict[str, str]:
        """Load language file map from YAML file.

        Reads and parses the kilo_language_file_map.yaml file,
        extracting the language_file_map dictionary.

        Returns:
            Dictionary mapping language name to conventions file.

        Raises:
            FileNotFoundError: If the language map YAML file doesn't exist.
            yaml.YAMLError: If the YAML file is malformed.
        """
        with self._language_map_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("language_file_map", {})
