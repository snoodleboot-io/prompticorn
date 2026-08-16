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
        return self is DriftKind.UNIT


_HEADLINES: dict[DriftKind, str] = {
    DriftKind.MANIFEST: "The manifest changed since the lock was written",
    DriftKind.ARTIFACT: "A declared artifact resolved to something else",
    DriftKind.PACKAGE: "This prompticorn is not the one that wrote the lock",
    DriftKind.UNIT: "Content changed under a pinned version — a source was modified in place",
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
}
