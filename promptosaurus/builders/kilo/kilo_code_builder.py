"""Base class for Kilo Code configuration builders.

This module provides the KiloCodeBuilder base class that contains common
functionality shared between CLI and IDE targets for Kilo Code.

Classes:
    KiloCodeBuilder: Base builder for Kilo Code configurations.
"""

from pathlib import Path
from typing import Any

from promptosaurus.builders.builder import Builder
from promptosaurus.builders.config import KiloConfig
from promptosaurus.builders.ignore_generator import KiloIgnoreBuilder
from promptosaurus.builders.utils import HeaderStripper
from promptosaurus.registry import registry


class KiloCodeBuilder(Builder):
    """Base builder for Kilo Code configurations.

    This abstract class provides common functionality for both CLI and IDE
    output formats. It handles:
    - Configuration management via KiloConfig
    - File copying with template variable substitution
    - Manifest file generation
    - Ignore file generation
    - Base and mode file creation

    Attributes:
        kilo_modes: Property returning the kilo modes from config.
        language_file_map: Property returning the language file map from config.
        _kilo_builtin_modes: Frozenset of built-in Kilo mode names.

    Args:
        config: Optional KiloConfig instance. If not provided, uses default config.
    """

    # Modes that are built-in to Kilo and should not be generated in output
    _kilo_builtin_modes = frozenset(
        {
            "architect",
            "code",
            "ask",
            "debug",
            "orchestrator",
        }
    )

    def __init__(self, config: KiloConfig | None = None) -> None:
        """Initialize builder with optional config.

        Args:
            config: KiloConfig instance. Uses default if not provided.
        """
        super().__init__()
        self._config = config or KiloConfig()

    @property
    def kilo_modes(self) -> dict[str, Any]:
        """Return the kilo modes from config.

        Returns:
            Dictionary of mode slug to mode configuration.
        """
        return self._config.kilo_modes

    @property
    def language_file_map(self) -> dict[str, str]:
        """Return the language file map from config.

        Returns:
            Dictionary mapping language name to conventions file.
        """
        return self._config.language_file_map

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """Build Kilo Code configuration. Subclasses implement specific output formats.

        This method must be implemented by subclasses to generate the
        appropriate output format for their target.

        Args:
            output: Directory path where files will be created.
            config: Optional configuration dict with template variables.
            dry_run: If True, preview what would be written without touching filesystem.

        Returns:
            List of action strings describing what was created.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError()

    def _get_agents_md_content(self) -> str:
        """Get the AGENTS.md content specific to the builder type.

        Returns:
            The content for the AGENTS.md file.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError()

    def _write_manifest(self, destination: Path, dry_run: bool) -> str:
        """Write the .kilocodemodes manifest file.

        Simply copies the kilo_modes.yaml source file to preserve exact formatting.

        Args:
            destination: Path where the manifest file will be written.
            dry_run: If True, return preview string without writing.

        Returns:
            Action string describing the operation.
        """
        # Read from the source YAML file to preserve exact formatting
        source_path = Path(__file__).parent / "kilo_modes.yaml"

        if dry_run:
            return "[dry-run] .kilocodemodes (copied from kilo_modes.yaml)"

        # Copy the file content directly
        content = source_path.read_text(encoding="utf-8")
        destination.write_text(content, encoding="utf-8")
        return "✓ .kilocodemodes"

    def _build_ignore(self, output: Path, dry_run: bool) -> list[str]:
        """Generate .kiloignore file.

        Helper method that uses KiloIgnoreBuilder to generate the
        ignore file for Kilo Code.

        Args:
            output: Output directory path.
            dry_run: If True, return preview without writing.

        Returns:
            List containing action string for the ignore file.
        """
        return KiloIgnoreBuilder().build(output, dry_run)

    def _create_base_md(
        self,
        rules_dir: Path,
        language_file: str | None,
        dry_run: bool,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Create _base.md by concatenating core files.

        Creates the base rules file by combining core convention files
        and optionally adding language-specific conventions.

        Args:
            rules_dir: The rules directory path.
            language_file: Optional language conventions filename.
            dry_run: If True, return preview without writing.
            config: Optional config for template substitution.

        Returns:
            Action string describing the operation.
        """
        destination = rules_dir / "_base.md"
        label = ".opencode/rules/_base.md"

        if dry_run:
            return f"[dry-run] {label}"

        # Collect content from base files
        parts: list[str] = []

        for filename in self._base_files:
            source_path = registry.prompt_path(filename)
            if source_path.exists():
                content = source_path.read_text(encoding="utf-8")
                parts.append(HeaderStripper.strip(content))

        # Add language-specific conventions if selected
        if language_file:
            source_path = registry.prompt_path(language_file)
            if source_path.exists():
                content = source_path.read_text(encoding="utf-8")
                # Apply template substitution for language files
                if config:
                    content = self._substitute_template_variables(content, config)
                parts.append(HeaderStripper.strip(content))

        # Join all parts with clear separators
        full_content = "\n---\n\n".join(parts)

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(full_content, encoding="utf-8")
        return f"✓ {label}"

    def _create_collapsed_mode_md(
        self,
        rules_dir: Path,
        mode_key: str,
        filenames: list[str],
        dry_run: bool,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Create a collapsed {MODE}.md file from multiple subagent files.

        Creates a single markdown file that contains all the subagent
        content for a given mode, joined together with separators.

        Args:
            rules_dir: The rules directory path.
            mode_key: The mode identifier (e.g., 'code', 'architect').
            filenames: List of prompt filenames to include.
            dry_run: If True, return preview without writing.
            config: Optional config for template substitution.

        Returns:
            Action string describing the operation.
        """
        destination = rules_dir / f"{mode_key}.md"
        label = f".opencode/rules/{mode_key}.md"

        if dry_run:
            return f"[dry-run] {label}"

        # Collect content from all subagent files
        parts: list[str] = []

        for filename in filenames:
            source_path = registry.prompt_path(filename)
            if source_path.exists():
                content = source_path.read_text(encoding="utf-8")
                parts.append(HeaderStripper.strip(content))

        # Join all parts with clear separators
        full_content = "\n---\n\n".join(parts)

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(full_content, encoding="utf-8")
        return f"✓ {label}"

    def _create_agents_md(self, output: Path, dry_run: bool) -> str:
        """Create AGENTS.md user guide.

        Generates the AGENTS.md file that serves as the user guide
        for the Kilo Code configuration.

        Args:
            output: Output directory path.
            dry_run: If True, return preview without writing.

        Returns:
            Action string describing the operation.
        """
        destination = output / "AGENTS.md"
        label = "AGENTS.md"

        # Get builder-specific content
        content = self._get_agents_md_content()

        if dry_run:
            return f"[dry-run] {label}"

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        return f"✓ {label}"
