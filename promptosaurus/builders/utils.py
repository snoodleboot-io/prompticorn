"""Shared utilities for builder classes.

This module provides utility classes and functions used across the builder
package for common operations like header stripping and caching.

Classes:
    HeaderStripper: Utility for stripping header comments from markdown files.

Functions:
    _prompt_body_cached: Cached function for reading and processing prompt files.
"""

from functools import lru_cache
from pathlib import Path


class HeaderStripper:
    """Utility for stripping header comments from markdown files.

    This class removes various types of header comments that are commonly
    found in markdown prompt files, including:

    - Filename comments like `# filename.md`
    - HTML path comments like `<!-- path: ... -->`
    - Behavior headers like "Behavior when" style headers

    This is useful when generating concatenated output where you want
    clean content without the metadata headers.
    """

    @staticmethod
    def strip(content: str) -> str:
        """Strip header comments from markdown content.

        Removes the first few lines that match common header comment patterns.
        Only checks the first 3 lines to avoid removing legitimate content.

        Args:
            content: Raw markdown content with potential header comments.

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

    This function reads a prompt file from disk and strips its header comments.
    Results are cached using LRU cache for performance when repeatedly
    accessing the same files.

    Args:
        prompts_dir: Path to prompts directory.
        filename: Filename to read (relative to prompts_dir).

    Returns:
        Content with headers stripped.

    Raises:
        FileNotFoundError: If the specified file doesn't exist.
    """
    path = prompts_dir / filename
    content = path.read_text(encoding="utf-8")
    return HeaderStripper.strip(content)
