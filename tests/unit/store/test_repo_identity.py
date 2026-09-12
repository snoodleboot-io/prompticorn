"""A repository's identity, independent of where it sits (PRO-128).

The whole point is that the index key is not the path. These tests move
checkouts and clone them, because those are the two events that break a
path-keyed index and neither is unusual.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from prompticorn.store.repo_identity import REPO_ID_FILENAME, repo_id

pytestmark = pytest.mark.skipif(
    shutil.which("git") is None, reason="git identity needs git installed"
)


def git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    git("init", "-q", cwd=root)
    git("config", "user.email", "t@example.com", cwd=root)
    git("config", "user.name", "T", cwd=root)
    (root / "README.md").write_text("hello\n", encoding="utf-8")
    git("add", ".", cwd=root)
    git("commit", "-qm", "first", cwd=root)
    return root


class TestGitRepositories:
    def test_identity_is_stable_across_calls(self, repo: Path):
        assert repo_id(repo) == repo_id(repo)

    def test_identity_survives_moving_the_checkout(self, repo: Path, tmp_path: Path):
        """A path-keyed index orphans every install the moment someone
        reorganises their projects directory."""
        before = repo_id(repo)
        moved = tmp_path / "elsewhere" / "renamed"
        moved.parent.mkdir()
        shutil.move(str(repo), str(moved))

        assert repo_id(moved) == before

    def test_identity_survives_re_cloning(self, repo: Path, tmp_path: Path):
        """Two clones of one project are the same project."""
        clone = tmp_path / "clone"
        subprocess.run(
            ["git", "clone", "-q", str(repo), str(clone)], check=True, capture_output=True
        )

        assert repo_id(clone) == repo_id(repo)

    def test_identity_does_not_change_when_new_commits_land(self, repo: Path):
        """It is the *root* commit; HEAD moves constantly."""
        before = repo_id(repo)
        (repo / "second.md").write_text("more\n", encoding="utf-8")
        git("add", ".", cwd=repo)
        git("commit", "-qm", "second", cwd=repo)

        assert repo_id(repo) == before

    def test_two_unrelated_repositories_differ(self, repo: Path, tmp_path: Path):
        other = tmp_path / "other"
        other.mkdir()
        git("init", "-q", cwd=other)
        git("config", "user.email", "t@example.com", cwd=other)
        git("config", "user.name", "T", cwd=other)
        (other / "x").write_text("x\n", encoding="utf-8")
        git("add", ".", cwd=other)
        git("commit", "-qm", "first", cwd=other)

        assert repo_id(repo) != repo_id(other)

    def test_a_git_repo_writes_no_id_file(self, repo: Path):
        """Nothing to persist when the repository already has an identity."""
        repo_id(repo)

        assert not (repo / ".prompticorn" / REPO_ID_FILENAME).exists()


class TestOutsideGit:
    def test_an_identity_is_generated_and_persisted(self, tmp_path: Path):
        root = tmp_path / "plain"
        root.mkdir()

        first = repo_id(root)

        assert (root / ".prompticorn" / REPO_ID_FILENAME).is_file()
        assert repo_id(root) == first

    def test_the_persisted_identity_survives_a_move(self, tmp_path: Path):
        root = tmp_path / "plain"
        root.mkdir()
        before = repo_id(root)
        moved = tmp_path / "moved"
        shutil.move(str(root), str(moved))

        assert repo_id(moved) == before

    def test_two_plain_directories_differ(self, tmp_path: Path):
        one, two = tmp_path / "one", tmp_path / "two"
        one.mkdir()
        two.mkdir()

        assert repo_id(one) != repo_id(two)

    def test_a_repository_with_no_commits_still_gets_an_identity(self, tmp_path: Path):
        """`git init` with nothing committed has no root commit to read."""
        root = tmp_path / "empty"
        root.mkdir()
        git("init", "-q", cwd=root)

        assert repo_id(root)
