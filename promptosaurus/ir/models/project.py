"""Project model for the Intermediate Representation layer.

This module defines the Project model, which represents the configuration
for a project containing agents, skills, workflows, and tools.
"""

from typing import Any, Literal

from pydantic import BaseModel, Field


class Project(BaseModel):
    """Represents a project configuration.

    A project encapsulates registry settings, verbosity preferences,
    and builder configurations for a specific AI tooling setup.

    Attributes:
        registry_settings: Dictionary of registry configuration settings
        verbosity: Logging verbosity level (minimal or verbose)
        builder_configs: Dictionary of builder-specific configurations
    """

    registry_settings: dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary of registry configuration settings",
    )
    verbosity: Literal["minimal", "verbose"] = Field(
        default="minimal",
        description="Logging verbosity level",
    )
    builder_configs: dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary of builder-specific configurations",
    )

    class Config:
        """Pydantic configuration for the Project model."""

        frozen = True
