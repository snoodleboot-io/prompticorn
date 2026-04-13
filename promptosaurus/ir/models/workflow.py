"""Workflow model for the Intermediate Representation layer.

This module defines the Workflow model, which represents a sequence of
steps that an agent can execute in a defined order.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List


class Workflow(BaseModel):
    """Represents a workflow as a sequence of steps.

    Workflows define a series of steps that an agent can execute
    in a defined order. Each step is a string describing an action.

    Attributes:
        name: Unique identifier for the workflow
        description: One-sentence description of the workflow's purpose
        steps: List of step descriptions (non-empty)
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1, description="Unique identifier for the workflow")
    description: str = Field(
        ...,
        min_length=1,
        description="One-sentence description of the workflow's purpose",
    )
    steps: List[str] = Field(..., description="List of steps in the workflow (must be non-empty)")

    @field_validator("steps")
    @classmethod
    def validate_steps(cls, v: List[str]) -> List[str]:
        """Ensure steps list is non-empty."""
        if not v:
            raise ValueError("Workflow must have at least one step")
        return v
