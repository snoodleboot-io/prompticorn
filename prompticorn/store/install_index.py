"""Which repository on this machine has which artifacts (PRO-128).

The local counterpart of what becomes a hosted service in EE. It answers
questions no single repository can — "where else did I install this?", "which of
my projects are still on 2.1.0?" — and that is the *only* kind of question it is
allowed to answer.

**It is an index, not an authority.** Every repository's own lock is the truth
about that repository. This is a cross-repo convenience, and it must be
rebuildable by rescanning the repositories it knows about; a test deletes the
database and asserts behaviour is unchanged afterwards. Anything that would be
lost by deleting this file does not belong in it.

Two consequences of that rule shape the code below. A corrupt database is
discarded and rebuilt rather than reported as a fault, because the data was
never irreplaceable. And WAL mode is on, because several CLI invocations can run
at once and a reader must not block behind a writer to answer a question whose
answer is only a convenience anyway.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterable
from pathlib import Path

from prompticorn.store.install_record import InstallRecord
from prompticorn.store.schema import SCHEMA_VERSION, current_version, migrate
from prompticorn.store.store_paths import database_path, ensure_directory


class InstallIndex:
    """A SQLite index of installs, keyed by repository identity.

    Args:
        path: Where the database lives. Defaults to the one under
            ``PROMPTICORN_HOME``.
    """

    def __init__(self, path: Path | None = None) -> None:
        self._path = path
        self._connection: sqlite3.Connection | None = None

    @property
    def path(self) -> Path:
        """Resolved late, so a store built at import time does not freeze
        ``PROMPTICORN_HOME`` before a test sets it."""
        return self._path if self._path is not None else database_path()

    # -- lifecycle -------------------------------------------------------

    def connect(self) -> sqlite3.Connection:
        """Open the database, creating or repairing it as needed."""
        if self._connection is not None:
            return self._connection
        ensure_directory(self.path.parent)
        try:
            connection = self._open(self.path)
        except sqlite3.DatabaseError:
            # Not a fault worth reporting: the file is an index over data that
            # still exists elsewhere. Discard and start again.
            self.path.unlink(missing_ok=True)
            connection = self._open(self.path)
        self._connection = connection
        return connection

    @staticmethod
    def _open(path: Path) -> sqlite3.Connection:
        connection = sqlite3.connect(path)
        connection.row_factory = sqlite3.Row
        # WAL so concurrent CLI invocations read while one writes. NORMAL
        # synchronous because losing the last write of a rebuildable index to a
        # power cut is not worth an fsync on every commit.
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = NORMAL")
        connection.execute("PRAGMA foreign_keys = ON")
        migrate(connection)
        return connection

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def __enter__(self) -> InstallIndex:
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @property
    def schema_version(self) -> int:
        return current_version(self.connect())

    # -- writing ---------------------------------------------------------

    def record_repo(self, repo_id: str, path: Path, seen_at: str) -> None:
        """Note that a repository exists and where it was last seen.

        The path is updated on every sighting rather than inserted once, which
        is what lets a moved checkout be found again — the identity is stable,
        the location is not.
        """
        connection = self.connect()
        with connection:
            connection.execute(
                """
                INSERT INTO repos (repo_id, path, last_seen_at) VALUES (?, ?, ?)
                ON CONFLICT (repo_id) DO UPDATE SET path = excluded.path,
                                                    last_seen_at = excluded.last_seen_at
                """,
                (repo_id, str(path), seen_at),
            )

    def record_installs(self, repo_id: str, records: Iterable[InstallRecord]) -> None:
        """Replace what this repository is known to have installed.

        Replace rather than merge: the caller has just read a lock, which is the
        complete truth about that repository. Merging would let an artifact that
        was removed from the lock linger in the index forever.
        """
        connection = self.connect()
        rows = [
            (repo_id, r.artifact_id, r.version, r.digest, r.source, r.installed_at) for r in records
        ]
        with connection:
            connection.execute("DELETE FROM installs WHERE repo_id = ?", (repo_id,))
            connection.executemany(
                """
                INSERT INTO installs
                    (repo_id, artifact_id, version, digest, source, installed_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                rows,
            )

    def forget_repo(self, repo_id: str) -> None:
        """Drop a repository and its installs."""
        connection = self.connect()
        with connection:
            connection.execute("DELETE FROM installs WHERE repo_id = ?", (repo_id,))
            connection.execute("DELETE FROM repos WHERE repo_id = ?", (repo_id,))

    # -- reading ---------------------------------------------------------

    def installs_for(self, repo_id: str) -> tuple[InstallRecord, ...]:
        """What one repository has installed, ordered by artifact id."""
        rows = self.connect().execute(
            """
            SELECT artifact_id, version, digest, source, installed_at
            FROM installs WHERE repo_id = ? ORDER BY artifact_id
            """,
            (repo_id,),
        )
        return tuple(
            InstallRecord(
                artifact_id=row["artifact_id"],
                version=row["version"],
                digest=row["digest"],
                source=row["source"],
                installed_at=row["installed_at"],
            )
            for row in rows
        )

    def repos(self) -> tuple[tuple[str, Path], ...]:
        """Every known repository as ``(repo_id, path)``, ordered by id.

        The list `upgrade --all` iterates, and the list a rebuild rescans.
        """
        rows = self.connect().execute("SELECT repo_id, path FROM repos ORDER BY repo_id")
        return tuple((row["repo_id"], Path(row["path"])) for row in rows)

    def repos_with(self, artifact_id: str) -> tuple[str, ...]:
        """Every repository holding one artifact — the cross-repo question."""
        rows = self.connect().execute(
            "SELECT repo_id FROM installs WHERE artifact_id = ? ORDER BY repo_id",
            (artifact_id,),
        )
        return tuple(row["repo_id"] for row in rows)

    def is_empty(self) -> bool:
        return not self.repos()


__all__ = ["SCHEMA_VERSION", "InstallIndex", "InstallRecord"]
