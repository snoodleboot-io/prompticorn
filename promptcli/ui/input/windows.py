"""Windows-specific input provider."""

from collections.abc import Iterator

from promptcli.ui.domain.events import InputEvent, InputEventType
from promptcli.ui.domain.input_provider import InputProvider


class WindowsInputProvider(InputProvider):
    """Windows-specific input using msvcrt."""

    def get_events(self) -> Iterator[InputEvent]:
        """Yield input events."""
        import msvcrt

        while True:
            key = msvcrt.getch()  # type: ignore[attr-defined]
            yield self._parse_key(key, msvcrt)

    def _parse_key(self, key: bytes, msvcrt) -> InputEvent:
        """Parse Windows key codes into events."""
        if key == b"\r":
            return InputEvent(event_type=InputEventType.ENTER)
        elif key == b"q":
            return InputEvent(event_type=InputEventType.QUIT)
        elif key == b"\xe0":  # Arrow key prefix
            arrow = msvcrt.getch()
            if arrow == b"H":
                return InputEvent(event_type=InputEventType.UP)
            elif arrow == b"P":
                return InputEvent(event_type=InputEventType.DOWN)
        elif key.isdigit():
            return InputEvent(event_type=InputEventType.NUMBER, value=int(key.decode()))

        return InputEvent(event_type=InputEventType.UNKNOWN, raw_key=key)

    def supports_raw(self) -> bool:
        """Whether raw input is supported."""
        return True
