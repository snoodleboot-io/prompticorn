"""Interface and implementations for generating ignore files.

This module provides builder classes for generating various ignore files
used by different AI assistant tools. Each builder creates a tool-specific
ignore file that prevents the AI from processing certain files.

Uses interface pattern (NotImplementedError) per core-conventions -
no ABC, just raise NotImplementedError for required methods.

Classes:
    IgnoreFileBuilder: Abstract base interface for ignore file builders.
    KiloIgnoreBuilder: Generates .kiloignore content for Kilo Code.
    ClineIgnoreBuilder: Generates .clineignore content for Cline.
    CursorIgnoreBuilder: Generates .cursorignore content for Cursor.
    CopilotIgnoreBuilder: Generates .copilotignore content for GitHub Copilot.
    GitIgnoreBuilder: Generates .gitignore content.

Example:
    >>> from promptosaurus.builders.ignore_generator import KiloIgnoreBuilder
    >>> builder = KiloIgnoreBuilder()
    >>> print(builder.filename)
    .kiloignore
"""

from pathlib import Path

from promptosaurus.registry import registry


class IgnoreFileBuilder:
    """Interface for ignore file builders.

    This abstract class defines the interface for generating tool-specific
    ignore files. Subclasses must implement the filename and content properties.

    Uses interface pattern (NotImplementedError) per conventions -
    no ABC, just raise NotImplementedError for required methods.

    Attributes:
        filename: Property that returns the ignore filename.
        content: Property that returns the ignore file content.

    Methods:
        build: Generate and write the ignore file.

    Example:
        >>> class MyIgnoreBuilder(IgnoreFileBuilder):
        ...     @property
        ...     def filename(self) -> str:
        ...         return ".myignore"
        ...     @property
        ...     def content(self) -> str:
        ...         return "*.log\\n"
    """

    @property
    def filename(self) -> str:
        """Filename for the ignore file (e.g., '.kiloignore').

        Returns:
            The filename string including the leading dot.

        Raises:
            NotImplementedError: If subclass doesn't implement this property.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement filename")

    @property
    def content(self) -> str:
        """Content for the ignore file.

        Returns:
            The complete ignore file content as a string.

        Raises:
            NotImplementedError: If subclass doesn't implement this property.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement content")

    def build(self, output: Path, dry_run: bool = False) -> list[str]:
        """Build the ignore file.

        Generates the ignore file in the specified output directory.

        Args:
            output: Output directory path where the ignore file will be created.
            dry_run: If True, return preview string without writing to filesystem.

        Returns:
            List containing a single action string describing the operation.

        Raises:
            FileExistsError: If the file already exists and cannot be overwritten.

        Example:
            >>> from pathlib import Path
            >>> from promptosaurus.builders.ignore_generator import KiloIgnoreBuilder
            >>> builder = KiloIgnoreBuilder()
            >>> actions = builder.build(Path("./output"))
            >>> print(actions)
            ['✓ .kiloignore (42 lines)']
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
    """Generates .kiloignore content for Kilo Code.

    This builder creates the ignore file that tells Kilo Code which files
    to exclude from processing. Content is generated from the registry.

    Example:
        >>> builder = KiloIgnoreBuilder()
        >>> print(builder.filename)
        .kiloignore
    """

    @property
    def filename(self) -> str:
        return ".kiloignore"

    @property
    def content(self) -> str:
        return registry.generate_kiloignore()


class ClineIgnoreBuilder(IgnoreFileBuilder):
    """Generates .clineignore content for Cline.

    This builder creates the ignore file that tells Cline which files
    to exclude from processing. Content is generated from the registry.

    Example:
        >>> builder = ClineIgnoreBuilder()
        >>> print(builder.filename)
        .clineignore
    """

    @property
    def filename(self) -> str:
        return ".clineignore"

    @property
    def content(self) -> str:
        return registry.generate_clineignore()


class CursorIgnoreBuilder(IgnoreFileBuilder):
    """Generates .cursorignore content for Cursor.

    This builder creates the ignore file that tells Cursor which files
    to exclude from processing. Content is generated from the registry.

    Example:
        >>> builder = CursorIgnoreBuilder()
        >>> print(builder.filename)
        .cursorignore
    """

    @property
    def filename(self) -> str:
        return ".cursorignore"

    @property
    def content(self) -> str:
        return registry.generate_cursorignore()


class CopilotIgnoreBuilder(IgnoreFileBuilder):
    """Generates .copilotignore content for GitHub Copilot.

    This builder creates the ignore file that tells GitHub Copilot which files
    to exclude from processing. Content is generated from the registry.

    Example:
        >>> builder = CopilotIgnoreBuilder()
        >>> print(builder.filename)
        .copilotignore
    """

    @property
    def filename(self) -> str:
        return ".copilotignore"

    @property
    def content(self) -> str:
        return registry.generate_copilotignore()


class GitIgnoreBuilder(IgnoreFileBuilder):
    """Generates .gitignore content.

    This builder creates a standard .gitignore file with common ignore patterns
    for Python projects. Content is generated from the registry.

    Example:
        >>> builder = GitIgnoreBuilder()
        >>> print(builder.filename)
        .gitignore
    """

    @property
    def filename(self) -> str:
        return ".gitignore"

    @property
    def content(self) -> str:
        return registry.generate_gitignore()
