"""The contract every ArtifactSource implementation must satisfy (PRO-124).

Written once, mirroring `tests/unit/content/content_source_contract.py`. A git
source and a hosted registry reuse it unchanged by subclassing and supplying a
source, so "does this behave like a source?" is answered the same way for all of
them and a new implementation cannot quietly define its own semantics.

Usage::

    class TestMySource(ArtifactSourceContract):
        @pytest.fixture
        def source(self):
            return MySource(...)

        @pytest.fixture
        def known(self, source):
            return next(iter(source.list_artifacts()))
"""

from __future__ import annotations

import pytest

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.semantic_version import SemanticVersion
from prompticorn.content.content_source import ContentSource
from prompticorn.sources import ArtifactNotFoundError, ArtifactSource, FetchedArtifact

# A well-formed identity no real source is expected to carry.
ABSENT = ArtifactId(
    namespace="local", name="definitely-not-real-pro124", version=SemanticVersion.parse("9.9.9")
)


class ArtifactSourceContract:
    """Behaviour required of every artifact source."""

    @pytest.fixture
    def source(self) -> ArtifactSource:  # pragma: no cover - overridden
        raise NotImplementedError("provide a `source` fixture")

    @pytest.fixture
    def known(self, source: ArtifactSource) -> ArtifactId:  # pragma: no cover - overridden
        raise NotImplementedError("provide a `known` fixture")

    # -- identity --------------------------------------------------------

    def test_name_is_a_non_empty_string(self, source):
        assert isinstance(source.name, str) and source.name

    # -- enumeration -----------------------------------------------------

    def test_lists_artifact_ids(self, source):
        for artifact in source.list_artifacts():
            assert isinstance(artifact, ArtifactId)

    def test_enumeration_is_repeatable(self, source):
        """Two listings of an unchanged source must agree, order included."""
        assert list(source.list_artifacts()) == list(source.list_artifacts())

    def test_enumeration_is_sorted(self, source):
        """Filesystem order differs between machines; the source must not."""
        rendered = [artifact.render() for artifact in source.list_artifacts()]
        assert rendered == sorted(rendered)

    def test_enumeration_is_unique(self, source):
        rendered = [artifact.render() for artifact in source.list_artifacts()]
        assert len(rendered) == len(set(rendered))

    def test_every_listed_artifact_is_present(self, source):
        for artifact in source.list_artifacts():
            assert source.has(artifact)

    def test_an_absent_artifact_is_not_present(self, source):
        assert not source.has(ABSENT)

    # -- fetching --------------------------------------------------------

    def test_every_listed_artifact_can_be_fetched(self, source):
        """Enumeration and retrieval must not drift: anything listed is readable."""
        for artifact in source.list_artifacts():
            fetched = source.fetch(artifact)
            assert isinstance(fetched, FetchedArtifact)
            assert fetched.identity == artifact

    def test_a_fetched_artifact_exposes_a_content_source(self, source, known):
        """So the resolver can layer it in without learning a second interface."""
        assert isinstance(source.fetch(known).content, ContentSource)

    def test_fetching_an_absent_artifact_raises(self, source):
        with pytest.raises(ArtifactNotFoundError):
            source.fetch(ABSENT)

    def test_fetch_verifies_the_digest(self, source, known):
        """The base class checks; this pins that the implementation did not
        override `fetch` and skip it."""
        fetched = source.fetch(known)
        assert fetched.computed_digest() == fetched.digest

    def test_fetches_are_repeatable(self, source, known):
        assert source.fetch(known).digest == source.fetch(known).digest

    # -- version resolution ----------------------------------------------

    def test_resolves_an_exact_version(self, source, known):
        assert source.resolve_version(known.coordinate, f"=={known.version.render()}") == known

    def test_versions_are_ordered_by_version_not_by_string(self, source, known):
        versions = source.versions_of(known.coordinate)
        assert list(versions) == sorted(versions, key=lambda artifact: artifact.version)
