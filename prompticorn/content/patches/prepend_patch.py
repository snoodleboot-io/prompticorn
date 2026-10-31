"""Add content at the start of a unit, after its title (PRO-119)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.content.patches.patch_operation import PatchOperation
from prompticorn.content.unit_id import UnitId


@dataclass(frozen=True)
class PrependPatch(PatchOperation):
    """Insert before the body, but *after* a leading H1 when there is one.

    Going in above the title would push the document's own heading down the
    page and leave the patch looking like the artifact's name. Keeping the
    title first is what makes a prepended policy read as a note on the
    document rather than as a replacement for it.
    """

    @property
    def operation(self) -> str:
        return "prepend"

    def apply(self, unit_id: UnitId, text: str) -> str:
        body = self.content.strip()
        lines = text.splitlines()
        if lines and lines[0].startswith("# "):
            rest = "\n".join(lines[1:]).lstrip("\n")
            return f"{lines[0]}\n\n{body}\n\n{rest}".rstrip() + "\n"
        return f"{body}\n\n{text.lstrip()}".rstrip() + "\n"
