"""Something that contributes a layer to the stack (PRO-117).

The seam EE plugs into. A provider is registered under the
``prompticorn.layer_providers`` entry-point group, so an ``org`` or ``team``
layer arrives by installing a package — core never imports it, and there is no
fork of the resolver to maintain.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from prompticorn.layers.layer import Layer
from prompticorn.layers.layer_context import LayerContext


class LayerProvider(ABC):
    """Contributes zero or one layer for a given project."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique among providers. Two providers with one name is a
        configuration error, not a tie to break silently."""

    @property
    @abstractmethod
    def precedence(self) -> int:
        """Where this provider's layer sits; higher wins."""

    @abstractmethod
    def provide(self, context: LayerContext) -> Layer | None:
        """This provider's layer for the project, or None to contribute nothing.

        None is an ordinary answer — a project with no override directory, an
        org provider with no org configured. Absence must never be an error.
        """
