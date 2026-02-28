"""Quit command implementation."""

from promptcli.ui.commands.result import CommandResult
from promptcli.ui.domain.context import PipelineContext


class QuitCommand:
    """Command to quit with defaults."""

    def execute(self, context: PipelineContext) -> CommandResult:
        """Execute quit command - return default value(s)."""
        default = context.question.options[context.question.default_index]

        if context.question.allow_multiple:
            return CommandResult(
                continue_pipeline=False,
                output_value=[default],
            )
        return CommandResult(
            continue_pipeline=False,
            output_value=default,
        )
