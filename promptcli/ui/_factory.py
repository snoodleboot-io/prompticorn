"""Factory for creating UI components via sweet_tea."""

import os

from sweet_tea.abstract_factory import AbstractFactory
from sweet_tea.registry import Registry

from promptcli.ui.domain.context import PipelineContext
from promptcli.ui.render.columns import ColumnLayoutRenderer
from promptcli.ui.render.explain import ExplainRenderer
from promptcli.ui.render.renderer import Renderer
from promptcli.ui.render.vertical import VerticalLayoutRenderer

# Register renderers with snake_case keys for sweet_tea factory
Registry.register("column_layout_renderer", ColumnLayoutRenderer, library="promptcli")
Registry.register("vertical_layout_renderer", VerticalLayoutRenderer, library="promptcli")
Registry.register("explain_renderer", ExplainRenderer, library="promptcli")


class UIFactory:
    """Factory for creating UI components via sweet_tea."""

    @staticmethod
    def create_input_provider():
        """Create appropriate input provider for current platform."""
        from promptcli.ui.input.fallback import FallbackInputProvider
        from promptcli.ui.input.unix import UnixInputProvider
        from promptcli.ui.input.windows import WindowsInputProvider

        try:
            if os.name == "nt":
                return WindowsInputProvider()
            else:
                return UnixInputProvider()
        except Exception:
            return FallbackInputProvider()

    @staticmethod
    def create_renderer(context: PipelineContext) -> Renderer:
        """Create appropriate renderer based on context."""
        factory = AbstractFactory[Renderer]

        if context.mode == "explain":
            return factory.create("explain_renderer")

        # Choose layout based on option count
        if len(context.display_options) > 8:
            return factory.create("column_layout_renderer")
        return factory.create("vertical_layout_renderer")
