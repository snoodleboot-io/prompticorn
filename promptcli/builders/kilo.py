"""
builders/kilo.py
Builds the .kilocode/ directory structure for Kilo Code.

Output layout:
  {output}/.kilocode/rules/            ← always-on (all modes)
  {output}/.kilocode/rules-{mode}/     ← per-mode files
"""

from pathlib import Path
import shutil

from promptcli.registry import (
    ALWAYS_ON,
    MODE_FILES,
    prompt_path,
    dest_name,
)
from promptcli.builders.builder import Builder


class KiloBuilder(Builder):
    """Builder for Kilo Code .kilocode/ directory structure."""

    def build(self, output: Path, dry_run: bool = False) -> list[str]:
        """
        Write the Kilo .kilocode/ structure under `output`.
        Returns a list of action strings for display.
        """
        actions: list[str] = []
        base = output / ".kilocode"

        # Always-on rules
        for filename in ALWAYS_ON:
            dst = base / "rules" / filename
            actions.append(self._copy(prompt_path(filename), dst, dry_run))

        # Per-mode rules
        for mode_key, files in MODE_FILES.items():
            for filename in files:
                dst = base / f"rules-{mode_key}" / dest_name(mode_key, filename)
                actions.append(self._copy(prompt_path(filename), dst, dry_run))

        return actions

    def _copy(self, src: Path, dst: Path, dry_run: bool) -> str:
        rel = str(dst).split(".kilocode/", 1)[-1]
        label = f".kilocode/{rel}"
        if dry_run:
            return f"[dry-run] {src.name} → {label}"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return f"✓ {src.name} → {label}"
