"""Command factory for UI pipeline."""

from prompticorn.ui.commands.confirm import ConfirmCommand
from prompticorn.ui.commands.explain import ExplainCommand
from prompticorn.ui.commands.navigate import NavigateCommand
from prompticorn.ui.commands.noop import NoOpCommand
from prompticorn.ui.commands.quit import QuitCommand
from prompticorn.ui.commands.select import SelectCommand
from prompticorn.ui.domain.events import InputEvent, InputEventType


class CommandFactory:
    """Factory for creating commands from input events."""

    def __init__(self) -> None:
        self._digit_buffer = ""

    def create_command(self, event: InputEvent, allow_multiple: bool = False) -> object:
        """Create command from input event."""
        if event.event_type == InputEventType.NUMBER and event.value is not None:
            if allow_multiple and event.value <= 9:
                # Multi-select raw: buffer single digits; commit on separator/timeout
                self._digit_buffer += str(event.value)
                return NoOpCommand()
            if allow_multiple:
                # Multi-select fallback: value already a full integer (e.g. 10, 12)
                self._digit_buffer = ""
                return SelectCommand(event.value)
            # Single-select: accumulate digits and jump cursor immediately
            self._digit_buffer += str(event.value)
            return SelectCommand(int(self._digit_buffer))

        if event.event_type in (InputEventType.SEPARATOR, InputEventType.TIMEOUT):
            if self._digit_buffer:
                value = int(self._digit_buffer)
                self._digit_buffer = ""
                return SelectCommand(value)
            return NoOpCommand()

        # Non-digit, non-separator: clear buffer and process event normally
        self._digit_buffer = ""
        if event.event_type == InputEventType.UP:
            return NavigateCommand(-1)
        elif event.event_type == InputEventType.DOWN:
            return NavigateCommand(1)
        elif event.event_type == InputEventType.ENTER:
            return ConfirmCommand()
        elif event.event_type == InputEventType.QUIT:
            return QuitCommand()
        elif event.event_type == InputEventType.EXPLAIN:
            return ExplainCommand()
        else:
            return NoOpCommand()
