"""Add content at the end of a unit (PRO-119)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.content.patches.patch_operation import PatchOperation
from prompticorn.content.unit_id import UnitId


@dataclass(frozen=True)
class AppendPatch(PatchOperation):
    """Append to the body, separated by a blank line.

    Needs no anchor, so it cannot fail on a document whose headings moved —
    which makes it the operation to reach for when the target is a tree of
    units whose internals the patch author does not track.
    """

    @property
    def operation(self) -> str:
        return "append"

    def apply(self, unit_id: UnitId, text: str) -> str:
        return f"{text.rstrip()}\n\n{self.content.strip()}\n"
