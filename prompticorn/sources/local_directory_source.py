"""Artifacts published to a directory on this machine (PRO-124).

The simplest real source, and the one every other implementation is checked
against: a git source is this plus a clone, and a remote registry is this plus a
download.

Layout, mirroring the identity it serves::

    <root>/<namespace>/<name>/<version>/
        artifact.yaml     # at minimum: digest
        agents/ skills/ workflows/ ...   # the unit tree, laid out as bundled

The digest lives in ``artifact.yaml`` rather than being computed from the tree.
A digest derived from the content it is meant to certify would agree with itself
no matter what happened to the files, which is a checksum that can never fail.

**Symlinks are resolved and checked, not trusted.** A published directory is
data from somewhere else, and the cheapest way to read ``/etc/shadow`` through a
tool like this is to publish an artifact whose version directory is a symlink.
Every path is resolved and confirmed to still sit under the root before it is
opened.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import yaml

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.errors import ArtifactError
from prompticorn.artifact.pinned_artifact import PinnedArtifact
from prompticorn.artifact.semantic_version import SemanticVersion
from prompticorn.sources.artifact_content_source import ArtifactContentSource
from prompticorn.sources.artifact_source import ArtifactSource
from prompticorn.sources.errors import ArtifactNotFoundError, SourceUnavailableError
from prompticorn.sources.fetched_artifact import FetchedArtifact

MANIFEST_FILENAME = "artifact.yaml"
DIGEST_KEY = "digest"


class LocalDirectorySource(ArtifactSource):
    """Artifacts published under a directory tree.

    Args:
        root: Directory holding ``<namespace>/<name>/<version>/`` artifacts.
        name: What this source calls itself in errors and in the lock.
    """

    def __init__(self, root: Path, name: str = "local-dir") -> None:
        self._root = Path(root)
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def root(self) -> Path:
        return self._root

    def list_artifacts(self) -> Iterable[ArtifactId]:
        """Every published version, sorted by rendered identity.

        Entries that are not artifacts — a stray file, a directory whose name is
        not a version — are skipped rather than raised on. A source is a shared
        directory; refusing to list anything because someone left a README in it
        would make the whole source unusable for one irrelevant file.
        """
        root = self._resolved_root()
        found: list[ArtifactId] = []
        for namespace_dir in self._safe_children(root):
            for name_dir in self._safe_children(namespace_dir):
                for version_dir in self._safe_children(name_dir):
                    if not (version_dir / MANIFEST_FILENAME).is_file():
                        continue
                    try:
                        version = SemanticVersion.parse(version_dir.name)
                    except ArtifactError:
                        # A directory whose name is not a version — a `draft/`
                        # or a working copy. Not an artifact, not an error.
                        continue
                    found.append(
                        ArtifactId(
                            namespace=namespace_dir.name, name=name_dir.name, version=version
                        )
                    )
        return tuple(sorted(found, key=lambda artifact: artifact.render()))

    def _fetch(self, artifact_id: ArtifactId) -> FetchedArtifact:
        """Read one artifact's manifest and expose its unit tree."""
        directory = self._directory_for(artifact_id)
        manifest_path = directory / MANIFEST_FILENAME
        if not manifest_path.is_file():
            raise ArtifactNotFoundError(self._name, artifact_id.render())

        try:
            raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
            raise SourceUnavailableError(
                self._name, f"unreadable {manifest_path}: {error}"
            ) from error

        if not isinstance(raw, dict) or not isinstance(raw.get(DIGEST_KEY), str):
            raise SourceUnavailableError(self._name, f"{manifest_path} records no {DIGEST_KEY}")

        return FetchedArtifact(
            pinned=PinnedArtifact(artifact_id=artifact_id, digest=raw[DIGEST_KEY]),
            content=ArtifactContentSource(root=directory, layer=artifact_id.render()),
        )

    # -- path safety ----------------------------------------------------

    def _resolved_root(self) -> Path:
        """The root, resolved once, or a typed failure if it is not usable."""
        try:
            resolved = self._root.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise SourceUnavailableError(self._name, f"{self._root}: {error}") from error
        if not resolved.is_dir():
            raise SourceUnavailableError(self._name, f"{self._root} is not a directory")
        return resolved

    def _safe_children(self, directory: Path) -> list[Path]:
        """Sub-directories that genuinely live under the root, sorted by name.

        Sorted because enumeration order reaches the caller, and filesystem
        order differs between machines. Filtered because a symlink is the
        obvious way to make a directory listing read somewhere it should not.
        """
        try:
            children = sorted(directory.iterdir(), key=lambda path: path.name)
        except OSError as error:
            raise SourceUnavailableError(self._name, f"{directory}: {error}") from error
        return [child for child in children if child.is_dir() and self._is_inside_root(child)]

    def _is_inside_root(self, path: Path) -> bool:
        """Whether ``path`` still sits under the root once symlinks are followed."""
        try:
            resolved = path.resolve(strict=True)
        except (OSError, RuntimeError):
            return False
        return resolved == self._resolved_root() or self._resolved_root() in resolved.parents

    def _directory_for(self, artifact_id: ArtifactId) -> Path:
        """Where one artifact lives, refusing anything that escapes the root.

        The identity's own fields are validated by ``ArtifactId``, but this does
        not assume that: the check is on the resolved path, which is the thing
        that actually gets opened.
        """
        root = self._resolved_root()
        candidate = root / artifact_id.namespace / artifact_id.name / artifact_id.version.render()
        if not self._is_inside_root(candidate):
            raise ArtifactNotFoundError(self._name, artifact_id.render())
        return candidate
