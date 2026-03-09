"""Command interface for the UI domain.

This module defines the Command abstract base class that represents
user input actions in the interactive CLI. Commands are created by
the CommandFactory from input events and executed by the StateUpdateStage.

Classes:
    Command: Abstract base class for all command implementations.

Example:
    >>> from promptosaurus.ui.commands.command import Command
    >>> from promptosaurus.ui.commands.result import CommandResult
    >>> from promptosaurus.ui.domain.context import PipelineContext
    >>>
    >>> # Subclass to create a new command
    >>> class MyCommand(Command):
    ...     def execute(self, context: PipelineContext) -> CommandResult | None:
    ...         # Implementation
    ...         return CommandResult(continue_pipeline=True)
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

    Example:
        >>> from promptosaurus.ui.commands.select import SelectCommand
        >>> from promptosaurus.ui.domain.context import PipelineContext, QuestionContext
        >>> from promptosaurus.ui.state.single_selection_state import SingleSelectionState
        >>>
        >>> qc = QuestionContext(
        ...     question="Test?",
        ...     options=["A", "B", "C"],
        ...     explanations={},
        ...     question_explanation=""
        ... )
        >>> state = SingleSelectionState(0, 3)
        >>> ctx = PipelineContext(question=qc, state=state, mode="select")
        >>> cmd = SelectCommand(1)
        >>> result = cmd.execute(ctx)
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

        Example:
            >>> class MyCommand(Command):
            ...     def execute(self, context: PipelineContext) -> CommandResult | None:
            ...         context.state.toggle(0)
            ...         return CommandResult(continue_pipeline=True)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement execute()")
