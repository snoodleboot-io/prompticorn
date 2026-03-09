"""Domain events for UI input handling."""

from enum import Enum, auto

from pydantic import BaseModel


class InputEventType(Enum):
    """Types of input events - extensible without code changes."""

    NUMBER = auto()
    UP = auto()
    DOWN = auto()
    ENTER = auto()
    QUIT = auto()
    EXPLAIN = auto()  # Direct trigger for explain mode
    UNKNOWN = auto()


class InputEvent(BaseModel):
    """Immutable input event - all context included."""

    event_type: InputEventType
    value: int | None = None  # For NUMBER events
    raw_key: str | bytes = ""

    class Config:
        frozen = True
