"""Input provider interface for the UI domain.

This module defines the abstract interface for input providers,
which handle platform-specific keyboard input.

Classes:
    InputProvider: Abstract base class for input providers.
"""

from collections.abc import Iterator

from promptosaurus.ui.domain.events import InputEvent


class InputProvider:
    """Abstract base class for input providers.

    Input providers handle platform-specific keyboard input and convert
    raw key presses into InputEvent objects. This abstraction allows
    the UI to work on different platforms (Windows, Unix) with
    different terminal capabilities.

    Attributes:
        events: Property that yields InputEvent objects from user input.

    Methods:
        supports_raw: Check if raw input mode is supported.
    """

    @property
    def events(self) -> Iterator[InputEvent]:
        """Yield input events.

        This property should be implemented by subclasses to yield
        InputEvent objects as the user presses keys.

        Yields:
            InputEvent objects representing user keyboard input.

        Raises:
            NotImplementedError: If subclass doesn't implement this property.
        """
        raise NotImplementedError("Subclasses must implement the events property")

    def supports_raw(self) -> bool:
        """Whether raw input is supported.

        Returns:
            True if raw terminal input is supported, False otherwise.

        Raises:
            NotImplementedError: If subclass doesn't implement this method.
        """
        raise NotImplementedError("Subclasses must implement supports_raw()")
