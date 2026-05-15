from typing import Any

from prompticorn.builders.template_handlers.template_handler import TemplateHandler


class CoverageHandler(TemplateHandler):
    """Handler for coverage-related template variables."""

    def can_handle(self, variable_name: str) -> bool:
        return variable_name in {
            "LINE_COVERAGE_%",
            "BRANCH_COVERAGE_%",
            "FUNCTION_COVERAGE_%",
            "STATEMENT_COVERAGE_%",
            "MUTATION_COVERAGE_%",
            "PATH_COVERAGE_%",
        }

    def handle(self, variable_name: str, config: dict[str, Any]) -> str:
        # Coverage can be either a dict (legacy) or a string preset from the question
        coverage_value = config.get("coverage", {})

        # If coverage is a string preset, convert it to a dict
        if isinstance(coverage_value, str):
            COVERAGE_PRESETS = {
                "strict": {
                    "line": 90,
                    "branch": 80,
                    "function": 95,
                    "statement": 90,
                    "mutation": 85,
                    "path": 70,
                },
                "standard": {
                    "line": 80,
                    "branch": 70,
                    "function": 90,
                    "statement": 85,
                    "mutation": 80,
                    "path": 60,
                },
                "minimal": {
                    "line": 70,
                    "branch": 60,
                    "function": 80,
                    "statement": 75,
                    "mutation": 70,
                    "path": 50,
                },
            }
            coverage = COVERAGE_PRESETS.get(coverage_value, {})
        else:
            coverage = coverage_value if isinstance(coverage_value, dict) else {}

        # Map variable names to coverage keys
        variable_to_key = {
            "LINE_COVERAGE_%": "line",
            "BRANCH_COVERAGE_%": "branch",
            "FUNCTION_COVERAGE_%": "function",
            "STATEMENT_COVERAGE_%": "statement",
            "MUTATION_COVERAGE_%": "mutation",
            "PATH_COVERAGE_%": "path",
        }

        key = variable_to_key.get(variable_name)
        if key:
            return str(
                coverage.get(
                    key,
                    {
                        "line": 80,
                        "branch": 70,
                        "function": 90,
                        "statement": 85,
                        "mutation": 80,
                        "path": 60,
                    }.get(key, 0),
                )
            )

        return ""
