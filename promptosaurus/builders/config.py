"""
builders/config.py
Configuration loader for Kilo builder settings.
"""

from pathlib import Path
from typing import Any

import yaml


class KiloConfig:
    """Configuration loader for Kilo builder settings.

    This class loads configuration from YAML files and provides
    typed access to settings. Can be subclassed or extended
    for different agent systems.

    Args:
        modes_path: Optional custom path to kilo_modes.yaml
        language_map_path: Optional custom path to kilo_language_file_map.yaml
    """

    def __init__(
        self,
        modes_path: Path | None = None,
        language_map_path: Path | None = None,
    ) -> None:
        """Initialize config with optional custom paths."""
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
        return Path(__file__).parent / "kilo" / "kilo_modes.yaml"

    @staticmethod
    def _default_language_map_path() -> Path:
        return Path(__file__).parent / "kilo" / "kilo_language_file_map.yaml"

    @property
    def kilo_modes(self) -> dict[str, Any]:
        """Lazy-load and return kilo modes from YAML.

        Returns:
            Dictionary of mode slug to mode configuration.
        """
        if self._kilo_modes is None:
            self._kilo_modes = self._load_modes()
        return self._kilo_modes

    @property
    def language_file_map(self) -> dict[str, str]:
        """Lazy-load and return language file map from YAML.

        Returns:
            Dictionary of language name to conventions file.
        """
        if self._language_file_map is None:
            self._language_file_map = self._load_language_map()
        return self._language_file_map

    @property
    def base_files(self) -> frozenset[str]:
        """Return set of core base files needed for .kilocode/rules/.

        Returns:
            Frozenset of core file paths.
        """
        return self._base_files

    def _load_modes(self) -> dict[str, Any]:
        """Load custom modes from YAML file.

        Returns:
            Dictionary mapping mode slug to mode configuration.
        """
        with self._modes_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        modes_list = data.get("customModes", [])
        return {mode["slug"]: mode for mode in modes_list if isinstance(mode, dict)}

    def _load_language_map(self) -> dict[str, str]:
        """Load language file map from YAML file.

        Returns:
            Dictionary mapping language name to conventions file.
        """
        with self._language_map_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("language_file_map", {})
