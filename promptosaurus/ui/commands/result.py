"""Command result class."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from promptosaurus.ui.state.selection_state import SelectionState


class CommandResult:
    """Result of command execution."""

    def __init__(
        self,
        continue_pipeline: bool = True,
        new_state: "SelectionState | None" = None,
        output_value: str | list[str] | None = None,
        transition_to: str | None = None,
    ):
        self.continue_pipeline = continue_pipeline
        self.new_state = new_state
        self.output_value = output_value
        self.transition_to = transition_to
