"""Loader for Workflow IR models from markdown files.

This module provides utilities for loading and parsing workflow definitions
from markdown files with YAML frontmatter.
"""

from typing import Any

from pydantic import ValidationError as PydanticValidationError

from prompticorn.ir.exceptions import ParseError, ValidationError
from prompticorn.ir.models import Workflow
from prompticorn.ir.parsers import MarkdownParser, YAMLParser


class WorkflowLoader:
    """Loader for Workflow IR models from markdown files.

    Parses workflow definition files that contain YAML frontmatter with workflow
    metadata and markdown sections with step definitions.

    Workflow file format:
        ---
        name: workflow-name
        description: One-line description
        steps:
          - Step 1
          - Step 2
        ---
        ## Steps
        Detailed step information.

    Example:
        >>> loader = WorkflowLoader()
        >>> workflow = loader.load("src/workflows/example.md")
        >>> isinstance(workflow, Workflow)
        True
        >>> workflow.name
        'example'
    """

    def __init__(self):
        """Initialize the WorkflowLoader."""
        self._yaml_parser = YAMLParser()
        self._markdown_parser = MarkdownParser()

    def parse(self, text: str, source: str = "<memory>") -> Workflow:
        """Load a workflow from a markdown file.

        Parses the YAML frontmatter to extract workflow metadata (name, description,
        steps) and validates the workflow structure.

        Args:
            text: Workflow markdown text.
            source: Label used in error messages (a unit id or path).

        Returns:
            Loaded Workflow IR model.

        Raises:
            MissingFileError: If the file does not exist.
            ParseError: If the file cannot be parsed.
            ValidationError: If the loaded data fails Workflow model validation.

        Example:
            >>> loader = WorkflowLoader()
            >>> workflow = loader.load("src/workflows/analysis.md")
            >>> len(workflow.steps) > 0
            True
        """
        try:
            # Parse YAML frontmatter for metadata
            metadata = self._yaml_parser.parse(text)

            # Build the workflow data
            workflow_data = self._build_workflow_data(metadata, source)

            # Create and validate the Workflow model
            return Workflow(**workflow_data)

        except PydanticValidationError as e:
            raise ValidationError(f"Invalid workflow definition in {source}: {str(e)}") from e
        except ParseError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to parse workflow from {source}: {str(e)}") from e

    def _build_workflow_data(self, metadata: dict[str, Any], source: str) -> dict[str, Any]:
        """Build workflow data from parsed metadata.

        Combines YAML metadata to create complete workflow data suitable
        for the Workflow model.

        Args:
            metadata: Parsed YAML frontmatter.
            source: Label for error messages.

        Returns:
            Dictionary with workflow data ready for Workflow model instantiation.

        Raises:
            ValidationError: If required fields are missing or invalid.
        """
        workflow_data = {}

        # Extract required fields from metadata
        if "name" not in metadata:
            raise ValidationError(
                f"Workflow file {source} is missing required 'name' field in frontmatter"
            )
        workflow_data["name"] = metadata["name"]

        if "description" not in metadata:
            raise ValidationError(
                f"Workflow file {source} is missing required 'description' field in frontmatter"
            )
        workflow_data["description"] = metadata["description"]

        if "steps" not in metadata:
            raise ValidationError(
                f"Workflow file {source} is missing required 'steps' field in frontmatter"
            )

        steps = metadata["steps"]

        # Validate steps is a list and non-empty
        if not isinstance(steps, list):
            raise ValidationError(
                f"Workflow file {source}: 'steps' must be a list, got {type(steps).__name__}"
            )

        if not steps:
            raise ValidationError(f"Workflow file {source}: 'steps' must contain at least one step")

        # Ensure all steps are strings
        validated_steps = []
        for i, step in enumerate(steps):
            if not isinstance(step, str):
                raise ValidationError(
                    f"Workflow file {source}: step {i} must be a string, got {type(step).__name__}"
                )
            validated_steps.append(step)

        workflow_data["steps"] = validated_steps

        return workflow_data
