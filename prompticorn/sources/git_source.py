"""Artifacts published as tags in a git repository (PRO-125).

Git as the OSS registry: no service to run, yet one definition set can be shared
across every repository you own, and carried between machines by pushing and
pulling.

**A tag is a rendered artifact identity.** The tag ``local/house-standards@2.1.0``
parses with :meth:`ArtifactId.parse` unchanged, so the version list is the tag
list and there is no second naming scheme to keep in step. At that tag the tree
holds a local-directory layout, so fetching is a checkout followed by the source
that already reads that layout.

**Commits are pinned; tags are not trusted.** A tag can be moved upstream; a
commit cannot. Everything cached here is keyed by the commit a tag resolved to,
and :meth:`fetch_pinned` builds from a commit rather than a tag. A moved tag is
therefore reported by :meth:`ref_moved` as drift to decide on — never followed
silently, which is the one thing a lock exists to prevent.

**Auth is git's.** SSH agent, credential helper, existing config — whatever the
user's git already does. This module handles no credentials, which keeps the
source free of any secret-management surface.

**Offline works for pinned builds.** A commit already checked out needs no
remote, because its content cannot change. Only listing and re-resolution need
the network, and both fail with a message that says so.
"""

from __future__ import annotations

import hashlib
import shutil
import subprocess
from collections.abc import Iterable
from pathlib import Path

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.errors import ArtifactError
from prompticorn.sources.artifact_source import ArtifactSource
from prompticorn.sources.errors import (
    ArtifactNotFoundError,
    DigestMismatchError,
    RefMovedError,
    SourceUnavailableError,
)
from prompticorn.sources.fetched_artifact import FetchedArtifact
from prompticorn.sources.local_directory_source import LocalDirectorySource
from prompticorn.store.store_paths import ensure_directory, git_cache_root
from prompticorn.text_writer import write_text

TAG_PREFIX = "refs/tags/"
# Annotated tags list twice in ls-remote: the tag object, and `^{}` for the
# commit it peels to. The peeled line is the commit, which is what gets pinned.
_PEELED_SUFFIX = "^{}"

# A hung remote must not hang the CLI. Generous, because a first fetch over a
# slow link is legitimate; bounded, because an unbounded wait is not.
GIT_TIMEOUT_SECONDS = 120

# Characters of the URL digest used to name a remote's cache directory. The
# directory is a namespace, not an identity, so a short prefix is plenty.
_URL_DIGEST_CHARS = 16


