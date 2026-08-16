"""How drift is presented (PRO-111).

AC 1 requires each kind to be "named distinctly in output". The point is not
cosmetic: a run that finds both "you edited your manifest" and "a pinned source
changed underneath you" must not present them as a flat list of equals.
"""

import pytest

from prompticorn.lockfile import Drift, DriftKind, DriftReport

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64


def drift(kind: DriftKind, subject: str = "thing") -> Drift:
    return Drift(kind, subject, DIGEST_A, DIGEST_B)


def test_a_clean_report_says_so() -> None:
    assert DriftReport().is_clean
    assert "No drift" in DriftReport().render()


def test_each_kind_has_its_own_headline() -> None:
    headlines = {kind.headline for kind in DriftKind}

    assert len(headlines) == len(DriftKind), "two kinds share wording"


def test_each_kind_has_its_own_remediation() -> None:
    remediations = {kind.remediation for kind in DriftKind}

    assert len(remediations) == len(DriftKind)


def test_the_unit_remediation_says_investigate_rather_than_re_lock() -> None:
    """The others tell you to re-lock. This one must not, at least not first."""
    assert "Investigate" in DriftKind.UNIT.remediation

    for kind in DriftKind:
        if kind is not DriftKind.UNIT:
            assert "Run `prompticorn lock`" in kind.remediation


def test_a_rendered_report_carries_headline_evidence_and_remediation() -> None:
    rendered = DriftReport((drift(DriftKind.MANIFEST, ".prompticorn.yaml"),)).render()

    assert DriftKind.MANIFEST.headline in rendered
    assert ".prompticorn.yaml" in rendered
    assert DriftKind.MANIFEST.remediation in rendered


def test_digests_are_abbreviated_in_the_evidence_line() -> None:
    """Two 64-character hashes on one line push the difference off the terminal."""
    rendered = DriftReport((drift(DriftKind.UNIT, "agent/code"),)).render()

    assert DIGEST_A[:12] in rendered
    assert DIGEST_A not in rendered


def test_non_digest_values_are_left_alone() -> None:
    rendered = DriftReport((Drift(DriftKind.PACKAGE, "prompticorn", "0.5.0", "0.6.0"),)).render()

    assert "0.5.0 -> 0.6.0" in rendered


def test_an_absent_side_is_shown_as_absent() -> None:
    rendered = DriftReport((Drift(DriftKind.UNIT, "agent/new", None, DIGEST_B),)).render()

    assert "(absent)" in rendered


def test_suspicious_drift_is_marked_differently() -> None:
    ordinary = DriftReport((drift(DriftKind.MANIFEST),)).render()
    suspicious = DriftReport((drift(DriftKind.UNIT),)).render()

    assert ordinary.lstrip().startswith("--")
    assert suspicious.lstrip().startswith("!!")


def test_suspicious_drift_is_rendered_last() -> None:
    """So the most important finding is what is still on screen at the end."""
    rendered = DriftReport((drift(DriftKind.UNIT), drift(DriftKind.MANIFEST))).render()

    assert rendered.index(DriftKind.MANIFEST.headline) < rendered.index(DriftKind.UNIT.headline)


def test_drifts_are_grouped_by_kind() -> None:
    report = DriftReport(
        (
            drift(DriftKind.MANIFEST, "one"),
            drift(DriftKind.UNIT, "two"),
            drift(DriftKind.MANIFEST, "three"),
        )
    )

    assert len(report.of_kind(DriftKind.MANIFEST)) == 2
    assert report.render().count(DriftKind.MANIFEST.headline) == 1, "one section per kind"


def test_the_count_is_shown_per_kind() -> None:
    report = DriftReport((drift(DriftKind.UNIT, "a"), drift(DriftKind.UNIT, "b")))

    assert "(2)" in report.render()


@pytest.mark.parametrize("kind", list(DriftKind))
def test_every_kind_renders_without_error(kind: DriftKind) -> None:
    assert DriftReport((drift(kind),)).render()


def test_str_is_the_rendered_report() -> None:
    report = DriftReport((drift(DriftKind.UNIT),))

    assert str(report) == report.render()
