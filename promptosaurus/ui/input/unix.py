"""Unix-specific input provider."""

from collections.abc import Iterator

from promptosaurus.ui.domain.events import InputEvent, InputEventType
from promptosaurus.ui.domain.input_provider import InputProvider


class UnixInputProvider(InputProvider):
    """Unix-specific input using termios/tty."""

    def get_events(self) -> Iterator[InputEvent]:
        """Yield input events."""
        import sys
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)  # type: ignore[attr-defined]

        try:
            tty.setraw(fd)  # type: ignore[attr-defined]
            while True:
                key = sys.stdin.read(1)
                yield self._parse_key(key, sys.stdin)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # type: ignore[attr-defined]

    def _parse_key(self, key: str, stdin) -> InputEvent:
        """Parse Unix key codes into events."""
        if key == "\r":
            return InputEvent(event_type=InputEventType.ENTER)
        elif key == "q":
            return InputEvent(event_type=InputEventType.QUIT)
        elif key == "\x1b":  # Escape sequence (arrow keys)
            import select

            # Check if there's more data to read (arrow keys)
            if select.select([stdin], [], [], 0.05)[0]:
                seq = stdin.read(2)
                if seq == "[A":
                    return InputEvent(event_type=InputEventType.UP)
                elif seq == "[B":
                    return InputEvent(event_type=InputEventType.DOWN)
            # Just ESC key pressed - ignore it (not shown in UI)
            return InputEvent(event_type=InputEventType.UNKNOWN, raw_key=key)
        elif key == "\x03":  # Ctrl+C
            return InputEvent(event_type=InputEventType.QUIT)
        elif key.isdigit():
            return InputEvent(event_type=InputEventType.NUMBER, value=int(key))

        return InputEvent(event_type=InputEventType.UNKNOWN, raw_key=key)

    def supports_raw(self) -> bool:
        """Whether raw input is supported."""
        return True
