"""Spec handler for managing repository configuration specs.

This module provides abstractions for handling spec configuration
differently based on repository type (single-language vs multi-language-monorepo).
"""

from typing import Any

from prompticorn.questions.base.folder_spec import (
    FolderSpec,
    FolderSpecRegistry,
)


class SpecHandler:
    """Interface class for spec handlers.

    This follows the Interface Segregation Principle from SOLID,
    providing a clean abstraction for handling different spec formats.
    """

    def create_spec(self, *args: Any, **kwargs: Any) -> dict[str, Any] | list[dict[str, Any]]:
        """Create a new spec.

        Returns:
            Either a dict (single-language) or list (multi-language-monorepo)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement create_spec()")

    def get_language(self, spec: dict[str, Any] | list[dict[str, Any]]) -> str:
        """Get the primary language from spec.

        Args:
            spec: The spec to extract language from

        Returns:
            The primary language
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement get_language()")

    def is_multi_language(self) -> bool:
        """Check if this handler manages multi-language specs.

        Returns:
            True if this is a multi-language handler
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement is_multi_language()")

    @staticmethod
    def for_repository_type(repo_type: str) -> "SpecHandler":
        """Factory method to get appropriate handler for repository type.

        Args:
            repo_type: The repository type

        Returns:
            Appropriate SpecHandler instance

        Raises:
            ValueError: If repository type is unknown
        """
        if repo_type == "single-language":
            return SingleLanguageSpecHandler()
        elif repo_type == "multi-language-monorepo":
            return MultiLanguageSpecHandler()
        else:
            raise ValueError(f"Unknown repository type: {repo_type}")


class SingleLanguageSpecHandler(SpecHandler):
    """Handler for single-language repository configuration.

    This handles the case where there's one language for the entire repository.
    Uses FolderSpecRegistry to load language defaults and coverage targets.
    """

    def create_spec(self, language: str, **overrides: Any) -> dict[str, Any]:
        """Create a single-language spec.

        Args:
            language: The programming language
            **overrides: Optional overrides for default values

        Returns:
            Dictionary with language configuration
        """
        # Get language defaults from registry
        language_defaults = FolderSpecRegistry.get_language_defaults()
        defaults: dict[str, str] = (
            language_defaults.get(language.lower()) or language_defaults.get("python") or {}
        )

        linter = defaults.get("linter", "")
        spec: dict[str, Any] = {
            "language": language,
            "runtime": defaults.get("runtime", ""),
            "package_manager": defaults.get("package_manager", ""),
            "test_framework": defaults.get("test_framework", ""),
            "linter": linter,
            "linters": [linter] if linter else [],  # List version for advanced templating
            "formatter": defaults.get("formatter", ""),
            "coverage": FolderSpecRegistry.get_default_coverage(),
        }

        # Apply overrides
        for key, value in overrides.items():
            if value:
                spec[key] = value

        return spec

    def get_language(self, spec: dict[str, Any] | list[dict[str, Any]]) -> str:
        """Get language from spec dict.

        Args:
            spec: The spec dictionary (or list of specs - uses first one)

        Returns:
            The language
        """
        if isinstance(spec, list):
            return spec[0].get("language", "") if spec else ""
        return spec.get("language", "")

    def is_multi_language(self) -> bool:
        """Return False for single language handler."""
        return False


class MultiLanguageSpecHandler(SpecHandler):
    """Handler for multi-language-monorepo repository configuration.

    This handles the case where there are multiple folders,
    each with potentially different languages.
    """

    def __init__(self) -> None:
        """Initialize with empty spec list."""
        self._spec: list[dict[str, Any]] = []
        self._folder_specs: list[FolderSpec] = []

    def create_spec(self) -> list[dict[str, Any]]:
        """Create an empty spec list.

        Returns:
            Empty list for folder specs
        """
        return self._spec

    def add_folder_spec(
        self,
        folder: str,
        folder_type: str,
        subtype: str,
        language: str,
        **overrides: Any,
    ) -> None:
        """Add a folder spec to the list.

        Args:
            folder: The folder path
            folder_type: The folder type ("backend" or "frontend")
            subtype: The folder subtype
            language: The programming language
            **overrides: Optional overrides for default values

        Raises:
            ValueError: If folder path is empty or duplicate
        """
        if not folder or not folder.strip():
            raise ValueError("Folder path cannot be empty")

        # Check for duplicates
        if any(spec.get("folder") == folder for spec in self._spec):
            raise ValueError(f"Duplicate folder path: {folder}")

        # Create FolderSpec with overrides
        folder_spec = FolderSpec(
            folder=folder,
            type=folder_type,
            subtype=subtype,
            language=language,
            **overrides,
        )

        self._folder_specs.append(folder_spec)
        self._spec.append(folder_spec.to_dict())

    def get_spec(self) -> list[dict[str, Any]]:
        """Get the current spec list.

        Returns:
            List of folder specs
        """
        return self._spec

    def get_language(self, spec: dict[str, Any] | list[dict[str, Any]]) -> str:
        """Get primary language from first folder.

        Args:
            spec: The spec (ignored, uses internal state)

        Returns:
            Language of first folder, or empty string
        """
        if self._folder_specs:
            return self._folder_specs[0].language
        return ""

    def is_multi_language(self) -> bool:
        """Return True for multi language handler."""
        return True

    def clear(self) -> None:
        """Clear all folder specs."""
        self._spec.clear()
        self._folder_specs.clear()
