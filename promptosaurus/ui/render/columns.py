"""Column layout renderer."""

from promptosaurus.ui.domain.context import PipelineContext
from promptosaurus.ui.render.renderer import Renderer


class ColumnLayoutRenderer(Renderer):
    """Renders options in columns with selection markers and explanations.

    Displays multiple columns of options with:
    - Selection markers (→ for selected single-select, [*] for multi-select selected, [ ] for unselected)
    - Numeric indices for keyboard selection
    - Explanations shown below for selected items
    - Arrow keys and number keys work across columns
    """

    def __init__(self, items_per_column: int = 6, column_width: int = 20):
        """Initialize column renderer.

        Args:
            items_per_column: Number of items per column (default 6).
            column_width: Width of each column (default 20).
        """
        self.items_per_column = items_per_column
        self.column_width = column_width

    def render(self, context: PipelineContext) -> str:
        """Render options in column layout with selection markers.

        Args:
            context: The pipeline context with options and selection state.

        Returns:
            Formatted multi-column display string.
        """
        options = context.display_options
        state = context.state
        question = context.question
        lines = []

        num_items = len(options)
        num_columns = (num_items + self.items_per_column - 1) // self.items_per_column

        # Render column grid
        for row in range(self.items_per_column):
            line_parts = []
            for col in range(num_columns):
                idx = col * self.items_per_column + row
                if idx < num_items:
                    # Determine selection marker
                    if question.allow_multiple:
                        marker = "[*]" if state.is_selected(idx) else "[ ]"
                    else:
                        marker = "→" if state.is_selected(idx) else " "

                    num_str = f"{idx + 1}."
                    content = f"{marker} {num_str:>2} {options[idx]}"
                    part = content.ljust(self.column_width)
                    line_parts.append(part)
            if line_parts:
                lines.append("".join(line_parts))

        # Add explanations for selected items (like vertical layout)
        selected_idx = None
        if not question.allow_multiple:
            # Single-select: show explanation for current selection
            selection = state.current_selection
            if isinstance(selection, int):
                selected_idx = selection
        else:
            # Multi-select: show explanation for first selected item
            selection = state.current_selection
            if isinstance(selection, set) and selection:
                selected_idx = min(selection)

        # Add explanation section if there's a selected item with explanation
        if selected_idx is not None and 0 <= selected_idx < len(options):
            selected_option = options[selected_idx]
            exp = context.get_explanation(selected_option)
            if exp:
                lines.append("")  # Blank line before explanation
                lines.append(f"Selection: {selected_option}")
                lines.append(f"└─ {exp}")

        return "\n".join(lines)
