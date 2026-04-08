"""Curses-based input provider using stdscr.getch()."""

import curses
from collections.abc import Iterator
from typing import Any

from promptosaurus.ui.domain.events import InputEvent, InputEventType
from promptosaurus.ui.domain.input_provider import InputProvider


class CursesInputProvider(InputProvider):
    """Input provider using curses stdscr.getch() for keyboard events.

    This provider uses the curses window for input, eliminating the stdin
    conflicts that occur when mixing curses rendering with manual stdin reading.

    The key advantage is that curses.getch() returns special key codes for
    arrow keys (KEY_UP, KEY_DOWN) without requiring manual escape sequence parsing.

    Attributes:
        stdscr: The curses window object to use for input.
    """

    def __init__(self, stdscr: Any):
        """Initialize with a curses window object.

        Args:
            stdscr: The curses window (from curses.initscr() or render_stage.stdscr).
        """
        self.stdscr = stdscr

    @property
    def events(self) -> Iterator[InputEvent]:
        """Yield input events from curses.getch().

        Reads keyboard input using curses.getch(), which:
        - Handles arrow keys natively (KEY_UP = 259, KEY_DOWN = 258)
        - Doesn't conflict with curses rendering
        - Handles timeout and special keys properly

        Yields:
            InputEvent objects for each key press.
        """
        while True:
            try:
                key = self.stdscr.getch()
                yield self._parse_key(key)
            except KeyboardInterrupt:
                yield InputEvent(event_type=InputEventType.QUIT)
                break

    @staticmethod
    def _parse_key(key: int) -> InputEvent:
        """Parse curses key codes into events.

        Args:
            key: The integer key code from stdscr.getch().

        Returns:
            An InputEvent representing the key press.
        """
        # Curses special key codes
        KEY_UP = 259
        KEY_DOWN = 258

        # Handle special keys
        if key == curses.KEY_UP or key == KEY_UP:
            return InputEvent(event_type=InputEventType.UP)
        elif key == curses.KEY_DOWN or key == KEY_DOWN:
            return InputEvent(event_type=InputEventType.DOWN)
        elif key == ord("\n") or key == ord("\r"):
            return InputEvent(event_type=InputEventType.ENTER)
        elif key == ord("q") or key == ord("Q"):
            return InputEvent(event_type=InputEventType.QUIT)
        elif key == ord("\x03"):  # Ctrl+C
            return InputEvent(event_type=InputEventType.QUIT)
        elif chr(key).isdigit():
            return InputEvent(event_type=InputEventType.NUMBER, value=int(chr(key)))
        elif chr(key).lower() in "abcd":
            # Map letters a-d (and A-D) to selection indices 0-3
            letter_to_index = {"a": 0, "b": 1, "c": 2, "d": 3}
            index = letter_to_index[chr(key).lower()]
            return InputEvent(event_type=InputEventType.NUMBER, value=index)
        elif chr(key).lower() == "e":
            # 'e' or 'E' triggers explain mode
            return InputEvent(event_type=InputEventType.EXPLAIN)
        elif key == ord("?"):
            # Help - for future use
            return InputEvent(event_type=InputEventType.EXPLAIN)

        # Unknown key
        return InputEvent(event_type=InputEventType.UNKNOWN, raw_key=str(key))

    def supports_raw(self) -> bool:
        """Whether raw input is supported.

        Curses manages raw mode automatically, so this always returns True.

        Returns:
            True - curses handles raw input mode.
        """
        return True
