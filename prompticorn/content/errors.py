"""Custom exceptions for the content module.

Mirrors the structure of ``prompticorn.builders.errors``: one base class per
module, with typed subclasses carrying the context a caller needs to act.
"""


class ContentError(Exception):
    """Base class for every error raised by the content module."""


class InvalidUnitIdError(ContentError):
    """A unit ID failed to parse or violated the grammar.

    Carries the offending input alongside a reason phrased for the person who
    typed it. This validator is the single traversal-safety control that pack
    loading and remote unpacking both reuse, so its errors are read by authors,
    not only by tests.

    Attributes:
        raw_id: The input exactly as supplied, un-normalised.
        reason: Why it was rejected, in terms the author can act on.
    """

    def __init__(self, raw_id: str, reason: str) -> None:
        self.raw_id = raw_id
        self.reason = reason
        super().__init__(f"invalid unit id {raw_id!r}: {reason}")
