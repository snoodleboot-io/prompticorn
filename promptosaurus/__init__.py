"""promptosaurus — prompt library build tool."""

from importlib.metadata import PackageNotFoundError, version

from sweet_tea.registry import Registry

try:
    __version__ = version("promptosaurus")
except PackageNotFoundError:
    __version__ = "unknown"

# sweet_tea auto-registers all imported classes
Registry.fill_registry(library="promptosaurus")
