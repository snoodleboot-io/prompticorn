"""Input provider interface for the UI domain."""

from collections.abc import Iterator

from promptosaurus.ui.domain.events import InputEvent


class InputProvider:
    """Abstract base class for input providers."""

    @property
    def events(self) -> Iterator[InputEvent]:
        """Yield input events."""
        raise NotImplementedError("Subclasses must implement the events property")

    def supports_raw(self) -> bool:
        """Whether raw input is supported."""
        raise NotImplementedError("Subclasses must implement supports_raw()")
