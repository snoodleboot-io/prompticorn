# Python formatter question

from promptosaurus.questions.base.question import Question


class PythonFormatterQuestion(Question):
    """Question for Python formatter - supports multiple selection."""

    @property
    def key(self) -> str:
        return "python_formatter"

    @property
    def question_text(self) -> str:
        return "What code formatter(s) do you want to use?"

    @property
    def explanation(self) -> str:
        return """Formatters ensure consistent code style. You can select multiple:
- ruff: Fastest (Rust), format + lint in one tool
- black: Most popular, opinionated style
- yapf: Google style, configurable"""

    @property
    def options(self) -> list[str]:
        return ["ruff", "black", "yapf"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "ruff": "Fastest (Rust) - format + lint in one, recommended",
            "black": "Most popular - opinionated, consistent, widely adopted",
            "yapf": "Google style - configurable, good for existing codebases",
        }

    @property
    def default(self) -> str:
        return "ruff"

    @property
    def allow_multiple(self) -> bool:
        """Allow selecting multiple formatters."""
        return True
