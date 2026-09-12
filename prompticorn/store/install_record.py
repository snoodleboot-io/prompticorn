"""One artifact installed in one repository (PRO-128)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstallRecord:
    """What the index knows about one installed artifact.

    Attributes:
        artifact_id: Rendered identity, e.g. ``local/house-standards@2.1.0``.
        version: The resolved version, stored alongside the identity so the
            index can be queried by version without parsing every id.
        digest: The artifact digest recorded at install time.
        source: Which source supplied it, or None for the bundled stack.
        installed_at: ISO-8601 UTC, supplied by the caller rather than read
            from the clock here — the same rule the lock follows, so a test can
            compare two writes without one of them being a moving target.
    """

    artifact_id: str
    version: str
    digest: str
    source: str | None
    installed_at: str
