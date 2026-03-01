"""Input provider interface for the UI domain."""

from abc import ABC, abstractmethod
from collections.abc import Iterator

from promptcli.ui.domain.events import InputEvent


class InputProvider(ABC):
    """Abstract base class for input providers."""

    @abstractmethod
    def get_events(self) -> Iterator[InputEvent]:
        """Yield input events."""
        raise NotImplementedError("Subclasses must implement get_events()")

    @abstractmethod
    def supports_raw(self) -> bool:
        """Whether raw input is supported."""
        raise NotImplementedError("Subclasses must implement supports_raw()")
