"""Explain mode renderer."""

from promptcli.ui.domain.context import PipelineContext


class ExplainRenderer:
    """Renders explain mode."""

    def render(self, context: PipelineContext) -> str:
        """Render explain mode display."""
        lines = [
            f"\n{context.question.question}\n",
            "=" * len(context.question.question),
            f"\n{context.question.question_explanation}\n",
            "Available options:\n",
        ]

        for opt in context.question.options:
            lines.append(f"  • {opt}")
            exp = context.question.explanations.get(opt, "")
            if exp:
                lines.append(f"    {exp}")
            lines.append("")

        lines.append("\nPress any key to return...")
        return "\n".join(lines)
