"""The comparison operators a version constraint can use (PRO-107)."""

from __future__ import annotations

from enum import Enum

from prompticorn.artifact.semantic_version import SemanticVersion


class ComparisonOperator(Enum):
    """How a constraint compares a candidate version against its operand."""

    GREATER_EQUAL = ">="
    GREATER = ">"
    LESS_EQUAL = "<="
    LESS = "<"
    EQUAL = "=="
    NOT_EQUAL = "!="

    @classmethod
    def symbols_longest_first(cls) -> tuple[str, ...]:
        """Operator symbols ordered so that longer ones match first.

        Without this ordering a naive scan reads ``>=2.1`` as ``>`` followed by
        the version ``=2.1``, which then fails to parse for the wrong reason.
        """
        return tuple(sorted((member.value for member in cls), key=len, reverse=True))

    def compare(self, candidate: SemanticVersion, operand: SemanticVersion) -> bool:
        """Whether ``candidate <op> operand`` holds under semver precedence.

        Pure comparison: the prerelease-visibility rule lives on the range, not
        here, because it is a property of the range as a whole rather than of
        any single comparator.
        """
        match self:
            case ComparisonOperator.GREATER_EQUAL:
                return candidate >= operand
            case ComparisonOperator.GREATER:
                return candidate > operand
            case ComparisonOperator.LESS_EQUAL:
                return candidate <= operand
            case ComparisonOperator.LESS:
                return candidate < operand
            case ComparisonOperator.EQUAL:
                return candidate == operand
            case ComparisonOperator.NOT_EQUAL:
                return candidate != operand
