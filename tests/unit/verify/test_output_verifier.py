"""The three checks `prompticorn verify` runs (PRO-115).

Check 2 — "nothing extra exists" — is the one worth the most attention. A
verifier that only walks the lock's own list passes a tree with a rogue agent
added to it, because the rogue file is not in the list, so nothing looks at it.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from prompticorn.content.unit_id import UnitId
from prompticorn.lockfile.exit_code import ExitCode
from prompticorn.lockfile.lock_file import LockFile
from prompticorn.lockfile.locked_output import LockedOutput
from prompticorn.lockfile.locked_unit import LockedUnit
from prompticorn.provenance import OutputFormat, ProvenanceHeader, ProvenanceRecord
from prompticorn.verify import OutputVerifier, VerificationKind

_TOOL = "claude"


def _lock(*outputs: LockedOutput, units: tuple[LockedUnit, ...] = ()) -> LockFile:
    return LockFile(
        prompticorn_version="0.0.0",
        resolved_at="2026-01-01T00:00:00Z",
        outputs=outputs,
        units=units,
    )


class VerifierTestCase(unittest.TestCase):
    """Builds a small fake generated tree under .claude/, which is claude's root."""

    def setUp(self) -> None:
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / ".claude" / "agents").mkdir(parents=True)
        self.verifier = OutputVerifier(root=self.root, tool=_TOOL)

    def write(self, relative: str, body: str) -> LockedOutput:
        """Write a generated file and return the lock entry that describes it."""
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return LockedOutput(path=relative, digest=self.verifier.digest_of(relative))


class TestCleanTree(VerifierTestCase):
    def test_a_matching_tree_verifies(self) -> None:
        recorded = self.write(".claude/agents/code.md", "# Code\n")

        report = self.verifier.verify(_lock(recorded))

        self.assertTrue(report.is_clean)
        self.assertEqual(report.exit_code, ExitCode.CLEAN)

    def test_a_header_does_not_read_as_a_modification(self) -> None:
        """The digest covers the body with the header stripped, so a file
        carrying provenance still matches a lock entry for the same content."""
        recorded = self.write(".claude/agents/code.md", "# Code\n")
        path = self.root / ".claude/agents/code.md"
        record = ProvenanceRecord("agent/code", "builtin", "9.9.9", recorded.digest)
        path.write_text(
            ProvenanceHeader.render(path.read_text(), record, OutputFormat.MARKDOWN),
            encoding="utf-8",
        )

        self.assertTrue(self.verifier.verify(_lock(recorded)).is_clean)


class TestTampering(VerifierTestCase):
    def test_a_hand_edited_output_fails_and_names_the_file(self) -> None:
        recorded = self.write(".claude/agents/code.md", "# Code\n")
        (self.root / ".claude/agents/code.md").write_text("# Edited\n", encoding="utf-8")

        report = self.verifier.verify(_lock(recorded))

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].kind, VerificationKind.TAMPERED)
        self.assertEqual(report.findings[0].path, ".claude/agents/code.md")

    def test_tampering_exits_four_not_one(self) -> None:
        """4, not 2: click owns 2 for usage errors, and the highest-severity
        signal in the system must not fire on a mistyped flag."""
        recorded = self.write(".claude/agents/code.md", "# Code\n")
        (self.root / ".claude/agents/code.md").write_text("# Edited\n", encoding="utf-8")

        self.assertEqual(self.verifier.verify(_lock(recorded)).exit_code, ExitCode.TAMPERED)

    def test_the_finding_reports_both_digests(self) -> None:
        recorded = self.write(".claude/agents/code.md", "# Code\n")
        (self.root / ".claude/agents/code.md").write_text("# Edited\n", encoding="utf-8")

        detail = self.verifier.verify(_lock(recorded)).findings[0].detail

        self.assertIn(recorded.digest[:12], detail)

    def test_tampering_outranks_other_findings(self) -> None:
        """A run that finds both must exit on the one a pipeline cannot let through."""
        edited = self.write(".claude/agents/code.md", "# Code\n")
        (self.root / ".claude/agents/code.md").write_text("# Edited\n", encoding="utf-8")
        gone = LockedOutput(path=".claude/agents/absent.md", digest="a" * 64)

        report = self.verifier.verify(_lock(edited, gone))

        self.assertEqual(len(report.findings), 2)
        self.assertEqual(report.exit_code, ExitCode.TAMPERED)


