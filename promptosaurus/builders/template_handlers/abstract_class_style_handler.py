"""Handler for ABSTRACT_CLASS_STYLE template variable."""

from typing import Any

from promptosaurus.builders.template_handlers.template_handler import TemplateHandler


class AbstractClassStyleHandler(TemplateHandler):
    """Handler for ABSTRACT_CLASS_STYLE template variable."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "ABSTRACT_CLASS_STYLE"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return str(config.get("abstract_class_style", ""))
