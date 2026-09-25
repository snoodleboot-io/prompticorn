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
    CacheCorruptError,
    CommitNotFoundError,
    GitSource,
    InvalidCommitError,
    RefMovedError,
    SourceUnavailableError,
    VersionNotFoundError,
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

    def publish(self, name: str, version: str, body: str, annotated: bool = False) -> str:
        """Commit one artifact version, tag it, push. Returns the commit.

        Args:
            annotated: Tag with a tag *object* rather than a lightweight ref.
                Annotated tags list twice in ``ls-remote``, so they are the only
                thing that exercises peeling.
        """
        directory = self.work / "local" / name / version
        skill = directory / "skills" / "testing-strategies" / "minimal"
        skill.mkdir(parents=True, exist_ok=True)
        (skill / "SKILL.md").write_text(body, encoding="utf-8")
        digest = artifact_digest([(UNIT, digest_text(body))])
        (directory / "artifact.yaml").write_text(yaml.safe_dump({"digest": digest}), encoding="utf-8")
        git("add", ".", cwd=self.work)
        git("commit", "-qm", f"{name} {version}", cwd=self.work)
        tag = f"local/{name}@{version}"
        if annotated:
            git("tag", "-f", "-a", "-m", f"release {version}", tag, cwd=self.work)
        else:
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


# A commit id and nothing else. Everything else in this list is something a
# `prompticorn.lock` could carry into a path join or a git argument list, and a
# lock file travels with a repository — so it is input from outside.
REFUSED_PINS = [
    pytest.param("", id="empty"),
    pytest.param("..", id="parent"),
    pytest.param("../../victim", id="traversal"),
    pytest.param("/nonexistent-prompticorn-victim", id="absolute"),
    pytest.param("--upload-pack=false", id="option"),
    pytest.param("-q", id="short-option"),
    pytest.param("0" * 40 + "\n", id="trailing-newline"),
    pytest.param("0" * 40 + " ", id="trailing-space"),
    pytest.param("0" * 39, id="too-short"),
    pytest.param("0" * 41, id="between-lengths"),
    pytest.param("0" * 65, id="too-long"),
    pytest.param("A" * 40, id="uppercase"),
    pytest.param("z" * 40, id="not-hex"),
    pytest.param("refs/tags/local/house-standards@1.0.0", id="ref-name"),
    pytest.param("HEAD", id="head"),
    pytest.param("main", id="branch"),
]


@pytest.fixture
def no_remote(tmp_path: Path) -> GitSource:
    """A source whose remote does not exist.

    A refused pin is refused before anything is contacted, and asserting that
    against an unreachable remote is what proves it: reaching the remote at all
    would raise `SourceUnavailableError` instead.
    """
    return GitSource(
        str(tmp_path / "no-such-remote.git"), name="house", cache_root=tmp_path / "cache"
    )


class TestPinValidation:
    """A pin is a commit id, checked before it is used for anything (PRO-163).

    The pin reaches a filesystem path and a git argument list, and both are
    dangerous: the path is handed to `shutil.rmtree` and the argument is parsed
    by git as an option if it starts with a dash.
    """

    @pytest.mark.parametrize("pin", REFUSED_PINS)
    def test_a_pin_that_is_not_a_commit_id_is_refused(self, no_remote: GitSource, pin: str):
        with pytest.raises(InvalidCommitError):
            no_remote.fetch_pinned(identity("house-standards", "1.0.0"), pin)

    @pytest.mark.parametrize("pin", REFUSED_PINS)
    def test_the_path_for_a_bad_pin_is_never_even_computed(self, no_remote: GitSource, pin: str):
        """`checkout_path` is public and is where the traversal would land."""
        with pytest.raises(InvalidCommitError):
            no_remote.checkout_path(pin)

    @pytest.mark.parametrize("pin", REFUSED_PINS)
    def test_re_resolution_refuses_a_bad_pin_before_touching_the_remote(
        self, no_remote: GitSource, pin: str
    ):
        with pytest.raises(InvalidCommitError):
            no_remote.fetch_resolving(identity("house-standards", "1.0.0"), pin)

    def test_a_traversing_pin_does_not_delete_the_directory_it_points_at(
        self, no_remote: GitSource, tmp_path: Path
    ):
        """The blocker. `cache/<digest>/../../victim` is `tmp_path/victim`, and
        the unguarded path handed it straight to `shutil.rmtree`."""
        victim = tmp_path / "victim"
        (victim / "keep").mkdir(parents=True)
        (victim / "keep" / "file.txt").write_text("precious\n", encoding="utf-8")

        with pytest.raises(InvalidCommitError):
            no_remote.fetch_pinned(identity("house-standards", "1.0.0"), "../../victim")

        assert (victim / "keep" / "file.txt").read_text(encoding="utf-8") == "precious\n"

    def test_a_parent_pin_does_not_wipe_the_cache(self, source: GitSource):
        """`..` resolves to the cache directory itself, taking every other
        checkout with it — including ones a concurrent build is reading."""
        source.fetch(identity("house-standards", "1.0.0"))
        cached = source.resolve_commit(identity("house-standards", "1.0.0"))

        with pytest.raises(InvalidCommitError):
            source.fetch_pinned(identity("house-standards", "1.0.0"), "..")

        assert source.is_cached(cached)

    def test_an_option_shaped_pin_is_not_handed_to_git_as_an_option(
        self, source: GitSource, tmp_path: Path
    ):
        """`git fetch <url> --upload-pack=<command>` runs <command>. The pin is
        positional, but git parses options after positionals too, so ordering is
        no defence — only refusing the value is."""
        sentinel = tmp_path / "pwned"

        with pytest.raises(InvalidCommitError):
            source.fetch_pinned(
                identity("house-standards", "1.0.0"), f"--upload-pack=touch {sentinel}"
            )

        assert not sentinel.exists()

    @pytest.mark.parametrize("pin", ["0" * 40, "a" * 64, "0123456789abcdef" * 4])
    def test_a_commit_id_is_accepted(self, no_remote: GitSource, pin: str):
        """sha1 is 40 hex, sha256 is 64. Both are commit ids; refusing the
        longer one would break the moment a repository is converted."""
        assert no_remote.checkout_path(pin).name == pin
        assert not no_remote.is_cached(pin)