class GitSource(ArtifactSource):
    """Artifacts tagged in a git repository.

    Args:
        url: Anything ``git`` accepts as a remote — URL, SSH address, or path.
        name: What this source calls itself in errors and in the lock.
        cache_root: Where checkouts live. Defaults to the one under
            ``PROMPTICORN_HOME``.
    """

    def __init__(self, url: str, name: str = "git", cache_root: Path | None = None) -> None:
        self._url = url
        self._name = name
        self._cache_root = cache_root

    @property
    def name(self) -> str:
        return self._name

    @property
    def url(self) -> str:
        return self._url

    # -- listing ---------------------------------------------------------

    def list_artifacts(self) -> Iterable[ArtifactId]:
        """Every tag that is an artifact identity, sorted.

        Tags that do not parse — ``v1``, ``release-candidate`` — are skipped. A
        repository can carry tags that have nothing to do with prompticorn, and
        refusing to list anything because of one would make the source useless.
        """
        return tuple(sorted(self._tags(), key=lambda artifact: artifact.render()))

    def resolve_commit(self, artifact_id: ArtifactId) -> str:
        """The commit this version's tag points at on the remote right now.

        Raises:
            ArtifactNotFoundError: If there is no such tag.
            SourceUnavailableError: If the remote cannot be reached.
        """
        commit = self._tags().get(artifact_id)
        if commit is None:
            raise ArtifactNotFoundError(self._name, artifact_id.render())
        return commit

    def ref_moved(self, artifact_id: ArtifactId, pinned_commit: str) -> bool:
        """Whether the tag has moved away from the commit a lock pinned.

        Raises:
            SourceUnavailableError: If the remote cannot be reached. Deliberately
                not treated as "unmoved": an unanswerable question must not be
                recorded as a clean one.
        """
        return self.resolve_commit(artifact_id) != pinned_commit

    # -- fetching --------------------------------------------------------

    def _fetch(self, artifact_id: ArtifactId) -> FetchedArtifact:
        """Fetch whatever the tag points at now. Requires the network."""
        return self._fetch_commit(artifact_id, self.resolve_commit(artifact_id))

    def fetch_pinned(self, artifact_id: ArtifactId, commit: str) -> FetchedArtifact:
        """Fetch a version from the exact commit a lock recorded.

        The path a locked build takes. It uses a cached checkout when one exists
        and contacts the remote only when one does not, so a build that has run
        once keeps working with the remote unreachable.

        Integrity is still checked: the pinned commit's content is verified
        against its manifest digest exactly as :meth:`fetch` would.

        Raises:
            SourceUnavailableError: If the commit is not cached and the remote
                cannot be reached.
            ArtifactNotFoundError: If the commit does not carry this version.
            DigestMismatchError: If its content does not match its digest.
        """
        fetched = self._fetch_commit(artifact_id, commit)
        actual = fetched.computed_digest()
        if actual != fetched.digest:
            raise DigestMismatchError(fetched.identity.render(), fetched.digest, actual)
        return fetched

    def fetch_resolving(self, artifact_id: ArtifactId, pinned_commit: str) -> FetchedArtifact:
        """Fetch the pinned commit, refusing if the tag has moved.

        For re-resolution: where :meth:`fetch_pinned` builds what was locked no
        matter what, this checks that what was locked is still what the tag
        says, and raises rather than following it.

        Raises:
            RefMovedError: If the tag now points somewhere else.
        """
        current = self.resolve_commit(artifact_id)
        if current != pinned_commit:
            raise RefMovedError(artifact_id.render(), pinned_commit, current)
        return self.fetch_pinned(artifact_id, pinned_commit)

    def _fetch_commit(self, artifact_id: ArtifactId, commit: str) -> FetchedArtifact:
        """Check out ``commit`` if needed, then read the version from it."""
        checkout = self._checkout(commit)
        # The tree is a local-directory layout, so the reading is delegated to
        # the source that already understands it rather than restated here.
        return LocalDirectorySource(checkout, name=self._name)._fetch(artifact_id)

    # -- cache -----------------------------------------------------------

    @property
    def cache_directory(self) -> Path:
        """This remote's checkouts. Keyed by URL so two remotes never share one."""
        root = self._cache_root if self._cache_root is not None else git_cache_root()
        digest = hashlib.sha256(self._url.encode("utf-8")).hexdigest()[:_URL_DIGEST_CHARS]
        return root / digest

    def checkout_path(self, commit: str) -> Path:
        """Where one commit's tree lives, whether or not it has been fetched."""
        return self.cache_directory / commit

    def is_cached(self, commit: str) -> bool:
        return (self.checkout_path(commit) / ".complete").is_file()

    def _checkout(self, commit: str) -> Path:
        """A working tree for ``commit``, fetched shallowly on first use.

        Keyed by commit, so an entry can never be stale: a commit's content is
        fixed forever, and a moved tag resolves to a *different* directory rather
        than rewriting this one.

        A marker is written last. A checkout interrupted halfway has no marker,
        is treated as absent, and is rebuilt — otherwise a killed fetch would
        leave a partial tree that every later offline build trusted.
        """
        target = self.checkout_path(commit)
        if self.is_cached(commit):
            return target

        if target.exists():
            shutil.rmtree(target)
        ensure_directory(self.cache_directory)
        staging = self.cache_directory / f".{commit}.partial"
        if staging.exists():
            shutil.rmtree(staging)

        try:
            self._git("init", "--quiet", str(staging))
            # Shallow and by commit id: one commit's tree, no history. Fetching
            # by id rather than by tag is what lets a pinned build succeed after
            # the tag has moved on.
            self._git("fetch", "--quiet", "--depth", "1", self._url, commit, cwd=staging)
            self._git("checkout", "--quiet", "FETCH_HEAD", cwd=staging)
            write_text(staging / ".complete", f"{commit}\n")
            staging.rename(target)
        except BaseException:
            shutil.rmtree(staging, ignore_errors=True)
            raise
        return target

    # -- git -------------------------------------------------------------

    def _tags(self) -> dict[ArtifactId, str]:
        """Artifact identity → commit, from one ls-remote call."""
        output = self._git("ls-remote", "--tags", self._url)
        tags: dict[str, str] = {}
        for line in output.splitlines():
            commit, _, ref = line.partition("\t")
            if not ref.startswith(TAG_PREFIX):
                continue
            name = ref.removeprefix(TAG_PREFIX)
            if name.endswith(_PEELED_SUFFIX):
                # The peeled commit wins over the annotated tag object.
                tags[name.removesuffix(_PEELED_SUFFIX)] = commit
            else:
                tags.setdefault(name, commit)

        found: dict[ArtifactId, str] = {}
        for name, commit in tags.items():
            try:
                found[ArtifactId.parse(name)] = commit
            except ArtifactError:
                continue
        return found

    def _git(self, *args: str, cwd: Path | None = None) -> str:
        """Run git, turning every failure into an actionable source error."""
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=cwd,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=GIT_TIMEOUT_SECONDS,
                check=False,
            )
        except FileNotFoundError as error:
            raise SourceUnavailableError(
                self._name, "git is not installed or not on PATH"
            ) from error
        except subprocess.TimeoutExpired as error:
            raise SourceUnavailableError(
                self._name,
                f"git {args[0]} timed out after {GIT_TIMEOUT_SECONDS}s against {self._url}",
            ) from error
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip().splitlines()
            reason = detail[-1] if detail else f"git {args[0]} exited {completed.returncode}"
            raise SourceUnavailableError(
                self._name,
                f"{reason} (remote: {self._url}). Check the URL and that your git "
                "credentials can reach it; a build pinned to a cached commit will "
                "still work offline.",
            )
        return completed.stdout
