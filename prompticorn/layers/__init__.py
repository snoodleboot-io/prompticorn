"""The content layer stack: which sources a project resolves from, in what order.

Highest precedence wins. The bundled library is the bottom; a project's own
``.prompticorn/content/`` overrides it; ``org`` and ``team`` positions are
reserved for providers that EE registers through the
``prompticorn.layer_providers`` entry point, without core importing them.
"""

from prompticorn.layers.builtin_layer_provider import BuiltinLayerProvider
from prompticorn.layers.layer import Layer
from prompticorn.layers.layer_context import LayerContext
from prompticorn.layers.layer_precedence import LayerPrecedence
from prompticorn.layers.layer_provider import LayerProvider
from prompticorn.layers.layer_stack import (
    ENTRY_POINT_GROUP,
    DuplicateLayerProviderError,
    LayerStack,
    discover_providers,
)
from prompticorn.layers.project_layer_provider import PROJECT_LAYER, ProjectLayerProvider
from prompticorn.layers.user_layer_provider import ENABLE_VARIABLE, USER_LAYER, UserLayerProvider

__all__ = [
    "ENABLE_VARIABLE",
    "ENTRY_POINT_GROUP",
    "PROJECT_LAYER",
    "USER_LAYER",
    "BuiltinLayerProvider",
    "DuplicateLayerProviderError",
    "Layer",
    "LayerContext",
    "LayerPrecedence",
    "LayerProvider",
    "LayerStack",
    "ProjectLayerProvider",
    "UserLayerProvider",
    "discover_providers",
]
