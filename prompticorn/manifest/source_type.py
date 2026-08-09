"""The kinds of content source a manifest may declare (PRO-109)."""

from __future__ import annotations

from enum import Enum


class SourceType(Enum):
    """A declarable source of artifacts.

    Only ``builtin`` exists today — it is the one
    :class:`~prompticorn.content.content_source.ContentSource` implementation
    that ships (PRO-104). The enum exists now anyway so that declaring a source
    is validated from the start: adding ``path`` or ``git`` later becomes a new
    member rather than a format change, and a manifest naming an unknown type
    fails with a list of what is legal instead of being silently ignored.
    """

    BUILTIN = "builtin"

    @classmethod
    def known(cls) -> str:
        """Legal values, sorted, for use in error messages."""
        return ", ".join(sorted(member.value for member in cls))
