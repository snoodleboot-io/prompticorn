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


class UnitNotFoundError(ContentError):
    """A source was asked for a unit it does not carry.

    Distinct from :class:`SourceUnavailableError`: the source answered, and the
    answer was "not mine". A resolver consulting several layers treats this as
    "try the next one", so conflating the two would make one broken source look
    like a universally missing unit.

    Attributes:
        unit_id: The requested unit, rendered.
        source: Name of the source that did not have it.
    """

    def __init__(self, unit_id: str, source: str) -> None:
        self.unit_id = unit_id
        self.source = source
        super().__init__(f"unit {unit_id!r} not found in source {source!r}")


class SourceUnavailableError(ContentError):
    """A source could not be consulted at all.

    The bundled tree is missing, a checkout is absent, a remote is unreachable.
    The unit may well exist — this says nothing about it. Callers must not
    swallow this as a miss; an unavailable source that reads as "empty" turns a
    broken install into a silently degraded build.

    Attributes:
        source: Name of the source that could not be consulted.
        reason: Why, in terms the operator can act on.
    """

    def __init__(self, source: str, reason: str) -> None:
        self.source = source
        self.reason = reason
        super().__init__(f"source {source!r} unavailable: {reason}")
