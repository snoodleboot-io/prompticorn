"""What can go wrong when talking to an artifact source (PRO-124).

Typed rather than generic, because these failures want different responses and
a caller cannot tell them apart from a message. A source that is unreachable is
worth retrying; an artifact that does not exist is not; a digest that does not
match is neither — it is a reason to stop.
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


class RefMovedError(SourceError):
    """A version's tag now points at a different commit than the lock pinned.

    Tags are mutable; commits are not. A lock pins the commit precisely so that
    a tag moved upstream cannot silently change what a locked build produces.
    When re-resolution finds the tag elsewhere, that is drift to be reported and
    decided on — not an update to adopt quietly.
    """

    def __init__(self, artifact: str, pinned: str, current: str) -> None:
        super().__init__(
            f"{artifact} has moved: the lock pinned {pinned[:12]}, "
            f"the tag now points at {current[:12]}"
        )
        self.artifact = artifact
        self.pinned = pinned
        self.current = current


class InvalidCommitError(SourceError):
    """A pin that is not a commit id at all.

    Raised before the value is used for anything, because a lock file travels
    with a repository and is therefore input from outside: a pin of ``..`` or
    ``--upload-pack=…`` is only harmless while nothing has joined it to a path
    or handed it to a subprocess. Refusing it is cheap; recovering from it is
    not (PRO-163).
    """

    def __init__(self, source: str, commit: str) -> None:
        super().__init__(
            f"source {source!r} was given {commit!r} as a commit, which is not a "
            "commit id (40 or 64 lowercase hex characters)"
        )
        self.source = source
        self.commit = commit


class CommitNotFoundError(SourceError):
    """The remote answered, and does not have the commit a lock pinned.

    Kept apart from :class:`SourceUnavailableError` because the advice is the
    opposite of it: no retry and no credential check brings back a commit that
    was garbage-collected or force-pushed away. It is the one failure a lock
    exists to surface, so reporting it as a network problem sends the reader to
    the wrong place.
    """

    def __init__(self, source: str, commit: str, reason: str) -> None:
        super().__init__(f"source {source!r} has no commit {commit[:12]}: {reason}")
        self.source = source
        self.commit = commit
        self.reason = reason


class CacheCorruptError(SourceError):
    """A local cache entry is not the kind of thing the cache puts there.

    A file, or a symlink, where a checkout directory belongs. Reported with the
    path rather than cleared away, because deleting whatever is found is how a
    cache path turns into a delete primitive.
    """

    def __init__(self, source: str, path: str, reason: str) -> None:
        super().__init__(f"source {source!r} cannot use cache entry {path}: {reason}")
        self.source = source
        self.path = path
        self.reason = reason
