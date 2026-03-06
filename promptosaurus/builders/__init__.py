"""
promptosaurus.builders
Builders for different AI assistant configurations.
"""

from promptosaurus.builders.kilo import KiloCodeBuilder
from promptosaurus.builders.kilo_cli import KiloCLIBuilder
from promptosaurus.builders.kilo_ide import KiloIDEBuilder

# Backwards compatibility alias
KiloBuilder = KiloCLIBuilder

__all__ = [
    "KiloCodeBuilder",
    "KiloCLIBuilder",
    "KiloIDEBuilder",
    "KiloBuilder",  # alias for backwards compatibility
]
