# Python coverage targets question

from promptosaurus.questions.base.question import Question


class PythonCoverageTargetsQuestion(Question):
    """Question for Python code coverage targets."""

    _coverage_presets = {
        "strict": '{"line": 90, "branch": 80, "function": 95, "statement": 90, "mutation": 85, "path": 70}',
        "standard": '{"line": 80, "branch": 70, "function": 90, "statement": 85, "mutation": 80, "path": 60}',
        "minimal": '{"line": 70, "branch": 60, "function": 80, "statement": 75, "mutation": 70, "path": 50}',
    }

    @property
    def key(self) -> str:
        return "coverage"

    @property
    def question_text(self) -> str:
        return "What code coverage targets do you want to enforce?"

    @property
    def explanation(self) -> str:
        return """Coverage targets define the minimum acceptable test coverage for your project.
Higher coverage ensures better code quality but requires more test effort.
These targets are used by pytest-cov and enforced in CI/CD pipelines."""

    @property
    def options(self) -> list[str]:
        return list(self._coverage_presets.keys())

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "strict": "Line: 90%, Branch: 80%, Function: 95%, Statement: 90%, Mutation: 85%, Path: 70% - For production libraries",
            "standard": "Line: 80%, Branch: 70%, Function: 90%, Statement: 85%, Mutation: 80%, Path: 60% - Balanced approach (recommended)",
            "minimal": "Line: 70%, Branch: 60%, Function: 80%, Statement: 75%, Mutation: 70%, Path: 50% - For prototypes or legacy code",
        }

    @property
    def default(self) -> str:
        return "standard"

    def explain_option(self, option: str) -> str:
        """Get explanation for a specific option."""
        return self.option_explanations.get(option, "")

    def get_value(self, option: str) -> dict[str, int] | None:
        """
        Get the coverage targets for a given option.
        Returns a dict with coverage targets.
        """
        if option in self._coverage_presets:
            import json

            return json.loads(self._coverage_presets[option])
        return None
