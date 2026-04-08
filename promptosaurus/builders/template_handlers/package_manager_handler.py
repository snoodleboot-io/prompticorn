"""Handler for PACKAGE_MANAGER template variable."""

from typing import Any

from promptosaurus.builders.template_handlers.template_handler import TemplateHandler


class PackageManagerHandler(TemplateHandler):
    """Handler for PACKAGE_MANAGER template variable."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name == "PACKAGE_MANAGER"

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        return str(config.get("package_manager", ""))
