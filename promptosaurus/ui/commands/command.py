"""Command interface for the UI domain.

This module defines the Command abstract base class that represents
user input actions in the interactive CLI. Commands are created by
the CommandFactory from input events and executed by the StateUpdateStage.

Classes:
    Command: Abstract base class for all command implementations.
"""

from promptosaurus.ui.commands.result import CommandResult
from promptosaurus.ui.domain.context import PipelineContext


class Command:
    """Abstract base class for commands.

    This class defines the interface that all command implementations must follow.
    Commands represent user input actions (select, navigate, quit, etc.) that
    modify the selection state.

    Attributes:
        Not applicable - abstract class.

    Methods:
        execute: Apply the command action to the pipeline context.
    """

    def execute(self, context: PipelineContext) -> CommandResult | None:
        """Execute the command.

        This method must be implemented by subclasses to define the command's
        behavior. It modifies the pipeline context and returns a result
        indicating what happened.

        Args:
            context: The PipelineContext to modify.

        Returns:
            CommandResult containing the outcome of the command execution.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement execute()")
