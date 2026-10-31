"""The single place consumers ask for content (PRO-106).

Every consumer depends on this rather than on a filesystem path. Today it wraps
one source, so behaviour is unchanged; when packs and remote sources arrive they
are additional layers here and no consumer changes.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from prompticorn.content.builtin_content_source import BuiltinContentSource
from prompticorn.content.content_cache import ContentCache
from prompticorn.content.content_source import ContentSource
from prompticorn.content.content_unit import ContentUnit
from prompticorn.content.errors import UnitNotFoundError
from prompticorn.content.unit_id import UnitId
from prompticorn.content.unit_kind import UnitKind

RESOLVER_NAME = "resolver"


class ContentResolver:
    """Resolves unit IDs to text across an ordered stack of sources.

    Sources are consulted in order and the **first** that carries a unit wins,
    so a higher-priority layer shadows the bundled tree without removing it.

    Parameter slots are filled here (PRO-118), not by each builder, so no
    consumer can forget to — which is exactly how workflow and subagent
    overrides shipped broken in PRO-165. Configuration units are exempt: the
    slot schema and values are themselves configuration, and filling them would
    be circular.

    Still to come in the resolver milestone: patch operations and resolution
    traces.
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
        # units() is a full walk of every layer; memoised because the stack is
        # fixed for this resolver's lifetime (one per command) and discovery
        # asks per agent. Without it a build walked the tree ~290k times.
        self._units_memo: list[ContentUnit] | None = None
        # Slot schema and values, loaded on first use and then fixed. Typed
        # loosely to avoid importing slots at module scope: slots imports
        # ConfigurationDocument, which imports this module. (PRO-118)
        self._slot_schema: Any = None
        self._slot_values: Any = None

    @property
    def name(self) -> str:
        """What this composite calls itself in errors (PRO-117).

        Present so a resolver can be checked against the ContentSource contract
        as a composite — it answers every question a single source does, over
        the whole stack.
        """
        return RESOLVER_NAME

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
        text = self._fill_slots(unit_id, source.read(unit_id))
        self._cache.put(source.name, unit_id, text)
        return text

    def _fill_slots(self, unit_id: UnitId, text: str) -> str:
        """``text`` with its declared slots filled (PRO-118).

        Configuration units are returned untouched: the slot schema and the
        slot values are configuration themselves, so filling them would ask
        this method to resolve the documents it depends on.

        The schema and values are loaded once per resolver and cached, because
        the layer stack is fixed for a resolver's lifetime and ``read`` is
        called once per unit per build — reloading would reparse two YAML
        documents hundreds of times, which is the shape of the regression
        PRO-168 fixed in ``units()``.
        """
        if unit_id.kind is UnitKind.CONFIGURATION:
            return text
        if "<<slot:" not in text:
            return text
        from prompticorn.content import slots

        if self._slot_schema is None:
            self._slot_schema = slots.SlotSchema.load()
            self._slot_values = slots.SlotValues.load()
        assert self._slot_values is not None
        return slots.fill(unit_id, text, self._slot_schema, self._slot_values)

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
        if self._units_memo is None:
            winners: dict[str, ContentUnit] = {}
            for source in self._sources:
                for unit in source.units():
                    winners.setdefault(unit.id.render(), unit)
            self._units_memo = [winners[key] for key in sorted(winners)]
        return list(self._units_memo)

    def owner_of(self, unit_id: UnitId) -> ContentSource | None:
        """The source that wins for this unit, or None when nothing carries it.

        Public because "which layer won, and where does its copy live" is a
        question about one unit, and answering it by enumerating the whole stack
        reads every layer to learn something a single lookup already knows.
        Callers that only want the name should use :meth:`layer_of`.
        """
        return self._owner(unit_id)

    def layer_of(self, unit_id: UnitId) -> str | None:
        """Name of the layer that wins for this unit, or None."""
        source = self._owner(unit_id)
        return None if source is None else source.name

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


def install_resolver(resolver: ContentResolver) -> None:
    """Make ``resolver`` the one every consumer reads through (PRO-117).

    The CLI installs a project's layer stack here before a command runs, so the
    builders and the lock resolver — which both read through
    :func:`default_resolver` — see the same layers without either being told
    about them. Pair with :func:`reset_default_resolver` when the command ends.
    """
    global _default_resolver
    _default_resolver = resolver


def read_configuration(name: str) -> str:
    """Text of a bundled configuration YAML, by name.

    A convenience over the resolver for the many consumers that want exactly one
    configuration document. Keeps them from re-deriving `configuration/{name}`
    and, more importantly, from reaching for a filesystem path. (PRO-106)
    """
    return default_resolver().read(UnitId.parse(f"configuration/{name}"))


def read_core_convention(name: str) -> str | None:
    """Text of a core convention (``system``, ``conventions``, …), or None."""
    return default_resolver().read_optional(UnitId.parse(f"convention/core/{name}"))


def read_language_convention(language: str) -> str | None:
    """Text of a language convention, or None when the language has none.

    An illegal segment (uppercase, punctuation) is a miss rather than an error:
    a config may name a language that was never a unit.
    """
    from prompticorn.content.errors import InvalidUnitIdError

    try:
        unit_id = UnitId.parse(f"convention/language/{language}")
    except InvalidUnitIdError:
        return None
    return default_resolver().read_optional(unit_id)


def available_convention_languages() -> list[str]:
    """Every language with a bundled convention, sorted."""
    return sorted(
        unit.id.segments[1]
        for unit in default_resolver().units()
        if unit.kind is UnitKind.CONVENTION and unit.id.segments[0] == "language"
    )


def read_variant_unit(kind: UnitKind, name: str, variant: str) -> str | None:
    """Text of a variant-addressed unit, falling back to the other variant.

    The fallback matches long-standing builder behaviour: a unit authored in one
    variant only is still emitted rather than silently dropped.
    """
    from prompticorn.content.errors import InvalidUnitIdError

    resolver = default_resolver()
    other = "verbose" if variant == "minimal" else "minimal"
    for candidate in (variant, other):
        try:
            unit_id = UnitId.parse(f"{kind.value}/{name}/{candidate}")
        except InvalidUnitIdError:
            return None
        text = resolver.read_optional(unit_id)
        if text is not None:
            return text
    return None
