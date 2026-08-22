"""The collected result of verifying a generated tree (PRO-115)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.lockfile.exit_code import ExitCode
from prompticorn.verify.verification_finding import VerificationFinding
from prompticorn.verify.verification_kind import VerificationKind


@dataclass(frozen=True)
class VerificationReport:
    """Every finding, grouped so each kind speaks in its own words.

    Grouping is not cosmetic, for the same reason it is not in ``DriftReport``: a
    run that finds both "a file is missing" and "a file was edited by hand" must
    not present them as a flat list of equals.
    """

    findings: tuple[VerificationFinding, ...] = ()

    @property
    def is_clean(self) -> bool:
        """Whether the generated tree matches the lock exactly."""
        return not self.findings

    @property
    def has_tampering(self) -> bool:
        """Whether anything found warrants investigation rather than a rebuild."""
        return any(finding.is_suspicious for finding in self.findings)

    @property
    def exit_code(self) -> ExitCode:
        """What this report means to the shell.

        Tampering outranks everything else present: a run that finds both a
        missing file and an edited one should exit on the edited one, because
        that is the finding a pipeline must not let through.
        """
        if self.is_clean:
            return ExitCode.CLEAN
        return ExitCode.TAMPERED if self.has_tampering else ExitCode.DRIFT

    @property
    def kinds(self) -> tuple[VerificationKind, ...]:
        """The kinds present, in the enum's declared order.

        Declared order rather than discovery order, so the same set of problems
        always reports the same way.
        """
        present = {finding.kind for finding in self.findings}
        return tuple(kind for kind in VerificationKind if kind in present)

    def of_kind(self, kind: VerificationKind) -> tuple[VerificationFinding, ...]:
        """Every finding of one kind, in the order found."""
        return tuple(finding for finding in self.findings if finding.kind is kind)

    def render(self) -> str:
        """A human-readable report, one section per kind.

        Suspicious kinds render last, so the most important finding is the one
        still on screen when the output stops scrolling.
        """
        if self.is_clean:
            return "Verified: every output matches the lock, and nothing extra exists."

        ordinary = [kind for kind in self.kinds if not kind.is_suspicious]
        suspicious = [kind for kind in self.kinds if kind.is_suspicious]
        return "\n\n".join(self._render_kind(kind) for kind in (*ordinary, *suspicious))

    def _render_kind(self, kind: VerificationKind) -> str:
        findings = self.of_kind(kind)
        marker = "!!" if kind.is_suspicious else "--"
        lines = [f"{marker} {kind.headline} ({len(findings)})"]
        lines.extend(f"     {finding.describe()}" for finding in findings)
        lines.append(f"     {kind.remediation}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.render()
