"""Renderer base class for UI components.

This module defines the abstract interface for renderers,
which handle displaying the UI to the user.

Classes:
    Renderer: Abstract base class for renderers.

Example:
    >>> from promptosaurus.ui.domain.renderer import Renderer
    >>> from promptosaurus.ui.domain.context import PipelineContext
    >>>
    >>> # Implement a custom renderer
    >>> class MyRenderer(Renderer):
    ...     def render(self, context: PipelineContext) -> str:
    ...         return "Custom output"
"""

from promptosaurus.ui.domain.context import PipelineContext


class Renderer:
    """Base class for renderers that can render pipeline context.

    Renderers handle the presentation layer of the UI pipeline.
    They take a PipelineContext and return a string representation
    of the current state to display to the user.

    Different renderer implementations can provide different layouts:
    - VerticalLayoutRenderer: Simple vertical list
    - ColumnLayoutRenderer: Multi-column for many options
    - ExplainRenderer: Detailed explanation view

    Methods:
        render: Render the given context and return the output string.

    Example:
        >>> from promptosaurus.ui.render.vertical import VerticalLayoutRenderer
        >>> renderer = VerticalLayoutRenderer()
        >>> # Would render context to string
    """

    def render(self, context: PipelineContext) -> str:
        """Render the given context and return the output string.

        Args:
            context: The PipelineContext containing current state.

        Returns:
            String representation of the UI to display.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError("Subclasses must implement render()")
