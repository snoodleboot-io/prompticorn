"""Command factory for UI pipeline."""

from promptosaurus.ui.commands.confirm import ConfirmCommand
from promptosaurus.ui.commands.navigate import NavigateCommand
from promptosaurus.ui.commands.noop import NoOpCommand
from promptosaurus.ui.commands.quit import QuitCommand
from promptosaurus.ui.commands.select import SelectCommand
from promptosaurus.ui.domain.events import InputEvent, InputEventType


class CommandFactory:
    """Factory for creating commands from input events."""

    def create_command(self, event: InputEvent) -> object:
        """Create command from input event."""
        if event.event_type == InputEventType.NUMBER and event.value is not None:
            return SelectCommand(event.value)
        elif event.event_type == InputEventType.UP:
            return NavigateCommand(-1)
        elif event.event_type == InputEventType.DOWN:
            return NavigateCommand(1)
        elif event.event_type == InputEventType.ENTER:
            return ConfirmCommand()
        elif event.event_type == InputEventType.QUIT:
            return QuitCommand()
        else:
            return NoOpCommand()
