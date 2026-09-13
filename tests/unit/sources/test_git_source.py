"""`GitSource` against a local bare repository (PRO-125).

No network anywhere: the remote is a bare repository on disk, which exercises
the same transport code as a hosted one without depending on a service.

Most of these are about the tag being untrustworthy. A tag moved upstream must
never change what a pinned build produces, must be *reported* when re-resolving,
and must not strand a build that already has the pinned commit cached.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from prompticorn.artifact.artifact_digest import artifact_digest
from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.content.digest import digest_text
from prompticorn.sources import (
    ArtifactNotFoundError,
    GitSource,
    RefMovedError,
    SourceUnavailableError,
)
from tests.unit.sources.artifact_source_contract import ArtifactSourceContract

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="needs git")

UNIT = "skill/testing-strategies/minimal"


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout.strip()


class Registry:
    """A bare remote plus a working clone used to publish tags into it."""

    def __init__(self, root: Path) -> None:
        self.remote = root / "remote.git"
        self.work = root / "work"
        subprocess.run(["git", "init", "-q", "--bare", str(self.remote)], check=True)
        subprocess.run(
            ["git", "clone", "-q", str(self.remote), str(self.work)],
            check=True,
            capture_output=True,
        )
        git("config", "user.email", "t@example.com", cwd=self.work)
        git("config", "user.name", "T", cwd=self.work)
        git("config", "commit.gpgsign", "false", cwd=self.work)

    def publish(self, name: str, version: str, body: str) -> str:
        """Commit one artifact version, tag it, push. Returns the commit."""
        directory = self.work / "local" / name / version
        skill = directory / "skills" / "testing-strategies" / "minimal"
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(body, encoding="utf-8")
        digest = artifact_digest([(UNIT, digest_text(body))])
        (directory / "artifact.yaml").write_text(yaml.safe_dump({"digest": digest}), encoding="utf-8")
        git("add", ".", cwd=self.work)
        git("commit", "-qm", f"{name} {version}", cwd=self.work)
        tag = f"local/{name}@{version}"
        git("tag", "-f", tag, cwd=self.work)
        git("push", "-q", "-f", "origin", "HEAD", f"refs/tags/{tag}", cwd=self.work)
        return git("rev-parse", "HEAD", cwd=self.work)

    def tag_other(self, name: str) -> None:
        """A tag that is not an artifact identity."""
        git("tag", name, cwd=self.work)
        git("push", "-q", "origin", f"refs/tags/{name}", cwd=self.work)


def identity(name: str, version: str) -> ArtifactId:
    return ArtifactId.parse(f"local/{name}@{version}")


@pytest.fixture
def registry(tmp_path: Path) -> Registry:
    return Registry(tmp_path / "registry")


@pytest.fixture
def source(registry: Registry, tmp_path: Path) -> GitSource:
    registry.publish("house-standards", "1.0.0", "# One\n")
    registry.publish("house-standards", "2.0.0", "# Two\n")
    return GitSource(str(registry.remote), name="house", cache_root=tmp_path / "cache")


class TestContract(ArtifactSourceContract):
    # Overridden here rather than inherited from module scope: the contract
    # declares its own `source` fixture, which shadows a module-level one.
    @pytest.fixture
    def source(self, registry: Registry, tmp_path: Path) -> GitSource:
        registry.publish("house-standards", "1.0.0", "# One\n")
        registry.publish("house-standards", "2.0.0", "# Two\n")
        return GitSource(str(registry.remote), name="house", cache_root=tmp_path / "cache")

    @pytest.fixture
    def known(self, source: GitSource) -> ArtifactId:
        return identity("house-standards", "2.0.0")


class TestTagsAreIdentities:
    def test_tags_list_as_artifacts(self, source: GitSource):
        assert [a.render() for a in source.list_artifacts()] == [
            "local/house-standards@1.0.0",
            "local/house-standards@2.0.0",
        ]

    def test_tags_that_are_not_identities_are_ignored(self, source: GitSource, registry: Registry):
        """A repo can carry tags unrelated to prompticorn; one must not break
        listing."""
        registry.tag_other("v1")
        registry.tag_other("release-candidate")

        assert len(list(source.list_artifacts())) == 2

    def test_a_fetched_version_has_its_content(self, source: GitSource):
        fetched = source.fetch(identity("house-standards", "1.0.0"))

        assert fetched.content.read(fetched.content.units()[0].id) == "# One\n"

    def test_an_unknown_version_raises(self, source: GitSource):
        with pytest.raises(ArtifactNotFoundError):
            source.fetch(identity("house-standards", "9.9.9"))


class TestPinning:
    def test_resolve_commit_returns_the_tagged_commit(self, source: GitSource, registry: Registry):
        commit = registry.publish("house-standards", "3.0.0", "# Three\n")

        assert source.resolve_commit(identity("house-standards", "3.0.0")) == commit

    def test_a_pinned_build_ignores_a_moved_tag(self, registry: Registry, tmp_path: Path):
        """The lockfile's whole guarantee. Moving the tag upstream must not
        change what a build pinned to the old commit produces."""
        source = GitSource(str(registry.remote), cache_root=tmp_path / "cache")
        pinned = registry.publish("house-standards", "1.0.0", "# Original\n")
        registry.publish("house-standards", "1.0.0", "# Rewritten under the same tag\n")

        fetched = source.fetch_pinned(identity("house-standards", "1.0.0"), pinned)

        assert fetched.content.read(fetched.content.units()[0].id) == "# Original\n"

    def test_a_moved_tag_is_detected(self, registry: Registry, tmp_path: Path):
        source = GitSource(str(registry.remote), cache_root=tmp_path / "cache")
        pinned = registry.publish("house-standards", "1.0.0", "# Original\n")
        registry.publish("house-standards", "1.0.0", "# Rewritten\n")

        assert source.ref_moved(identity("house-standards", "1.0.0"), pinned)

    def test_an_unmoved_tag_is_not_reported(self, registry: Registry, tmp_path: Path):
        source = GitSource(str(registry.remote), cache_root=tmp_path / "cache")
        pinned = registry.publish("house-standards", "1.0.0", "# Original\n")

        assert not source.ref_moved(identity("house-standards", "1.0.0"), pinned)

    def test_re_resolving_a_moved_tag_raises_rather_than_following_it(
        self, registry: Registry, tmp_path: Path
    ):
        """Drift to decide on, never an update adopted quietly."""
        source = GitSource(str(registry.remote), cache_root=tmp_path / "cache")
        pinned = registry.publish("house-standards", "1.0.0", "# Original\n")
        registry.publish("house-standards", "1.0.0", "# Rewritten\n")

        with pytest.raises(RefMovedError) as caught:
            source.fetch_resolving(identity("house-standards", "1.0.0"), pinned)

        assert caught.value.pinned == pinned


class TestCache:
    def test_checkouts_are_keyed_by_commit(self, source: GitSource, registry: Registry):
        commit = source.resolve_commit(identity("house-standards", "1.0.0"))

        source.fetch(identity("house-standards", "1.0.0"))

        assert source.is_cached(commit)
        assert source.checkout_path(commit).name == commit

    def test_a_moved_tag_gets_a_new_checkout_not_a_rewritten_one(
        self, registry: Registry, tmp_path: Path
    ):
        """An entry keyed by commit can never be stale."""
        source = GitSource(str(registry.remote), cache_root=tmp_path / "cache")
        first = registry.publish("house-standards", "1.0.0", "# Original\n")
        source.fetch(identity("house-standards", "1.0.0"))
        second = registry.publish("house-standards", "1.0.0", "# Rewritten\n")
        source.fetch(identity("house-standards", "1.0.0"))

        assert source.is_cached(first) and source.is_cached(second)

    def test_two_remotes_do_not_share_a_cache(self, tmp_path: Path):
        one = GitSource("https://example.com/a.git", cache_root=tmp_path / "cache")
        two = GitSource("https://example.com/b.git", cache_root=tmp_path / "cache")

        assert one.cache_directory != two.cache_directory

    def test_the_fetch_is_shallow(self, source: GitSource):
        """One commit's tree, no history."""
        commit = source.resolve_commit(identity("house-standards", "2.0.0"))
        source.fetch(identity("house-standards", "2.0.0"))

        depth = git("rev-list", "--count", "HEAD", cwd=source.checkout_path(commit))

        assert depth == "1"

    def test_an_interrupted_checkout_is_not_trusted(self, source: GitSource, registry: Registry):
        """No marker, no cache hit — a killed fetch must not leave a partial
        tree that every later offline build believes."""
        commit = source.resolve_commit(identity("house-standards", "1.0.0"))
        source.checkout_path(commit).mkdir(parents=True)

        assert not source.is_cached(commit)
        assert source.fetch(identity("house-standards", "1.0.0")).identity == identity(
            "house-standards", "1.0.0"
        )


