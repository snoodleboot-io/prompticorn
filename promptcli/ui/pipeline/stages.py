"""Pipeline stages for UI orchestration."""

from collections.abc import Callable

from promptcli.ui.commands.confirm import ConfirmCommand
from promptcli.ui.commands.navigate import NavigateCommand
from promptcli.ui.commands.noop import NoOpCommand
from promptcli.ui.commands.quit import QuitCommand
from promptcli.ui.commands.result import CommandResult
from promptcli.ui.commands.select import SelectCommand
from promptcli.ui.domain.context import PipelineContext
from promptcli.ui.domain.events import InputEvent, InputEventType


class RenderStage:
    """Renders current state."""

    def __init__(self, renderer_selector: Callable[[PipelineContext], object]):
        self.renderer_selector = renderer_selector

    def render(self, context: PipelineContext) -> None:
        """Render current state."""
        # Clear screen
        print("\033[2J\033[H", end="")

        renderer = self.renderer_selector(context)
        output = renderer.render(context)  # type: ignore[attr-defined]
        print(output)

        if context.mode == "select":
            print("\nControls: Numbers to select, Enter to confirm, q to quit")


class StateUpdateStage:
    """Applies command to update state."""

    def apply(self, command: object, context: PipelineContext) -> CommandResult:
        """Apply command and return result."""
        return command.execute(context)  # type: ignore[attr-defined, no-any-return]


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
