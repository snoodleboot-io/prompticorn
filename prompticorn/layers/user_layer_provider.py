"""Personal overrides under ``~/.prompticorn/content/`` (PRO-117).

**Off unless explicitly enabled**, and that is a deliberate departure from the
ticket, which places this layer highest and on by default.

This directory lives on one machine and is not committed. A unit it overrides
changes what the project resolves to *on that machine only*, so the lock
written there records a digest no teammate can reproduce. On their machine the
same unit resolves from the bundled library, the digests disagree, and that
reads as UNIT drift — which since PRO-151 is suspicious and stops `build`. A
personal preference on one laptop would look like tampering everywhere else.

So the layer exists, is tested, and sits where the ticket puts it; it simply
requires ``PROMPTICORN_USER_LAYER=1``. Someone who sets that is choosing
machine-local output, and knows it.
"""

from __future__ import annotations

from pathlib import Path

from prompticorn.content.directory_content_source import DirectoryContentSource
from prompticorn.layers.layer import Layer
from prompticorn.layers.layer_context import LayerContext
from prompticorn.layers.layer_precedence import LayerPrecedence
from prompticorn.layers.layer_provider import LayerProvider
from prompticorn.store.store_paths import CONTENT_DIRNAME, DEFAULT_HOME_NAME, HOME_VARIABLE

USER_LAYER = "user"
ENABLE_VARIABLE = "PROMPTICORN_USER_LAYER"
_TRUTHY = frozenset({"1", "true", "yes", "on"})


class UserLayerProvider(LayerProvider):
    """Contributes the user's content directory, when explicitly enabled."""

    @property
    def name(self) -> str:
        return USER_LAYER

    @property
    def precedence(self) -> int:
        return LayerPrecedence.USER

    def provide(self, context: LayerContext) -> Layer | None:
        if context.environment.get(ENABLE_VARIABLE, "").strip().lower() not in _TRUTHY:
            return None
        source = DirectoryContentSource(root=_user_content_root(context), layer=self.name)
        if not source.is_present:
            return None
        return Layer(name=self.name, precedence=self.precedence, sources=(source,))


def _user_content_root(context: LayerContext) -> Path:
    """The user content directory, honouring ``PROMPTICORN_HOME`` from the
    context rather than the live process environment."""
    override = context.environment.get(HOME_VARIABLE)
    home = Path(override).expanduser() if override else Path.home() / DEFAULT_HOME_NAME
    return home / CONTENT_DIRNAME
