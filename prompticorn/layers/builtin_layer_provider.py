"""The bundled library, as the bottom layer (PRO-117)."""

from __future__ import annotations

from prompticorn.content.builtin_content_source import BuiltinContentSource
from prompticorn.content.content_unit import BUILTIN_LAYER
from prompticorn.layers.layer import Layer
from prompticorn.layers.layer_context import LayerContext
from prompticorn.layers.layer_precedence import LayerPrecedence
from prompticorn.layers.layer_provider import LayerProvider


class BuiltinLayerProvider(LayerProvider):
    """Always present. Everything else overrides it."""

    @property
    def name(self) -> str:
        return BUILTIN_LAYER

    @property
    def precedence(self) -> int:
        return LayerPrecedence.BUILTIN

    def provide(self, context: LayerContext) -> Layer | None:
        return Layer(name=self.name, precedence=self.precedence, sources=(BuiltinContentSource(),))
