"""Confirm command implementation."""

from promptcli.ui.commands.result import CommandResult
from promptcli.ui.domain.context import PipelineContext
from promptcli.ui.state.multi import MultiSelectState


class ConfirmCommand:
    """Command to confirm selection."""

    def execute(self, context: PipelineContext) -> CommandResult:
        """Execute confirm command."""
        selection = context.state.current_selection

        # Handle explain option
        explain_index = len(context.question.options)

        if isinstance(selection, int):
            if selection == explain_index:
                return CommandResult(
                    continue_pipeline=True,
                    transition_to="explain",
                )
            return CommandResult(
                continue_pipeline=False,
                output_value=context.question.options[selection],
            )
        else:  # Multi-select (Set[int])
            if explain_index in selection:
                selection = {s for s in selection if s != explain_index}
                return CommandResult(
                    continue_pipeline=True,
                    new_state=MultiSelectState(selection, len(context.question.options)),
                    transition_to="explain",
                )
            return CommandResult(
                continue_pipeline=False,
                output_value=[context.question.options[i] for i in sorted(selection)],
            )
