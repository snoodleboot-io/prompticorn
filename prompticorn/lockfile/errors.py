"""Custom exceptions for the lockfile module (PRO-110).

Same structure as the content, artifact and manifest modules: one base class,
typed subclasses carrying what a caller needs to act.

The lock is **generated**, not hand-written, so its errors are read in a
different situation from the manifest's: something has gone wrong with a file the
user did not author. The messages therefore say what to *do* — re-lock, or
upgrade — rather than describing a syntax fault the reader is expected to fix by
hand.
"""


class LockError(Exception):
    """Base class for every error raised by the lockfile module."""


class LockCorruptError(LockError):
    """The lock file could not be read as a lock.

    Unparseable YAML, a missing required key, a value of the wrong type, or a
    digest that is not a digest. All of it means the same thing to the user —
    the file cannot be trusted — so it is one error with a specific reason
    rather than a family they would have to tell apart.

    Attributes:
        path: The lock file that could not be read.
        reason: What is wrong with it.
    """

    def __init__(self, path: str, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(
            f"lock file {path!r} is corrupt: {reason}. "
            "Regenerate it with `prompticorn lock`; do not hand-edit it."
        )


class LockSchemaVersionError(LockError):
    """The lock declares a schema version this build cannot read.

    Kept separate from :class:`LockCorruptError` because the remedy is the
    opposite. A corrupt lock should be regenerated; a *newer* lock must not be —
    regenerating it would silently downgrade a file a newer prompticorn wrote,
    discarding whatever it recorded that this build does not understand.

    Attributes:
        path: The lock file.
        found: The schema version it declares.
        supported: The versions this build understands.
    """

    def __init__(self, path: str, found: str, supported: tuple[str, ...]) -> None:
        self.path = path
        self.found = found
        self.supported = supported
        readable = ", ".join(supported)
        super().__init__(
            f"lock file {path!r} declares schema version {found!r}, which this "
            f"version of prompticorn cannot read (supported: {readable}). "
            "Upgrade prompticorn — do not regenerate the lock, or you will "
            "discard what the newer version recorded."
        )
