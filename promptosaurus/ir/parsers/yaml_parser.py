"""YAML parser for extracting frontmatter from markdown files.

This module provides utilities for parsing YAML frontmatter (---\nYAML\n---)
from markdown files and returning structured dictionaries.
"""

import re
from typing import Any

import yaml

from promptosaurus.ir.exceptions import ParseError


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

    def parse(self, content: str) -> dict[str, Any]:
        """Parse YAML frontmatter from markdown content.

        Extracts the YAML content between the first set of --- delimiters
        and returns it as a dictionary. Also extracts the markdown body
        after the closing --- and adds it as 'system_prompt' key if present.

        Args:
            content: The markdown content with optional YAML frontmatter.

        Returns:
            Dictionary containing the parsed YAML data and system_prompt body
            (if present and not already in frontmatter).

        Raises:
            ParseError: If the content is not valid YAML or frontmatter
                       extraction fails.

        Example:
            >>> parser = YAMLParser()
            >>> yaml_content = "name: my-skill\\ndescription: Does something"
            >>> result = parser.parse(f"---\\n{yaml_content}\\n---\\nBody content")
            >>> result['name']
            'my-skill'
            >>> result['system_prompt']
            'Body content'
        """
        try:
            # Pattern to match YAML frontmatter and body:
            # --- at start, YAML content, then ---, then optional body content
            pattern = r"^---\s*\n(.*?)\n---\s*(?:\n(.*))?$"
            match = re.match(pattern, content, re.DOTALL)

            if not match:
                # No frontmatter found - return empty dict
                return {}

            yaml_content = match.group(1)
            body_content = match.group(2)

            # Parse the YAML content
            parsed = yaml.safe_load(yaml_content)

            # Ensure we return a dict
            if parsed is None:
                parsed = {}

            if not isinstance(parsed, dict):
                raise ParseError(
                    f"YAML frontmatter must be a dictionary, got {type(parsed).__name__}"
                )

            # Add body content as system_prompt if present and not already set
            if body_content and body_content.strip():
                if "system_prompt" not in parsed:
                    parsed["system_prompt"] = body_content.strip()

            return parsed

        except yaml.YAMLError as e:
            raise ParseError(f"Invalid YAML in frontmatter: {str(e)}") from e
        except Exception as e:
            raise ParseError(f"Failed to parse YAML frontmatter: {str(e)}") from e

    def parse_file(self, file_path: str) -> dict[str, Any]:
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
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
            return self.parse(content)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to parse file {file_path}: {str(e)}") from e
