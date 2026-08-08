"""An artifact identity paired with the digest of its content (PRO-107).

The "plus content hash" half of the identity model, and the shape a lock entry
takes: *this* version, and *these* bytes.

Why the digest is not a field on :class:`~prompticorn.artifact.artifact_id.ArtifactId`
-------------------------------------------------------------------------------------

Identity and integrity answer different questions. ``local/acme-sec@2.1.0``
names a release; the digest attests to what that release contained. Folding the
hash into the identity would mean two things:

- the id would stop being writable by a human in a manifest, and
- every future attestation — a signature, a provenance statement, an SBOM
  reference — would have to be squeezed into the identity string too, breaking
  the format each time one was added.

Keeping them paired but separate means later attestations attach to *this* type
without touching ``ArtifactId`` at all. The digest covers canonical content (see
:mod:`prompticorn.content.digest`), never the identity string, so re-rendering
or re-namespacing an id can never invalidate a hash.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.errors import InvalidDigestError
from prompticorn.content.digest import digest_text

# sha256 as lowercase hex, matching what `prompticorn.content.digest` emits.
# Uppercase is rejected rather than folded: two spellings of one hash would
# compare unequal as strings, which is exactly the bug a digest exists to catch.
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class PinnedArtifact:
    """An exact artifact version together with the digest of its content.

    Attributes:
        artifact_id: Which artifact, at which exact version.
        digest: sha256 of the canonical content, as lowercase hex.
    """

    artifact_id: ArtifactId
    digest: str

    @classmethod
    def for_content(cls, artifact_id: ArtifactId, text: str) -> PinnedArtifact:
        """Pin ``artifact_id`` to the canonical digest of ``text``.

        Delegates to :func:`prompticorn.content.digest.digest_text` rather than
        hashing here, so there is exactly one definition of "canonical" in the
        codebase. A second one would drift, and a lockfile written against the
        drifted definition would be unverifiable.
        """
        return cls(artifact_id=artifact_id, digest=digest_text(text))

    def __post_init__(self) -> None:
        """Reject a digest that is not well-formed.

        A malformed digest is worse than none: it looks like verification is
        happening while never matching anything.
        """
        if not isinstance(self.digest, str):
            raise InvalidDigestError(
                str(self.digest), f"expected a string, got {type(self.digest).__name__}"
            )
        if not _DIGEST_RE.match(self.digest):
            if self.digest != self.digest.lower():
                raise InvalidDigestError(
                    self.digest, "contains uppercase; digests are lowercase hex"
                )
            raise InvalidDigestError(
                self.digest,
                f"expected 64 lowercase hex characters (sha256), got {len(self.digest)}",
            )

    def matches_content(self, text: str) -> bool:
        """Whether ``text`` canonicalises to the pinned digest."""
        return digest_text(text) == self.digest

    def render(self) -> str:
        """The canonical string form: ``id sha256:digest``."""
        return f"{self.artifact_id.render()} sha256:{self.digest}"

    def __str__(self) -> str:
        return self.render()
