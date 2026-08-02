"""A conjunction of version constraints, and the rules for matching (PRO-107).

A range is comma-separated comparators combined with **AND**: ``>=2.1,<3`` means
"at least 2.1.0 and below 3.0.0". There is no ``||`` — a single manifest entry
naming two disjoint acceptable windows is a smell, and leaving it out keeps
resolution decidable by inspection.

Precedence rules
----------------

Comparison follows semver 2.0.0 precedence exactly (see
:mod:`prompticorn.artifact.semantic_version`), with one rule layered on top:

**Prereleases are opt-in.** A prerelease candidate satisfies a range only when
some comparator in that range *itself* names a prerelease of the same
``major.minor.patch``. So:

- ``>=1.0.0`` does **not** match ``2.0.0-alpha`` — the range names no prerelease.
- ``>=1.0.0-rc.1`` **does** match ``1.0.0-rc.2`` — same release, and the range
  opted in.
- ``>=1.0.0-rc.1`` does **not** match ``2.0.0-alpha`` — a different release, so
  the opt-in does not carry over.

Without this, every open-ended range silently enrolls its users in unreleased
versions: ``>=1.0.0`` would match the first ``2.0.0-alpha`` published, which is
never what the author meant. This is the npm and Cargo convention.

The gate is evaluated over the range as a whole rather than per comparator,
because ``>=1.0.0-rc.1,<2`` must accept ``1.0.0-rc.2``: the second comparator
names no prerelease, and requiring every comparator to opt in would reject it.
"""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.artifact.errors import InvalidVersionRangeError
from prompticorn.artifact.semantic_version import SemanticVersion
from prompticorn.artifact.version_constraint import VersionConstraint

_CONSTRAINT_SEPARATOR = ","


@dataclass(frozen=True)
class VersionRange:
    """A set of constraints every matching version must satisfy.

    Attributes:
        constraints: The comparators, in the order written. At least one.
    """

    constraints: tuple[VersionConstraint, ...]

    @classmethod
    def parse(cls, raw_range: str) -> VersionRange:
        """Parse a comma-separated range.

        Args:
            raw_range: The candidate range, e.g. ``>=2.1,<3``.

        Returns:
            The parsed value object.

        Raises:
            InvalidVersionRangeError: With a reason naming what to fix.
        """
        if not isinstance(raw_range, str):
            raise InvalidVersionRangeError(
                str(raw_range), f"expected a string, got {type(raw_range).__name__}"
            )
        if not raw_range.strip():
            raise InvalidVersionRangeError(raw_range, "is empty")

        parts = raw_range.split(_CONSTRAINT_SEPARATOR)
        constraints = tuple(VersionConstraint.parse(part, raw_range) for part in parts)
        return cls(constraints=constraints)

    @classmethod
    def exact(cls, version: SemanticVersion) -> VersionRange:
        """The range matching exactly one version — what a lock file pins to."""
        return cls.parse(version.render())

    def contains(self, candidate: SemanticVersion) -> bool:
        """Whether ``candidate`` satisfies every constraint.

        Applies the prerelease opt-in rule documented in the module docstring
        before consulting the comparators.
        """
        if candidate.is_prerelease and not self._admits_prereleases_of(candidate):
            return False
        return all(constraint.allows(candidate) for constraint in self.constraints)

    def _admits_prereleases_of(self, candidate: SemanticVersion) -> bool:
        """Whether any comparator opted this candidate's release into prereleases."""
        return any(
            constraint.operand.is_prerelease and constraint.operand.core == candidate.core
            for constraint in self.constraints
        )

    def render(self) -> str:
        """The canonical string form. ``parse(render())`` round-trips."""
        return _CONSTRAINT_SEPARATOR.join(constraint.render() for constraint in self.constraints)

    def __str__(self) -> str:
        return self.render()
