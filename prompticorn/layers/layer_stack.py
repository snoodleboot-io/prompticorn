"""Ordering providers into one resolver (PRO-117).

`ContentResolver` already composes an ordered stack with first-wins semantics
(PRO-106). This supplies what it was missing: *which* sources, in *which* order,
for a given project — and a way for a package to add a layer without core
importing it.

**The ordering trap, stated once.** Precedence is "higher wins", but
`ContentResolver` consults sources in order and takes the first that holds a
unit. So the stack is built highest-precedence *first*. Built the other way,
the bundled library silently wins over every override, and any test that only
checks one layer at a time still passes. `TestLayerBoundaryMatrix` exists to
make that mistake fail.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from importlib.metadata import entry_points

from prompticorn.content.content_resolver import ContentResolver
from prompticorn.layers.builtin_layer_provider import BuiltinLayerProvider
from prompticorn.layers.layer import Layer
from prompticorn.layers.layer_context import LayerContext
from prompticorn.layers.layer_provider import LayerProvider
from prompticorn.layers.project_layer_provider import ProjectLayerProvider
from prompticorn.layers.user_layer_provider import UserLayerProvider

ENTRY_POINT_GROUP = "prompticorn.layer_providers"


class DuplicateLayerProviderError(ValueError):
    """Two providers claimed the same name.

    Raised rather than resolved by picking one: which of two same-named layers
    wins would otherwise depend on install order, which nobody chose.
    """


@dataclass(frozen=True)
class LayerStack:
    """An ordered set of layer providers.

    Attributes:
        providers: In any order; they are sorted by precedence when used.
    """

    providers: tuple[LayerProvider, ...]

    @classmethod
    def default(cls, extra: Iterable[LayerProvider] = ()) -> LayerStack:
        """The OSS layers, plus anything registered through entry points.

        A core-only install registers nothing and resolves the local layers —
        builtin and project — which is a complete, working answer rather than a
        degraded one.
        """
        built_in: list[LayerProvider] = [
            BuiltinLayerProvider(),
            ProjectLayerProvider(),
            UserLayerProvider(),
        ]
        return cls(providers=tuple(_unique([*built_in, *discover_providers(), *extra])))

    def layers(self, context: LayerContext) -> tuple[Layer, ...]:
        """The layers that contribute for this project, highest precedence first.

        Ties on precedence break by name, so the order never depends on the
        sequence providers were registered in.
        """
        provided = [
            layer for provider in self.providers if (layer := provider.provide(context)) is not None
        ]
        return tuple(sorted(provided, key=lambda layer: (-layer.precedence, layer.name)))

    def resolver(self, context: LayerContext) -> ContentResolver:
        """A content resolver over this project's layers.

        Sources are flattened highest-precedence first, because the resolver
        takes the first source that holds a unit.
        """
        return ContentResolver(
            sources=[source for layer in self.layers(context) for source in layer.sources]
        )

    def describe(self, context: LayerContext) -> list[str]:
        """Active layers, highest first, for a human reading `status`."""
        return [f"{layer.name} ({layer.precedence})" for layer in self.layers(context)]


def discover_providers() -> list[LayerProvider]:
    """Providers registered under :data:`ENTRY_POINT_GROUP`.

    Each entry point may name a provider class or an instance. A provider that
    fails to load is skipped rather than allowed to break every command — a
    broken plugin should cost its own layer, not the tool.
    """
    found: list[LayerProvider] = []
    for entry in _entry_points():
        try:
            loaded = entry.load()
            provider = loaded() if isinstance(loaded, type) else loaded
        except Exception:  # noqa: BLE001 - a bad plugin must not take the CLI down
            continue
        if isinstance(provider, LayerProvider):
            found.append(provider)
    return found


def _entry_points() -> Sequence:
    return tuple(entry_points(group=ENTRY_POINT_GROUP))


def _unique(providers: Iterable[LayerProvider]) -> list[LayerProvider]:
    seen: set[str] = set()
    unique: list[LayerProvider] = []
    for provider in providers:
        if provider.name in seen:
            raise DuplicateLayerProviderError(
                f"two layer providers are both named {provider.name!r}"
            )
        seen.add(provider.name)
        unique.append(provider)
    return unique
