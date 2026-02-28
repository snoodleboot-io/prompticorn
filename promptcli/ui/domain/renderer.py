"""Renderer base class for UI components."""

from promptcli.ui.domain.context import PipelineContext


class Renderer:
    """Base class for renderers that can render pipeline context."""

    def render(self, context: PipelineContext) -> str:
        """Render the given context and return the output string."""
        raise NotImplementedError("Subclasses must implement render()")
