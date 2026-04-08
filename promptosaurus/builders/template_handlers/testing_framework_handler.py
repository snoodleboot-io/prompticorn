from typing import Any

from promptosaurus.builders.template_handlers.template_handler import TemplateHandler


class TestingFrameworkHandler(TemplateHandler):
    """Handler for TESTING_FRAMEWORK template variable."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "TESTING_FRAMEWORK"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return str(config.get("test_framework", ""))
