"""Classifying divergence between a lock and reality (PRO-111).

AC 1 wants each `DriftKind` reproduced by a targeted fixture and named
distinctly. The classification rules are the substance: in particular UNIT drift
is defined by what it *excludes*, and getting that wrong would either cry wolf on
every upgrade or stay silent on the one case that matters.
"""

import pytest

from prompticorn.artifact import ArtifactId, PinnedArtifact
from prompticorn.content import UnitId
from prompticorn.lockfile import (
    DriftDetector,
    DriftKind,
    LockedArtifact,
    LockedUnit,
    LockFile,
)

DIGEST_A = "a" * 64
DIGEST_B = "b" * 64
MANIFEST_A = "1" * 64
MANIFEST_B = "2" * 64
STAMP = "2026-08-09T03:00:00Z"


def lock(
    *,
    version: str = "0.5.0",
    manifest: str | None = MANIFEST_A,
    artifacts: tuple = (),
    units: tuple = (),
) -> LockFile:
    return LockFile(
        prompticorn_version=version,
        resolved_at=STAMP,
        artifacts=artifacts,
        units=units,
        manifest_digest=manifest,
    )


def artifact(coordinate: str = "local/sec", version: str = "1.0.0", digest: str = DIGEST_A):
    return LockedArtifact(PinnedArtifact(ArtifactId.parse(f"{coordinate}@{version}"), digest))


def unit(raw_id: str = "agent/code", digest: str = DIGEST_A):
    return LockedUnit(UnitId.parse(raw_id), "builtin", digest)


# ── AC 1: one targeted fixture per kind ────────────────────────────────────────


def test_no_drift_when_nothing_moved() -> None:
    recorded = lock(artifacts=(artifact(),), units=(unit(),))

    assert DriftDetector.compare(recorded, recorded).is_clean


def test_manifest_drift() -> None:
    report = DriftDetector.compare(lock(manifest=MANIFEST_A), lock(manifest=MANIFEST_B))

    assert report.kinds == (DriftKind.MANIFEST,)
    assert report.of_kind(DriftKind.MANIFEST)[0].subject == ".prompticorn.yaml"


def test_package_drift() -> None:
    report = DriftDetector.compare(lock(version="0.5.0"), lock(version="0.6.0"))

    assert report.kinds == (DriftKind.PACKAGE,)
    drift = report.of_kind(DriftKind.PACKAGE)[0]
    assert (drift.expected, drift.actual) == ("0.5.0", "0.6.0")


@pytest.mark.parametrize(
    ("before", "after", "why"),
    [
        (artifact(version="1.0.0"), artifact(version="2.0.0"), "version moved"),
        (artifact(digest=DIGEST_A), artifact(digest=DIGEST_B), "republished at same version"),
    ],
)
def test_artifact_drift(before, after, why: str) -> None:
    report = DriftDetector.compare(lock(artifacts=(before,)), lock(artifacts=(after,)))

    assert report.kinds == (DriftKind.ARTIFACT,), why


def test_a_republished_version_is_drift_even_though_the_version_matches() -> None:
    """Same version, different content, is exactly what a lock exists to catch."""
    report = DriftDetector.compare(
        lock(artifacts=(artifact(version="1.0.0", digest=DIGEST_A),)),
        lock(artifacts=(artifact(version="1.0.0", digest=DIGEST_B),)),
    )

    assert report.kinds == (DriftKind.ARTIFACT,)


def test_unit_drift() -> None:
    report = DriftDetector.compare(
        lock(units=(unit(digest=DIGEST_A),)), lock(units=(unit(digest=DIGEST_B),))
    )

    assert report.kinds == (DriftKind.UNIT,)
    assert report.of_kind(DriftKind.UNIT)[0].subject == "agent/code"


