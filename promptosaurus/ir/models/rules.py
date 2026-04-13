"""Rules model for the Intermediate Representation layer.

This module defines the Rules model, which represents constraints and
guidelines that govern behavior across agents and workflows.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List


class Rules(BaseModel):
    """Represents rules and constraints for agent behavior.

    Rules define constraints and guidelines that govern how agents,
    skills, and workflows behave. The structure is flexible to support
    different types of rules across different use cases.

    Attributes:
        constraints: List of constraints that must be enforced
        guidelines: Dictionary of guidelines organized by category
    """

    model_config = ConfigDict(frozen=True)

    constraints: List[str] = Field(
        default_factory=list,
        description="List of constraints that must be enforced",
    )
    guidelines: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary of guidelines organized by category",
    )
