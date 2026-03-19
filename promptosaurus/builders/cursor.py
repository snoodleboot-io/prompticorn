"""Builder for Cursor rule files and .cursorignore.

This module provides the CursorBuilder class that generates the configuration
files required by Cursor AI editor.

Output:
  {output}/.cursor/rules/core-system.mdc          ← always-on as .mdc
  {output}/.cursor/rules/core.mdc
  {output}/.cursor/rules/{mode}/{topic}.mdc        ← per-mode as .mdc
  {output}/.cursorrules                            ← legacy fallback (concatenated)
  {output}/.cursorignore                           ← ignore patterns

Classes:
    CursorBuilder: Generates Cursor rule files in multiple formats.

Example:
    >>> from pathlib import Path
    >>> from promptosaurus.builders.cursor import CursorBuilder
    >>> builder = CursorBuilder()
    >>> actions = builder.build(Path("./output"))
    >>> for action in actions[:3]:
    ...     print(action)
    ✓ core-system.mdc → .cursor/rules/core-system.mdc
    ✓ core-conventions.mdc → .cursor/rules/core-conventions.mdc
    ✓ core-session.mdc → .cursor/rules/core-session.mdc
"""

import shutil
from pathlib import Path
from typing import Any

from promptosaurus.builders.builder import Builder
from promptosaurus.builders.ignore_generator import CursorIgnoreBuilder
from promptosaurus.registry import registry


class CursorBuilder(Builder):
    """Builder for Cursor rule files.

    This builder creates multiple output formats for Cursor:
    - Individual .mdc files in .cursor/rules/ directory for always-on rules
    - Per-mode .mdc files in subdirectories
    - Legacy .cursorrules file as fallback
    - .cursorignore file with ignore patterns

    Cursor uses .mdc (Markdown Cursor) files as its rule format, which
    are processed as markdown with special Cursor directives.

    Attributes:
        Inherits _base_files from Builder base class.

    Example:
        >>> builder = CursorBuilder()
        >>> # Build all files
        >>> actions = builder.build(Path("./my-project"))
        >>> # Check results
        >>> print(f\"Generated {len(actions)} files\")
    """

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """Write Cursor rule files under `output`.

        Generates Cursor configuration by:
        1. Creating always-on rules as .mdc files in .cursor/rules/
        2. Creating per-mode rules as .mdc files in mode subdirectories
        3. Creating legacy .cursorrules fallback file
        4. Creating .cursorignore file

        Args:
            output: Directory path where the files will be created.
            config: Optional configuration dict with template variables.
            dry_run: If True, preview what would be written without touching filesystem.

        Returns:
            List of action strings describing what was created.

        Example:
            >>> from pathlib import Path
            >>> builder = CursorBuilder()
            >>> # Normal run
            >>> actions = builder.build(Path("./output"))
            >>> # Dry run
            >>> actions = builder.build(Path("./output"), dry_run=True)
        """
        actions: list[str] = []
        rules_base = output / ".cursor" / "rules"

        # Always-on rules as .mdc
        for filename in registry.always_on:
            mdc_name = filename.replace(".md", ".mdc")
            destination = rules_base / mdc_name
            actions.append(self._copy(registry.prompt_path(filename), destination, dry_run, config))

        # Per-mode rules as .mdc in subdirectories
        for mode_key, files in registry.mode_files.items():
            for filename in files:
                dname = registry.dest_name(mode_key, filename, ext=".mdc")
                destination = rules_base / mode_key / dname
                actions.append(self._copy(registry.prompt_path(filename), destination, dry_run, config))

        # Legacy .cursorrules fallback
        legacy_dst = output / ".cursorrules"
        content = self._build_concatenated("# .cursorrules", config)
        if dry_run:
            actions.append(f"[dry-run] .cursorrules ({content.count(chr(10))} lines, legacy)")
        else:
            legacy_dst.parent.mkdir(parents=True, exist_ok=True)
            legacy_dst.write_text(content, encoding="utf-8")
            actions.append(f"✓ .cursorrules ({content.count(chr(10))} lines, legacy fallback)")

        # Build .cursorignore
        actions.extend(self._build_ignore(output, dry_run))

        return actions

    def _build_ignore(self, output: Path, dry_run: bool) -> list[str]:
        """Generate .cursorignore file.

        Helper method that uses CursorIgnoreBuilder to generate the
        ignore file for Cursor.

        Args:
            output: Output directory path.
            dry_run: If True, return preview without writing.

        Returns:
            List containing action string for the ignore file.
        """
        return CursorIgnoreBuilder().build(output, dry_run)

    def _copy(self, source_path: Path, destination: Path, dry_run: bool) -> str:
        """Copy a source file to destination.

        Internal helper that handles the file copying operation with
        proper path formatting for display.

        Args:
            source_path: Source file path to copy from.
            destination: Destination file path to copy to.
            dry_run: If True, return preview string without copying.

        Returns:
            Action string describing the copy operation.

        Example:
            >>> action = self._copy(Path("core-system.md"), Path(".cursor/rules/core-system.mdc"), False)
            >>> print(action)
            ✓ core-system.mdc → .cursor/rules/core-system.mdc
        """
        rel = str(destination).split(".cursor/", 1)[-1]
        label = f".cursor/{rel}"
        if dry_run:
            return f"[dry-run] {source_path.name} → {label}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        return f"✓ {source_path.name} → {label}"
