"""Render stage for UI pipeline."""

from collections.abc import Callable

from promptosaurus.ui.domain.context import PipelineContext


class RenderStage:
    """Renders current state."""

    def __init__(self, renderer_selector: Callable[[PipelineContext], object]):
        self.renderer_selector = renderer_selector

    def render(self, context: PipelineContext) -> None:
        """Render current state."""
        # Clear screen
        print("\033[2J\033[H", end="")

        # Show question and explanation at the top
        question = context.question
        print(f"\n{question.question}\n")
        if question.question_explanation:
            print(f"{question.question_explanation}\n")

        renderer = self.renderer_selector(context)
        output = renderer.render(context)  # type: ignore[attr-defined]
        print(output)

        if context.mode == "select":
            # Show current selection at bottom
            selection_text = self._format_current_selection(context)
            print(f"\nCurrent selection: {selection_text}")
            print("\nControls: Numbers to select, Enter to confirm, q to quit, ? for help")

    @staticmethod
    def _format_current_selection(context: PipelineContext) -> str:
        """Format the current selection for display."""
        state = context.state
        options = context.question.options
        selection = state.current_selection

        if isinstance(selection, set):
            # Multi-select: show comma-delimited selections
            if selection:
                selected_options = [options[i] for i in sorted(selection) if 0 <= i < len(options)]
                return ", ".join(selected_options) if selected_options else "None"
            return "None"
        else:
            # Single select: show current selection
            if 0 <= selection < len(options):
                return options[selection]
            return "None"
