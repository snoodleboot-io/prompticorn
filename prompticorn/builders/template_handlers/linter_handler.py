"""Handler for LINTER template variable."""

from typing import Any

from prompticorn.builders.template_handlers.template_handler import TemplateHandler


class LinterHandler(TemplateHandler):
    """Handler for LINTER template variable."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "LINTER"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return str(config.get("linter", ""))
