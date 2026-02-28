"""
builders/builder.py
Base Builder class for all output builders.
"""

from pathlib import Path


class Builder:
    """Base class for all builders that generate output configs."""

    def build(self, output: Path, dry_run: bool = False) -> list[str]:
        """
        Build output configs.

        Args:
            output: Directory to write output into.
            dry_run: If True, preview what would be written without touching filesystem.

        Returns:
            List of action strings for display.
        """
        raise NotImplementedError("Subclasses must implement build()")
