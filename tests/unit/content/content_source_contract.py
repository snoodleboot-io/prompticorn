"""The contract every ContentSource implementation must satisfy (PRO-104).

Written once. The git source, local-directory source, and pack source all reuse
it unchanged by subclassing and supplying a source — so "does this behave like a
source?" is answered the same way for all of them, and a new implementation
cannot quietly define its own semantics.

Usage::

    class TestMySource(ContentSourceContract):
        @pytest.fixture
        def source(self):
            return MySource(...)
"""

from __future__ import annotations

import pytest

from prompticorn.content import (
    ContentSource,
    ContentUnit,
    UnitId,
    UnitNotFoundError,
    digest_text,
)

# A well-formed ID that no real source is expected to carry.
ABSENT_UNIT = UnitId.parse("skill/definitely-not-a-real-unit-pro104/minimal")


class ContentSourceContract:
    """Behaviour required of every source. Subclass and provide a ``source``."""

    @pytest.fixture
    def source(self) -> ContentSource:  # pragma: no cover - overridden
        raise NotImplementedError("provide a `source` fixture")

    # -- enumeration -----------------------------------------------------

    def test_units_are_content_units(self, source):
        for unit in source.units():
            assert isinstance(unit, ContentUnit)
            assert isinstance(unit.id, UnitId)

    def test_units_are_sorted_by_rendered_id(self, source):
        """Order feeds lockfiles and golden output — it must not depend on the
        filesystem's enumeration order."""
        rendered = [unit.id.render() for unit in source.units()]
        assert rendered == sorted(rendered)

    def test_units_are_unique(self, source):
        rendered = [unit.id.render() for unit in source.units()]
        assert len(rendered) == len(set(rendered))

    def test_enumeration_is_repeatable(self, source):
        assert [u.id for u in source.units()] == [u.id for u in source.units()]

    def test_every_unit_declares_the_sources_layer(self, source):
        for unit in source.units():
            assert unit.layer == source.name

    def test_unit_kind_agrees_with_its_id(self, source):
        for unit in source.units():
            assert unit.kind is unit.id.kind

    # -- reading ---------------------------------------------------------

    def test_every_enumerated_unit_is_readable(self, source):
        """Enumeration and reading must not drift: anything listed can be read."""
        for unit in source.units():
            assert isinstance(source.read(unit.id), str)

    def test_reads_are_repeatable(self, source):
        for unit in list(source.units())[:20]:
            assert source.read(unit.id) == source.read(unit.id)

    def test_has_agrees_with_units(self, source):
        for unit in list(source.units())[:20]:
            assert source.has(unit.id)

    def test_missing_unit_raises_unit_not_found(self, source):
        assert not source.has(ABSENT_UNIT)
        with pytest.raises(UnitNotFoundError) as exc:
            source.read(ABSENT_UNIT)
        assert exc.value.unit_id == ABSENT_UNIT.render()
        assert exc.value.source == source.name

    # -- digest ----------------------------------------------------------

    def test_digest_matches_canonical_hash_of_read(self, source):
        """A source may cache or precompute digests, but it must not invent its
        own — two sources holding identical content have to agree."""
        for unit in list(source.units())[:20]:
            assert source.digest(unit.id) == digest_text(source.read(unit.id))

    def test_digest_is_stable_across_calls(self, source):
        for unit in list(source.units())[:20]:
            assert source.digest(unit.id) == source.digest(unit.id)

    def test_digest_is_hex_sha256(self, source):
        for unit in list(source.units())[:10]:
            value = source.digest(unit.id)
            assert len(value) == 64
            assert all(c in "0123456789abcdef" for c in value)

    def test_digest_of_missing_unit_raises(self, source):
        with pytest.raises(UnitNotFoundError):
            source.digest(ABSENT_UNIT)

    # -- identity --------------------------------------------------------

    def test_name_is_a_non_empty_string(self, source):
        assert isinstance(source.name, str)
        assert source.name
