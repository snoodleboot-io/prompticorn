"""The single place consumers ask for content (PRO-106).

Every consumer depends on this rather than on a filesystem path. Today it wraps
one source, so behaviour is unchanged; when packs and remote sources arrive they
are additional layers here and no consumer changes.
"""

from __future__ import annotations

from collections.abc import Sequence

from prompticorn.content.builtin_content_source import BuiltinContentSource
from prompticorn.content.content_cache import ContentCache
from prompticorn.content.content_source import ContentSource
from prompticorn.content.content_unit import ContentUnit
from prompticorn.content.errors import UnitNotFoundError
from prompticorn.content.unit_id import UnitId

RESOLVER_NAME = "resolver"


class ContentResolver:
    """Resolves unit IDs to text across an ordered stack of sources.

    Sources are consulted in order and the **first** that carries a unit wins,
    so a higher-priority layer shadows the bundled tree without removing it.
    Full override semantics — patching, parameter slots, resolution traces —
    belong to the resolver milestone; this is deliberately the minimum that lets
    consumers stop touching the filesystem.
    """

    def __init__(
        self,
        sources: Sequence[ContentSource] | None = None,
        cache: ContentCache | None = None,
    ) -> None:
        self._sources: tuple[ContentSource, ...] = tuple(
            sources if sources is not None else (BuiltinContentSource(),)
        )
        self._cache = cache if cache is not None else ContentCache()

    @property
    def sources(self) -> tuple[ContentSource, ...]:
        return self._sources

    @property
    def cache(self) -> ContentCache:
        return self._cache

    def read(self, unit_id: UnitId) -> str:
        """Text of the winning unit.

        Raises:
            UnitNotFoundError: If no source carries it.
        """
        source = self._owner(unit_id)
        if source is None:
            raise UnitNotFoundError(unit_id.render(), RESOLVER_NAME)
        cached = self._cache.get(source.name, unit_id)
        if cached is not None:
            return cached
        text = source.read(unit_id)
        self._cache.put(source.name, unit_id, text)
        return text

    def read_optional(self, unit_id: UnitId) -> str | None:
        """Text, or None when absent.

        For genuinely optional content. Callers that need a hard failure must
        use :meth:`read` — swallowing a miss is how missing content becomes
        silently truncated output.
        """
        try:
            return self.read(unit_id)
        except UnitNotFoundError:
            return None

    def digest(self, unit_id: UnitId) -> str:
        source = self._owner(unit_id)
        if source is None:
            raise UnitNotFoundError(unit_id.render(), RESOLVER_NAME)
        return source.digest(unit_id)

    def has(self, unit_id: UnitId) -> bool:
        return self._owner(unit_id) is not None

    def units(self) -> list[ContentUnit]:
        """Every resolvable unit, shadowed entries removed, sorted by ID.

        Sorted because this feeds discovery and lockfiles; enumeration order
        must not depend on the filesystem.
        """
        winners: dict[str, ContentUnit] = {}
        for source in self._sources:
            for unit in source.units():
                winners.setdefault(unit.id.render(), unit)
        return [winners[key] for key in sorted(winners)]

    def _owner(self, unit_id: UnitId) -> ContentSource | None:
        for source in self._sources:
            if source.has(unit_id):
                return source
        return None


_default_resolver: ContentResolver | None = None


def default_resolver() -> ContentResolver:
    """The process-wide resolver over the bundled tree.

    A module-level singleton so the cache is shared rather than rebuilt per
    consumer. Tests that need isolation construct their own, or call
    ``default_resolver().cache.clear()``.
    """
    global _default_resolver
    if _default_resolver is None:
        _default_resolver = ContentResolver()
    return _default_resolver


def reset_default_resolver() -> None:
    """Drop the singleton. For tests that swap the bundled tree."""
    global _default_resolver
    _default_resolver = None
