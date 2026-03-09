"""Explain command implementation."""

from promptosaurus.ui.commands.command import Command
from promptosaurus.ui.commands.result import CommandResult
from promptosaurus.ui.domain.context import PipelineContext


class ExplainCommand(Command):
    """Command to trigger explain mode directly (via 'e' keystroke)."""

    def execute(self, context: PipelineContext) -> CommandResult:
        """Execute explain command - directly trigger explain mode."""
        return CommandResult(
            continue_pipeline=True,
            transition_to="explain",
        )
