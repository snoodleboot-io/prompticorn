"""Custom exceptions for the artifact module (PRO-107).

Mirrors ``prompticorn.content.errors``: one base class per module, with typed
subclasses carrying the offending input un-normalised alongside a reason phrased
for the person who typed it. These messages are read by authors editing a
manifest, not only by tests.
"""


class ArtifactError(Exception):
    """Base class for every error raised by the artifact module."""


class InvalidSemanticVersionError(ArtifactError):
    """A version string failed to parse as semver 2.0.0.

    Attributes:
        raw_version: The input exactly as supplied, un-normalised.
        reason: Why it was rejected, in terms the author can act on.
    """

    def __init__(self, raw_version: str, reason: str) -> None:
        self.raw_version = raw_version
        self.reason = reason
        super().__init__(f"invalid semantic version {raw_version!r}: {reason}")


class InvalidVersionRangeError(ArtifactError):
    """A version range failed to parse.

    Attributes:
        raw_range: The input exactly as supplied, un-normalised.
        reason: Why it was rejected, in terms the author can act on.
    """

    def __init__(self, raw_range: str, reason: str) -> None:
        self.raw_range = raw_range
        self.reason = reason
        super().__init__(f"invalid version range {raw_range!r}: {reason}")


class InvalidDigestError(ArtifactError):
    """A digest was not a lowercase-hex sha256.

    A malformed digest is worse than an absent one: it looks like verification
    is happening while never matching anything.

    Attributes:
        raw_digest: The input exactly as supplied, un-normalised.
        reason: Why it was rejected.
    """

    def __init__(self, raw_digest: str, reason: str) -> None:
        self.raw_digest = raw_digest
        self.reason = reason
        super().__init__(f"invalid digest {raw_digest!r}: {reason}")


class InvalidArtifactIdError(ArtifactError):
    """An artifact id or requirement failed to parse.

    Covers both halves of ``namespace/name@version``: a bad namespace, a bad
    name, and a malformed or missing version all surface here with a reason
    naming which part is at fault. One type with a specific reason matches
    :class:`prompticorn.content.errors.InvalidUnitIdError`, whose callers likewise
    act on the message rather than on the exception subclass.

    Attributes:
        raw_id: The input exactly as supplied, un-normalised.
        reason: Why it was rejected, in terms the author can act on.
    """

    def __init__(self, raw_id: str, reason: str) -> None:
        self.raw_id = raw_id
        self.reason = reason
        super().__init__(f"invalid artifact id {raw_id!r}: {reason}")
