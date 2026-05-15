"""Explain command implementation."""

from prompticorn.ui.commands.command import Command
from prompticorn.ui.commands.result import CommandResult
from prompticorn.ui.domain.context import PipelineContext


class ExplainCommand(Command):
    """Command to trigger explain mode directly (via 'e' keystroke)."""

    def execute(self, context: PipelineContext) -> CommandResult:
        """Execute explain command - directly trigger explain mode."""
        return CommandResult(
            continue_pipeline=True,
            transition_to="explain",
        )
