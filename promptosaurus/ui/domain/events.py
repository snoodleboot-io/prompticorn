"""Domain events for UI input handling.

This module provides the event types and event models used for
handling keyboard input in the UI pipeline.

Classes:
    InputEventType: Enum of supported input event types.
    InputEvent: Immutable input event with type and value.
"""

from enum import Enum, auto

from pydantic import BaseModel, ConfigDict


class InputEventType(Enum):
    """Types of input events - extensible without code changes.

    This enum defines all supported keyboard input types. New event
    types can be added without modifying existing code.

    Attributes:
        NUMBER: Number key(s) pressed for option selection.
        UP: Up arrow key for navigation.
        DOWN: Down arrow key for navigation.
        ENTER: Enter key to confirm selection.
        QUIT: Quit/cancel key (q or Escape).
        EXPLAIN: Direct trigger for explain mode (e key).
        UNKNOWN: Unrecognized key press.
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
        value: Optional integer value for NUMBER events.
        raw_key: The raw key representation as string or bytes.

    Config:
        frozen: True - instances are immutable after creation.
    """

    model_config = ConfigDict(frozen=True)

    event_type: InputEventType
    value: int | None = None
    raw_key: str | bytes = ""
