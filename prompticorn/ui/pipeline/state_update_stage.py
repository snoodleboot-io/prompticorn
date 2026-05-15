"""State update stage for UI pipeline."""

from prompticorn.ui.commands.result import CommandResult
from prompticorn.ui.domain.context import PipelineContext


class StateUpdateStage:
    """Applies command to update state."""

    @staticmethod
    def apply(command: object, context: PipelineContext) -> CommandResult:
        """Apply command and return result."""
        return command.execute(context)  # type: ignore[attr-defined, no-any-return]
