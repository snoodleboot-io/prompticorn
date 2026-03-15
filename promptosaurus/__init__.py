"""promptosaurus — prompt library build tool."""

from sweet_tea.registry import Registry

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("promptosaurus")
except PackageNotFoundError:
    __version__ = "unknown"

# sweet_tea auto-registers all imported classes
Registry.fill_registry(library="promptosaurus")
