"""Base class and configuration for all builders.

This module defines the Builder interface class that all tool-specific
builders must implement, as well as the BuildOptions configuration class.
"""

from dataclasses import dataclass
from typing import Any

from promptosaurus.ir.models import Agent


@dataclass
class BuildOptions:
    """Configuration options for building tool-specific output.

    Attributes:
        variant: Build variant ('minimal' for lightweight output, 'verbose' for detailed)
        agent_name: Name of the agent being built (for context in error messages)
        include_subagents: Whether to include subagents in the output
        include_skills: Whether to include skills in the output
        include_workflows: Whether to include workflows in the output
        include_rules: Whether to include rules in the output
        include_tools: Whether to include tools in the output
    """

    variant: str = "minimal"
    agent_name: str = ""
    include_subagents: bool = True
    include_skills: bool = True
    include_workflows: bool = True
    include_rules: bool = True
    include_tools: bool = True

    def __post_init__(self) -> None:
        """Validate build options after initialization."""
        if self.variant not in ("minimal", "verbose"):
            raise ValueError(f"Invalid variant: {self.variant}. Must be 'minimal' or 'verbose'")


class Builder:
    """Interface class for tool-specific builders.

    All tool-specific builders (Kilo, Claude, Cline, etc.) must inherit
    from this class and implement the interface methods. The builder is
    responsible for transforming Agent IR models into tool-specific output.

    This class defines the interface that all builders must follow,
    ensuring consistent behavior across different tool targets.
    """

    def build(
        self, agent: Agent, options: BuildOptions, config: dict | None = None
    ) -> str | dict[str, Any]:
        """Build tool-specific output from an Agent IR model.

        Args:
            agent: The Agent IR model to build from
            options: Build configuration options

        Returns:
            str or dict depending on the tool's output format.
            String for text-based formats (YAML, JSON strings, Markdown),
            dict for structured formats.

        Raises:
            BuilderValidationError: If the agent model fails validation
            BuilderException: For other builder-specific errors
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement build()")

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent IR model for this builder.

        This method should check all requirements specific to the builder's
        target tool. For example, a Kilo builder might validate that
        required fields are present, while a Cline builder might have
        different requirements.

        Args:
            agent: The Agent IR model to validate

        Returns:
            List of validation error messages. Empty list if valid.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement validate()")

    def supports_feature(self, feature_name: str) -> bool:
        """Check if this builder supports a specific feature.

        Features are optional capabilities that a builder may or may not
        support, such as 'skills', 'workflows', 'rules', 'subagents'.

        Args:
            feature_name: The name of the feature to check

        Returns:
            True if the feature is supported, False otherwise.
        """
        supported_features = {
            "skills",
            "workflows",
            "rules",
            "subagents",
            "tools",
        }
        return feature_name.lower() in supported_features

    def get_output_format(self) -> str:
        """Get a human-readable description of the output format.

        Returns:
            Description of what format this builder outputs (e.g., "YAML", "JSON", "Markdown")
        """
        return "Unknown"

    def get_tool_name(self) -> str:
        """Get the name of the tool this builder targets.

        Returns:
            The tool name (e.g., 'kilo', 'claude', 'cline')
        """
        return self.__class__.__name__.replace("Builder", "").lower()
