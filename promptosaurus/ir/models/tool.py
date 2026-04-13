"""Tool model for the Intermediate Representation layer.

This module defines the Tool model, which represents a capability that
agents can invoke to perform actions.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Tool(BaseModel):
    """Represents a tool that agents can invoke.

    Tools are capabilities that agents can use to perform actions.
    Each tool has a JSON schema that describes its parameters.

    Attributes:
        name: Unique identifier for the tool
        description: One-sentence description of what the tool does
        parameters: JSON schema describing the tool's parameters
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1, description="Unique identifier for the tool")
    description: str = Field(
        ...,
        min_length=1,
        description="One-sentence description of what the tool does",
    )
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema describing the tool's parameters",
    )
