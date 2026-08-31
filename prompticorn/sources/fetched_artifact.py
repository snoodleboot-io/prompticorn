"""What a source hands back, once it has been verified (PRO-124).

A fetched artifact is a pinned identity plus the units it contains, and it
carries its own :class:`ContentSource` so the resolver can layer it in directly.
That is the point of returning it in this shape: an artifact pulled from a
source and the bundled tree are the same kind of thing to everything downstream,
so nothing has to learn a second way to read content.
"""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.artifact.artifact_digest import artifact_digest
from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.pinned_artifact import PinnedArtifact
from prompticorn.content.content_source import ContentSource


@dataclass(frozen=True)
class FetchedArtifact:
    """An artifact's content, with the identity and digest it was verified against.

    Attributes:
        pinned: Exact identity plus the digest its content hashes to.
        content: The artifact's units, behind the same interface as every other
            content source.
    """

    pinned: PinnedArtifact
    content: ContentSource

    @property
    def identity(self) -> ArtifactId:
        """The resolved identity, always at an exact version."""
        return self.pinned.artifact_id

    @property
    def digest(self) -> str:
        """The digest recorded for this artifact."""
        return self.pinned.digest

    def computed_digest(self) -> str:
        """Hash the content as it stands, for comparison against :attr:`digest`.

        Recomputed from the units rather than cached, because the whole value of
        the check is that it reads what is actually there.
        """
        return artifact_digest(
            (unit.id.render(), self.content.digest(unit.id)) for unit in self.content.units()
        )

    def __str__(self) -> str:
        return self.pinned.render()
