"""A content layer read from a directory that may not exist (PRO-117).

The project layer (``.prompticorn/content/``) and the user layer
(``~/.prompticorn/content/``) use the bundled layout, so they reuse
:class:`BuiltinContentSource`'s ID-to-path mapping rather than restating it.

What differs is absence. The bundled tree must exist — an installed package
without its content is broken, and saying so loudly is right. An override layer
is optional by nature: most projects will never create one, and a project
without ``.prompticorn/content/`` failing to build would make the feature a tax
on everyone who does not use it. So a missing directory is an empty layer, not
an error.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from prompticorn.content.builtin_content_source import BuiltinContentSource
from prompticorn.content.content_unit import ContentUnit
from prompticorn.content.errors import UnitNotFoundError
from prompticorn.content.unit_id import UnitId


class DirectoryContentSource(BuiltinContentSource):
    """The bundled layout, read from an optional directory, under a layer name.

    Args:
        root: The directory. Need not exist.
        layer: What this source calls itself, e.g. ``project``.
    """

    def __init__(self, root: Path, layer: str) -> None:
        super().__init__(root=root)
        self._layer = layer

    @property
    def name(self) -> str:
        return self._layer

    @property
    def is_present(self) -> bool:
        """Whether the directory exists at all."""
        return self.root.is_dir()

    def units(self) -> Iterable[ContentUnit]:
        if not self.is_present:
            return []
        return super().units()

    def read(self, unit_id: UnitId) -> str:
        if not self.is_present:
            raise UnitNotFoundError(unit_id.render(), self.name)
        return super().read(unit_id)
