"""Project model for the Intermediate Representation layer.

This module defines the Project model, which represents the configuration
for a project containing agents, skills, workflows, and tools.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Literal


class Project(BaseModel):
    """Represents a project configuration.

    A project encapsulates registry settings, verbosity preferences,
    and builder configurations for a specific AI tooling setup.

    Attributes:
        registry_settings: Dictionary of registry configuration settings
        verbosity: Logging verbosity level (minimal or verbose)
        builder_configs: Dictionary of builder-specific configurations
    """

    model_config = ConfigDict(frozen=True)

    registry_settings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary of registry configuration settings",
    )
    verbosity: Literal["minimal", "verbose"] = Field(
        default="minimal",
        description="Logging verbosity level",
    )
    builder_configs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary of builder-specific configurations",
    )
