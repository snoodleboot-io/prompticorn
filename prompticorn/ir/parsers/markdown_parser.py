"""Markdown parser for extracting sections by header.

This module provides utilities for parsing markdown files and extracting
content organized by headers (## Section Name format).
"""

import re

from prompticorn.ir.exceptions import ParseError


class MarkdownParser:
    """Parser for extracting markdown sections by header.

    Extracts sections from markdown content organized by headers (## Header Name).
    Returns a dictionary mapping section names to their content.

    Example:
        >>> parser = MarkdownParser()
        >>> content = '''## Section 1
        ... Content here
        ... ## Section 2
        ... More content
        ... '''
        >>> sections = parser.parse(content)
        >>> 'section_1' in sections
        True
    """

    def parse(self, content: str) -> dict[str, str]:
        """Parse markdown sections by header.

        Extracts all ## header sections from markdown content and returns
        them as a dictionary where keys are normalized header names
        (lowercase, underscores replacing spaces).

        Args:
            content: The markdown content to parse.

        Returns:
            Dictionary mapping section names to section content.
            Section names are normalized (lowercase, spaces -> underscores).

        Raises:
            ParseError: If parsing fails.

        Example:
            >>> parser = MarkdownParser()
            >>> content = '''## Overview
            ... This is the overview.
            ... ## Instructions
            ... Do this then that.
            ... '''
            >>> sections = parser.parse(content)
            >>> sections['overview']
            'This is the overview.'
        """
        try:
            sections = {}

            # Pattern to match ## Header lines
            # Captures header name and everything until the next ## or end of string
            pattern = r"^##\s+(.+?)$\n(.*?)(?=^##\s|\Z)"
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)

            for match in matches:
                header_name = match.group(1).strip()
                section_content = match.group(2).strip()

                # Normalize header name: lowercase, spaces -> underscores
                normalized_name = self._normalize_header(header_name)

                sections[normalized_name] = section_content

            return sections

        except Exception as e:
            raise ParseError(f"Failed to parse markdown sections: {str(e)}") from e

    def parse_file(self, file_path: str) -> dict[str, str]:
        """Parse markdown sections from a file.

        Args:
            file_path: Path to the markdown file.

        Returns:
            Dictionary mapping section names to section content.

        Raises:
            ParseError: If the file cannot be read or parsing fails.
            FileNotFoundError: If the file does not exist.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            return self.parse(content)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to parse file {file_path}: {str(e)}") from e

    @staticmethod
    def _normalize_header(header: str) -> str:
        """Normalize a header name for use as a dictionary key.

        Converts to lowercase and replaces spaces with underscores.

        Args:
            header: The header text to normalize.

        Returns:
            Normalized header name (lowercase, spaces as underscores).
        """
        # Remove leading/trailing whitespace
        header = header.strip()
        # Convert to lowercase
        header = header.lower()
        # Replace spaces with underscores
        header = re.sub(r"\s+", "_", header)
        # Remove special characters except underscores
        header = re.sub(r"[^a-z0-9_]", "", header)
        # Remove multiple consecutive underscores
        header = re.sub(r"_+", "_", header)
        return header
