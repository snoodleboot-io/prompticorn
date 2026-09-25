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


class SkippedContentWarning(UserWarning):
    """A file in a content layer was not addressable as a unit, and was skipped.

    A *warning* rather than an error because the tree a layer is read from is
    authored by a person, not generated: a ``README.md`` beside the overrides
    that explains them is an entirely reasonable thing to commit, and refusing
    to build because of it would make the layer feature a trap. It is not
    silence either — the message names the file, the layer it came from and the
    unit id the name would have had to be, because the other reading of an
    unaddressable name is a typo in an override that is now doing nothing.

    A warning class rather than an exception, and so not a
    :class:`ContentError`: nothing should be able to catch it as one.
    """


class MalformedConfigurationError(ValueError):
    """A ``configuration/...`` unit parsed as YAML that cannot be used.

    Deliberately **not** a :class:`ContentError`. Consumers already tolerate
    "this configuration is absent" by catching :class:`ContentError` and
    carrying on with a default; a document that is *present and wrong* must not
    take that path, because the result is a build that silently emits something
    other than what was asked for. Making this a sibling of ContentError rather
    than a subclass is what keeps those handlers from swallowing it.

    Attributes:
        name: The configuration's unit name, e.g. ``personas``.
        layer: Which layer supplied it — the one whose file needs fixing.
        location: The file it was read from, when the layer can name one.
        reason: What is wrong with it, in terms the author can act on.
    """

    def __init__(self, name: str, layer: str, location: str, reason: str) -> None:
        self.name = name
        self.layer = layer
        self.location = location
        self.reason = reason
        super().__init__(
            f"{location} (the {layer!r} content layer) is not a usable "
            f"{name!r} configuration: {reason}"
        )
