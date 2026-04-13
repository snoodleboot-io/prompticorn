"""Loader for Workflow IR models from markdown files.

This module provides utilities for loading and parsing workflow definitions
from markdown files with YAML frontmatter.
"""

from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from promptosaurus.ir.exceptions import MissingFileError, ParseError, ValidationError
from promptosaurus.ir.models import Workflow
from promptosaurus.ir.parsers import MarkdownParser, YAMLParser


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

    def load(self, file_path: str) -> Workflow:
        """Load a workflow from a markdown file.

        Parses the YAML frontmatter to extract workflow metadata (name, description,
        steps) and validates the workflow structure.

        Args:
            file_path: Path to the workflow markdown file.

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
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise MissingFileError(f"Workflow file not found: {file_path}")

        try:
            # Read the file content
            with open(file_path_obj, encoding="utf-8") as f:
                content = f.read()

            # Parse YAML frontmatter for metadata
            metadata = self._yaml_parser.parse(content)

            # Build the workflow data
            workflow_data = self._build_workflow_data(metadata, file_path)

            # Create and validate the Workflow model
            return Workflow(**workflow_data)

        except MissingFileError:
            raise
        except PydanticValidationError as e:
            raise ValidationError(f"Invalid workflow definition in {file_path}: {str(e)}") from e
        except ParseError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            raise ParseError(f"Failed to load workflow from {file_path}: {str(e)}") from e

    def _build_workflow_data(self, metadata: dict[str, Any], file_path: str) -> dict[str, Any]:
        """Build workflow data from parsed metadata.

        Combines YAML metadata to create complete workflow data suitable
        for the Workflow model.

        Args:
            metadata: Parsed YAML frontmatter.
            file_path: Path to the workflow file (for error messages).

        Returns:
            Dictionary with workflow data ready for Workflow model instantiation.

        Raises:
            ValidationError: If required fields are missing or invalid.
        """
        workflow_data = {}

        # Extract required fields from metadata
        if "name" not in metadata:
            raise ValidationError(
                f"Workflow file {file_path} is missing required 'name' field in frontmatter"
            )
        workflow_data["name"] = metadata["name"]

        if "description" not in metadata:
            raise ValidationError(
                f"Workflow file {file_path} is missing required 'description' field in frontmatter"
            )
        workflow_data["description"] = metadata["description"]

        if "steps" not in metadata:
            raise ValidationError(
                f"Workflow file {file_path} is missing required 'steps' field in frontmatter"
            )

        steps = metadata["steps"]

        # Validate steps is a list and non-empty
        if not isinstance(steps, list):
            raise ValidationError(
                f"Workflow file {file_path}: 'steps' must be a list, got {type(steps).__name__}"
            )

        if not steps:
            raise ValidationError(
                f"Workflow file {file_path}: 'steps' must contain at least one step"
            )

        # Ensure all steps are strings
        validated_steps = []
        for i, step in enumerate(steps):
            if not isinstance(step, str):
                raise ValidationError(
                    f"Workflow file {file_path}: step {i} must be a string, got {type(step).__name__}"
                )
            validated_steps.append(step)

        workflow_data["steps"] = validated_steps

        return workflow_data
