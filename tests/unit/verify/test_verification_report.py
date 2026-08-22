"""How verification findings are grouped and reported (PRO-115)."""

import unittest

from prompticorn.lockfile.exit_code import ExitCode
from prompticorn.verify import VerificationFinding, VerificationKind, VerificationReport

_TAMPERED = VerificationFinding(VerificationKind.TAMPERED, "a.md", "lock aaa…, file bbb…")
_MISSING = VerificationFinding(VerificationKind.MISSING, "b.md")
_UNKNOWN = VerificationFinding(VerificationKind.UNKNOWN, "c.md")


class TestExitCode(unittest.TestCase):
    def test_clean_is_zero(self) -> None:
        self.assertEqual(VerificationReport().exit_code, ExitCode.CLEAN)

    def test_ordinary_findings_are_drift(self) -> None:
        report = VerificationReport((_MISSING, _UNKNOWN))

        self.assertEqual(report.exit_code, ExitCode.DRIFT)

    def test_tampering_wins_over_drift(self) -> None:
        report = VerificationReport((_MISSING, _TAMPERED, _UNKNOWN))

        self.assertEqual(report.exit_code, ExitCode.TAMPERED)

    def test_two_is_never_returned(self) -> None:
        """click owns 2 for usage errors; no verification outcome may claim it."""
        codes = {
            VerificationReport().exit_code,
            VerificationReport((_MISSING,)).exit_code,
            VerificationReport((_TAMPERED,)).exit_code,
        }

        self.assertNotIn(2, {code.value for code in codes})


class TestRendering(unittest.TestCase):
    def test_a_clean_report_says_both_halves(self) -> None:
        """Not just 'outputs match' — 'and nothing extra exists' is the other
        half of the guarantee, and the half people forget is being checked."""
        rendered = VerificationReport().render()

        self.assertIn("matches the lock", rendered)
        self.assertIn("nothing extra", rendered)

    def test_the_suspicious_section_renders_last(self) -> None:
        """The most important finding should be the one still on screen when
        the output stops scrolling."""
        rendered = VerificationReport((_TAMPERED, _MISSING, _UNKNOWN)).render()

        self.assertGreater(
            rendered.index(VerificationKind.TAMPERED.headline),
            rendered.index(VerificationKind.MISSING.headline),
        )

    def test_tampering_is_marked_differently_from_ordinary_findings(self) -> None:
        rendered = VerificationReport((_TAMPERED, _MISSING)).render()

        self.assertIn(f"!! {VerificationKind.TAMPERED.headline}", rendered)
        self.assertIn(f"-- {VerificationKind.MISSING.headline}", rendered)

    def test_every_path_appears(self) -> None:
        rendered = VerificationReport((_TAMPERED, _MISSING, _UNKNOWN)).render()

        for path in ("a.md", "b.md", "c.md"):
            self.assertIn(path, rendered)

    def test_each_kind_carries_its_own_remediation(self) -> None:
        rendered = VerificationReport((_MISSING, _UNKNOWN)).render()

        self.assertIn(VerificationKind.MISSING.remediation, rendered)
        self.assertIn(VerificationKind.UNKNOWN.remediation, rendered)

    def test_kinds_report_in_declared_order_not_discovery_order(self) -> None:
        """The same set of problems must always report the same way."""
        forward = VerificationReport((_MISSING, _TAMPERED, _UNKNOWN)).kinds
        backward = VerificationReport((_UNKNOWN, _TAMPERED, _MISSING)).kinds

        self.assertEqual(forward, backward)


class TestKindSemantics(unittest.TestCase):
    def test_only_tampering_is_suspicious(self) -> None:
        suspicious = {kind for kind in VerificationKind if kind.is_suspicious}

        self.assertEqual(suspicious, {VerificationKind.TAMPERED})

    def test_tampering_remediation_says_not_to_hand_patch(self) -> None:
        """The advice that matters is 'move it into source', not 'rebuild'."""
        self.assertIn("source", VerificationKind.TAMPERED.remediation)

    def test_every_kind_has_a_headline_and_remediation(self) -> None:
        for kind in VerificationKind:
            with self.subTest(kind=kind):
                self.assertTrue(kind.headline)
                self.assertTrue(kind.remediation)


if __name__ == "__main__":
    unittest.main()
