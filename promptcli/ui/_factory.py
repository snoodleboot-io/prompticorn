"""Factory for creating UI components via sweet_tea."""

import os

from sweet_tea.abstract_factory import AbstractFactory
from sweet_tea.registry import Registry

from promptcli.ui.domain.context import PipelineContext
from promptcli.ui.domain.input_provider import InputProvider
from promptcli.ui.domain.renderer import Renderer
from promptcli.ui.input.fallback import FallbackInputProvider
from promptcli.ui.input.unix import UnixInputProvider
from promptcli.ui.input.windows import WindowsInputProvider
from promptcli.ui.render.columns import ColumnLayoutRenderer
from promptcli.ui.render.explain import ExplainRenderer
from promptcli.ui.render.vertical import VerticalLayoutRenderer

# Register input providers with snake_case keys for sweet_tea factory
Registry.register("windows_input", WindowsInputProvider, library="promptcli")
Registry.register("unix_input", UnixInputProvider, library="promptcli")
Registry.register("fallback_input", FallbackInputProvider, library="promptcli")

# Register renderers with snake_case keys for sweet_tea factory
Registry.register("column_layout_renderer", ColumnLayoutRenderer, library="promptcli")
Registry.register("vertical_layout_renderer", VerticalLayoutRenderer, library="promptcli")
Registry.register("explain_renderer", ExplainRenderer, library="promptcli")


class UIFactory:
    """Factory for creating UI components via sweet_tea."""

    @staticmethod
    def create_input_provider():
        """Create appropriate input provider for current platform."""
        factory = AbstractFactory[InputProvider]

        try:
            if os.name == "nt":
                return factory.create("windows_input")
            else:
                return factory.create("unix_input")
        except Exception:
            return factory.create("fallback_input")

    @staticmethod
    def create_renderer(context: PipelineContext):
        """Create appropriate renderer based on context."""
        factory = AbstractFactory[Renderer]

        if context.mode == "explain":
            return factory.create("explain_renderer")

        # Choose layout based on option count
        if len(context.display_options) > 8:
            return factory.create("column_layout_renderer")
        return factory.create("vertical_layout_renderer")
