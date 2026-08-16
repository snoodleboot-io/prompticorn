"""One classified divergence, with the evidence for it (PRO-111)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.lockfile.drift_kind import DriftKind

_ABSENT = "(absent)"
_SHORT_DIGEST = 12


@dataclass(frozen=True)
class Drift:
    """A single difference between what the lock recorded and what is true now.

    Carries expected and actual side by side because "something changed" is not
    actionable. A user looking at this needs to see *what* it was and *what it
    became* without going and computing digests themselves.

    Attributes:
        kind: Which of the four conditions this is.
        subject: What drifted — an artifact identity, a unit id, or a filename.
        expected: The value the lock recorded, or None if there was none.
        actual: The value found now, or None if it has gone.
    """

    kind: DriftKind
    subject: str
    expected: str | None
    actual: str | None

    @property
    def is_suspicious(self) -> bool:
        """Whether this warrants investigation rather than a re-lock."""
        return self.kind.is_suspicious

    def describe(self) -> str:
        """A one-line account of this specific difference."""
        return f"{self.subject}: {_short(self.expected)} -> {_short(self.actual)}"

    def __str__(self) -> str:
        return f"[{self.kind.value}] {self.describe()}"


def _short(value: str | None) -> str:
    """Digests abbreviated, everything else left alone.

    A full 64-character hash twice on one line pushes the part that differs off
    the edge of a terminal, which is where it is least likely to be read.
    """
    if value is None:
        return _ABSENT
    if len(value) == 64 and all(character in "0123456789abcdef" for character in value):
        return value[:_SHORT_DIGEST]
    return value
