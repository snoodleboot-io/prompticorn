# Python linter question

from promptcli.questions.base import Question


class PythonLinterQuestion(Question):
    """Question for Python linter - supports multiple selection."""

    @property
    def key(self) -> str:
        return "python_linter"

    @property
    def question_text(self) -> str:
        return "What linter(s) do you want to use?"

    @property
    def explanation(self) -> str:
        return """Linters check code quality, style, and bugs. You can select multiple:
- ruff: Ultra-fast (Rust), modern, replaces flake8+isort
- flake8: Classic, simple, stable rules
- pylint: Comprehensive deep analysis, very strict
- mypy: Static type checker for Python"""

    @property
    def options(self) -> list[str]:
        return ["ruff", "flake8", "pylint", "mypy"]

    @property
    def option_explanations(self) -> dict[str, str]:
        return {
            "ruff": "Ultra-fast (Rust) - modern, replaces flake8+isort, recommended",
            "flake8": "Classic - simple, stable, good default rules",
            "pylint": "Comprehensive - deep analysis, strict, many rules",
            "mypy": "Type checker - optional static typing enforcement",
        }

    @property
    def default(self) -> str:
        return "ruff"

    @property
    def allow_multiple(self) -> bool:
        """Allow selecting multiple linters."""
        return True
