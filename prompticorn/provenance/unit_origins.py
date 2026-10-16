"""Which layer supplied each unit a build read, and at what version (PRO-165).

``layer`` in a provenance header is documented as "which layer won". That was a
constant for as long as ``builtin`` was the only possible answer; once a project
layer can override a unit it is a per-unit fact, and the build already knows it —
``ContentUnit.layer`` carries it, and ``prompticorn.lock`` records it from the
same place. A per-build constant made the two disagree about the same unit in the
same run: the lock said ``project`` and the file's own header said ``builtin``.

The version stamp has the same shape of error for the same reason. The bundled
package version describes bundled content; it says nothing true about a file that
came out of somebody's ``.prompticorn/content/``. That content is not versioned at
all, and this says so rather than borrowing a number from a layer that lost.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from prompticorn.content.content_resolver import ContentResolver
from prompticorn.content.content_unit import BUILTIN_LAYER

# What to stamp for content that has no version. A directory layer is a working
# tree, not a release: there is no number to report, and inventing one would put
# a version in the header that nothing could ever be compared against.
#
# An artifact layer is the exception that needs no special case — it names itself
# by its rendered identity, `namespace/name@version`, so the version it supplied
# is already in the `layer` field.
UNVERSIONED = "unversioned"


@dataclass(frozen=True)
class UnitOrigins:
    """The layer that won for each unit, and the version to stamp for it.

    Attributes:
        layers: Rendered unit id to the name of the layer that supplied it.
        bundled_version: The version to report for units that came from the
            bundled library.
        fallback_layer: What to report for an attributed output that names no
            real unit. Aggregates (``generated/...``) are assembled from many
            units and belong to no single layer; the bundled library is the
            honest answer for them because the templates that assemble them ship
            with the package.
    """

    layers: Mapping[str, str] = field(default_factory=dict)
    bundled_version: str = UNVERSIONED
    fallback_layer: str = BUILTIN_LAYER

    @classmethod
    def from_resolver(cls, resolver: ContentResolver, bundled_version: str) -> UnitOrigins:
        """Snapshot the winners from the resolver the build read through.

        Taken from the resolver rather than recomputed per file so that the
        header, the sidecar and the lock are three renderings of one answer.

        Args:
            resolver: The stack the build resolved content from.
            bundled_version: Version to report for bundled units.
        """
        return cls(
            layers={unit.id.render(): unit.layer for unit in resolver.units()},
            bundled_version=bundled_version,
        )

    def layer_of(self, unit: str) -> str:
        """Which layer supplied ``unit``."""
        return self.layers.get(unit, self.fallback_layer)

    def version_of(self, unit: str) -> str:
        """The version to stamp for ``unit``."""
        return self.bundled_version if self.layer_of(unit) == BUILTIN_LAYER else UNVERSIONED
