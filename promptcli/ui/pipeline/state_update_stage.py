"""State update stage for UI pipeline."""

from promptcli.ui.commands.result import CommandResult
from promptcli.ui.domain.context import PipelineContext


class StateUpdateStage:
    """Applies command to update state."""

    def apply(self, command: object, context: PipelineContext) -> CommandResult:
        """Apply command and return result."""
        return command.execute(context)  # type: ignore[attr-defined, no-any-return]
