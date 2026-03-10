"""promptosaurus — prompt library build tool."""

from importlib.metadata import version

from sweet_tea.registry import Registry

__version__ = version("promptosaurus")

# sweet_tea auto-registers all imported classes
Registry.fill_registry(library="promptosaurus")
