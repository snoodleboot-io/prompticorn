"""Fallback input provider using standard input."""

from collections.abc import Iterator

from prompticorn.ui.domain.events import InputEvent, InputEventType
from prompticorn.ui.domain.input_provider import InputProvider


class FallbackInputProvider(InputProvider):
    """Fallback using standard input - no raw mode."""

    @property
    def events(self) -> Iterator[InputEvent]:
        """Yield input events from standard input."""
        user_input = input(
            "Enter number(s) or letter (a-d), separated by comma or space (e.g. 1,2 or 1 2) (or 'e' for explain): "
        ).strip()

        # Check for explain mode first
        if user_input.lower() == "e":
            yield InputEvent(event_type=InputEventType.EXPLAIN)
            yield InputEvent(event_type=InputEventType.ENTER)
            return

        # Map letters to numbers
        letter_to_index = {"a": 0, "b": 1, "c": 2, "d": 3}

        # Parse comma- or space-separated numbers or letters
        try:
            for part in user_input.replace(",", " ").split():
                part = part.strip().lower()
                if part in letter_to_index:
                    yield InputEvent(event_type=InputEventType.NUMBER, value=letter_to_index[part])
                else:
                    # Try to parse as number
                    num = int(part)
                    yield InputEvent(event_type=InputEventType.NUMBER, value=num)
        except ValueError:
            pass

        yield InputEvent(event_type=InputEventType.ENTER)

    def supports_raw(self) -> bool:
        """Whether raw input is supported."""
        return False
