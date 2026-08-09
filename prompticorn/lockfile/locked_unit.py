"""One resolved content unit in the lock (PRO-110)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.content.unit_id import UnitId

ID_KEY = "id"
LAYER_KEY = "layer"
DIGEST_KEY = "digest"


@dataclass(frozen=True)
class LockedUnit:
    """A unit as resolved, together with which layer supplied it.

    ``layer`` is recorded rather than recomputed because it is the answer to
    "which source won", and that answer stops being derivable the moment the
    source stack changes. `ContentUnit` carries it at enumeration time for the
    same reason (PRO-104); the lock is where it becomes durable.

    Attributes:
        id: The unit's address.
        layer: Provenance — which source supplied it.
        digest: sha256 of its canonical content, as lowercase hex.
    """

    id: UnitId
    layer: str
    digest: str

    @property
    def sort_key(self) -> str:
        """Rendered unit id — the defined order for units in the lock."""
        return self.id.render()

    def to_mapping(self) -> dict[str, str]:
        """Plain, JSON-shaped data for the writer. A fresh dict every call."""
        return {
            ID_KEY: self.id.render(),
            LAYER_KEY: self.layer,
            DIGEST_KEY: self.digest,
        }
