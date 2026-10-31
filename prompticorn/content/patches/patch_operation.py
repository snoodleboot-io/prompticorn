"""What every patch operation has in common (PRO-119)."""

from __future__ import annotations

import fnmatch
from abc import ABC, abstractmethod
from dataclasses import dataclass

from prompticorn.content.unit_id import UnitId


@dataclass(frozen=True)
class PatchOperation(ABC):
    """One edit a layer makes to units it does not own.

    Replacement is all-or-nothing, which makes "add one paragraph to every
    skill" cost ownership of every skill. A patch is the alternative: an org
    adds its rule without adopting the artifact, so upstream edits keep
    arriving.

    Attributes:
        units: Glob over rendered unit ids, e.g. ``skill/*/minimal``. A glob
            rather than a list because the whole point is to reach units the
            patch author has not enumerated and may not know about.
        content: The text the operation inserts.
        layer: Which layer declared it, for error messages and ordering.
        index: Position within that layer's document, so two patches from one
            layer have a defined order.
        allow_empty: When false (the default) a glob matching no unit is an
            error. Silent zero-match is how a patch rots unnoticed after an
            upstream rename — the patch keeps "working" and does nothing.
    """

    units: str
    content: str
    layer: str
    index: int
    allow_empty: bool = False

    @property
    @abstractmethod
    def operation(self) -> str:
        """The name used in the document and in messages, e.g. ``append``."""

    @abstractmethod
    def apply(self, unit_id: UnitId, text: str) -> str:
        """``text`` with this operation applied.

        Raises:
            PatchTargetMissingError: If the operation needs an anchor the text
                does not have.
            AmbiguousPatchTargetError: If the anchor appears more than once.
        """

    def matches(self, unit_id: UnitId) -> bool:
        """Whether this operation targets ``unit_id``."""
        return fnmatch.fnmatchcase(unit_id.render(), self.units)

    def describe(self) -> str:
        """How this operation names itself in a message."""
        return f"{self.operation} patch {self.index} from the {self.layer!r} layer"
