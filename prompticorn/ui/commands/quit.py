"""Quit command implementation."""

from prompticorn.ui.commands.command import Command
from prompticorn.ui.domain.context import PipelineContext
from prompticorn.ui.exceptions import UserCancelledError


class QuitCommand(Command):
    """Command to quit/exit the CLI."""

    def execute(self, context: PipelineContext) -> None:
        """Execute quit command - raises UserCancelledError to exit CLI."""
        raise UserCancelledError("User cancelled the operation")
