"""Lock → index, and the proof that the index is disposable (PRO-128).

`TestRebuildability` is the ticket's central claim made executable: delete
`store.db`, point the recorder at the same repositories, and get the same
answers. If that ever stops holding, something has been stored here that exists
nowhere else — which is the failure the "index, not authority" rule exists to
prevent.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from prompticorn.cli import cli
from prompticorn.store import store_paths
from prompticorn.store.install_index import InstallIndex
from prompticorn.store.install_recorder import InstallRecorder
from prompticorn.store.repo_identity import repo_id

NOW = "2026-09-06T12:00:00Z"

# Declares an artifact, because an install index over a manifest that declares
# none records nothing and every assertion below would pass vacuously.
MANIFEST = """\
version: '2.0'
repository:
  type: single-language
spec:
  language: python
variant: minimal
active_personas:
  - software_engineer
ai_tool: claude
artifacts:
  - name: local/agent.code
    version: ">=0.0.0-0"
"""


@pytest.fixture
def project(tmp_path: Path, monkeypatch) -> Path:
    """A built and locked project, with the store relocated."""
    monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
    root = tmp_path / "project"
    (root / ".prompticorn").mkdir(parents=True)
    (root / ".prompticorn" / ".prompticorn.yaml").write_text(MANIFEST, encoding="utf-8")
    monkeypatch.chdir(root)
    CliRunner().invoke(cli, ["build"])
    CliRunner().invoke(cli, ["lock"])
    return root


@pytest.fixture
def index(tmp_path: Path) -> InstallIndex:
    with InstallIndex(path=tmp_path / "store" / "store.db") as opened:
        yield opened


class TestRecording:
    def test_a_locked_project_is_recorded(self, project: Path, index: InstallIndex):
        identity = InstallRecorder(index=index).record(project, NOW)

        assert identity == repo_id(project)
        assert index.installs_for(identity)

    def test_records_match_the_lock(self, project: Path, index: InstallIndex):
        """The lock is the authority; the index restates it and nothing more."""
        from prompticorn.lockfile.lock_reader import LockReader
        from prompticorn.lockfile.lock_service import LockService

        lock = LockReader.read(LockService.lock_path(project))
        identity = InstallRecorder(index=index).record(project, NOW)

        assert [r.artifact_id for r in index.installs_for(identity)] == sorted(
            artifact.identity.render() for artifact in lock.artifacts
        )

    def test_a_project_with_no_lock_is_not_an_error(self, tmp_path: Path, index: InstallIndex):
        """Not opting in is not a fault. Indexing is a side errand and must not
        fail the command the user actually ran."""
        bare = tmp_path / "unlocked"
        bare.mkdir()

        assert InstallRecorder(index=index).record(bare, NOW) is None

    def test_an_unreadable_lock_is_not_an_error(self, project: Path, index: InstallIndex):
        from prompticorn.lockfile.lock_service import LockService

        LockService.lock_path(project).write_text(": not a lock\n", encoding="utf-8")

        assert InstallRecorder(index=index).record(project, NOW) is None

    def test_recording_twice_is_stable(self, project: Path, index: InstallIndex):
        recorder = InstallRecorder(index=index)
        identity = recorder.record(project, NOW)
        first = index.installs_for(identity)

        recorder.record(project, NOW)

        assert index.installs_for(identity) == first


class TestRebuildability:
    def test_deleting_the_database_costs_nothing(self, project: Path, tmp_path: Path):
        """The ticket's central claim, executable. Anything lost by deleting
        this file was stored somewhere it should not have been."""
        path = tmp_path / "store" / "store.db"

        with InstallIndex(path=path) as index:
            identity = InstallRecorder(index=index).record(project, NOW)
            before = index.installs_for(identity)
            repos_before = index.repos()

        for leftover in path.parent.glob("store.db*"):
            leftover.unlink()

        with InstallIndex(path=path) as rebuilt:
            assert rebuilt.is_empty()
            assert InstallRecorder(index=rebuilt).record(project, NOW) == identity
            assert rebuilt.installs_for(identity) == before
            assert rebuilt.repos() == repos_before

    def test_a_rebuild_after_corruption_restores_the_same_rows(self, project: Path, tmp_path):
        path = tmp_path / "store" / "store.db"
        with InstallIndex(path=path) as index:
            identity = InstallRecorder(index=index).record(project, NOW)
            before = index.installs_for(identity)

        path.write_bytes(b"corrupt")

        with InstallIndex(path=path) as rebuilt:
            InstallRecorder(index=rebuilt).record(project, NOW)

            assert rebuilt.installs_for(identity) == before


class TestStatusCommand:
    def test_status_reports_the_projects_artifacts(self, project: Path):
        result = CliRunner().invoke(cli, ["status"])

        assert result.exit_code == 0, result.output
        assert "artifact(s)" in result.output

    def test_status_names_the_repo_identity(self, project: Path):
        result = CliRunner().invoke(cli, ["status"])

        assert repo_id(project) in result.output

    def test_status_without_a_lock_says_so_rather_than_failing(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
        bare = tmp_path / "unlocked"
        (bare / ".prompticorn").mkdir(parents=True)
        (bare / ".prompticorn" / ".prompticorn.yaml").write_text(MANIFEST, encoding="utf-8")
        monkeypatch.chdir(bare)

        result = CliRunner().invoke(cli, ["status"])

        assert result.exit_code == 0, result.output
        assert "prompticorn lock" in result.output

    def test_status_refreshes_the_index_from_the_lock(self, project: Path, tmp_path: Path):
        """Every run re-reads the authority, so a stale index self-corrects."""
        CliRunner().invoke(cli, ["status"])

        with InstallIndex(path=tmp_path / "store" / "store.db") as index:
            assert index.installs_for(repo_id(project))
