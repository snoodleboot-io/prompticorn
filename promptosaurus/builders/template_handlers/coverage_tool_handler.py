"""Handler for COVERAGE_TOOL template variable."""

from typing import Any

from promptosaurus.builders.template_handlers.template_handler import TemplateHandler


class CoverageToolHandler(TemplateHandler):
    """Handler for COVERAGE_TOOL template variable."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "COVERAGE_TOOL"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return str(config.get("coverage_tool", ""))
