"""Overrides committed to the project, under ``.prompticorn/content/`` (PRO-117).

The layer a team uses to adjust a bundled agent for one repository. Committed
with the code, so every checkout resolves it the same way and the lock it
produces is the same on every machine.
"""

from __future__ import annotations

from prompticorn.config_handler import ConfigHandler
from prompticorn.content.directory_content_source import DirectoryContentSource
from prompticorn.layers.layer import Layer
from prompticorn.layers.layer_context import LayerContext
from prompticorn.layers.layer_precedence import LayerPrecedence
from prompticorn.layers.layer_provider import LayerProvider

PROJECT_LAYER = "project"
CONTENT_DIRNAME = "content"


class ProjectLayerProvider(LayerProvider):
    """Contributes ``.prompticorn/content/`` when the project has one."""

    @property
    def name(self) -> str:
        return PROJECT_LAYER

    @property
    def precedence(self) -> int:
        return LayerPrecedence.PROJECT

    def provide(self, context: LayerContext) -> Layer | None:
        root = context.project_root / ConfigHandler.DEFAULT_CONFIG_DIR.name / CONTENT_DIRNAME
        source = DirectoryContentSource(root=root, layer=self.name)
        if not source.is_present:
            return None
        return Layer(name=self.name, precedence=self.precedence, sources=(source,))
