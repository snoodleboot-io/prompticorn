"""Custom exceptions for the builders module.

This module defines a hierarchy of exceptions specific to builder operations,
enabling clear error handling and diagnostics.
"""


class BuilderException(Exception):
    """Base exception for all builder-related errors."""

    pass


class BuilderNotFoundError(BuilderException):
    """Raised when a builder cannot be found for a specified tool.

    Attributes:
        tool_name: The tool name for which no builder was registered
        message: The error message
    """

    def __init__(self, tool_name: str, message: str | None = None) -> None:
        """Initialize BuilderNotFoundError.

        Args:
            tool_name: The tool name for which no builder was found
            message: Optional custom error message
        """
        self.tool_name = tool_name
        if message is None:
            message = f"No builder registered for tool: '{tool_name}'"
        super().__init__(message)


class BuilderValidationError(BuilderException):
    """Raised when an Agent IR model fails validation.

    Attributes:
        errors: List of validation error messages
        message: The error message
    """

    def __init__(self, errors: list[str], message: str | None = None) -> None:
        """Initialize BuilderValidationError.

        Args:
            errors: List of validation error messages
            message: Optional custom error message
        """
        self.errors = errors
        if message is None:
            error_list = "\n  - ".join(errors)
            message = f"Agent IR model validation failed:\n  - {error_list}"
        super().__init__(message)


class UnsupportedFeatureError(BuilderException):
    """Raised when a builder does not support a requested feature.

    Attributes:
        builder_name: The name/type of the builder
        feature_name: The unsupported feature name
        message: The error message
    """

    def __init__(self, builder_name: str, feature_name: str, message: str | None = None) -> None:
        """Initialize UnsupportedFeatureError.

        Args:
            builder_name: The name/type of the builder
            feature_name: The unsupported feature name
            message: Optional custom error message
        """
        self.builder_name = builder_name
        self.feature_name = feature_name
        if message is None:
            message = f"Builder '{builder_name}' does not support feature: '{feature_name}'"
        super().__init__(message)


class ComponentNotFoundError(BuilderException):
    """Raised when a required component file cannot be found.

    Attributes:
        component_name: The name of the component (e.g., 'prompt.md')
        path: The path where the component was expected
        message: The error message
    """

    def __init__(self, component_name: str, path: str, message: str | None = None) -> None:
        """Initialize ComponentNotFoundError.

        Args:
            component_name: Name of the component (e.g., 'prompt.md')
            path: Path where component was expected
            message: Optional custom error message
        """
        self.component_name = component_name
        self.path = path
        if message is None:
            message = f"Component '{component_name}' not found at {path}"
        super().__init__(message)


class VariantNotFoundError(BuilderException):
    """Raised when a requested variant cannot be found for an agent.

    Attributes:
        agent_name: The name of the agent
        variant: The requested variant
        message: The error message
    """

    def __init__(self, agent_name: str, variant: str, message: str | None = None) -> None:
        """Initialize VariantNotFoundError.

        Args:
            agent_name: Name of the agent
            variant: The requested variant (e.g., 'minimal')
            message: Optional custom error message
        """
        self.agent_name = agent_name
        self.variant = variant
        if message is None:
            message = f"Variant '{variant}' not found for agent '{agent_name}'"
        super().__init__(message)
