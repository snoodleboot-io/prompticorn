"""Vertical layout renderer."""

from promptcli.ui.domain.context import PipelineContext


class VerticalLayoutRenderer:
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

            if state.is_selected(i) or (not question.allow_multiple and opt == "Explain"):
                exp = context.get_explanation(opt)
                if exp:
                    lines.append(f"  {marker} {num} {opt}{default_tag}")
                    lines.append(f"       └─ {exp}")
                else:
                    lines.append(f"  {marker} {num} {opt}{default_tag}")
            else:
                lines.append(f"  {marker} {num} {opt}")

        return "\n".join(lines)
