"""
builders/cline.py
Builds the .clinerules file for Cline.

Output:
  {output}/.clinerules   ← all rules concatenated with section headers
"""

from pathlib import Path

from promptcli.builders._concat import build_concatenated
from promptcli.builders.builder import Builder


class ClineBuilder(Builder):
    """Builder for Cline .clinerules file."""

    def build(self, output: Path, dry_run: bool = False) -> list[str]:
        """
        Write .clinerules under `output`.
        Returns a list of action strings for display.
        """
        dst = output / ".clinerules"
        content = build_concatenated("# .clinerules")

        if dry_run:
            lines = content.count("\n")
            return [f"[dry-run] .clinerules ({lines} lines)"]

        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
        lines = content.count("\n")
        return [f"✓ .clinerules ({lines} lines)"]
