"""One addressable piece of authored content, with its provenance (PRO-104)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.content.unit_id import UnitId
from prompticorn.content.unit_kind import UnitKind

BUILTIN_LAYER = "builtin"


@dataclass(frozen=True)
class ContentUnit:
    """A unit a source can supply, and where it came from.

    ``layer`` is provenance, and it is on the unit rather than inferred by the
    caller because once several sources are stacked, "which layer won" is the
    question `prompticorn why` has to answer. Recording it at enumeration time
    is what makes that answerable later.

    Enumeration deliberately does not carry content: listing what a source has
    should not require reading all of it.
    """

    id: UnitId
    layer: str

    @property
    def kind(self) -> UnitKind:
        """The unit's kind. Derived from the ID rather than stored separately,
        so the two cannot disagree."""
        return self.id.kind

    def __str__(self) -> str:
        return f"{self.id.render()} [{self.layer}]"