class TestTheCheckoutIsTheRequestedCommit:
    def test_a_fetch_that_lands_elsewhere_is_refused(self, source: GitSource):
        """`git fetch <url> <refish>` takes refs as well as object ids, so the
        promise that a cache entry is keyed by its own content rests on a check,
        not on how git happens to resolve a 40-hex argument today.

        Faked at the `git` seam because today's git does resolve a full hex
        argument as an object id, which is exactly why the branch would
        otherwise ship untested.
        """
        other = source.resolve_commit(identity("house-standards", "2.0.0"))
        pinned = source.resolve_commit(identity("house-standards", "1.0.0"))
        original = GitSource._git

        def lying_git(self, *args: str, **kwargs):
            if args[0] == "rev-parse":
                return f"{other}\n"
            return original(self, *args, **kwargs)

        source._git = lying_git.__get__(source, GitSource)

        with pytest.raises(CommitNotFoundError) as caught:
            source.fetch_pinned(identity("house-standards", "1.0.0"), pinned)

        assert caught.value.commit == pinned
        assert not source.is_cached(pinned)

    def test_a_pinned_commit_the_remote_no_longer_has_is_not_a_network_error(
        self, registry: Registry, tmp_path: Path
    ):
        """The one failure a lock exists to surface. Reporting it as "check your
        credentials" sends the reader to the wrong problem entirely."""
        source = GitSource(str(registry.remote), name="house", cache_root=tmp_path / "cache")
        registry.publish("house-standards", "1.0.0", "# One\n")

        with pytest.raises(CommitNotFoundError):
            source.fetch_pinned(identity("house-standards", "1.0.0"), "0" * 40)


class TestCorruptCache:
    def test_a_file_where_a_checkout_belongs_is_reported_not_crashed(self, source: GitSource):
        """`shutil.rmtree` raises `NotADirectoryError` on a file, which escapes
        as an unhandled crash instead of an error the CLI can report."""
        commit = source.resolve_commit(identity("house-standards", "1.0.0"))
        squatter = source.checkout_path(commit)
        squatter.parent.mkdir(parents=True, exist_ok=True)
        squatter.write_text("not a checkout\n", encoding="utf-8")

        with pytest.raises(CacheCorruptError):
            source.fetch(identity("house-standards", "1.0.0"))


