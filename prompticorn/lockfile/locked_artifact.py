"""One resolved artifact in the lock (PRO-110)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.pinned_artifact import PinnedArtifact

IDENTITY_KEY = "identity"
DIGEST_KEY = "digest"
SOURCE_KEY = "source"


@dataclass(frozen=True)
class LockedArtifact:
    """What one manifest requirement resolved to.

    The manifest declares a *range*; this records the exact version it resolved
    to, plus the digest of what was actually fetched. That pairing is the whole
    point of the lock — the range can start matching something new tomorrow, and
    the digest is how you find out.

    Attributes:
        pinned: Exact identity plus content digest.
        source: Name of the source it came from, or None for the default stack.
    """

    pinned: PinnedArtifact
    source: str | None = None

    @property
    def identity(self) -> ArtifactId:
        """The resolved artifact identity, always at an exact version."""
        return self.pinned.artifact_id

    @property
    def sort_key(self) -> str:
        """Rendered identity — the defined order for artifacts in the lock."""
        return self.identity.render()

    def to_mapping(self) -> dict[str, str]:
        """Plain, JSON-shaped data for the writer.

        A fresh dict every call, deliberately: sharing one would let PyYAML emit
        an anchor and a reference instead of two entries.
        """
        mapping = {
            IDENTITY_KEY: self.identity.render(),
            DIGEST_KEY: self.pinned.digest,
        }
        # Omitted rather than written as null: an absent source means "the
        # default stack", and a lock full of `source: null` lines is noise in
        # every review of the file.
        if self.source is not None:
            mapping[SOURCE_KEY] = self.source
        return mapping
