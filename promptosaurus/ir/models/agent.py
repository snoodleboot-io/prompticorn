"""Agent model for the Intermediate Representation layer.

This module defines the Agent model, which represents a tool-agnostic agent
configuration that can be used across different AI tools and frameworks.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Agent(BaseModel):
    """Represents a tool-agnostic agent configuration.

    An agent encapsulates a complete AI entity with its configuration,
    capabilities (tools and skills), and behavioral patterns (workflows).
    Agents can contain subagents for hierarchical composition.

    Attributes:
        name: Unique identifier for the agent (e.g., 'code', 'architect')
        description: One-sentence description of the agent's purpose
        mode: Agent mode - 'primary' (user-selectable), 'subagent' (delegable only), or 'all' (both)
        system_prompt: The system prompt that defines the agent's behavior
        tools: List of tool names this agent can use
        skills: List of skill names this agent can perform
        workflows: List of workflow names this agent can execute
        subagents: List of subagent names for hierarchical composition
        permissions: Permission rules for the agent (tool-specific)
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the agent (e.g., 'code', 'architect')",
    )
    description: str = Field(
        ..., min_length=1, description="One-sentence description of agent's purpose"
    )
    mode: str = Field(
        default="all",
        description="Agent mode: 'primary' (user-selectable), 'subagent' (delegable only), or 'all' (both)",
    )
    system_prompt: str = Field(
        ..., min_length=1, description="System prompt defining agent behavior"
    )
    tools: list[str] = Field(
        default_factory=list, description="List of tool names this agent can use"
    )
    skills: list[str] = Field(
        default_factory=list, description="List of skill names this agent can perform"
    )
    workflows: list[str] = Field(
        default_factory=list, description="List of workflow names this agent can execute"
    )
    subagents: list[str] = Field(
        default_factory=list, description="List of subagent names for composition"
    )
    permissions: dict[str, Any] | None = Field(
        default=None, description="Permission rules for the agent (tool-specific)"
    )