class TestConcurrentFetches:
    """Two builds of the same commit must not corrupt each other.

    Nothing here locks, so the staging area has to be private to one fetch and
    the hand-over has to tolerate losing the race.
    """

    def test_staging_is_private_to_one_fetch(self, source: GitSource):
        """A deterministic `.{commit}.partial` is shared state: the second build
        deletes the first one's half-fetched tree, and the first one's rename
        then fails with a bare `OSError: Directory not empty`."""
        seen: list[str] = []
        original = GitSource._git

        def recording_git(self: GitSource, *args: str, **kwargs: object) -> str:
            if args[0] == "init":
                seen.append(Path(args[-1]).name)
            return original(self, *args, **kwargs)

        source._git = recording_git.__get__(source, GitSource)
        wanted = identity("house-standards", "1.0.0")
        commit = source.resolve_commit(wanted)

        source.fetch(wanted)
        shutil.rmtree(source.checkout_path(commit))
        source.fetch(wanted)

        assert len(seen) == 2
        assert seen[0] != seen[1]

    def test_a_checkout_another_build_finished_first_is_kept(
        self, source: GitSource, tmp_path: Path
    ):
        """The loser of the race must not crash on the hand-over. The winner's
        tree is the same tree by construction — the entry is named after the
        commit — so keeping it is correct as well as cheaper."""
        wanted = identity("house-standards", "1.0.0")
        commit = source.resolve_commit(wanted)
        source.fetch(wanted)
        winner = tmp_path / "winner"
        shutil.copytree(source.checkout_path(commit), winner, symlinks=True)
        shutil.rmtree(source.checkout_path(commit))
        original = GitSource._git

        def racing_git(self: GitSource, *args: str, **kwargs: object) -> str:
            output = original(self, *args, **kwargs)
            if args[0] == "checkout":
                # Another build completes this commit while this one still has
                # its tree in staging.
                shutil.copytree(winner, self.checkout_path(commit))
            return output

        source._git = racing_git.__get__(source, GitSource)

        fetched = source.fetch_pinned(wanted, commit)

        assert fetched.content.read(fetched.content.units()[0].id) == "# One\n"
        assert source.is_cached(commit)


class TestAnnotatedTags:
    """Annotated tags list twice in `ls-remote`: the tag object, then `^{}` for
    the commit it peels to. Only the peeled line may be pinned, and every other
    test here tags lightweight — so without these the peeling branch is guesswork.
    """

    def test_an_annotated_tag_resolves_to_the_commit_not_the_tag_object(
        self, registry: Registry, tmp_path: Path
    ):
        commit = registry.publish("house-standards", "4.0.0", "# Four\n", annotated=True)
        source = GitSource(str(registry.remote), name="house", cache_root=tmp_path / "cache")

        resolved = source.resolve_commit(identity("house-standards", "4.0.0"))

        assert resolved == commit
        assert resolved != git("rev-parse", "local/house-standards@4.0.0", cwd=registry.work)

    def test_an_annotated_tag_re_resolves_and_checks_out_clean(
        self, registry: Registry, tmp_path: Path
    ):
        """End to end: the commit a lock would record from an annotated tag has
        to be the one re-resolution finds and the one that checks out. Pinning
        the tag object instead reads as drift on the very next build."""
        commit = registry.publish("house-standards", "4.0.0", "# Four\n", annotated=True)
        source = GitSource(str(registry.remote), name="house", cache_root=tmp_path / "cache")

        fetched = source.fetch_resolving(identity("house-standards", "4.0.0"), commit)

        assert fetched.content.read(fetched.content.units()[0].id) == "# Four\n"


class TestOneResolutionPerLock:
    """The pin and the content it describes come from the same lookup (PRO-164).

    `resolve_version`, then `fetch`, then `commit_for` was three `ls-remote`
    calls: the digest came from the second lookup's tree and the pin from the
    third. A tag moved in that gap made the lock record digest(A) beside
    commit(B) — a lock nothing can ever verify.
    """

    def test_resolve_pinned_returns_the_version_and_its_commit(self, source: GitSource):
        artifact_id, commit = source.resolve_pinned("local/house-standards", ">=1.0.0")

        assert artifact_id == identity("house-standards", "2.0.0")
        assert commit == source.resolve_commit(artifact_id)

    def test_resolve_pinned_applies_the_range(self, source: GitSource):
        """The same selection rule as `resolve_version`, not a second copy of it."""
        artifact_id, _ = source.resolve_pinned("local/house-standards", ">=1.0.0,<2.0.0")

        assert artifact_id == identity("house-standards", "1.0.0")

    def test_an_unsatisfiable_range_still_names_what_is_available(self, source: GitSource):
        with pytest.raises(VersionNotFoundError) as caught:
            source.resolve_pinned("local/house-standards", ">=9.0.0")

        assert caught.value.available == ("1.0.0", "2.0.0")

    def test_it_asks_the_remote_once(self, source: GitSource, monkeypatch):
        """The reason it is one method. Counted rather than asserted in prose,
        because "three calls where one would do" is exactly what regressed."""
        calls: list[tuple[str, ...]] = []
        real = GitSource._git

        def counting(self, *args: str, **kwargs):
            calls.append(args)
            return real(self, *args, **kwargs)

        monkeypatch.setattr(GitSource, "_git", counting)

        source.resolve_pinned("local/house-standards", ">=1.0.0")

        assert [args[0] for args in calls] == ["ls-remote"]
