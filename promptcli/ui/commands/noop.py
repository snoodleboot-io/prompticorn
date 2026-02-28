"""No-op command implementation."""

from promptcli.ui.commands.result import CommandResult
from promptcli.ui.domain.context import PipelineContext


class NoOpCommand:
    """No-op command for unknown inputs."""

    def execute(self, context: PipelineContext) -> CommandResult:
        """Execute no-op - continue pipeline without changes."""
        return CommandResult(continue_pipeline=True)
