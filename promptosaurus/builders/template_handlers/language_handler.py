"""Handler for LANGUAGE template variable."""

from typing import Any

from promptosaurus.builders.template_handlers.template_handler import TemplateHandler


class LanguageHandler(TemplateHandler):
    """Handler for LANGUAGE template variable."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "LANGUAGE"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return str(config.get("language", ""))
