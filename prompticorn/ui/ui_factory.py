"""Factory for creating UI components via sweet_tea."""

import os

from sweet_tea.abstract_factory import AbstractFactory
from sweet_tea.registry import Registry

from prompticorn.ui.domain.context import PipelineContext
from prompticorn.ui.domain.input_provider import InputProvider
from prompticorn.ui.domain.renderer import Renderer
from prompticorn.ui.input.fallback import FallbackInputProvider
from prompticorn.ui.input.unix import UnixInputProvider
from prompticorn.ui.input.windows import WindowsInputProvider
from prompticorn.ui.render.columns import ColumnLayoutRenderer
from prompticorn.ui.render.explain import ExplainRenderer
from prompticorn.ui.render.vertical import VerticalLayoutRenderer

# Register input providers with snake_case keys for sweet_tea factory
Registry.register("windows_input", WindowsInputProvider, library="prompticorn")
Registry.register("unix_input", UnixInputProvider, library="prompticorn")
Registry.register("fallback_input", FallbackInputProvider, library="prompticorn")

# Register renderers with snake_case keys for sweet_tea factory
Registry.register("column_layout_renderer", ColumnLayoutRenderer, library="prompticorn")
Registry.register("vertical_layout_renderer", VerticalLayoutRenderer, library="prompticorn")
Registry.register("explain_renderer", ExplainRenderer, library="prompticorn")


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
        """Create appropriate renderer based on context.

        Uses column layout for 6+ options (saves screen space),
        vertical layout for fewer options (cleaner for small lists).
        """
        factory = AbstractFactory[Renderer]

        if context.mode == "explain":
            return factory.create("explain_renderer")

        # Choose layout based on option count
        # Use columns for 6+ options to save screen space and make layout cleaner
        if len(context.display_options) >= 6:
            return factory.create("column_layout_renderer")
        return factory.create("vertical_layout_renderer")
