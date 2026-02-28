"""Column layout renderer."""

from promptcli.ui.domain.context import PipelineContext


class ColumnLayoutRenderer:
    """Renders options in columns."""

    def __init__(self, items_per_column: int = 8, column_width: int = 20):
        self.items_per_column = items_per_column
        self.column_width = column_width

    def render(self, context: PipelineContext) -> str:
        """Render options in column layout."""
        options = context.display_options
        lines = []

        num_items = len(options)
        num_columns = (num_items + self.items_per_column - 1) // self.items_per_column

        for row in range(self.items_per_column):
            line_parts = []
            for col in range(num_columns):
                idx = col * self.items_per_column + row
                if idx < num_items:
                    num_str = f"{idx + 1}."
                    content = f"{num_str:>3} {options[idx]}"
                    part = content.ljust(self.column_width)
                    line_parts.append(part)
            if line_parts:
                lines.append("".join(line_parts))

        return "\n".join(lines)