def test_every_kind_is_reachable() -> None:
    """Guards against a kind that exists in the enum but can never be produced."""
    reachable = {
        DriftKind.MANIFEST: DriftDetector.compare(lock(), lock(manifest=MANIFEST_B)),
        DriftKind.PACKAGE: DriftDetector.compare(lock(), lock(version="9.9.9")),
        DriftKind.ARTIFACT: DriftDetector.compare(lock(), lock(artifacts=(artifact(),))),
        DriftKind.UNIT: DriftDetector.compare(
            lock(units=(unit(),)), lock(units=(unit(digest=DIGEST_B),))
        ),
    }

    for kind, report in reachable.items():
        assert kind in report.kinds, f"{kind} is unreachable"


# ── the classification rules ───────────────────────────────────────────────────


def test_unit_drift_is_suppressed_when_an_artifact_changed() -> None:
    """A unit digest moving because its artifact was upgraded is expected.

    Reporting it as UNIT would make the alarming message routine — which is how
    alarming messages stop being read.
    """
    report = DriftDetector.compare(
        lock(artifacts=(artifact(version="1.0.0"),), units=(unit(digest=DIGEST_A),)),
        lock(artifacts=(artifact(version="2.0.0"),), units=(unit(digest=DIGEST_B),)),
    )

    assert report.kinds == (DriftKind.ARTIFACT,)
    assert report.of_kind(DriftKind.UNIT) == ()


def test_unit_drift_is_the_only_suspicious_kind() -> None:
    """It means a source mutated in place; the others mean someone did something."""
    assert DriftKind.UNIT.is_suspicious
    assert not any(kind.is_suspicious for kind in DriftKind if kind is not DriftKind.UNIT)


def test_a_report_with_unit_drift_is_flagged_suspicious() -> None:
    report = DriftDetector.compare(lock(units=(unit(),)), lock(units=(unit(digest=DIGEST_B),)))

    assert report.has_suspicious_drift


def test_a_report_without_unit_drift_is_not() -> None:
    report = DriftDetector.compare(lock(), lock(manifest=MANIFEST_B))

    assert not report.has_suspicious_drift


def test_an_added_or_removed_unit_is_unit_drift() -> None:
    added = DriftDetector.compare(lock(), lock(units=(unit(),)))
    removed = DriftDetector.compare(lock(units=(unit(),)), lock())

    assert added.kinds == (DriftKind.UNIT,)
    assert removed.kinds == (DriftKind.UNIT,)
    assert added.of_kind(DriftKind.UNIT)[0].expected is None
    assert removed.of_kind(DriftKind.UNIT)[0].actual is None


def test_an_artifact_that_moved_version_reads_as_one_change_not_two() -> None:
    """Keyed by coordinate, so an upgrade is not "one removed, one added"."""
    report = DriftDetector.compare(
        lock(artifacts=(artifact(version="1.0.0"),)),
        lock(artifacts=(artifact(version="2.0.0"),)),
    )

    assert len(report.of_kind(DriftKind.ARTIFACT)) == 1


def test_a_lock_without_a_manifest_digest_reports_no_manifest_drift() -> None:
    """It cannot answer the question, so it must not claim an answer.

    Hand-made locks, and any written before the field existed, would otherwise
    report manifest drift forever.
    """
    report = DriftDetector.compare(lock(manifest=None), lock(manifest=MANIFEST_B))

    assert report.is_clean


def test_several_kinds_are_reported_together() -> None:
    report = DriftDetector.compare(
        lock(version="0.5.0", manifest=MANIFEST_A),
        lock(version="0.6.0", manifest=MANIFEST_B),
    )

    assert set(report.kinds) == {DriftKind.PACKAGE, DriftKind.MANIFEST}


def test_kinds_are_reported_in_declared_order_not_discovery_order() -> None:
    """The same set of problems must always report the same way."""
    report = DriftDetector.compare(
        lock(version="0.5.0", manifest=MANIFEST_A, units=(unit(),)),
        lock(version="0.6.0", manifest=MANIFEST_B, units=(unit(digest=DIGEST_B),)),
    )

    assert list(report.kinds) == [kind for kind in DriftKind if kind in report.kinds]
