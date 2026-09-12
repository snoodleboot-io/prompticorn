"""Turning a repository's lock into index rows (PRO-128).

The one direction data flows. The lock is the authority about a repository, and
this reads it; nothing writes back the other way. That is what makes the index
disposable — every row here can be reconstructed by pointing this at the same
repositories again, which a test proves by deleting the database and doing so.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from prompticorn.lockfile.errors import LockError
from prompticorn.lockfile.lock_file import LockFile
from prompticorn.lockfile.lock_reader import LockReader
from prompticorn.lockfile.lock_service import LockService
from prompticorn.store.install_index import InstallIndex
from prompticorn.store.install_record import InstallRecord
from prompticorn.store.repo_identity import repo_id


@dataclass(frozen=True)
class InstallRecorder:
    """Records what a repository's lock says it has installed.

    Attributes:
        index: Where the rows go.
    """

    index: InstallIndex

    def record(self, root: Path, seen_at: str) -> str | None:
        """Read the lock at ``root`` and store what it describes.

        Args:
            root: The project directory.
            seen_at: ISO-8601 UTC for this sighting. Supplied rather than read
                from the clock, so two runs can be compared.

        Returns:
            The repository's identity, or None if it has no usable lock — a
            project that has not opted in yet is not an error, it simply has
            nothing to index.
        """
        location = LockService.lock_path(root)
        if not location.is_file():
            return None
        try:
            lock = LockReader.read(location)
        except LockError:
            # An unreadable lock is the repository's problem to report, not
            # this one's. Indexing is a side errand; failing it must not fail
            # the command the user actually ran.
            return None

        identity = repo_id(root)
        self.index.record_repo(identity, root, seen_at)
        self.index.record_installs(identity, _records_from(lock, seen_at))
        return identity


def _records_from(lock: LockFile, seen_at: str) -> tuple[InstallRecord, ...]:
    """One row per locked artifact, in the lock's own canonical order."""
    return tuple(
        InstallRecord(
            artifact_id=artifact.identity.render(),
            version=artifact.identity.version.render(),
            digest=artifact.pinned.digest,
            source=artifact.source,
            installed_at=seen_at,
        )
        for artifact in lock.canonical().artifacts
    )
