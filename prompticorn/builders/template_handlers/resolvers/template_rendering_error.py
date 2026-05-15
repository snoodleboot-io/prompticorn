from typing import Any


class TemplateRenderingError(Exception):
    """Custom exception for template rendering failures."""

    def __init__(
        self,
        message: str,
        template_content: str | None = None,
        variables: dict[str, Any] | None = None,
        original_error: Exception | None = None,
    ) -> None:
        """Initialize the template rendering error.

        Args:
            message: Error message describing what went wrong
            template_content: The template content that failed (optional)
            variables: The variables used in rendering (optional)
            original_error: The underlying Jinja2 error (optional)
        """
        super().__init__(message)
        self.template_content = template_content
        self.variables = variables or {}
        self.original_error = original_error

    def __str__(self) -> str:
        """String representation including context."""
        parts = [super().__str__()]

        if self.template_content:
            # Include truncated template content for debugging
            template_preview = self.template_content[:100]
            if len(self.template_content) > 100:
                template_preview += "..."
            parts.append(f"Template: {template_preview!r}")

        if self.variables:
            parts.append(f"Variables: {list(self.variables.keys())}")

        if self.original_error:
            parts.append(
                f"Original error: {type(self.original_error).__name__}: {self.original_error}"
            )

        return " | ".join(parts)
