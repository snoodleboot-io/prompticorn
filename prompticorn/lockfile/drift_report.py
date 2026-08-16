"""The collected result of comparing a lock against reality (PRO-111)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.lockfile.drift import Drift
from prompticorn.lockfile.drift_kind import DriftKind


@dataclass(frozen=True)
class DriftReport:
    """Every divergence found, grouped so each kind speaks in its own words.

    Grouping is not cosmetic. A run that finds both "you edited your manifest"
    and "a pinned source changed underneath you" must not present them as a flat
    list of equals — the second is the one that should stop the reader.
    """

    drifts: tuple[Drift, ...] = ()

    @property
    def is_clean(self) -> bool:
        """Whether reality matches the lock."""
        return not self.drifts

    @property
    def has_suspicious_drift(self) -> bool:
        """Whether anything found warrants investigation rather than a re-lock."""
        return any(drift.is_suspicious for drift in self.drifts)

    @property
    def kinds(self) -> tuple[DriftKind, ...]:
        """The kinds present, in the enum's declared order.

        Declared order rather than discovery order, so the same set of problems
        always reports the same way.
        """
        present = {drift.kind for drift in self.drifts}
        return tuple(kind for kind in DriftKind if kind in present)

    def of_kind(self, kind: DriftKind) -> tuple[Drift, ...]:
        """Every drift of one kind, in the order found."""
        return tuple(drift for drift in self.drifts if drift.kind is kind)

    def render(self) -> str:
        """A human-readable report, one section per kind.

        Suspicious kinds are rendered last, so the most important finding is the
        one still on screen when the output stops scrolling.
        """
        if self.is_clean:
            return "No drift: outputs match the lock."

        ordinary = [kind for kind in self.kinds if not kind.is_suspicious]
        suspicious = [kind for kind in self.kinds if kind.is_suspicious]

        sections = [self._render_kind(kind) for kind in (*ordinary, *suspicious)]
        return "\n\n".join(sections)

    def _render_kind(self, kind: DriftKind) -> str:
        drifts = self.of_kind(kind)
        marker = "!!" if kind.is_suspicious else "--"
        lines = [f"{marker} {kind.headline} ({len(drifts)})"]
        lines.extend(f"     {drift.describe()}" for drift in drifts)
        lines.append(f"     {kind.remediation}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.render()
