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


class UndeclaredSlotError(ValueError):
    """A slot was referenced that the unit does not declare (PRO-118).

    Either a layer supplied a value for a slot the artifact never offered, or
    the artifact's body references one its declaration has lost. Both mean body
    and declaration have diverged, and there is no safe guess: treating a
    stray value as a typo-to-ignore silently drops a customisation someone is
    relying on, and treating a stray placeholder as empty silently blanks part
    of a document.

    Deliberately **not** a :class:`ContentError`, for the same reason as
    :class:`MalformedConfigurationError`: consumers catch ContentError to mean
    "absent, carry on with the default", and this is present-and-wrong.

    Attributes:
        unit_id: The unit whose slots disagree.
        slot: The name that is not declared.
        layer: Which layer supplied the value, or ``"body"`` when the
            placeholder in the artifact itself is the undeclared one.
        declared: What the unit does declare, so the message can show the
            likely intended name rather than only the wrong one.
    """

    def __init__(self, unit_id: str, slot: str, layer: str, declared: list[str]) -> None:
        self.unit_id = unit_id
        self.slot = slot
        self.layer = layer
        self.declared = declared
        offered = ", ".join(repr(name) for name in declared) if declared else "no slots at all"
        origin = (
            "the unit's own body references"
            if layer == "body"
            else f"the {layer!r} content layer supplies a value for"
        )
        super().__init__(
            f"{origin} slot {slot!r}, which {unit_id} does not declare; it offers {offered}"
        )


class RequiredSlotUnfilledError(ValueError):
    """A slot declared ``required: true`` has no value (PRO-118).

    Required is opt-in precisely so this can be strict: an artifact that marks
    a slot required is saying it cannot render usefully without one, and
    emitting it blank would ship a document with a hole where a command or a
    target belongs. Slots without the marker render empty and warn instead, so
    declaring a new slot upstream does not break every layer below it.

    Not a :class:`ContentError`, as above.

    Attributes:
        unit_id: The unit with the unfilled slot.
        slot: Which slot needs a value.
    """

    def __init__(self, unit_id: str, slot: str) -> None:
        self.unit_id = unit_id
        self.slot = slot
        super().__init__(
            f"{unit_id} declares slot {slot!r} as required and nothing fills it; "
            f"set it in configurations/slot-values.yaml"
        )


class UnfilledSlotWarning(UserWarning):
    """A declared, undefaulted, not-required slot rendered empty (PRO-118).

    A warning and not an error because that combination is a legitimate way to
    say "optional, omit when unset". It is not silent either: an empty string
    where a value was expected is indistinguishable in the output from content
    that was never written, so the message names the unit and the slot.

    A warning class, so not a :class:`ContentError` — nothing should catch it
    as one.
    """
