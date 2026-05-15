"""Vertical layout renderer."""

from prompticorn.ui.domain.context import PipelineContext
from prompticorn.ui.render.renderer import Renderer


class VerticalLayoutRenderer(Renderer):
    """Renders options in vertical list."""

    def render(self, context: PipelineContext) -> str:
        """Render options in vertical layout."""
        options = context.display_options
        lines = []
        state = context.state
        question = context.question

        for i, opt in enumerate(options):
            num = f"{i + 1}."
            default_tag = " (default)" if i == question.default_index else ""

            if question.allow_multiple:
                marker = "[*]" if state.is_selected(i) else "[ ]"
            else:
                marker = "→" if state.is_selected(i) else " "

            # Show subtext for selected options (including Explain when selected)
            if state.is_selected(i):
                exp = context.get_explanation(opt)
                if exp:
                    lines.append(f"  {marker} {num} {opt}{default_tag}")
                    lines.append(f"       └─ {exp}")
                else:
                    lines.append(f"  {marker} {num} {opt}{default_tag}")
            else:
                lines.append(f"  {marker} {num} {opt}")

        return "\n".join(lines)
