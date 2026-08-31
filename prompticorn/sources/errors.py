"""What can go wrong when talking to an artifact source (PRO-124).

Typed rather than generic, because the three failures below want three
different responses and a caller cannot tell them apart from a message. A
source that is unreachable is worth retrying; an artifact that does not exist
is not; a digest that does not match is neither — it is a reason to stop.
"""

from __future__ import annotations


class SourceError(Exception):
    """Base class for every error raised by an artifact source."""


class SourceUnavailableError(SourceError):
    """The source itself could not be reached or read.

    Says nothing about whether the artifact exists. A missing directory, an
    unreadable clone, a registry that timed out — the answer is "ask again
    later", not "it is not there".
    """

    def __init__(self, source: str, reason: str) -> None:
        super().__init__(f"source {source!r} is unavailable: {reason}")
        self.source = source
        self.reason = reason


class ArtifactNotFoundError(SourceError):
    """The source is fine; it does not carry this artifact.

    Distinct from :class:`SourceUnavailableError` so that "you asked for
    something that does not exist" never gets retried as though it were a
    transient outage.
    """

    def __init__(self, source: str, artifact: str) -> None:
        super().__init__(f"source {source!r} has no artifact {artifact!r}")
        self.source = source
        self.artifact = artifact


class VersionNotFoundError(ArtifactNotFoundError):
    """The artifact exists, but no released version satisfies the range.

    A subclass rather than a sibling: callers that only care whether they can
    have the artifact should not have to catch two exceptions, while a caller
    reporting to a human can say "2.x exists, you asked for 3.x".
    """

    def __init__(self, source: str, coordinate: str, spec: str, available: tuple[str, ...]) -> None:
        offer = ", ".join(available) if available else "none"
        super().__init__(source, f"{coordinate}@{spec}")
        self.coordinate = coordinate
        self.spec = spec
        self.available = available
        self.args = (
            f"source {source!r} has no version of {coordinate!r} matching {spec!r} "
            f"(available: {offer})",
        )


class DigestMismatchError(SourceError):
    """Fetched content does not hash to what its identity claims.

    The one failure here that is never routine. It means the bytes on the far
    end changed under a version that is supposed to be immutable, so the safe
    response is to stop rather than to use them and record the new digest.
    """

    def __init__(self, artifact: str, expected: str, actual: str) -> None:
        super().__init__(
            f"{artifact} does not match its recorded digest: "
            f"expected {expected[:12]}…, got {actual[:12]}…"
        )
        self.artifact = artifact
        self.expected = expected
        self.actual = actual
