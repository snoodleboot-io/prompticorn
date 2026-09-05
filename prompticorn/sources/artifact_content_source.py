"""An artifact's units, read from its own root (PRO-124).

An artifact on disk is laid out exactly like the bundled tree — same
directories, same filenames — so the ID-to-path mapping is the one
:class:`BuiltinContentSource` already declares. Subclassing it reuses that
mapping rather than restating it; a second copy would be free to drift, and a
unit that enumerated but could not be read is precisely the bug that mapping was
centralised to prevent.

Only the layer name differs. The bundled source answers ``builtin`` because it
*is* the bundled tree; a fetched artifact answers with its own identity, so
``ContentUnit.layer`` and the lock both say which artifact supplied a unit
rather than claiming everything came from the package.
"""

from __future__ import annotations

from pathlib import Path

from prompticorn.content.builtin_content_source import BuiltinContentSource


class ArtifactContentSource(BuiltinContentSource):
    """The bundled layout, read from an artifact root, under the artifact's name.

    Args:
        root: Directory holding the artifact's unit tree.
        layer: What this source calls itself — the artifact's rendered identity.
    """

    def __init__(self, root: Path, layer: str) -> None:
        super().__init__(root=root)
        self._layer = layer

    @property
    def name(self) -> str:
        return self._layer
