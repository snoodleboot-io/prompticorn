"""One resolved layer: a name, a position, and the sources it contributes (PRO-117)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.content.content_source import ContentSource


@dataclass(frozen=True)
class Layer:
    """What a provider contributes to the stack.

    Attributes:
        name: Shown to people, e.g. ``project``.
        precedence: Position; higher wins.
        sources: In the order they should be consulted *within* this layer.
            Most layers have one. The artifacts layer has one per declared
            artifact, which is why this is a sequence rather than a single source.
    """

    name: str
    precedence: int
    sources: tuple[ContentSource, ...]
