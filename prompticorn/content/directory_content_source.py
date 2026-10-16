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

Unreadable is neither. A directory that exists but cannot be listed — wrong
mode, wrong owner — answers ``is_dir()`` with True and then hands back nothing,
so before PRO-165 a layer whose permissions were broken read as a layer with no
content in it: every override silently ignored, exit 0, no output that differed
from a project that had no overrides at all. Absence is a choice somebody made;
this is a fault, and it is reported as one.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from prompticorn.content.builtin_content_source import BuiltinContentSource
from prompticorn.content.content_unit import ContentUnit
from prompticorn.content.errors import SourceUnavailableError, UnitNotFoundError
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
        """Whether the directory exists at all.

        Says nothing about whether it can be read — see
        :meth:`_require_available`.
        """
        return self.root.is_dir()

    def units(self) -> Iterable[ContentUnit]:
        if not self.is_present:
            return []
        return super().units()

    def read(self, unit_id: UnitId) -> str:
        if not self.is_present:
            raise UnitNotFoundError(unit_id.render(), self.name)
        return super().read(unit_id)

    def _require_available(self) -> None:
        """An absent layer is available and empty; an unreadable one is neither.

        The base class treats a missing root as a broken install, which is right
        for the bundled tree and wrong here — :meth:`units` and :meth:`read`
        have already answered for absence by the time this runs. What is left to
        check is the case absence hid: a directory that exists and cannot be
        listed. Listing it is the check, because it is the operation that
        actually has to work; ``os.access`` answers a different question and
        answers it wrongly under ACLs and for root.
        """
        if not self.is_present:
            return
        try:
            next(iter(self.root.iterdir()), None)
        except OSError as error:
            raise SourceUnavailableError(
                self.name,
                f"content layer directory cannot be read: {self.root} ({error.strerror})",
            ) from error
