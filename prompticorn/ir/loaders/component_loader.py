"""Loader for loading complete component bundles from directories.

This module provides utilities for loading a complete set of component files
(prompt.md, skills.md, workflow.md) from a directory.
"""

from pathlib import Path
from typing import Any, NamedTuple

from prompticorn.ir.exceptions import MissingFileError, ParseError
from prompticorn.ir.parsers import MarkdownParser, YAMLParser


class ComponentBundle(NamedTuple):
    """A bundle of loaded components from a directory.

    Attributes:
        prompt_content: Content of prompt.md
        skills_content: Content of skills.md (optional)
        workflow_content: Content of workflow.md (optional)
    """

    prompt_content: dict[str, Any]
    skills_content: dict[str, Any] | None = None
    workflow_content: dict[str, Any] | None = None


class ComponentLoader:
    """Loader for loading complete component bundles from directories.

    Loads a set of component files from a directory:
    - prompt.md (required)
    - skills.md (optional)
    - workflow.md (optional)

    Returns the loaded content as a ComponentBundle or dictionary.

    Example:
        >>> loader = ComponentLoader()
        >>> bundle = loader.load("src/prompts/my-agent/")
        >>> isinstance(bundle, ComponentBundle)
        True
        >>> bundle.prompt_content is not None
        True
    """

    def __init__(self):
        """Initialize the ComponentLoader."""
        self._yaml_parser = YAMLParser()
        self._markdown_parser = MarkdownParser()

    def load(self, directory: str) -> ComponentBundle:
        """Load all component files from a directory.

        Loads the required prompt.md file and optional skills.md and workflow.md
        files from the specified directory.

        Args:
            directory: Path to the directory containing component files.

        Returns:
            ComponentBundle containing loaded component content.

        Raises:
            MissingFileError: If the required prompt.md file is not found.
            ParseError: If parsing any file fails.

        Example:
            >>> loader = ComponentLoader()
            >>> bundle = loader.load("src/prompts/analyzer/")
            >>> 'name' in bundle.prompt_content
            True
        """
        dir_path = Path(directory)

        if not dir_path.is_dir():
            raise MissingFileError(f"Directory not found: {directory}")

        try:
            # Load required prompt.md
            prompt_file = dir_path / "prompt.md"
            if not prompt_file.exists():
                raise MissingFileError(f"Required file 'prompt.md' not found in {directory}")

            prompt_content = self._load_file(prompt_file)

            # Load optional skills.md
            skills_file = dir_path / "skills.md"
            skills_content = None
            if skills_file.exists():
                skills_content = self._load_file(skills_file)

            # Load optional workflow.md
            workflow_file = dir_path / "workflow.md"
            workflow_content = None
            if workflow_file.exists():
                workflow_content = self._load_file(workflow_file)

            return ComponentBundle(
                prompt_content=prompt_content,
                skills_content=skills_content,
                workflow_content=workflow_content,
            )

        except MissingFileError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to load components from {directory}: {str(e)}") from e

    def load_as_dict(self, directory: str) -> dict[str, Any]:
        """Load all component files as a flat dictionary.

        Loads all component files and returns them as a single dictionary
        with keys: 'prompt', 'skills', 'workflow'.

        Args:
            directory: Path to the directory containing component files.

        Returns:
            Dictionary with keys 'prompt', 'skills', 'workflow' (optional keys
            may be absent if files don't exist).

        Raises:
            MissingFileError: If the required prompt.md file is not found.
            ParseError: If parsing any file fails.

        Example:
            >>> loader = ComponentLoader()
            >>> components = loader.load_as_dict("src/prompts/agent/")
            >>> 'prompt' in components
            True
        """
        bundle = self.load(directory)

        result = {
            "prompt": bundle.prompt_content,
        }

        if bundle.skills_content is not None:
            result["skills"] = bundle.skills_content

        if bundle.workflow_content is not None:
            result["workflow"] = bundle.workflow_content

        return result

    def _load_file(self, file_path: Path) -> dict[str, Any]:
        """Load and parse a single component file.

        Tries YAML parsing first, then falls back to markdown parsing.

        Args:
            file_path: Path to the file to load.

        Returns:
            Dictionary containing parsed content.

        Raises:
            ParseError: If parsing fails.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Try YAML parsing first (for files with frontmatter)
            yaml_data = self._yaml_parser.parse(content)
            if yaml_data:
                return yaml_data

            # Fall back to markdown section parsing
            sections = self._markdown_parser.parse(content)
            if sections:
                return sections

            # Return raw content if neither worked
            return {"content": content}

        except Exception as e:
            raise ParseError(f"Failed to load file {file_path}: {str(e)}") from e
