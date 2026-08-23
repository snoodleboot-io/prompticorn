"""Rebuilding a generated tree from the lock, with no re-resolution (PRO-116).

This is the mechanism that makes generated output disposable. Every other part
of the source/generated wall tells you that a hand-edit is wrong; this is the
command that undoes one. The documented answer to any patch applied to a
generated file is *recompile, don't edit*, and that answer is only usable if
recompiling is a single command that provably lands back on the lock.

**No re-resolution** is the property that separates this from ``build``. A build
resolves the project as it stands and then records what it found. A regeneration
starts from what the lock already recorded, and refuses if the sources no longer
agree with it — because a rebuild from moved sources produces a tree the lock
does not describe, which is the opposite of what the caller asked for. Nothing
here writes the lock, on any path.

**No network** follows from the same rule. Resolution reads bundled and local
content only, and the check below is a comparison against the lock rather than a
fetch, so there is nothing to reach for even when real remote sources arrive.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from prompticorn.lockfile.drift_detector import DriftDetector
from prompticorn.lockfile.drift_report import DriftReport
from prompticorn.lockfile.lock_file import LockFile
from prompticorn.lockfile.lock_service import LockService
from prompticorn.regenerate.regeneration_report import RegenerationReport
from prompticorn.tool_outputs import ToolOutputManager
from prompticorn.verify.output_verifier import OutputVerifier

if TYPE_CHECKING:  # pragma: no cover - import kept out of the runtime graph
    from prompticorn.prompt_builder import PromptBuilder


@dataclass(frozen=True)
class RegenerationService:
    """Wipes a tool's generated tree and rebuilds it to match the lock.

    Attributes:
        root: The project root the lock's paths are relative to.
        tool: The tool whose outputs are regenerated.
        config: The loaded manifest, passed to the builder unchanged.
    """

    root: Path
    tool: str
    config: dict

    def regenerate(
        self, lock: LockFile, builder: PromptBuilder, resolved_at: str
    ) -> RegenerationReport:
        """Reproduce the locked tree, or refuse and touch nothing.

        Args:
            lock: The committed lock to reproduce.
            builder: The prompt builder for :attr:`tool`.
            resolved_at: Timestamp for the comparison resolution. Required by
                :class:`~prompticorn.lockfile.lock_file.LockFile` and otherwise
                unused: the resolved lock is compared and discarded, never
                written.

        Returns:
            What happened, including the post-rebuild verification.
        """
        drift = self._source_drift(lock, resolved_at)
        if not drift.is_clean:
            return RegenerationReport(drift=drift)

        removed = tuple(ToolOutputManager(self.root).remove_outputs_created_by(self.tool))
        rebuilt = tuple(builder.build(self.root, config=self.config, dry_run=False))
        verification = OutputVerifier(root=self.root, tool=self.tool).verify(lock)
        return RegenerationReport(
            drift=drift, verification=verification, removed=removed, rebuilt=rebuilt
        )

    def _source_drift(self, lock: LockFile, resolved_at: str) -> DriftReport:
        """Whether the inputs still match what the lock recorded.

        Resolved with no output roots deliberately. Output digests are about to
        be invalidated by the wipe, and
        :meth:`~prompticorn.lockfile.drift_detector.DriftDetector.compare`
        ignores them in any case — reading every generated file to build digests
        that are then discarded would be work done to answer no question.
        """
        current = LockService.resolve_current(self.root, self.config, resolved_at)
        return DriftDetector.compare(lock, current)
