"""Navigate command implementation."""

from promptosaurus.ui.commands.command import Command
from promptosaurus.ui.commands.result import CommandResult
from promptosaurus.ui.domain.context import PipelineContext
from promptosaurus.ui.state.single_selection_state import SingleSelectionState


class NavigateCommand(Command):
    """Command to navigate up/down."""

    def __init__(self, direction: int):
        """Initialize with direction (-1 for up, +1 for down)."""
        self.direction = direction

    def execute(self, context: PipelineContext) -> CommandResult:
        """Execute navigate command.

        Uses column-aware navigation if multi-column layout is active,
        otherwise uses standard linear navigation.
        """
        # Use column-aware navigation if multi-column layout is active
        if (
            context.layout_columns
            and isinstance(context.state, SingleSelectionState)
            and context.items_per_column is not None
        ):
            # Multi-column layout: navigate within columns
            new_state = context.state.navigate_with_columns(
                self.direction, context.items_per_column
            )
        else:
            # Single-column layout: standard linear navigation
            new_state = context.state.navigate(self.direction)

        return CommandResult(
            continue_pipeline=True,
            new_state=new_state,
        )
