"""Comparing a recorded lock against the current state (PRO-111).

The classification is the substance here. Each of the four conditions is decided
by a different comparison, and the one that matters most —
:attr:`~prompticorn.lockfile.drift_kind.DriftKind.UNIT` — is defined by what it
*excludes*: a unit whose digest changed while its artifact version did not.

A unit whose digest changed because its artifact was upgraded is not UNIT drift;
it is the expected consequence of ARTIFACT drift. Reporting it as UNIT would cry
wolf on every routine upgrade and teach users to ignore the one message that
should stop them.
"""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.lockfile.drift import Drift
from prompticorn.lockfile.drift_kind import DriftKind
from prompticorn.lockfile.drift_report import DriftReport
from prompticorn.lockfile.lock_file import LockFile
from prompticorn.lockfile.locked_artifact import LockedArtifact

_MANIFEST_SUBJECT = ".prompticorn.yaml"
_PACKAGE_SUBJECT = "prompticorn"


@dataclass(frozen=True)
class DriftDetector:
    """Classifies the difference between a recorded lock and a fresh one."""

    @classmethod
    def compare(cls, recorded: LockFile, current: LockFile) -> DriftReport:
        """Every way ``current`` diverges from ``recorded``, classified.

        Args:
            recorded: The lock as committed.
            current: A lock resolved from the project right now.

        Returns:
            The classified report. Empty when they agree.
        """
        drifts: list[Drift] = []
        drifts.extend(cls._package_drift(recorded, current))
        drifts.extend(cls._manifest_drift(recorded, current))
        changed_artifacts = cls._artifact_drift(recorded, current)
        drifts.extend(changed_artifacts)
        drifts.extend(cls._unit_drift(recorded, current, bool(changed_artifacts)))
        return DriftReport(drifts=tuple(drifts))

    @staticmethod
    def _package_drift(recorded: LockFile, current: LockFile) -> list[Drift]:
        if recorded.prompticorn_version == current.prompticorn_version:
            return []
        return [
            Drift(
                DriftKind.PACKAGE,
                _PACKAGE_SUBJECT,
                recorded.prompticorn_version,
                current.prompticorn_version,
            )
        ]

    @staticmethod
    def _manifest_drift(recorded: LockFile, current: LockFile) -> list[Drift]:
        """Compare manifest digests, when the recorded lock has one.

        A lock without a ``manifest_digest`` predates the field or was written by
        hand. Reporting that as drift would flag every such lock forever on a
        question it simply cannot answer, so it is treated as "unknown, not
        changed".
        """
        if recorded.manifest_digest is None:
            return []
        if recorded.manifest_digest == current.manifest_digest:
            return []
        return [
            Drift(
                DriftKind.MANIFEST,
                _MANIFEST_SUBJECT,
                recorded.manifest_digest,
                current.manifest_digest,
            )
        ]

    @staticmethod
    def _artifact_drift(recorded: LockFile, current: LockFile) -> list[Drift]:
        """Artifacts added, removed, or resolved to a different version or digest.

        Keyed by coordinate rather than by full identity, so an artifact that
        moved from 2.1.0 to 2.2.0 reads as one changed artifact rather than one
        removed and one added.
        """
        before = {artifact.identity.coordinate: artifact for artifact in recorded.artifacts}
        after = {artifact.identity.coordinate: artifact for artifact in current.artifacts}

        drifts = []
        for coordinate in sorted(before.keys() | after.keys()):
            old, new = before.get(coordinate), after.get(coordinate)
            old_state = _artifact_state(old)
            new_state = _artifact_state(new)
            if old_state != new_state:
                drifts.append(Drift(DriftKind.ARTIFACT, coordinate, old_state, new_state))
        return drifts

    @staticmethod
    def _unit_drift(recorded: LockFile, current: LockFile, artifacts_changed: bool) -> list[Drift]:
        """Units whose content changed while their artifact version did not.

        Suppressed entirely when any artifact changed: a unit digest moving
        because its artifact was upgraded is the expected consequence of that
        upgrade, not evidence of tampering. Reporting both would make the
        alarming message routine, which is how alarming messages stop working.
        """
        if artifacts_changed:
            return []

        before = {unit.id.render(): unit for unit in recorded.units}
        after = {unit.id.render(): unit for unit in current.units}

        drifts = []
        for unit_id in sorted(before.keys() & after.keys()):
            if before[unit_id].digest != after[unit_id].digest:
                drifts.append(
                    Drift(DriftKind.UNIT, unit_id, before[unit_id].digest, after[unit_id].digest)
                )
        # Units appearing or disappearing under an unchanged artifact set is the
        # same class of surprise, and reported the same way.
        for unit_id in sorted(before.keys() ^ after.keys()):
            old = before.get(unit_id)
            new = after.get(unit_id)
            drifts.append(
                Drift(
                    DriftKind.UNIT,
                    unit_id,
                    old.digest if old else None,
                    new.digest if new else None,
                )
            )
        return drifts


def _artifact_state(artifact: LockedArtifact | None) -> str | None:
    """Version and digest as one comparable string, or None when absent.

    Both together, because either changing alone is drift: a new version is an
    upgrade, and a new digest at the *same* version means the release was
    republished with different content.
    """
    if artifact is None:
        return None
    return f"{artifact.identity.version.render()}@{artifact.pinned.digest}"
