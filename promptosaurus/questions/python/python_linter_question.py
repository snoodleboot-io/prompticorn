"""Question for selecting Python linter."""

from promptosaurus.questions.base.question import Question


class PythonLinterQuestion(Question):
    """Question handler for Python linter selection."""

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "python_linter"

    @property
    def question_text(self) -> str:
        """What to ask the user."""
        return "What linter?"

    @property
    def explanation(self) -> str:
        """Why we're asking this."""
        return "Select your preferred linter for code quality analysis."

    @property
    def options(self) -> list[str]:
        """Available linters."""
        return ["ruff", "flake8", "pylint", "pyright"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "ruff"

    @property
    def allow_multiple(self) -> bool:
        """Allow multiple linters."""
        return True

    @property
    def option_explanations(self) -> dict[str, str]:
        """Explanations for each option."""
        return {
            "ruff": "Fast, Rust-based, replaces many tools",
            "flake8": "Extensible, community plugins",
            "pylint": "Comprehensive, highly configurable",
            "pyright": "Static type checker, strict mode available",
        }
