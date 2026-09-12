"""The install index (PRO-128).

Two properties carry the design, and both are about what the index is *not*.
It is not an authority — deleting it must cost nothing, which
`TestRebuildability` proves by deleting it. And it is not durable state worth
protecting — a corrupt file is discarded rather than reported, because the data
it held still exists in every repository's lock.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from prompticorn.store.install_index import InstallIndex
from prompticorn.store.install_record import InstallRecord
from prompticorn.store.schema import SCHEMA_VERSION, current_version, migrate

NOW = "2026-09-06T12:00:00Z"
LATER = "2026-09-07T12:00:00Z"


def record(artifact: str = "local/house-standards@2.1.0", **overrides) -> InstallRecord:
    fields = {
        "artifact_id": artifact,
        "version": artifact.split("@")[-1],
        "digest": "a" * 64,
        "source": "house",
        "installed_at": NOW,
    }
    fields.update(overrides)
    return InstallRecord(**fields)


@pytest.fixture
def index(tmp_path: Path) -> InstallIndex:
    with InstallIndex(path=tmp_path / "store.db") as opened:
        yield opened


class TestSchema:
    def test_a_new_database_is_at_the_current_version(self, index: InstallIndex):
        assert index.schema_version == SCHEMA_VERSION

    def test_migration_is_idempotent(self, index: InstallIndex):
        """A CLI can be killed between statements and run again."""
        connection = index.connect()

        assert migrate(connection) == migrate(connection) == SCHEMA_VERSION

    def test_a_version_zero_database_migrates_forward(self, tmp_path: Path):
        """The v1 fixture: an empty file, which is what version 0 looks like."""
        path = tmp_path / "old.db"
        sqlite3.connect(path).close()

        with InstallIndex(path=path) as index:
            assert index.schema_version == SCHEMA_VERSION

    def test_a_newer_database_is_left_alone_not_downgraded(self, tmp_path: Path):
        """Rewriting a schema this version does not understand would destroy
        data the version that wrote it can still use."""
        path = tmp_path / "future.db"
        connection = sqlite3.connect(path)
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 5}")
        connection.close()

        connection = sqlite3.connect(path)
        assert migrate(connection) == SCHEMA_VERSION + 5
        assert current_version(connection) == SCHEMA_VERSION + 5
        connection.close()


class TestRecording:
    def test_installs_round_trip(self, index: InstallIndex, tmp_path: Path):
        index.record_repo("repo-1", tmp_path, NOW)
        index.record_installs("repo-1", [record()])

        assert index.installs_for("repo-1") == (record(),)

    def test_recording_replaces_rather_than_merges(self, index: InstallIndex, tmp_path: Path):
        """The caller has just read a lock, which is the complete truth. Merging
        would let a removed artifact linger in the index forever."""
        index.record_repo("repo-1", tmp_path, NOW)
        index.record_installs("repo-1", [record("local/a@1.0.0"), record("local/b@1.0.0")])

        index.record_installs("repo-1", [record("local/a@1.0.0")])

        assert [r.artifact_id for r in index.installs_for("repo-1")] == ["local/a@1.0.0"]

    def test_a_moved_repo_updates_its_path_not_its_identity(self, index: InstallIndex, tmp_path):
        index.record_repo("repo-1", tmp_path / "before", NOW)
        index.record_repo("repo-1", tmp_path / "after", LATER)

        assert index.repos() == (("repo-1", tmp_path / "after"),)

    def test_installs_are_ordered_by_artifact(self, index: InstallIndex, tmp_path: Path):
        index.record_repo("repo-1", tmp_path, NOW)
        index.record_installs("repo-1", [record("local/z@1.0.0"), record("local/a@1.0.0")])

        assert [r.artifact_id for r in index.installs_for("repo-1")] == [
            "local/a@1.0.0",
            "local/z@1.0.0",
        ]

    def test_forgetting_a_repo_removes_its_installs(self, index: InstallIndex, tmp_path: Path):
        index.record_repo("repo-1", tmp_path, NOW)
        index.record_installs("repo-1", [record()])

        index.forget_repo("repo-1")

        assert index.installs_for("repo-1") == ()
        assert index.is_empty()


class TestTheCrossRepoQuestion:
    def test_finds_every_repo_holding_an_artifact(self, index: InstallIndex, tmp_path: Path):
        """The question no single repository can answer, and the only reason
        this file exists."""
        for name in ("repo-1", "repo-2", "repo-3"):
            index.record_repo(name, tmp_path / name, NOW)
        index.record_installs("repo-1", [record("local/shared@1.0.0")])
        index.record_installs("repo-2", [record("local/shared@1.0.0")])
        index.record_installs("repo-3", [record("local/other@1.0.0")])

        assert index.repos_with("local/shared@1.0.0") == ("repo-1", "repo-2")


class TestCorruption:
    def test_a_corrupt_database_is_rebuilt_rather_than_raised(self, tmp_path: Path):
        """The file is an index over data that still exists. Reporting a fault
        would make a disposable cache look like a broken installation."""
        path = tmp_path / "store.db"
        path.write_bytes(b"this is not a database, it is a picture of one")

        with InstallIndex(path=path) as index:
            assert index.schema_version == SCHEMA_VERSION
            assert index.is_empty()

    def test_the_rebuilt_database_is_usable(self, tmp_path: Path):
        path = tmp_path / "store.db"
        path.write_bytes(b"garbage")

        with InstallIndex(path=path) as index:
            index.record_repo("repo-1", tmp_path, NOW)
            index.record_installs("repo-1", [record()])

            assert index.installs_for("repo-1") == (record(),)


class TestConcurrency:
    def test_wal_mode_is_on(self, index: InstallIndex):
        """Several CLI invocations run at once; a reader must not block behind
        a writer to answer a question that is only a convenience."""
        mode = index.connect().execute("PRAGMA journal_mode").fetchone()[0]

        assert mode.lower() == "wal"

    def test_two_connections_can_read_and_write(self, tmp_path: Path):
        path = tmp_path / "store.db"
        with InstallIndex(path=path) as writer, InstallIndex(path=path) as reader:
            writer.record_repo("repo-1", tmp_path, NOW)
            writer.record_installs("repo-1", [record()])

            assert reader.installs_for("repo-1") == (record(),)
