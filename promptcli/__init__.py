"""promptcli — prompt library build tool."""

from pathlib import Path as _Path

from sweet_tea.registry import Registry


def fill_registry():
    """Register all builders with sweet_tea."""
    # Get the path to the builders directory
    builders_path = str(_Path(__file__).parent / "builders")
    Registry.fill_registry(
        path=builders_path,
        module="promptcli.builders",
        library="promptcli"
    )
