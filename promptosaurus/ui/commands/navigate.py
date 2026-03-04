"""Navigate command implementation."""

from promptosaurus.ui.commands.result import CommandResult
from promptosaurus.ui.domain.context import PipelineContext


class NavigateCommand:
    """Command to navigate up/down."""

    def __init__(self, direction: int):
        """Initialize with direction (-1 for up, +1 for down)."""
        self.direction = direction

    def execute(self, context: PipelineContext) -> CommandResult:
        """Execute navigate command."""
        new_state = context.state.navigate(self.direction)
        return CommandResult(
            continue_pipeline=True,
            new_state=new_state,
        )
