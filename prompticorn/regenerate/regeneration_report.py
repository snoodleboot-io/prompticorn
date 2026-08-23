"""The collected result of regenerating a tree from the lock (PRO-116)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.lockfile.drift_report import DriftReport
from prompticorn.lockfile.exit_code import ExitCode
from prompticorn.verify.verification_report import VerificationReport


@dataclass(frozen=True)
class RegenerationReport:
    """What a regeneration did, and whether it landed where the lock says.

    A regeneration can fail in two places, and they mean opposite things. Before
    the rebuild, drift means the *sources* moved, so reproducing the locked tree
    is impossible and nothing is touched. After the rebuild, a failed
    verification means the sources are exactly what the lock recorded and the
    build still produced something else — which is a defect in prompticorn, not
    in the project.

    Attributes:
        drift: Divergence between the lock and the current sources. Non-empty
            means the rebuild was refused, and ``removed`` and ``rebuilt`` are
            empty.
        verification: The post-rebuild check against the lock, or None when the
            rebuild never ran.
        removed: What the wipe deleted, as reported by the output manager.
        rebuilt: What the builder wrote.
    """

    drift: DriftReport
    verification: VerificationReport | None = None
    removed: tuple[str, ...] = ()
    rebuilt: tuple[str, ...] = ()

    @property
    def refused(self) -> bool:
        """Whether the sources moved, so nothing was regenerated."""
        return not self.drift.is_clean

    @property
    def is_clean(self) -> bool:
        """Whether the tree now matches the lock exactly."""
        return self.verification is not None and self.verification.is_clean

    @property
    def exit_code(self) -> ExitCode:
        """What this report means to the shell.

        A refusal is DRIFT: the lock and the project disagree about their
        inputs, which is the same condition ``build --frozen`` reports. After a
        rebuild the verification's own code stands, so a tree that still fails
        to match reports it in the verifier's terms rather than being flattened
        into one number here.
        """
        if self.refused:
            return ExitCode.DRIFT
        if self.verification is None:
            return ExitCode.DRIFT
        return self.verification.exit_code

    def render(self) -> str:
        """A human-readable account of what happened."""
        if self.refused:
            return (
                "Refusing to regenerate: the sources no longer match the lock, so "
                "rebuilding would produce a tree the lock does not describe.\n\n"
                f"{self.drift.render()}\n\n"
                "Run `prompticorn build` to re-resolve and re-lock, or restore the "
                "sources the lock names."
            )

        assert self.verification is not None
        summary = (
            f"Regenerated from the lock: removed {len(self.removed)} path(s), "
            f"wrote {len(self.rebuilt)}."
        )
        if self.verification.is_clean:
            return f"{summary}\nThe tree matches the lock."
        return (
            f"{summary}\n\n{self.verification.render()}\n\n"
            "The sources match the lock and the rebuild still did not. That is a "
            "reproducibility defect in prompticorn, not in this project — please "
            "report it."
        )

    def __str__(self) -> str:
        return self.render()
