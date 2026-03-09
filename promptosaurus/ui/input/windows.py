"""Windows-specific input provider."""

from collections.abc import Iterator

from promptosaurus.ui.domain.events import InputEvent, InputEventType
from promptosaurus.ui.domain.input_provider import InputProvider


class WindowsInputProvider(InputProvider):
    """Windows-specific input using msvcrt."""

    @property
    def events(self) -> Iterator[InputEvent]:
        """Yield input events."""
        import msvcrt

        while True:
            key = msvcrt.getch()  # type: ignore[attr-defined]
            yield self._parse_key(key, msvcrt)

    @staticmethod
    def _parse_key(key: bytes, msvcrt) -> InputEvent:
        """Parse Windows key codes into events."""
        # Convert to int for easier comparison
        key_code = key[0] if key else 0

        if key == b"\r":
            return InputEvent(event_type=InputEventType.ENTER)
        elif key == b"q":
            return InputEvent(event_type=InputEventType.QUIT)
        elif key_code == 3:  # Ctrl+C
            return InputEvent(event_type=InputEventType.QUIT)
        elif key == b"\xe0":  # Arrow key prefix
            arrow = msvcrt.getch()
            if arrow == b"H":
                return InputEvent(event_type=InputEventType.UP)
            elif arrow == b"P":
                return InputEvent(event_type=InputEventType.DOWN)
        elif key.isdigit():
            return InputEvent(event_type=InputEventType.NUMBER, value=int(key.decode()))
        elif key.decode().lower() in "abcd":
            # Map letters a-d (and A-D) to selection indices 0-3
            letter_to_index = {"a": 0, "b": 1, "c": 2, "d": 3}
            index = letter_to_index[key.decode().lower()]
            return InputEvent(event_type=InputEventType.NUMBER, value=index)
        elif key.decode().lower() == "e":
            # 'e' or 'E' triggers explain mode directly
            return InputEvent(event_type=InputEventType.EXPLAIN)

        return InputEvent(event_type=InputEventType.UNKNOWN, raw_key=key)

    def supports_raw(self) -> bool:
        """Whether raw input is supported."""
        return True
