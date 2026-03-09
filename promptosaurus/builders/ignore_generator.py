"""
builders/ignore_generator.py
Interface and implementations for generating ignore files.

Uses interface pattern (NotImplementedError) per conventions.
"""

from pathlib import Path

from promptosaurus.registry import registry


class IgnoreFileBuilder:
    """Interface for ignore file builders.

    Uses interface pattern (NotImplementedError) per conventions -
    no ABC, just raise NotImplementedError for required methods.
    """

    @property
    def filename(self) -> str:
        """Filename for the ignore file (e.g., '.kiloignore')."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement filename")

    @property
    def content(self) -> str:
        """Content for the ignore file."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement content")

    def build(self, output: Path, dry_run: bool = False) -> list[str]:
        """Build the ignore file.

        Args:
            output: Output directory.
            dry_run: If True, return preview without writing.

        Returns:
            List of action strings for display.
        """
        destination = output / self.filename
        if dry_run:
            lines = self.content.count("\n")
            return [f"[dry-run] {self.filename} ({lines} lines)"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.content, encoding="utf-8")
        lines = self.content.count("\n")
        return [f"✓ {self.filename} ({lines} lines)"]


class KiloIgnoreBuilder(IgnoreFileBuilder):
    """Generates .kiloignore content for Kilo Code."""

    @property
    def filename(self) -> str:
        return ".kiloignore"

    @property
    def content(self) -> str:
        return registry.generate_kiloignore()


class ClineIgnoreBuilder(IgnoreFileBuilder):
    """Generates .clineignore content for Cline."""

    @property
    def filename(self) -> str:
        return ".clineignore"

    @property
    def content(self) -> str:
        return registry.generate_clineignore()


class CursorIgnoreBuilder(IgnoreFileBuilder):
    """Generates .cursorignore content for Cursor."""

    @property
    def filename(self) -> str:
        return ".cursorignore"

    @property
    def content(self) -> str:
        return registry.generate_cursorignore()


class CopilotIgnoreBuilder(IgnoreFileBuilder):
    """Generates .copilotignore content for GitHub Copilot."""

    @property
    def filename(self) -> str:
        return ".copilotignore"

    @property
    def content(self) -> str:
        return registry.generate_copilotignore()


class GitIgnoreBuilder(IgnoreFileBuilder):
    """Generates .gitignore content."""

    @property
    def filename(self) -> str:
        return ".gitignore"

    @property
    def content(self) -> str:
        return registry.generate_gitignore()
