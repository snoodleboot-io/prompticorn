"""Factory for creating UI components via sweet_tea."""

import os

from sweet_tea.abstract_factory import AbstractFactory
from sweet_tea.registry import Registry

from promptosaurus.ui.domain.context import PipelineContext
from promptosaurus.ui.domain.input_provider import InputProvider
from promptosaurus.ui.domain.renderer import Renderer
from promptosaurus.ui.input.fallback import FallbackInputProvider
from promptosaurus.ui.input.unix import UnixInputProvider
from promptosaurus.ui.input.windows import WindowsInputProvider
from promptosaurus.ui.render.columns import ColumnLayoutRenderer
from promptosaurus.ui.render.explain import ExplainRenderer
from promptosaurus.ui.render.vertical import VerticalLayoutRenderer

# Register input providers with snake_case keys for sweet_tea factory
Registry.register("windows_input", WindowsInputProvider, library="promptosaurus")
Registry.register("unix_input", UnixInputProvider, library="promptosaurus")
Registry.register("fallback_input", FallbackInputProvider, library="promptosaurus")

# Register renderers with snake_case keys for sweet_tea factory
Registry.register("column_layout_renderer", ColumnLayoutRenderer, library="promptosaurus")
Registry.register("vertical_layout_renderer", VerticalLayoutRenderer, library="promptosaurus")
Registry.register("explain_renderer", ExplainRenderer, library="promptosaurus")


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
