"""Domain events for UI input handling.

This module provides the event types and event models used for
handling keyboard input in the UI pipeline.

Classes:
    InputEventType: Enum of supported input event types.
    InputEvent: Immutable input event with type and value.

Example:
    >>> from promptosaurus.ui.domain.events import InputEventType, InputEvent
    >>>
    >>> # Create events
    >>> num_event = InputEvent(event_type=InputEventType.NUMBER, value=1, raw_key="1")
    >>> enter_event = InputEvent(event_type=InputEventType.ENTER, raw_key="\\n")
    >>>
    >>> print(num_event.event_type)
    InputEventType.NUMBER
"""

from enum import Enum, auto

from pydantic import BaseModel


class InputEventType(Enum):
    """Types of input events - extensible without code changes.

    This enum defines all supported keyboard input types. New event
    types can be added without modifying existing code.

    Attributes:
        NUMBER: Number key pressed (0-9) for option selection.
        UP: Up arrow key for navigation.
        DOWN: Down arrow key for navigation.
        ENTER: Enter key to confirm selection.
        QUIT: Quit/cancel key (q or Escape).
        EXPLAIN: Direct trigger for explain mode (e key).
        UNKNOWN: Unrecognized key press.

    Example:
        >>> print(InputEventType.UP.name)
        UP
        >>> InputEventType.UP == InputEventType.UP
        True
    """

    NUMBER = auto()
    UP = auto()
    DOWN = auto()
    ENTER = auto()
    QUIT = auto()
    EXPLAIN = auto()  # Direct trigger for explain mode
    UNKNOWN = auto()


class InputEvent(BaseModel):
    """Immutable input event - all context included.

    This Pydantic model represents a single input event from the user.
    It includes the event type, optional numeric value (for NUMBER events),
    and the raw key representation.

    Attributes:
        event_type: The type of input event.
        value: Optional integer value for NUMBER events (0-9).
        raw_key: The raw key representation as string or bytes.

    Config:
        frozen: True - instances are immutable after creation.

    Example:
        >>> event = InputEvent(event_type=InputEventType.NUMBER, value=2, raw_key="2")
        >>> print(event.value)
        2
        >>> event.event_type == InputEventType.NUMBER
        True
    """

    event_type: InputEventType
    value: int | None = None  # For NUMBER events
    raw_key: str | bytes = ""

    class Config:
        frozen = True
