"""Quit command implementation."""

from promptosaurus.ui.commands.command import Command
from promptosaurus.ui.domain.context import PipelineContext
from promptosaurus.ui.exceptions import UserCancelledError


class QuitCommand(Command):
    """Command to quit/exit the CLI."""

    def execute(self, context: PipelineContext) -> None:
        """Execute quit command - raises UserCancelledError to exit CLI."""
        raise UserCancelledError("User cancelled the operation")
