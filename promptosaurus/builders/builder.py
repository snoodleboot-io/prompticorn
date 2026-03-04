"""
builders/builder.py
Base Builder class for all output builders.
"""

from pathlib import Path
from typing import Any


class Builder:
    """Base class for all builders that generate output configs."""

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """
        Build output configs.

        Args:
            output: Directory to write output into.
            config: Optional configuration dict with template variables.
            dry_run: If True, preview what would be written without touching filesystem.

        Returns:
            List of action strings for display.
        """
        raise NotImplementedError("Subclasses must implement build()")
