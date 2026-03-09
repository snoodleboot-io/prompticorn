"""
builders/utils.py
Shared utilities for builder classes.
"""

from functools import lru_cache
from pathlib import Path


class HeaderStripper:
    """Utility for stripping header comments from markdown files.

    Removes:
    - # filename.md comments
    - <!-- path: ... --> comments
    - "Behavior when" style headers
    """

    @staticmethod
    def strip(content: str) -> str:
        """Strip header comments from markdown content.

        Args:
            content: Raw markdown content.

        Returns:
            Content with header comments removed.
        """
        lines = content.splitlines(keepends=True)
        start = 0
        for i, line in enumerate(lines[:3]):
            stripped = line.strip()
            if stripped.startswith("# ") and (
                stripped.endswith(".md") or "Behavior when" in stripped
            ):
                start = i + 1
            elif stripped.startswith("<!--") and stripped.endswith("-->"):
                start = i + 1
        return "".join(lines[start:])


# Module-level cached function for registry compatibility
# TODO: This should be removed once registry.py is updated to use HeaderStripper
@lru_cache(maxsize=32)
def _prompt_body_cached(prompts_dir: Path, filename: str) -> str:
    """Read and process a prompt file (cached for performance).

    Args:
        prompts_dir: Path to prompts directory.
        filename: Filename to read.

    Returns:
        Content with headers stripped.
    """
    path = prompts_dir / filename
    content = path.read_text(encoding="utf-8")
    return HeaderStripper.strip(content)
