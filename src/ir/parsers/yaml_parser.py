"""YAML parser for extracting frontmatter from markdown files.

This module provides utilities for parsing YAML frontmatter (---\nYAML\n---)
from markdown files and returning structured dictionaries.
"""

import re
from typing import Dict, Any

import yaml

from src.ir.exceptions import ParseError


class YAMLParser:
    """Parser for YAML frontmatter in markdown files.

    Extracts YAML content from markdown files that start with YAML frontmatter
    enclosed in --- delimiters (standard markdown frontmatter format).

    Example:
        >>> parser = YAMLParser()
        >>> content = '''---
        ... name: example
        ... description: An example
        ... ---
        ... # Markdown content
        ... '''
        >>> data = parser.parse(content)
        >>> data['name']
        'example'
    """

    def parse(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown content.

        Extracts the YAML content between the first set of --- delimiters
        and returns it as a dictionary.

        Args:
            content: The markdown content with optional YAML frontmatter.

        Returns:
            Dictionary containing the parsed YAML data.

        Raises:
            ParseError: If the content is not valid YAML or frontmatter
                       extraction fails.

        Example:
            >>> parser = YAMLParser()
            >>> yaml_content = "name: my-skill\\ndescription: Does something"
            >>> result = parser.parse(f"---\\n{yaml_content}\\n---\\n")
            >>> result == {'name': 'my-skill', 'description': 'Does something'}
            True
        """
        try:
            # Pattern to match YAML frontmatter: --- at start, then YAML, then ---
            pattern = r"^---\s*\n(.*?)\n---\s*\n"
            match = re.match(pattern, content, re.DOTALL)

            if not match:
                # No frontmatter found - return empty dict
                return {}

            yaml_content = match.group(1)

            # Parse the YAML content
            parsed = yaml.safe_load(yaml_content)

            # Ensure we return a dict
            if parsed is None:
                return {}

            if not isinstance(parsed, dict):
                raise ParseError(
                    f"YAML frontmatter must be a dictionary, got {type(parsed).__name__}"
                )

            return parsed

        except yaml.YAMLError as e:
            raise ParseError(f"Invalid YAML in frontmatter: {str(e)}") from e
        except Exception as e:
            raise ParseError(f"Failed to parse YAML frontmatter: {str(e)}") from e

    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from a file.

        Args:
            file_path: Path to the markdown file.

        Returns:
            Dictionary containing the parsed YAML data.

        Raises:
            ParseError: If the file cannot be read or YAML is invalid.
            FileNotFoundError: If the file does not exist.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            return self.parse(content)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to parse file {file_path}: {str(e)}") from e
