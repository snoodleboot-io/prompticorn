"""Handler for MUTATION_TOOL template variable."""

from typing import Any

from promptosaurus.builders.template_handlers.template_handler import TemplateHandler


class MutationToolHandler(TemplateHandler):
    """Handler for MUTATION_TOOL template variable."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "MUTATION_TOOL"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return str(config.get("mutation_tool", ""))
