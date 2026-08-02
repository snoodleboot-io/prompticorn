"""Semantic Versioning 2.0.0 — parsing, rendering, and precedence (PRO-107).

Implemented here rather than taken from a dependency because semver 2.0.0 is a
frozen specification: there is no upstream drift to track, and owning it lets
rejection surface as the module's typed error rather than a bare ``ValueError``.

``packaging`` is present in the lock file but implements **PEP 440**, whose
precedence rules differ from semver's (``1.0.0-rc.1`` and ``1.0.0rc1`` are not
the same grammar, and PEP 440 has no build metadata). It is not a substitute.

**Build metadata is excluded from precedence** (spec §10). ``1.0.0+build.1`` and
``1.0.0+build.2`` therefore compare equal — see :meth:`SemanticVersion.__eq__`
for why equality has to agree with ordering here. ``render`` still round-trips
build metadata faithfully; only *comparison* ignores it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from prompticorn.artifact.errors import InvalidSemanticVersionError

# The official regex from semver.org, which encodes the rules that are easy to
# get wrong by hand: no leading zeros on numeric identifiers, prerelease
# identifiers that are alphanumeric may carry leading zeros, build metadata is
# unrestricted beyond its charset.
_SEMVER_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)"
    r"\.(?P<minor>0|[1-9]\d*)"
    r"\.(?P<patch>0|[1-9]\d*)"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

# Range operands may omit minor and patch (`>=2.1` means `>=2.1.0`). Deliberately
# separate from _SEMVER_RE: an identity is always fully qualified, and letting a
# lock entry parse as `2.1` would make the pinned version ambiguous.
_PARTIAL_RE = re.compile(
    r"^(?P<major>0|[1-9]\d*)"
    r"(?:\.(?P<minor>0|[1-9]\d*))?"
    r"(?:\.(?P<patch>0|[1-9]\d*))?"
    r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)

_IDENTIFIER_SEPARATOR = "."
_PRERELEASE_PREFIX = "-"
_BUILD_PREFIX = "+"

# Sort classes for a prerelease identifier. The spec orders numeric identifiers
# below alphanumeric ones, so the class is the first element of the sort key.
_NUMERIC_CLASS = 0
_ALPHANUMERIC_CLASS = 1


def _identifier_key(identifier: str) -> tuple[int, int, str]:
    """Sort key for one prerelease identifier.

    Numeric identifiers compare numerically, alphanumeric ones lexically in
    ASCII, and numeric always sorts below alphanumeric. Encoding all three rules
    in a single tuple lets Python's own tuple comparison do the rest — including
    "a larger set of fields outranks a smaller one when the prefix is equal",
    which falls out of comparing tuples of different length.
    """
    if identifier.isdigit():
        return (_NUMERIC_CLASS, int(identifier), "")
    return (_ALPHANUMERIC_CLASS, 0, identifier)


@dataclass(frozen=True, eq=False)
class SemanticVersion:
    """A parsed semver 2.0.0 version.

    Immutable and hashable, so versions work as dict keys and set members.

    ``eq=False`` because the generated ``__eq__`` would compare ``build`` and so
    disagree with ordering, producing a type where ``a < b``, ``b < a`` and
    ``a == b`` are simultaneously false. See :meth:`__eq__`.

    Attributes:
        major: Breaking-change component.
        minor: Backwards-compatible feature component.
        patch: Backwards-compatible fix component.
        prerelease: Dot-separated prerelease identifiers, empty for a release.
        build: Dot-separated build-metadata identifiers. Carried for
            round-tripping; ignored by every comparison.
    """

    major: int
    minor: int
    patch: int
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()

    @classmethod
    def parse(cls, raw_version: str) -> SemanticVersion:
        """Parse a fully-qualified ``major.minor.patch`` version.

        Args:
            raw_version: The candidate version.

        Returns:
            The parsed value object.

        Raises:
            InvalidSemanticVersionError: With a reason naming what to fix.
        """
        return cls._parse_with(raw_version, _SEMVER_RE, partial=False)

    @classmethod
    def parse_partial(cls, raw_version: str) -> SemanticVersion:
        """Parse a possibly-abbreviated version, completing it with zeros.

        ``2.1`` becomes ``2.1.0`` and ``3`` becomes ``3.0.0``. **For range
        operands only** — an identity must always be fully qualified, so
        :meth:`parse` does not accept these forms.
        """
        return cls._parse_with(raw_version, _PARTIAL_RE, partial=True)

    @classmethod
    def _parse_with(
        cls, raw_version: str, pattern: re.Pattern[str], partial: bool
    ) -> SemanticVersion:
        if not isinstance(raw_version, str):
            raise InvalidSemanticVersionError(
                str(raw_version), f"expected a string, got {type(raw_version).__name__}"
            )
        if not raw_version:
            raise InvalidSemanticVersionError(raw_version, "is empty")

        match = pattern.match(raw_version)
        if match is None:
            raise InvalidSemanticVersionError(
                raw_version, cls._rejection_reason(raw_version, partial)
            )

        prerelease = match.group("prerelease")
        build = match.group("build")
        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor") or 0),
            patch=int(match.group("patch") or 0),
            prerelease=tuple(prerelease.split(_IDENTIFIER_SEPARATOR)) if prerelease else (),
            build=tuple(build.split(_IDENTIFIER_SEPARATOR)) if build else (),
        )

    @staticmethod
    def _rejection_reason(raw_version: str, partial: bool) -> str:
        """Name the actual defect rather than restating the grammar.

        The regex is all-or-nothing, so without these the author of ``v1.2.3``
        or ``01.2.3`` is told only that their input "is not of the form
        major.minor.patch", which is true of neither.
        """
        if raw_version != raw_version.strip():
            return "has leading or trailing whitespace"
        if raw_version.startswith("v"):
            return "starts with 'v'; versions are written without a leading 'v'"
        if raw_version.startswith(_PRERELEASE_PREFIX):
            # Otherwise the core split below sees an empty major and reports
            # "has 1 numeric component", which sends the author looking at the
            # wrong end of the string.
            return "starts with '-'; versions are unsigned and begin with the major number"
        core = raw_version.split(_PRERELEASE_PREFIX, 1)[0].split(_BUILD_PREFIX, 1)[0]
        numbers = core.split(_IDENTIFIER_SEPARATOR)
        if any(part.startswith("0") and len(part) > 1 and part.isdigit() for part in numbers):
            return "has a leading zero in a numeric component"
        if not partial and len(numbers) < 3:
            return f"has {len(numbers)} numeric component(s); expected major.minor.patch"
        if len(numbers) > 3:
            return f"has {len(numbers)} numeric components; expected at most major.minor.patch"
        if _PRERELEASE_PREFIX in raw_version and raw_version.endswith(_PRERELEASE_PREFIX):
            return "ends with '-'; the prerelease part is empty"
        if _BUILD_PREFIX in raw_version and raw_version.endswith(_BUILD_PREFIX):
            return "ends with '+'; the build-metadata part is empty"
        return (
            "is not of the form major.minor.patch[-prerelease][+build] "
            "with numeric components free of leading zeros"
        )

    @property
    def core(self) -> tuple[int, int, int]:
        """The ``(major, minor, patch)`` triple, ignoring prerelease and build.

        Range matching needs this to answer "does this comparator name a
        prerelease of the *same* release as the candidate", which is what gates
        prereleases out of ordinary ranges.
        """
        return (self.major, self.minor, self.patch)

    @property
    def is_prerelease(self) -> bool:
        """Whether this version carries prerelease identifiers."""
        return bool(self.prerelease)

    @property
    def _precedence_key(self) -> tuple[int, int, int, int, tuple[tuple[int, int, str], ...]]:
        """Everything the spec says participates in precedence, in order.

        The fourth element encodes "a prerelease sorts below its own release":
        an absent prerelease ranks above a present one, so ``1.0.0-rc.1`` is
        less than ``1.0.0``. ``build`` is absent by design.
        """
        has_prerelease = 0 if self.prerelease else 1
        identifiers = tuple(_identifier_key(part) for part in self.prerelease)
        return (self.major, self.minor, self.patch, has_prerelease, identifiers)

    def render(self) -> str:
        """The canonical string form. ``parse(render())`` round-trips.

        Build metadata is preserved even though it never affects precedence:
        dropping it would lose information the author wrote down.
        """
        rendered = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            rendered += _PRERELEASE_PREFIX + _IDENTIFIER_SEPARATOR.join(self.prerelease)
        if self.build:
            rendered += _BUILD_PREFIX + _IDENTIFIER_SEPARATOR.join(self.build)
        return rendered

    def __eq__(self, other: object) -> bool:
        """Precedence equality: build metadata is ignored.

        The spec defines equality through precedence, and two versions differing
        only in build metadata have equal precedence. Comparing ``build`` here
        instead would contradict :meth:`__lt__`, leaving pairs that are neither
        ordered nor equal — and any sort or dedupe over them would be junk.
        """
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._precedence_key == other._precedence_key

    def __hash__(self) -> int:
        """Agrees with :meth:`__eq__`, so equal versions share a bucket."""
        return hash(self._precedence_key)

    def __lt__(self, other: SemanticVersion) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._precedence_key < other._precedence_key

    def __le__(self, other: SemanticVersion) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._precedence_key <= other._precedence_key

    def __gt__(self, other: SemanticVersion) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._precedence_key > other._precedence_key

    def __ge__(self, other: SemanticVersion) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return self._precedence_key >= other._precedence_key

    def __str__(self) -> str:
        return self.render()
