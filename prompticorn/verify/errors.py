"""Typed failures raised by verification (PRO-115).

Same structure as the lockfile and manifest modules: one base, typed subclasses
carrying what a caller needs to act.

These exist for callers that want verification to *raise* rather than to hand
back a report — a build step that must stop, as opposed to the CLI, which
reports every finding before exiting. The CLI path never raises these: telling a
user about the first of nine problems and hiding the rest is how a verification
tool earns a reputation for wasting people's time.
"""

from __future__ import annotations


class VerificationError(Exception):
    """Base class for every error raised by the verify module."""


class OutputTamperedError(VerificationError):
    """A generated file's content does not match what the lock recorded.

    Attributes:
        path: The output that no longer matches.
        expected: The digest the lock recorded.
        actual: The digest the file has now.
    """

    def __init__(self, path: str, expected: str, actual: str) -> None:
        self.path = path
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"generated file {path!r} was modified by hand: "
            f"lock records {expected[:12]}…, file is {actual[:12]}…. "
            "Move the change into the authored source and rebuild; a hand-patched "
            "output is lost at the next build."
        )


class UnknownOutputError(VerificationError):
    """A generated file exists that the lock does not account for.

    Attributes:
        path: The file nothing accounts for.
    """

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(
            f"generated file {path!r} is not in the lock. "
            "Delete it, or run `prompticorn lock` if it belongs to the build."
        )
