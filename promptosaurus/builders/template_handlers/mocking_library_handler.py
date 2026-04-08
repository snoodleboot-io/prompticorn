"""Handler for MOCKING_LIBRARY template variable."""

from typing import Any

from promptosaurus.builders.template_handlers.template_handler import TemplateHandler


class MockingLibraryHandler(TemplateHandler):
    """Handler for MOCKING_LIBRARY template variable."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "MOCKING_LIBRARY"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return str(config.get("mocking_library", ""))
