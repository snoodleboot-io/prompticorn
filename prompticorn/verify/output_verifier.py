"""Checking that a generated tree still matches the lock (PRO-115).

This is the gate that makes the source/generated wall real rather than a
convention people are asked to respect. It answers three questions, and all
three matter:

1. Does every output the lock names still exist, with the content it recorded?
2. Is there anything in the generated roots the lock does *not* know about?
3. Does the lock reference any unit it does not itself carry a digest for?

Question 2 is the one that is easy to leave out and expensive to omit. A check
that only walked the lock's own list would pass a tree with a rogue agent added
to ``.claude/agents/`` — the file is not in the lock, so nothing looks at it, so
nothing complains. Verification that cannot see what it was not told about is
not verification.

**Digests are taken over the body with the provenance header stripped.** The
header contains the artifact version, so hashing it would make an output's
digest change on a version bump that touched no content — the same instability
that made the golden corpus unstable in PRO-112. Stripping also makes this agree
with `.prompticorn/provenance.json`, which digests the same way.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from prompticorn.lockfile.lock_file import LockFile
from prompticorn.provenance.output_format import OutputFormat
from prompticorn.provenance.provenance_header import ProvenanceHeader
from prompticorn.tool_outputs import TOOL_OUTPUT_FILES
from prompticorn.verify.verification_finding import VerificationFinding
from prompticorn.verify.verification_kind import VerificationKind
from prompticorn.verify.verification_report import VerificationReport

# Bookkeeping prompticorn writes about the build rather than as part of it. It
# is not in any tool's create set, so it is already outside the roots walked
# below; naming it here states the intent rather than relying on that.
_NOT_AN_OUTPUT = frozenset({".prompticorn"})


@dataclass(frozen=True)
class OutputVerifier:
    """Compares a generated tree against the lock that describes it.

    Attributes:
        root: The project root the lock's paths are relative to.
        tool: The tool whose output roots bound the "nothing extra" check. Files
            a team hand-maintains outside those roots are none of our business.
    """

    root: Path
    tool: str

    def verify(self, lock: LockFile) -> VerificationReport:
        """Run all three checks and collect every finding.

        Every check runs even when an earlier one failed. Reporting the first of
        nine problems and hiding the rest turns one fix into nine runs.
        """
        findings: list[VerificationFinding] = [
            *self._check_recorded_outputs(lock),
            *self._check_for_unknown_outputs(lock),
            *self._check_lock_is_self_consistent(lock),
        ]
        return VerificationReport(findings=tuple(findings))

    def digest_of(self, relative: str) -> str:
        """The digest an output currently has, header stripped."""
        text = (self.root / relative).read_text(encoding="utf-8")
        return ProvenanceHeader.body_digest(text, OutputFormat.of(relative))

    def _check_recorded_outputs(self, lock: LockFile) -> list[VerificationFinding]:
        """Check 1: everything the lock names exists and still matches."""
        findings: list[VerificationFinding] = []
        for output in lock.outputs:
            path = self.root / output.path
            if not path.is_file():
                findings.append(VerificationFinding(VerificationKind.MISSING, output.path))
                continue
            try:
                actual = self.digest_of(output.path)
            except (UnicodeDecodeError, OSError) as error:
                findings.append(
                    VerificationFinding(
                        VerificationKind.MISSING, output.path, f"unreadable: {error}"
                    )
                )
                continue
            if actual != output.digest:
                findings.append(
                    VerificationFinding(
                        VerificationKind.TAMPERED,
                        output.path,
                        f"lock {output.digest[:12]}…, file {actual[:12]}…",
                    )
                )
        return findings

    def _check_for_unknown_outputs(self, lock: LockFile) -> list[VerificationFinding]:
        """Check 2: nothing exists in the generated roots that the lock omits.

        Without this, adding a rogue agent to ``.claude/agents/`` passes
        unnoticed, which defeats the point of verifying at all.
        """
        known = {output.path for output in lock.outputs}
        return [
            VerificationFinding(VerificationKind.UNKNOWN, relative)
            for relative in self._generated_files()
            if relative not in known
        ]

    def _check_lock_is_self_consistent(self, lock: LockFile) -> list[VerificationFinding]:
        """Check 3: the lock carries a digest for every unit it references.

        A lock missing a unit digest cannot answer "did this source change",
        which makes every other guarantee it offers conditional.
        """
        return [
            VerificationFinding(
                VerificationKind.MISSING,
                unit.id.render(),
                "the lock references this unit but records no digest for it",
            )
            for unit in lock.units
            if not unit.digest
        ]

    def _generated_files(self) -> list[str]:
        """Every file under this tool's output roots, sorted.

        Sorted so the report does not depend on filesystem ordering — the same
        tree must produce the same report twice running.
        """
        created = TOOL_OUTPUT_FILES.get(self.tool, {}).get("create", set())
        found: set[str] = set()
        for entry in created:
            target = self.root / entry.rstrip("/")
            if target.is_file():
                found.add(target.relative_to(self.root).as_posix())
            elif target.is_dir():
                found.update(
                    path.relative_to(self.root).as_posix()
                    for path in target.rglob("*")
                    if path.is_file()
                )
        return sorted(
            relative for relative in found if relative.split("/", 1)[0] not in _NOT_AN_OUTPUT
        )
