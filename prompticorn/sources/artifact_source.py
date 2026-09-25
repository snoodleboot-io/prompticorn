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
        return self.highest_admitted(self.versions_of(coordinate), coordinate, spec)

    def highest_admitted(
        self, candidates: tuple[ArtifactId, ...], coordinate: str, spec: str
    ) -> ArtifactId:
        """The newest of ``candidates`` — oldest first — that ``spec`` admits.

        Separated from :meth:`resolve_version` so a source that already holds the
        candidate list from an earlier call can apply the *same* selection rule
        to it rather than restating the rule and drifting from it.

        Raises:
            VersionNotFoundError: If nothing satisfies the range.
        """
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

    # -- pinning (PRO-151, corrected by PRO-164) -------------------------
    #
    # Defaults describe a source whose versions are immutable by construction,
    # which is every source except one addressed by mutable names. A source
    # like git overrides these; nothing else needs to know it exists, so the
    # resolver never has to ask what kind of source it is holding.

    def resolve_pinned(self, coordinate: str, spec: str) -> tuple[ArtifactId, str | None]:
        """The version a range resolves to, and the immutable id to pin with it.

        One call rather than "resolve the version, then ask what it points at",
        because those are two answers to a question that can change between
        them: a tag moved in the gap would have the lock record the digest of one
        commit beside the id of another. Everything a source records about one
        resolution is therefore derived from a single lookup.

        Returns:
            The resolved identity, and the immutable id it resolved to — None
            when the version *is* the immutable reference and there is nothing
            further to pin.

        Raises:
            VersionNotFoundError: If nothing satisfies the range.
            SourceUnavailableError: If the source cannot be read at all.
        """
        return self.resolve_version(coordinate, spec), None

    def can_fetch_offline(self, artifact_id: ArtifactId, commit: str | None) -> bool:
        """Whether this locked version is already in hand, needing no network.

        **This decides whether the network is needed, never whether the lock is
        obeyed.** The lock is obeyed because it is the lock; a caller that
        conditioned that on this answer would make a pinned build depend on
        machine-local cache state, so the same lock and the same manifest would
        resolve to one thing on a developer's warm machine and another on a
        fresh CI runner (PRO-164).

        False by default: a source that cannot promise a cached copy must not be
        treated as though it can.
        """
        return False

    def fetch_locked(self, artifact_id: ArtifactId, commit: str | None) -> FetchedArtifact:
        """Fetch exactly what a lock recorded, cached or not.

        Defaults to :meth:`fetch`, which is exact for any source whose versions
        cannot move. Still integrity-checked either way.

        Implementations reach the source when they must: this is what the lock
        names, so a cold cache is a reason to fetch it, not a reason to resolve
        something else.

        Raises:
            SourceUnavailableError: If the pinned artifact is not in hand and
                the source cannot be reached.
        """
        return self.fetch(artifact_id)
