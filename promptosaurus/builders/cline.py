"""
builders/cline.py
Builds the .clinerules file and .clineignore for Cline.

Output:
  {output}/.clinerules   ← all rules concatenated with section headers
  {output}/.clineignore ← ignore patterns
"""

from pathlib import Path
from typing import Any

from promptosaurus.builders.builder import Builder
from promptosaurus.builders.ignore_generator import ClineIgnoreBuilder


class ClineBuilder(Builder):
    """Builder for Cline .clinerules file."""

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """
        Write .clinerules and .clineignore under `output`.
        Returns a list of action strings for display.
        """
        actions: list[str] = []

        # Build .clinerules
        destination = output / ".clinerules"
        content = self._build_concatenated("# .clinerules")

        if dry_run:
            lines = content.count("\n")
            actions.append(f"[dry-run] .clinerules ({lines} lines)")
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
            lines = content.count("\n")
            actions.append(f"✓ .clinerules ({lines} lines)")

        # Build .clineignore
        actions.extend(self._build_ignore(output, dry_run))

        return actions

    def _build_ignore(self, output: Path, dry_run: bool) -> list[str]:
        """Generate .clineignore file."""
        return ClineIgnoreBuilder().build(output, dry_run)
