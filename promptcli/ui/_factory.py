"""Factory for creating UI components via sweet_tea."""

import os

from sweet_tea.abstract_factory import AbstractFactory

from promptcli.ui.domain.context import PipelineContext
from promptcli.ui.input.windows import WindowsInputProvider
from promptcli.ui.render.columns import ColumnLayoutRenderer


class UIFactory:
    """Factory for creating UI components via sweet_tea."""

    @staticmethod
    def create_input_provider():
        """Create appropriate input provider for current platform."""
        factory = AbstractFactory[WindowsInputProvider]

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
        factory = AbstractFactory[ColumnLayoutRenderer]

        if context.mode == "explain":
            return factory.create("explain_renderer")

        # Choose layout based on option count
        if len(context.display_options) > 8:
            return factory.create("column_layout")
        return factory.create("vertical_layout")
