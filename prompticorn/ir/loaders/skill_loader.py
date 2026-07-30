"""Loader for Skill IR models from markdown files.

This module provides utilities for loading and parsing skill definitions
from markdown files with YAML frontmatter.
"""

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from prompticorn.ir.exceptions import ParseError, ValidationError
from prompticorn.ir.models import Skill
from prompticorn.ir.parsers import MarkdownParser, YAMLParser


class SkillLoader:
    """Loader for Skill IR models from markdown files.

    Parses skill definition files that contain YAML frontmatter with skill
    metadata and markdown sections with detailed instructions.

    Skill file format:
        ---
        name: skill-name
        description: One-line description
        tools_needed: [tool1, tool2]
        ---
        ## Instructions
        Detailed instructions here.

    Example:
        >>> loader = SkillLoader()
        >>> skill = loader.load("src/skills/example.md")
        >>> isinstance(skill, Skill)
        True
        >>> skill.name
        'example'
    """

    def __init__(self):
        """Initialize the SkillLoader."""
        self._yaml_parser = YAMLParser()
        self._markdown_parser = MarkdownParser()

    def parse(self, text: str, source: str = "<memory>") -> Skill:
        """Load a skill from a markdown file.

        Parses the YAML frontmatter to extract skill metadata (name, description,
        tools_needed) and the markdown sections to extract detailed instructions.

        Args:
            text: Skill markdown text.
            source: Label used in error messages (a unit id or path).

        Returns:
            Loaded Skill IR model.

        Raises:
            MissingFileError: If the file does not exist.
            ParseError: If the file cannot be parsed.
            ValidationError: If the loaded data fails Skill model validation.

        Example:
            >>> loader = SkillLoader()
            >>> skill = loader.load("src/skills/analysis.md")
            >>> skill.instructions
            'Perform detailed analysis...'
        """
        try:
            # Parse YAML frontmatter for metadata
            metadata = self._yaml_parser.parse(text)

            # Parse markdown sections for instructions
            sections = self._markdown_parser.parse(text)

            # Build the skill data
            skill_data = self._build_skill_data(metadata, sections, source)

            # Create and validate the Skill model
            return Skill(**skill_data)

        except PydanticValidationError as e:
            raise ValidationError(f"Invalid skill definition in {source}: {str(e)}") from e
        except ParseError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to parse skill from {source}: {str(e)}") from e

    def _build_skill_data(
        self, metadata: dict[str, Any], sections: dict[str, str], file_path: str
    ) -> dict[str, Any]:
        """Build skill data from parsed metadata and sections.

        Combines YAML metadata with markdown sections to create complete skill
        data suitable for the Skill model.

        Args:
            metadata: Parsed YAML frontmatter.
            sections: Parsed markdown sections.
            file_path: Path to the skill file (for error messages).

        Returns:
            Dictionary with skill data ready for Skill model instantiation.

        Raises:
            ValidationError: If required fields are missing or invalid.
        """
        skill_data = {}

        # Extract required fields from metadata
        if "name" not in metadata:
            raise ValidationError(
                f"Skill file {file_path} is missing required 'name' field in frontmatter"
            )
        skill_data["name"] = metadata["name"]

        if "description" not in metadata:
            raise ValidationError(
                f"Skill file {file_path} is missing required 'description' field in frontmatter"
            )
        skill_data["description"] = metadata["description"]

        # Get instructions from markdown sections
        if "instructions" not in sections:
            raise ValidationError(
                f"Skill file {file_path} is missing required '## Instructions' section"
            )
        skill_data["instructions"] = sections["instructions"]

        # Get optional tools_needed
        if "tools_needed" in metadata:
            tools = metadata["tools_needed"]
            # Ensure it's a list
            if isinstance(tools, str):
                tools = [tools]
            elif not isinstance(tools, list):
                raise ValidationError(
                    f"Skill file {file_path}: 'tools_needed' must be a list or string, got {type(tools).__name__}"
                )
            skill_data["tools_needed"] = tools
        else:
            skill_data["tools_needed"] = []

        return skill_data
