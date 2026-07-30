"""Loader for loading complete component bundles from directories.

This module provides utilities for loading a complete set of component files
(prompt.md, skills.md, workflow.md) supplied as text by a content source.
"""

from typing import Any, NamedTuple

from prompticorn.ir.exceptions import ParseError
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

    def parse(
        self,
        prompt_text: str,
        skills_text: str | None = None,
        workflow_text: str | None = None,
        source: str = "<memory>",
    ) -> ComponentBundle:
        """Parse component text into a bundle.

        Text in, model out. Fetching bytes is a source's job — this loader used
        to open ``prompt.md``/``skills.md``/``workflow.md`` itself, which meant a
        source abstraction above it changed nothing. (PRO-105)

        Args:
            prompt_text: Required prompt document text.
            skills_text: Optional skills document text.
            workflow_text: Optional workflow document text.
            source: Label used in error messages (a unit id or path).

        Returns:
            ComponentBundle containing parsed component content.

        Raises:
            ParseError: If parsing any document fails.
        """
        try:
            return ComponentBundle(
                prompt_content=self._parse_text(prompt_text),
                skills_content=self._parse_text(skills_text) if skills_text is not None else None,
                workflow_content=(
                    self._parse_text(workflow_text) if workflow_text is not None else None
                ),
            )
        except Exception as e:
            raise ParseError(f"Failed to parse components from {source}: {str(e)}") from e

    def as_dict(self, bundle: ComponentBundle) -> dict[str, Any]:
        """Flatten a bundle to ``{'prompt', 'skills', 'workflow'}``.

        Optional keys are absent when the corresponding document was not
        supplied, matching the previous ``load_as_dict`` shape.
        """
        result: dict[str, Any] = {"prompt": bundle.prompt_content}
        if bundle.skills_content is not None:
            result["skills"] = bundle.skills_content
        if bundle.workflow_content is not None:
            result["workflow"] = bundle.workflow_content
        return result

    def _parse_text(self, content: str) -> dict[str, Any]:
        """Parse one component document.

        Tries YAML parsing first, then falls back to markdown parsing.

        Args:
            content: Document text.

        Returns:
            Dictionary containing parsed content.

        Raises:
            ParseError: If parsing fails.
        """
        try:
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
            raise ParseError(f"Failed to parse component document: {str(e)}") from e
