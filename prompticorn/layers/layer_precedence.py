"""Where each layer sits in the stack (PRO-117).

Higher wins. The numbers are spaced so a provider can slot between two named
positions without renumbering everything — a gap is cheaper than a migration.

``ORG`` and ``TEAM`` are reserved and empty in OSS. They exist as named seams so
EE injects into the *same* engine through a provider rather than forking it.
"""

from __future__ import annotations

from enum import IntEnum


class LayerPrecedence(IntEnum):
    """Position in the layer stack; the highest precedence that holds a unit wins."""

    BUILTIN = 0
    ARTIFACTS = 10
    ORG = 20
    TEAM = 30
    PROJECT = 40
    USER = 50
