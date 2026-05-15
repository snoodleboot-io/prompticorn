"""Select command implementation."""

from prompticorn.ui.commands.command import Command
from prompticorn.ui.commands.result import CommandResult
from prompticorn.ui.domain.context import PipelineContext


class SelectCommand(Command):
    """Command to select an option by number."""

    def __init__(self, number: int):
        self.number = number

    def execute(self, context: PipelineContext) -> CommandResult:
        """Execute select command."""
        # Convert 1-based to 0-based
        index = self.number - 1
        new_state = context.state.select(index)

        return CommandResult(
            continue_pipeline=True,
            new_state=new_state,
        )
