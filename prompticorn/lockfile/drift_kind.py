"""The four ways reality can diverge from the lock (PRO-111).

Collapsing these into one "things changed" message would be the easy mistake and
the costly one. Three of them are ordinary workflow events. One is a
supply-chain signal.
"""

from __future__ import annotations

from enum import Enum


class DriftKind(Enum):
    """A classified divergence between the lock and the current state.

    ``UNIT`` is the alarming member. The others mean someone did something:
    edited the manifest, upgraded a dependency, upgraded prompticorn. ``UNIT``
    means content changed underneath a version that was supposed to be fixed —
    a source mutated in place. Phrasing it like the others would bury the one
    finding that warrants stopping work.
    """

    MANIFEST = "manifest"
    ARTIFACT = "artifact"
    PACKAGE = "package"
    UNIT = "unit"
    REF_MOVED = "ref_moved"

    @property
    def headline(self) -> str:
        """One line naming what happened, in the user's terms."""
        return _HEADLINES[self]

    @property
    def remediation(self) -> str:
        """What to do about it."""
        return _REMEDIATION[self]

    @property
    def is_suspicious(self) -> bool:
        """Whether this kind indicates something may be wrong rather than merely changed.

        Drives emphasis in the report. A build that fails because someone edited
        their own manifest should not look like a security incident, and a
        mutated source should not look like routine noise.
        """
        return self in _SUSPICIOUS


_HEADLINES: dict[DriftKind, str] = {
    DriftKind.MANIFEST: "The manifest changed since the lock was written",
    DriftKind.ARTIFACT: "A declared artifact resolved to something else",
    DriftKind.PACKAGE: "This prompticorn is not the one that wrote the lock",
    DriftKind.UNIT: "Content changed under a pinned version — a source was modified in place",
    DriftKind.REF_MOVED: "A version's tag now points at a different commit than the lock pinned",
}

_REMEDIATION: dict[DriftKind, str] = {
    DriftKind.MANIFEST: "Run `prompticorn lock` to record the manifest you now have.",
    DriftKind.ARTIFACT: (
        "Run `prompticorn lock` to accept the new resolution, or pin the "
        "version in `.prompticorn.yaml` if this was not intended."
    ),
    DriftKind.PACKAGE: (
        "Run `prompticorn lock` to re-record, or install the version named in "
        "the lock to reproduce the original build."
    ),
    DriftKind.UNIT: (
        "Investigate before re-locking. A pinned version should not change "
        "content; verify the source has not been tampered with, then run "
        "`prompticorn lock` only once you trust it."
    ),
    DriftKind.REF_MOVED: (
        "A release should never be re-tagged. Find out who moved it and why "
        "before accepting it — the locked commit still builds exactly as it did, "
        "and `prompticorn lock` would silently adopt the new one."
    ),
}

# Both mean a version that should be immutable is not. Grouped so the report,
# and anything deciding how loudly to say it, cannot treat them differently.
_SUSPICIOUS = frozenset({DriftKind.UNIT, DriftKind.REF_MOVED})
