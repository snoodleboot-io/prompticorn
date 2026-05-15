"""No-op command implementation."""

from prompticorn.ui.commands.command import Command
from prompticorn.ui.commands.result import CommandResult
from prompticorn.ui.domain.context import PipelineContext


class NoOpCommand(Command):
    """No-op command for unknown inputs."""

    def execute(self, context: PipelineContext) -> CommandResult:
        """Execute no-op - continue pipeline without changes."""
        return CommandResult(continue_pipeline=True)
