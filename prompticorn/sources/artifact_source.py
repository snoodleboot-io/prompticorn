"""Where artifacts come from (PRO-124).

The abstraction EE's hosted registry later implements. Getting the contract
right here is what keeps EE extending the core rather than forking it, so the
guarantees below belong to the *interface* and not to any one implementation.

**Named ``ArtifactSource``, not ``Source``.** The ticket says ``Source``, but
``ContentSource`` already exists one level down: it answers "give me this
*unit*'s bytes", while this answers "give me this *artifact*". Two interfaces a
letter apart, at different granularities, is the same overloading PRO-141 spent
a change removing from the word "artifact". The longer name costs nothing.

**Integrity is enforced here, once.** :meth:`fetch` is not overridden by
implementations; they implement :meth:`_fetch` and this class verifies what
comes back. A corrupt local directory therefore fails exactly as a corrupt
download will, and a future remote source inherits the guarantee instead of
being trusted to reimplement it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.version_range import VersionRange
from prompticorn.sources.errors import DigestMismatchError, VersionNotFoundError
from prompticorn.sources.fetched_artifact import FetchedArtifact


class ArtifactSource(ABC):
    """A place artifacts can be listed, resolved and fetched from."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier used in errors and recorded in the lock."""

    @abstractmethod
    def list_artifacts(self) -> Iterable[ArtifactId]:
        """Every artifact version this source carries.

        Returns:
            Identities in a stable order. Sorted rather than
            filesystem-ordered, so two machines enumerate the same source the
            same way.

        Raises:
            SourceUnavailableError: If the source cannot be read at all.
        """

    @abstractmethod
    def _fetch(self, artifact_id: ArtifactId) -> FetchedArtifact:
        """Retrieve one artifact, without verifying it.

        Implementations do the reading; :meth:`fetch` does the checking.

        Raises:
            ArtifactNotFoundError: If this source does not carry it.
            SourceUnavailableError: If the source cannot be read at all.
        """

    def fetch(self, artifact_id: ArtifactId) -> FetchedArtifact:
        """Retrieve one artifact and verify its content before returning it.

        Deliberately not abstract. An implementation that forgot to verify
        would be indistinguishable from one that did until the day it mattered.

        Raises:
            ArtifactNotFoundError: If this source does not carry it.
            DigestMismatchError: If the content does not hash to its recorded
                digest — the bytes changed under a version that is supposed to
                be immutable.
            SourceUnavailableError: If the source cannot be read at all.
        """
        fetched = self._fetch(artifact_id)
        actual = fetched.computed_digest()
        if actual != fetched.digest:
            raise DigestMismatchError(fetched.identity.render(), fetched.digest, actual)
        return fetched

    def versions_of(self, coordinate: str) -> tuple[ArtifactId, ...]:
        """Every version of one artifact, oldest first.

        Ordered by version rather than by name, so "the newest" is the last
        element rather than whichever string sorted highest — ``2.10.0`` sorts
        below ``2.9.0`` as text and above it as a version.
        """
        matches = [
            artifact for artifact in self.list_artifacts() if artifact.coordinate == coordinate
        ]
        return tuple(sorted(matches, key=lambda artifact: artifact.version))

    def resolve_version(self, coordinate: str, spec: str) -> ArtifactId:
        """The highest released version of ``coordinate`` that ``spec`` admits.

        Highest rather than first: a range exists to say "anything compatible",
        and the useful answer to that is the newest compatible thing.

        Args:
            coordinate: ``namespace/name``.
            spec: A version range, e.g. ``>=2.1.0,<3.0.0``.

        Raises:
            VersionNotFoundError: If nothing satisfies the range. The message
                names what *is* available, because "no match" without the
                alternatives leaves the reader with nowhere to go.
            SourceUnavailableError: If the source cannot be read at all.
        """
        candidates = self.versions_of(coordinate)
        admitted = VersionRange.parse(spec)
        for artifact in reversed(candidates):
            if admitted.contains(artifact.version):
                return artifact
        raise VersionNotFoundError(
            self.name,
            coordinate,
            spec,
            tuple(artifact.version.render() for artifact in candidates),
        )

    def has(self, artifact_id: ArtifactId) -> bool:
        """Whether this source carries an exact version."""
        return artifact_id in set(self.list_artifacts())

    # -- pinning (PRO-151) -----------------------------------------------
    #
    # Defaults describe a source whose versions are immutable by construction,
    # which is every source except one addressed by mutable names. A source
    # like git overrides these; nothing else needs to know it exists, so the
    # resolver never has to ask what kind of source it is holding.

    def commit_for(self, artifact_id: ArtifactId) -> str | None:
        """The immutable id a mutable version name resolved to, if any.

        None means the version *is* the immutable reference and there is
        nothing further to pin.
        """
        return None

    def can_fetch_offline(self, artifact_id: ArtifactId, commit: str | None) -> bool:
        """Whether a locked version can be fetched without reaching the source.

        False by default: a source that cannot promise it must not be treated
        as though it can, or a frozen build would contact a remote it claimed
        not to need.
        """
        return False

    def fetch_locked(self, artifact_id: ArtifactId, commit: str | None) -> FetchedArtifact:
        """Fetch exactly what a lock recorded.

        Defaults to :meth:`fetch`, which is exact for any source whose versions
        cannot move. Still integrity-checked either way.
        """
        return self.fetch(artifact_id)
