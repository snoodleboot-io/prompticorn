"""Replace the body under one exact heading (PRO-119)."""

from __future__ import annotations

import re
from dataclasses import dataclass

from prompticorn.content.errors import AmbiguousPatchTargetError, PatchTargetMissingError
from prompticorn.content.patches.patch_operation import PatchOperation
from prompticorn.content.unit_id import UnitId

_ATX = re.compile(r"^(#{1,6})\s")


@dataclass(frozen=True)
class ReplaceSectionPatch(PatchOperation):
    """Swap the content beneath a heading, keeping the heading itself.

    The heading is matched on **exact level and text**: ``## Core Techniques``
    does not match ``### Core Techniques``. Level-insensitive matching would
    let an upstream restructure silently relocate an org's rule into a
    subsection of something else, and the patch would keep reporting success.

    The heading line survives the replacement. A patch that could delete the
    heading as well would let one layer remove a section another layer's patch
    anchors to, turning a missing heading — already a hard error — into a
    failure whose cause is another patch rather than an upstream edit.

    Attributes:
        heading: The exact heading line, including its ``#`` markers.
    """

    heading: str = ""

    @property
    def operation(self) -> str:
        return "replace_section"

    def describe(self) -> str:
        return f"{super().describe()} targeting {self.heading!r}"

    def apply(self, unit_id: UnitId, text: str) -> str:
        wanted = self.heading.strip()
        lines = text.splitlines()
        found = [index for index, line in enumerate(lines) if line.strip() == wanted]

        if not found:
            raise PatchTargetMissingError(
                unit_id=unit_id.render(), heading=wanted, patch=self.describe()
            )
        if len(found) > 1:
            raise AmbiguousPatchTargetError(
                unit_id=unit_id.render(),
                heading=wanted,
                patch=self.describe(),
                occurrences=[index + 1 for index in found],
            )

        start = found[0]
        level = len(_ATX.match(wanted).group(1)) if _ATX.match(wanted) else 1
        end = len(lines)
        for index in range(start + 1, len(lines)):
            match = _ATX.match(lines[index])
            if match and len(match.group(1)) <= level:
                end = index
                break

        replaced = [lines[start], "", self.content.strip(), ""]
        return "\n".join([*lines[:start], *replaced, *lines[end:]]).rstrip() + "\n"