class TestUnknownOutputs(VerifierTestCase):
    def test_an_extra_file_in_a_generated_root_fails(self) -> None:
        """Without this check, a rogue agent passes CI unnoticed."""
        recorded = self.write(".claude/agents/code.md", "# Code\n")
        (self.root / ".claude/agents/rogue.md").write_text("# Rogue\n", encoding="utf-8")

        report = self.verifier.verify(_lock(recorded))

        self.assertEqual(
            [(f.kind, f.path) for f in report.findings],
            [(VerificationKind.UNKNOWN, ".claude/agents/rogue.md")],
        )

    def test_an_extra_file_is_drift_not_tampering(self) -> None:
        recorded = self.write(".claude/agents/code.md", "# Code\n")
        (self.root / ".claude/agents/rogue.md").write_text("# Rogue\n", encoding="utf-8")

        self.assertEqual(self.verifier.verify(_lock(recorded)).exit_code, ExitCode.DRIFT)

    def test_files_outside_the_generated_roots_are_not_our_business(self) -> None:
        """A team's own files must not be reported as unexpected build output."""
        recorded = self.write(".claude/agents/code.md", "# Code\n")
        (self.root / "README.md").write_text("hand-maintained\n", encoding="utf-8")
        (self.root / "src").mkdir()
        (self.root / "src" / "app.py").write_text("print('hi')\n", encoding="utf-8")

        self.assertTrue(self.verifier.verify(_lock(recorded)).is_clean)

    def test_the_provenance_sidecar_is_not_an_unexpected_file(self) -> None:
        """It is bookkeeping about the build, not part of it."""
        recorded = self.write(".claude/agents/code.md", "# Code\n")
        sidecar = self.root / ".prompticorn" / "provenance.json"
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        sidecar.write_text("{}\n", encoding="utf-8")

        self.assertTrue(self.verifier.verify(_lock(recorded)).is_clean)


class TestMissingOutputs(VerifierTestCase):
    def test_a_deleted_output_fails_and_names_it(self) -> None:
        report = self.verifier.verify(_lock(LockedOutput(".claude/agents/gone.md", "a" * 64)))

        self.assertEqual(
            [(f.kind, f.path) for f in report.findings],
            [(VerificationKind.MISSING, ".claude/agents/gone.md")],
        )

    def test_a_missing_output_is_drift_not_tampering(self) -> None:
        report = self.verifier.verify(_lock(LockedOutput(".claude/agents/gone.md", "a" * 64)))

        self.assertEqual(report.exit_code, ExitCode.DRIFT)


class TestLockSelfConsistency(VerifierTestCase):
    def test_a_unit_without_a_digest_is_reported(self) -> None:
        """A lock that cannot answer 'did this source change' makes every other
        guarantee it offers conditional."""
        unit = LockedUnit(id=UnitId.parse("agent/code"), layer="builtin", digest="")

        report = self.verifier.verify(_lock(units=(unit,)))

        self.assertEqual(
            [(f.kind, f.path) for f in report.findings],
            [(VerificationKind.MISSING, "agent/code")],
        )

    def test_a_complete_lock_passes(self) -> None:
        unit = LockedUnit(id=UnitId.parse("agent/code"), layer="builtin", digest="b" * 64)

        self.assertTrue(self.verifier.verify(_lock(units=(unit,))).is_clean)


class TestEveryCheckRuns(VerifierTestCase):
    def test_all_three_kinds_are_collected_in_one_run(self) -> None:
        """Reporting the first of nine problems turns one fix into nine runs."""
        edited = self.write(".claude/agents/code.md", "# Code\n")
        (self.root / ".claude/agents/code.md").write_text("# Edited\n", encoding="utf-8")
        (self.root / ".claude/agents/rogue.md").write_text("# Rogue\n", encoding="utf-8")
        gone = LockedOutput(path=".claude/agents/absent.md", digest="a" * 64)

        report = self.verifier.verify(_lock(edited, gone))

        self.assertEqual(
            set(report.kinds),
            {VerificationKind.MISSING, VerificationKind.TAMPERED, VerificationKind.UNKNOWN},
        )


if __name__ == "__main__":
    unittest.main()
