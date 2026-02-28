"""Renderer base class for UI components."""

from promptcli.ui.domain.renderer import Renderer as DomainRenderer


class Renderer(DomainRenderer):
    """Base class for renderers that can render pipeline context.

    This class extends the domain Renderer for use in the render module.
    All renderers should inherit from this class.
    """
