"""One thing verification found wrong (PRO-115)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.verify.verification_kind import VerificationKind


@dataclass(frozen=True)
class VerificationFinding:
    """A single verification failure, tied to the file it concerns.

    Attributes:
        kind: What sort of failure this is.
        path: Repository-relative POSIX path of the file concerned. Always
            present — a finding a reader cannot locate is not actionable.
        detail: Optional extra context, such as the digests that disagreed.
    """

    kind: VerificationKind
    path: str
    detail: str = ""

    @property
    def is_suspicious(self) -> bool:
        """Whether this finding warrants investigation rather than a rebuild."""
        return self.kind.is_suspicious

    def describe(self) -> str:
        """One line naming the file and, when useful, what disagreed."""
        return f"{self.path}{f' ({self.detail})' if self.detail else ''}"
