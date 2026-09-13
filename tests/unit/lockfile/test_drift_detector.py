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


def test_only_a_mutated_pinned_version_is_suspicious() -> None:
    """Suspicious means a version that should be immutable is not — content
    changed under it (UNIT) or its tag was moved (REF_MOVED, PRO-151). Every
    other kind means someone did something on purpose."""
    suspicious = {kind for kind in DriftKind if kind.is_suspicious}

    assert suspicious == {DriftKind.UNIT, DriftKind.REF_MOVED}


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


# -- REF_MOVED (PRO-151) -------------------------------------------------------

COMMIT_A = "a" * 40
COMMIT_B = "b" * 40


def _git_artifact(version: str = "1.0.0", commit: str | None = COMMIT_A, digest: str = DIGEST_A):
    from prompticorn.artifact.artifact_id import ArtifactId
    from prompticorn.artifact.pinned_artifact import PinnedArtifact
    from prompticorn.lockfile.locked_artifact import LockedArtifact

    return LockedArtifact(
        pinned=PinnedArtifact(artifact_id=ArtifactId.parse(f"local/house@{version}"), digest=digest),
        source="house",
        commit=commit,
    )


def test_a_moved_tag_at_the_same_version_is_ref_moved_drift() -> None:
    report = DriftDetector.compare(
        lock(artifacts=(_git_artifact(commit=COMMIT_A),)),
        lock(artifacts=(_git_artifact(commit=COMMIT_B),)),
    )

    assert report.kinds == (DriftKind.REF_MOVED,)
    assert report.has_suspicious_drift


def test_a_moved_tag_is_not_also_reported_as_ordinary_artifact_drift() -> None:
    """A moved tag usually changes the digest too. Reporting it twice would set
    the alarming finding next to a routine-looking duplicate of itself."""
    report = DriftDetector.compare(
        lock(artifacts=(_git_artifact(commit=COMMIT_A, digest=DIGEST_A),)),
        lock(artifacts=(_git_artifact(commit=COMMIT_B, digest=DIGEST_B),)),
    )

    assert DriftKind.ARTIFACT not in report.kinds
    assert report.kinds == (DriftKind.REF_MOVED,)


def test_a_version_upgrade_to_a_new_commit_is_not_ref_moved() -> None:
    """New version, new commit: an upgrade, not a re-tag."""
    report = DriftDetector.compare(
        lock(artifacts=(_git_artifact(version="1.0.0", commit=COMMIT_A),)),
        lock(artifacts=(_git_artifact(version="2.0.0", commit=COMMIT_B),)),
    )

    assert DriftKind.REF_MOVED not in report.kinds
    assert DriftKind.ARTIFACT in report.kinds


def test_an_unchanged_commit_is_not_drift() -> None:
    assert DriftDetector.compare(
        lock(artifacts=(_git_artifact(),)), lock(artifacts=(_git_artifact(),))
    ).is_clean


def test_a_non_git_artifact_never_reports_ref_moved() -> None:
    """No commit on either side means there is no tag to have moved."""
    report = DriftDetector.compare(
        lock(artifacts=(_git_artifact(commit=None),)),
        lock(artifacts=(_git_artifact(commit=None),)),
    )

    assert report.is_clean
