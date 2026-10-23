"""Declared sources, resolved into the lock (PRO-151).

End to end through the real CLI, against a local bare repository. These are the
acceptance criteria PRO-125 deferred, exercised where they are actually decided:
in `lock`, `build` and `regenerate`, not in the source on its own.

`TestMovedTag` carries the ticket. A tag moved upstream must be *found*, must be
*reported as suspicious*, and must not be adopted by an ordinary `build` — which
before this ticket re-locked every kind of drift automatically, including the
kinds its own report told the reader to investigate first.

`TestOffline` carries PRO-164. Its frozen-build and `regenerate` cases are each
written twice, warm and cold, because honouring the lock used to be conditioned
on whether a checkout directory happened to exist on this machine: the same lock,
manifest and remote produced one answer on a developer's laptop and another on a
fresh CI runner. A test that warms the cache first is exactly how that shipped,
so the cold path is named and asserted rather than left to the first machine that
hits it.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from prompticorn.artifact.artifact_digest import artifact_digest
from prompticorn.cli import cli
from prompticorn.content.digest import digest_text
from prompticorn.lockfile import ExitCode
from prompticorn.lockfile.lock_reader import LockReader
from prompticorn.sources.git_source import GitSource
from prompticorn.store import store_paths

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="needs git")

UNIT = "skill/testing-strategies/minimal"
COORDINATE = "local/house-standards"


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


class Remote:
    """A bare repository plus a clone to publish into it."""

    def __init__(self, root: Path) -> None:
        self.bare = root / "remote.git"
        self.work = root / "work"
        subprocess.run(["git", "init", "-q", "--bare", str(self.bare)], check=True)
        subprocess.run(["git", "clone", "-q", str(self.bare), str(self.work)], check=True, capture_output=True)
        for key, value in (("user.email", "t@example.com"), ("user.name", "T"), ("commit.gpgsign", "false")):
            git("config", key, value, cwd=self.work)

    def publish(self, version: str, body: str) -> str:
        directory = self.work / "local" / "house-standards" / version
        skill = directory / "skills" / "testing-strategies" / "minimal"
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(body, encoding="utf-8")
        digest = artifact_digest([(UNIT, digest_text(body))])
        (directory / "artifact.yaml").write_text(yaml.safe_dump({"digest": digest}), encoding="utf-8")
        git("add", ".", cwd=self.work)
        git("commit", "-qm", version, cwd=self.work)
        tag = f"{COORDINATE}@{version}"
        git("tag", "-f", tag, cwd=self.work)
        git("push", "-q", "-f", "origin", "HEAD", f"refs/tags/{tag}", cwd=self.work)
        return git("rev-parse", "HEAD", cwd=self.work)


def write_manifest(project: Path, sources: list, artifacts: list) -> None:
    config = project / ".prompticorn"
    config.mkdir(parents=True, exist_ok=True)
    manifest = {
        "version": "2.0",
        "repository": {"type": "single-language"},
        "spec": {"language": "python"},
        "variant": "minimal",
        "active_personas": ["software_engineer"],
        "ai_tool": "claude",
        "sources": sources,
        "artifacts": artifacts,
    }
    (config / ".prompticorn.yaml").write_text(yaml.safe_dump(manifest), encoding="utf-8")


def run(*args):
    return CliRunner().invoke(cli, list(args))


def locked(project: Path):
    lock = LockReader.read(project / ".prompticorn" / "prompticorn.lock")
    return {artifact.identity.coordinate: artifact for artifact in lock.artifacts}


def go_cold() -> None:
    """Forget every checkout, leaving the lock.

    The state of a fresh CI runner, a second machine, or a new clone: the
    committed lock is there and nothing has ever been fetched.
    """
    shutil.rmtree(store_paths.git_cache_root(), ignore_errors=True)


@pytest.fixture
def remote(tmp_path: Path) -> Remote:
    return Remote(tmp_path / "registry")


@pytest.fixture
def project(tmp_path: Path, monkeypatch, remote: Remote) -> Path:
    """A project that declares the git remote as a source."""
    monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
    root = tmp_path / "project"
    root.mkdir()
    write_manifest(
        root,
        sources=[{"name": "house", "type": "git", "url": str(remote.bare)}],
        artifacts=[{"name": COORDINATE, "version": ">=1.0.0", "source": "house"}],
    )
    monkeypatch.chdir(root)
    return root


class TestTheLockPinsTheCommit:
    def test_lock_records_the_commit_not_the_tag(self, remote: Remote, project: Path):
        """The AC. A tag is mutable, so the tag alone cannot be what is locked."""
        commit = remote.publish("1.0.0", "# One\n")

        result = run("lock")

        assert result.exit_code == ExitCode.CLEAN, result.output
        assert locked(project)[COORDINATE].commit == commit

    def test_lock_records_the_source_and_resolved_version(self, remote: Remote, project: Path):
        remote.publish("1.0.0", "# One\n")
        remote.publish("2.0.0", "# Two\n")

        run("lock")

        artifact = locked(project)[COORDINATE]
        assert artifact.source == "house"
        assert artifact.identity.version.render() == "2.0.0"

    def test_the_commit_appears_in_the_committed_file(self, remote: Remote, project: Path):
        """Checked on the text too, since the lock is read by people in review."""
        commit = remote.publish("1.0.0", "# One\n")

        run("lock")

        assert f"commit: {commit}" in (project / ".prompticorn" / "prompticorn.lock").read_text()


class TestMovedTag:
    def test_an_ordinary_build_reports_a_moved_tag(self, remote: Remote, project: Path):
        remote.publish("1.0.0", "# Original\n")
        run("lock")
        remote.publish("1.0.0", "# Re-tagged under the same version\n")

        result = run("build")

        assert result.exit_code == ExitCode.DRIFT, result.output
        assert "tag now points at a different commit" in result.output

    def test_an_ordinary_build_does_not_adopt_a_moved_tag(self, remote: Remote, project: Path):
        """The failure this ticket exists to prevent. Before PRO-151 `build`
        re-locked every kind of drift, suspicious or not."""
        pinned = remote.publish("1.0.0", "# Original\n")
        run("lock")
        remote.publish("1.0.0", "# Re-tagged\n")

        run("build")

        assert locked(project)[COORDINATE].commit == pinned

    def test_lock_is_the_deliberate_way_to_accept_it(self, remote: Remote, project: Path):
        remote.publish("1.0.0", "# Original\n")
        run("lock")
        moved = remote.publish("1.0.0", "# Re-tagged\n")

        run("lock")

        assert locked(project)[COORDINATE].commit == moved


class TestOffline:
    """A warm cache and a cold one must answer the same (PRO-164)."""

    def test_a_frozen_build_with_a_warm_cache_needs_no_remote(
        self, remote: Remote, project: Path
    ):
        """The AC: cached commits, no network. Proven by deleting the remote.

        The warm path, named as such. It passed before PRO-164 as well — which is
        why the cold path below had to be written separately.
        """
        remote.publish("1.0.0", "# One\n")
        run("lock")
        run("build")
        shutil.rmtree(remote.bare)

        result = run("build", "--frozen")

        assert result.exit_code == ExitCode.CLEAN, result.output

    def test_a_frozen_build_with_a_cold_cache_still_honours_the_lock(
        self, remote: Remote, project: Path
    ):
        """PRO-164, the defect. Nothing is warmed before the frozen build.

        The lock pins 1.0.0 and the range admits 2.0.0, so a resolution that did
        not honour the lock would land on 2.0.0 and report drift. It did exactly
        that on any machine without the checkout cached — the lock was obeyed or
        ignored according to whether a directory existed locally.
        """
        remote.publish("1.0.0", "# One\n")
        run("lock")
        remote.publish("2.0.0", "# Two\n")
        go_cold()

        result = run("build", "--frozen")

        assert result.exit_code == ExitCode.CLEAN, result.output
        assert locked(project)[COORDINATE].identity.version.render() == "1.0.0"

    def test_a_cold_frozen_build_fetches_the_pinned_commit_not_the_newest(
        self, remote: Remote, project: Path
    ):
        """Asserted on the cache, because a frozen build writes nothing.

        The lock on disk looks the same either way — a frozen build never
        updates it — so the observable difference is *which commit this machine
        went and got*. Fetching by id is what makes the cold path work at all.
        """
        pinned = remote.publish("1.0.0", "# One\n")
        run("lock")
        newest = remote.publish("2.0.0", "# Two\n")
        go_cold()

        run("build", "--frozen")

        source = GitSource(str(remote.bare))
        assert source.is_cached(pinned)
        assert not source.is_cached(newest)

    def test_a_cold_frozen_build_with_no_remote_refuses_rather_than_re_resolving(
        self, remote: Remote, project: Path
    ):
        """The offline promise, stated precisely.

        A pinned build needs no remote once the commit is cached. With a cold
        cache there is nothing to build from, and the only two honest answers are
        "fetch it" and "fail". Re-resolving is the third, which would report
        success for a build the lock does not describe.
        """
        remote.publish("1.0.0", "# One\n")
        run("lock")
        go_cold()
        shutil.rmtree(remote.bare)

        result = run("build", "--frozen")

        assert result.exit_code == ExitCode.SOURCE_ERROR, result.output
        assert "cannot be satisfied offline" in result.output
        assert locked(project)[COORDINATE].identity.version.render() == "1.0.0"

    def test_regenerate_with_a_warm_cache_and_the_remote_gone_still_works(
        self, remote: Remote, project: Path
    ):
        """`regenerate` works from the lock alone (PRO-116); a git source must
        not quietly break that."""
        remote.publish("1.0.0", "# One\n")
        run("build")
        run("lock")
        shutil.rmtree(remote.bare)

        result = run("regenerate")

        assert result.exit_code == ExitCode.CLEAN, result.output

    def test_regenerate_with_a_cold_cache_reproduces_the_locked_version(
        self, remote: Remote, project: Path
    ):
        """A fresh clone regenerates what the lock pins, not what the range now
        admits. Before PRO-164 this re-resolved to 2.0.0 and refused."""
        remote.publish("1.0.0", "# One\n")
        run("build")
        run("lock")
        remote.publish("2.0.0", "# Two\n")
        go_cold()

        result = run("regenerate")

        assert result.exit_code == ExitCode.CLEAN, result.output

    def test_regenerate_with_a_cold_cache_and_no_remote_refuses_cleanly(
        self, remote: Remote, project: Path
    ):
        """The normal state of a second machine, and it used to be a traceback.

        `regenerate` documents that it never re-resolves; with a cold cache it
        ran `git ls-remote` anyway and let `SourceUnavailableError` escape.
        """
        remote.publish("1.0.0", "# One\n")
        run("build")
        run("lock")
        go_cold()
        shutil.rmtree(remote.bare)

        result = run("regenerate")

        assert result.exit_code == ExitCode.SOURCE_ERROR, result.output
        assert result.exception is None or isinstance(result.exception, SystemExit)
        assert "Refusing to regenerate" in result.output

    def test_lock_with_the_remote_gone_reports_an_outage_not_drift(
        self, remote: Remote, project: Path
    ):
        """Re-resolving needs the remote. Recording an unreachable one as
        unchanged would be an unanswerable question written down as a clean
        answer.

        Asserted on the exact code: `!= CLEAN` was satisfied by the traceback
        this used to produce, and 1 would have made an outage indistinguishable
        from real drift.
        """
        remote.publish("1.0.0", "# One\n")
        run("lock")
        shutil.rmtree(remote.bare)

        result = run("lock")

        assert result.exit_code == ExitCode.SOURCE_ERROR, result.output
        assert result.exception is None or isinstance(result.exception, SystemExit)

    def test_a_corrupt_lock_outranks_an_unreachable_remote(self, remote: Remote, project: Path):
        """3, the documented "lock unusable", not 1 with a traceback.

        `inspect` read the lock, recorded that it was unusable, then resolved and
        died before it could return the outcome it already had.
        """
        remote.publish("1.0.0", "# One\n")
        run("lock")
        (project / ".prompticorn" / "prompticorn.lock").write_text(
            ": not a lock\n", encoding="utf-8"
        )
        shutil.rmtree(remote.bare)

        result = run("lock")

        assert result.exit_code == ExitCode.UNUSABLE_LOCK, result.output
        assert result.exception is None or isinstance(result.exception, SystemExit)


class TestLocalDirectory:
    def test_a_directory_source_resolves_without_a_commit(self, tmp_path: Path, monkeypatch):
        """A directory has no mutable names, so there is nothing to pin beyond
        the version itself — and the lock must not invent a commit."""
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
        registry = tmp_path / "registry"
        directory = registry / "local" / "house-standards" / "1.0.0"
        skill = directory / "skills" / "testing-strategies" / "minimal"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# One\n", encoding="utf-8")
        (directory / "artifact.yaml").write_text(
            yaml.safe_dump({"digest": artifact_digest([(UNIT, digest_text("# One\n"))])}),
            encoding="utf-8",
        )
        root = tmp_path / "project"
        root.mkdir()
        write_manifest(
            root,
            sources=[{"name": "shared", "type": "local-dir", "path": "../registry"}],
            artifacts=[{"name": COORDINATE, "version": ">=1.0.0", "source": "shared"}],
        )
        monkeypatch.chdir(root)

        result = run("lock")

        assert result.exit_code == ExitCode.CLEAN, result.output
        artifact = locked(root)[COORDINATE]
        assert artifact.source == "shared"
        assert artifact.commit is None


class TestNothingChangesForBundledArtifacts:
    def test_an_artifact_with_no_source_locks_exactly_as_before(self, tmp_path: Path, monkeypatch):
        """Every lock written before sources existed must still be written the
        same way."""
        monkeypatch.setenv(store_paths.HOME_VARIABLE, str(tmp_path / "store"))
        root = tmp_path / "project"
        root.mkdir()
        write_manifest(root, sources=[], artifacts=[{"name": "local/agent.code", "version": ">=0.0.0-0"}])
        monkeypatch.chdir(root)

        run("lock")

        text = (root / ".prompticorn" / "prompticorn.lock").read_text()
        assert "commit:" not in text
        assert "source:" not in text
