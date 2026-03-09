"""Command interface for the UI domain."""

from promptosaurus.ui.commands.result import CommandResult
from promptosaurus.ui.domain.context import PipelineContext


class Command:
    """Abstract base class for commands."""

    def execute(self, context: PipelineContext) -> CommandResult | None:
        """Execute the command. Must be implemented by subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement execute()")
