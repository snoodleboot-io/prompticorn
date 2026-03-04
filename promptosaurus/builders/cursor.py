"""
builders/cursor.py
Builds Cursor rule files and .cursorignore.

Output:
  {output}/.cursor/rules/core-system.mdc          ← always-on as .mdc
  {output}/.cursor/rules/core-conventions.mdc
  {output}/.cursor/rules/{mode}/{topic}.mdc        ← per-mode as .mdc
  {output}/.cursorrules                            ← legacy fallback (concatenated)
  {output}/.cursorignore                           ← ignore patterns
"""

import shutil
from pathlib import Path
from typing import Any

from promptosaurus.builders._concat import build_concatenated
from promptosaurus.builders.builder import Builder
from promptosaurus.registry import registry


class CursorBuilder(Builder):
    """Builder for Cursor rule files."""

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """
        Write Cursor rule files under `output`.
        Returns a list of action strings for display.
        """
        actions: list[str] = []
        rules_base = output / ".cursor" / "rules"

        # Always-on rules as .mdc
        for filename in registry.always_on:
            mdc_name = filename.replace(".md", ".mdc")
            destination = rules_base / mdc_name
            actions.append(self._copy(registry.prompt_path(filename), destination, dry_run))

        # Per-mode rules as .mdc in subdirectories
        for mode_key, files in registry.mode_files.items():
            for filename in files:
                dname = registry.dest_name(mode_key, filename, ext=".mdc")
                destination = rules_base / mode_key / dname
                actions.append(self._copy(registry.prompt_path(filename), destination, dry_run))

        # Legacy .cursorrules fallback
        legacy_dst = output / ".cursorrules"
        content = build_concatenated("# .cursorrules")
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
        """Generate .cursorignore file."""
        destination = output / ".cursorignore"
        content = registry.generate_cursorignore()

        if dry_run:
            lines = content.count("\n")
            return [f"[dry-run] .cursorignore ({lines} lines)"]

        destination.write_text(content, encoding="utf-8")
        lines = content.count("\n")
        return [f"✓ .cursorignore ({lines} lines)"]

    def _copy(self, source_path: Path, destination: Path, dry_run: bool) -> str:
        rel = str(destination).split(".cursor/", 1)[-1]
        label = f".cursor/{rel}"
        if dry_run:
            return f"[dry-run] {source_path.name} → {label}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        return f"✓ {source_path.name} → {label}"
