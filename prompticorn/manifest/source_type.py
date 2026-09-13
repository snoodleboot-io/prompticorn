"""The kinds of content source a manifest may declare (PRO-109)."""

from __future__ import annotations

from enum import Enum


class SourceType(Enum):
    """A declarable source of artifacts.

    ``builtin`` is the bundled tree (PRO-104). ``git`` and ``local-dir`` arrived
    with PRO-151, as the members this enum was created to make room for: each
    was a new member rather than a format change, which is the reason it existed
    before either had an implementation.
    """

    BUILTIN = "builtin"
    GIT = "git"
    LOCAL_DIR = "local-dir"

    @property
    def location_key(self) -> str | None:
        """The manifest key this type needs to say *where* it is, if any.

        ``builtin`` is the package itself and has nowhere to point. The others
        do, and each names the key in the terms its own users think in — a git
        remote is a URL, a directory is a path — rather than one generic key
        whose meaning depends on a sibling field.
        """
        return _LOCATION_KEYS.get(self)

    @classmethod
    def known(cls) -> str:
        """Legal values, sorted, for use in error messages."""
        return ", ".join(sorted(member.value for member in cls))


# Declared once, so the schema and the source factory cannot disagree about
# which key a type reads its location from.
_LOCATION_KEYS: dict[SourceType, str] = {
    SourceType.GIT: "url",
    SourceType.LOCAL_DIR: "path",
}
