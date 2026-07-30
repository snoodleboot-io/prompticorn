"""The addressing scheme every content source depends on (PRO-103).

A ``UnitId`` names one piece of authored content — an agent variant, a skill, a
convention — independently of where its bytes live. Sources resolve IDs to bytes;
nothing outside this module is entitled to invent its own addressing or its own
traversal checks.

No filesystem access occurs here. Parsing an ID says nothing about whether the
content exists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from prompticorn.content.errors import InvalidUnitIdError
from prompticorn.content.unit_kind import UnitKind

SEPARATOR = "/"

# Per-segment charset. Lowercase only — see the case-folding note on `parse`.
_SEGMENT_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")

# Inputs worth naming explicitly rather than letting the charset reject them with
# a generic message. Each maps to the reason an author needs to hear.
_TRAVERSAL = ".."
_BACKSLASH = "\\"
_NUL = "\x00"


@dataclass(frozen=True)
class UnitId:
    """A parsed, validated content address.

    Immutable and hashable, so IDs work as dict keys and set members — which is
    how resolvers and lockfiles index them.

    Attributes:
        kind: The category of content addressed.
        segments: The path segments after the kind prefix, already validated
            against the kind's arity and charset.
    """

    kind: UnitKind
    segments: tuple[str, ...]

    @classmethod
    def parse(cls, raw_id: str) -> UnitId:
        """Parse and validate a unit ID.

        **Case is rejected, not folded.** ``agent/Code`` and ``agent/code`` are
        distinct dict keys but the same file on APFS and NTFS, so accepting both
        yields a resolver that behaves differently on macOS than on Linux.
        Silently normalising would hide the ambiguity until it produced a
        platform-specific bug; rejecting surfaces it at authoring time.

        Args:
            raw_id: The candidate ID.

        Returns:
            The parsed value object.

        Raises:
            InvalidUnitIdError: With a reason naming what to fix.
        """
        if not isinstance(raw_id, str):
            raise InvalidUnitIdError(str(raw_id), f"expected a string, got {type(raw_id).__name__}")
        if not raw_id:
            raise InvalidUnitIdError(raw_id, "is empty")

        # Named before the charset check so the message points at the real
        # problem rather than "segment contains an illegal character".
        if _NUL in raw_id:
            raise InvalidUnitIdError(raw_id, "contains a NUL byte")
        if _BACKSLASH in raw_id:
            raise InvalidUnitIdError(
                raw_id, f"contains a backslash; segments are separated by {SEPARATOR!r}"
            )
        if raw_id.startswith(SEPARATOR):
            raise InvalidUnitIdError(raw_id, "is absolute; unit ids are relative")

        parts = raw_id.split(SEPARATOR)
        if any(part == _TRAVERSAL for part in parts):
            raise InvalidUnitIdError(raw_id, "contains a '..' path traversal segment")
        if any(not part for part in parts):
            raise InvalidUnitIdError(raw_id, "contains an empty segment")

        kind_token, *segments = parts
        kind = cls._parse_kind(raw_id, kind_token)

        for segment in segments:
            cls._validate_segment(raw_id, segment)

        cls._validate_arity(raw_id, kind, segments)
        cls._validate_discriminator(raw_id, kind, segments)

        return cls(kind=kind, segments=tuple(segments))

    @staticmethod
    def _parse_kind(raw_id: str, token: str) -> UnitKind:
        try:
            return UnitKind(token)
        except ValueError:
            known = ", ".join(sorted(k.value for k in UnitKind))
            raise InvalidUnitIdError(
                raw_id, f"unknown kind {token!r}; expected one of: {known}"
            ) from None

    @staticmethod
    def _validate_segment(raw_id: str, segment: str) -> None:
        if _SEGMENT_RE.match(segment):
            return
        if segment != segment.lower():
            raise InvalidUnitIdError(
                raw_id,
                f"segment {segment!r} contains uppercase; unit ids are lowercase so that "
                "resolution does not depend on filesystem case sensitivity",
            )
        raise InvalidUnitIdError(
            raw_id,
            f"segment {segment!r} is not of the form [a-z0-9][a-z0-9._-]*",
        )

    @staticmethod
    def _validate_arity(raw_id: str, kind: UnitKind, segments: list[str]) -> None:
        if len(segments) in kind.arities:
            return
        expected = " or ".join(str(n) for n in kind.arities)
        raise InvalidUnitIdError(
            raw_id,
            f"{kind.value} takes {expected} segment(s) after the kind, got {len(segments)}; "
            f"expected {kind.template}",
        )

    @staticmethod
    def _validate_discriminator(raw_id: str, kind: UnitKind, segments: list[str]) -> None:
        allowed = kind.discriminators
        if not allowed or segments[0] in allowed:
            return
        raise InvalidUnitIdError(
            raw_id,
            f"{kind.value} must be followed by one of {', '.join(allowed)}; "
            f"got {segments[0]!r}. Expected {kind.template}",
        )

    def render(self) -> str:
        """The canonical string form. ``parse(render())`` round-trips."""
        return SEPARATOR.join((self.kind.value, *self.segments))

    def __str__(self) -> str:
        return self.render()
