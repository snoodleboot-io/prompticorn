"""Fallback input provider using standard input."""

from collections.abc import Iterator

from promptosaurus.ui.domain.events import InputEvent, InputEventType
from promptosaurus.ui.domain.input_provider import InputProvider


class FallbackInputProvider(InputProvider):
    """Fallback using standard input - no raw mode."""

    def get_events(self) -> Iterator[InputEvent]:
        """Yield input events from standard input."""
        user_input = input("Enter number(s), comma-separated: ").strip()

        # Parse comma-separated numbers
        try:
            numbers = [int(x.strip()) for x in user_input.split(",")]
            for num in numbers:
                yield InputEvent(event_type=InputEventType.NUMBER, value=num)
        except ValueError:
            pass

        yield InputEvent(event_type=InputEventType.ENTER)

    def supports_raw(self) -> bool:
        """Whether raw input is supported."""
        return False
