"""Builder for Cline .clinerules file and .clineignore.

This module provides the ClineBuilder class that generates the configuration
files required by Cline (formerly Claude Dev) AI assistant.

Output:
  {output}/.clinerules   ← all rules concatenated with section headers
  {output}/.clineignore ← ignore patterns

Classes:
    ClineBuilder: Generates .clinerules and .clineignore for Cline.

Example:
    >>> from pathlib import Path
    >>> from promptosaurus.builders.cline import ClineBuilder
    >>> builder = ClineBuilder()
    >>> actions = builder.build(Path("./output"))
    >>> print(actions)
    ['✓ .clinerules (150 lines)', '✓ .clineignore (25 lines)']
"""

from pathlib import Path
from typing import Any

from promptosaurus.builders.builder import Builder
from promptosaurus.builders.ignore_generator import ClineIgnoreBuilder


class ClineBuilder(Builder):
    """Builder for Cline .clinerules file.

    This builder creates two files for Cline:
    - .clinerules: All rules concatenated with section headers
    - .clineignore: Ignore patterns for Cline

    The concatenated .clinerules file combines all prompts from the registry
    into a single file with clear section headers for each prompt category.

    Attributes:
        Inherits _base_files from Builder base class.

    Example:
        >>> builder = ClineBuilder()
        >>> # Build files
        >>> actions = builder.build(Path("./my-project"))
        >>> # Check output
        >>> for action in actions:
        ...     print(action)
    """

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """Write .clinerules and .clineignore under `output`.

        Generates the Cline configuration files by:
        1. Building a concatenated .clinerules file from all registry prompts
        2. Building a .clineignore file with ignore patterns

        Args:
            output: Directory path where the files will be created.
            config: Optional configuration dict with template variables.
            dry_run: If True, preview what would be written without touching filesystem.

        Returns:
            List of action strings describing what was created.

        Example:
            >>> from pathlib import Path
            >>> builder = ClineBuilder()
            >>> # Normal run
            >>> actions = builder.build(Path("./output"))
            >>> print(actions)
            ['✓ .clinerules (150 lines)', '✓ .clineignore (25 lines)']
            >>> # Dry run
            >>> actions = builder.build(Path("./output"), dry_run=True)
            >>> print(actions)
            ['[dry-run] .clinerules (150 lines)', '[dry-run] .clineignore (25 lines)']
        """
        actions: list[str] = []

        # Build .clinerules
        destination = output / ".clinerules"
        content = self._build_concatenated("# .clinerules", config)

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
        """Generate .clineignore file.

        Helper method that uses ClineIgnoreBuilder to generate the
        ignore file for Cline.

        Args:
            output: Output directory path.
            dry_run: If True, return preview without writing.

        Returns:
            List containing action string for the ignore file.
        """
        return ClineIgnoreBuilder().build(output, dry_run)
