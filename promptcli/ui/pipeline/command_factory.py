"""Command factory for UI pipeline."""

from promptcli.ui.commands.confirm import ConfirmCommand
from promptcli.ui.commands.navigate import NavigateCommand
from promptcli.ui.commands.noop import NoOpCommand
from promptcli.ui.commands.quit import QuitCommand
from promptcli.ui.commands.select import SelectCommand
from promptcli.ui.domain.events import InputEvent, InputEventType


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
