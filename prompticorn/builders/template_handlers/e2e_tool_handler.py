"""Handler for E2E_TOOL template variable."""

from typing import Any

from prompticorn.builders.template_handlers.template_handler import TemplateHandler


class E2EToolHandler(TemplateHandler):
    """Handler for E2E_TOOL template variable."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "E2E_TOOL"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return str(config.get("e2e_tool", ""))
