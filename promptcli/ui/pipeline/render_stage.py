"""Render stage for UI pipeline."""

from collections.abc import Callable

from promptcli.ui.domain.context import PipelineContext


class RenderStage:
    """Renders current state."""

    def __init__(self, renderer_selector: Callable[[PipelineContext], object]):
        self.renderer_selector = renderer_selector

    def render(self, context: PipelineContext) -> None:
        """Render current state."""
        # Clear screen
        print("\033[2J\033[H", end="")

        renderer = self.renderer_selector(context)
        output = renderer.render(context)  # type: ignore[attr-defined]
        print(output)

        if context.mode == "select":
            print("\nControls: Numbers to select, Enter to confirm, q to quit")
