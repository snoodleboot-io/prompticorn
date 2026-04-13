"""Skill model for the Intermediate Representation layer.

This module defines the Skill model, which represents a reusable capability
that can be composed into agents and workflows.
"""


from pydantic import BaseModel, ConfigDict, Field


class Skill(BaseModel):
    """Represents a reusable skill that agents can perform.

    Skills are composable capabilities that can be assigned to agents.
    Each skill has clear documentation and lists the tools it requires.

    Attributes:
        name: Unique identifier for the skill
        description: One-sentence description of what the skill does
        instructions: Detailed instructions for executing the skill
        tools_needed: List of tool names required by this skill
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(..., min_length=1, description="Unique identifier for the skill")
    description: str = Field(
        ...,
        min_length=1,
        description="One-sentence description of what the skill does",
    )
    instructions: str = Field(
        ...,
        min_length=1,
        description="Detailed instructions for executing the skill",
    )
    tools_needed: list[str] = Field(
        default_factory=list,
        description="List of tool names required by this skill",
    )
