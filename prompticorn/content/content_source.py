"""The one interface that answers "give me this unit's bytes" (PRO-104).

Every consumer of prompt content depends on this rather than on a filesystem
path. That inversion is the point of the seam: today the only implementation
wraps the bundled tree, but a git checkout, a local directory, or an unpacked
pack all satisfy the same contract, and no consumer changes when one is added.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from prompticorn.content.content_unit import ContentUnit
from prompticorn.content.digest import digest_text
from prompticorn.content.unit_id import UnitId


class ContentSource(ABC):
    """A place authored content can be read from.

    Implementations must be side-effect free: reading a unit twice returns the
    same text, and enumeration does not mutate anything.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier used in errors and provenance."""

    @abstractmethod
    def units(self) -> Iterable[ContentUnit]:
        """Every unit this source carries, sorted by rendered ID.

        Sorted because the order feeds lockfiles and golden output; an
        enumeration that depends on filesystem ordering makes builds differ
        between machines for no reason.

        Raises:
            SourceUnavailableError: If the source cannot be consulted.
        """

    @abstractmethod
    def read(self, unit_id: UnitId) -> str:
        """Return the unit's text exactly as authored.

        Raises:
            UnitNotFoundError: If this source does not carry the unit.
            SourceUnavailableError: If the source cannot be consulted.
        """

    def digest(self, unit_id: UnitId) -> str:
        """Canonical sha256 of the unit's authored text.

        Defaults to hashing :meth:`read`, so every implementation is consistent
        by construction. A source that can serve a precomputed digest may
        override — but it must produce the same value this default would, or
        two sources holding identical content would disagree about it.

        Raises:
            UnitNotFoundError: If this source does not carry the unit.
            SourceUnavailableError: If the source cannot be consulted.
        """
        return digest_text(self.read(unit_id))

    def has(self, unit_id: UnitId) -> bool:
        """Whether this source carries the unit.

        Defaults to scanning :meth:`units`. Implementations with a cheaper
        existence check should override.
        """
        return any(unit.id == unit_id for unit in self.units())