class TestOffline:
    def test_a_cached_pinned_build_succeeds_with_the_remote_gone(
        self, registry: Registry, tmp_path: Path
    ):
        """The AC: unreachable remote, cached build still succeeds."""
        source = GitSource(str(registry.remote), cache_root=tmp_path / "cache")
        pinned = registry.publish("house-standards", "1.0.0", "# One\n")
        source.fetch_pinned(identity("house-standards", "1.0.0"), pinned)
        shutil.rmtree(registry.remote)

        fetched = source.fetch_pinned(identity("house-standards", "1.0.0"), pinned)

        assert fetched.content.read(fetched.content.units()[0].id) == "# One\n"

    def test_an_unreachable_remote_gives_an_actionable_error(self, tmp_path: Path):
        source = GitSource(str(tmp_path / "no-such-remote.git"), cache_root=tmp_path / "cache")

        with pytest.raises(SourceUnavailableError) as caught:
            list(source.list_artifacts())

        message = str(caught.value)
        assert "no-such-remote.git" in message
        assert "offline" in message

    def test_moved_tag_detection_does_not_guess_when_offline(
        self, registry: Registry, tmp_path: Path
    ):
        """An unanswerable question must not be recorded as a clean answer."""
        source = GitSource(str(registry.remote), cache_root=tmp_path / "cache")
        pinned = registry.publish("house-standards", "1.0.0", "# One\n")
        shutil.rmtree(registry.remote)

        with pytest.raises(SourceUnavailableError):
            source.ref_moved(identity("house-standards", "1.0.0"), pinned)

    def test_an_uncached_pinned_build_needs_the_remote(self, registry: Registry, tmp_path: Path):
        source = GitSource(str(registry.remote), cache_root=tmp_path / "cache")
        pinned = registry.publish("house-standards", "1.0.0", "# One\n")
        shutil.rmtree(registry.remote)

        with pytest.raises(SourceUnavailableError):
            source.fetch_pinned(identity("house-standards", "1.0.0"), pinned)


class TestIntegrity:
    def test_a_pinned_fetch_still_verifies_the_digest(self, registry: Registry, tmp_path: Path):
        """Pinning by commit does not waive the content check."""
        from prompticorn.sources import DigestMismatchError

        directory = registry.work / "local" / "bad" / "1.0.0"
        skill = directory / "skills" / "testing-strategies" / "minimal"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("# Real\n", encoding="utf-8")
        (directory / "artifact.yaml").write_text(yaml.safe_dump({"digest": "0" * 64}), encoding="utf-8")
        git("add", ".", cwd=registry.work)
        git("commit", "-qm", "bad", cwd=registry.work)
        git("tag", "local/bad@1.0.0", cwd=registry.work)
        git("push", "-q", "origin", "HEAD", "refs/tags/local/bad@1.0.0", cwd=registry.work)
        commit = git("rev-parse", "HEAD", cwd=registry.work)
        source = GitSource(str(registry.remote), cache_root=tmp_path / "cache")

        with pytest.raises(DigestMismatchError):
            source.fetch_pinned(identity("bad", "1.0.0"), commit)
