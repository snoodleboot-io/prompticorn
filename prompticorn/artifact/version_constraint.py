"""One comparator within a version range (PRO-107)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.artifact.comparison_operator import ComparisonOperator
from prompticorn.artifact.errors import InvalidSemanticVersionError, InvalidVersionRangeError
from prompticorn.artifact.semantic_version import SemanticVersion


@dataclass(frozen=True)
class VersionConstraint:
    """An operator paired with the version it compares against.

    ``>=2.1`` parses to ``GREATER_EQUAL`` and ``2.1.0`` — the operand is
    completed with zeros, because a range operand is a boundary rather than an
    identity and ``>=2.1`` unambiguously means "2.1.0 or later".

    A bare version with no operator means exact equality, which is the form a
    lock file uses.

    Attributes:
        operator: How to compare.
        operand: The boundary version, always fully qualified.
    """

    operator: ComparisonOperator
    operand: SemanticVersion

    @classmethod
    def parse(cls, raw_constraint: str, raw_range: str) -> VersionConstraint:
        """Parse one comparator.

        Args:
            raw_constraint: The single comparator, e.g. ``>=2.1``.
            raw_range: The full range it came from, so errors quote what the
                author actually typed rather than a fragment of it.

        Returns:
            The parsed constraint.

        Raises:
            InvalidVersionRangeError: With a reason naming what to fix.
        """
        text = raw_constraint.strip()
        if not text:
            raise InvalidVersionRangeError(raw_range, "contains an empty comparator")

        operator, operand_text = cls._split_operator(text)
        if not operand_text:
            raise InvalidVersionRangeError(
                raw_range, f"comparator {text!r} has an operator but no version"
            )

        try:
            operand = SemanticVersion.parse_partial(operand_text)
        except InvalidSemanticVersionError as exc:
            # Re-typed rather than propagated: the author is editing a range, and
            # an error about a "semantic version" they never wrote in isolation
            # sends them looking in the wrong place. The underlying reason is
            # kept so the specific defect is not lost.
            raise InvalidVersionRangeError(
                raw_range, f"comparator {text!r} has an unparseable version: {exc.reason}"
            ) from exc

        return cls(operator=operator, operand=operand)

    @staticmethod
    def _split_operator(text: str) -> tuple[ComparisonOperator, str]:
        """Peel a leading operator off, defaulting to exact equality."""
        for symbol in ComparisonOperator.symbols_longest_first():
            if text.startswith(symbol):
                return ComparisonOperator(symbol), text[len(symbol) :].strip()
        return ComparisonOperator.EQUAL, text

    def allows(self, candidate: SemanticVersion) -> bool:
        """Whether ``candidate`` satisfies this comparator on its own.

        Prerelease visibility is decided by the enclosing
        :class:`~prompticorn.artifact.version_range.VersionRange`, not here.
        """
        return self.operator.compare(candidate, self.operand)

    def render(self) -> str:
        """The canonical string form. ``parse(render())`` round-trips.

        An exact constraint renders with its explicit ``==`` rather than as a
        bare version, so a rendered range never depends on the reader knowing
        that a missing operator means equality.
        """
        return f"{self.operator.value}{self.operand.render()}"

    def __str__(self) -> str:
        return self.render()
