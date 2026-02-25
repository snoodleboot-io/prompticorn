"""
builders/cursor.py
Builds Cursor rule files.

Output:
  {output}/.cursor/rules/core-system.mdc          ← always-on as .mdc
  {output}/.cursor/rules/core-conventions.mdc
  {output}/.cursor/rules/{mode}/{topic}.mdc        ← per-mode as .mdc
  {output}/.cursorrules                            ← legacy fallback (concatenated)
"""

from pathlib import Path
import shutil

from promptcli.registry import (
    ALWAYS_ON,
    MODE_FILES,
    prompt_path,
    dest_name,
)
from promptcli.builders._concat import build_concatenated
from promptcli.builders.builder import Builder


class CursorBuilder(Builder):
    """Builder for Cursor rule files."""

    def build(self, output: Path, dry_run: bool = False) -> list[str]:
        """
        Write Cursor rule files under `output`.
        Returns a list of action strings for display.
        """
        actions: list[str] = []
        rules_base = output / ".cursor" / "rules"

        # Always-on rules as .mdc
        for filename in ALWAYS_ON:
            mdc_name = filename.replace(".md", ".mdc")
            dst = rules_base / mdc_name
            actions.append(self._copy(prompt_path(filename), dst, dry_run))

        # Per-mode rules as .mdc in subdirectories
        for mode_key, files in MODE_FILES.items():
            for filename in files:
                dname = dest_name(mode_key, filename, ext=".mdc")
                dst = rules_base / mode_key / dname
                actions.append(self._copy(prompt_path(filename), dst, dry_run))

        # Legacy .cursorrules fallback
        legacy_dst = output / ".cursorrules"
        content = build_concatenated("# .cursorrules")
        if dry_run:
            actions.append(f"[dry-run] .cursorrules ({content.count(chr(10))} lines, legacy)")
        else:
            legacy_dst.parent.mkdir(parents=True, exist_ok=True)
            legacy_dst.write_text(content, encoding="utf-8")
            actions.append(f"✓ .cursorrules ({content.count(chr(10))} lines, legacy fallback)")

        return actions

    def _copy(self, src: Path, dst: Path, dry_run: bool) -> str:
        rel = str(dst).split(".cursor/", 1)[-1]
        label = f".cursor/{rel}"
        if dry_run:
            return f"[dry-run] {src.name} → {label}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return f"✓ {src.name} → {label}"
