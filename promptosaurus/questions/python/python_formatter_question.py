"""Question for selecting Python formatter."""

from promptosaurus.questions.base.question import Question


class PythonFormatterQuestion(Question):
    """Question handler for Python formatter selection."""

    @property
    def key(self) -> str:
        """Unique identifier for this question."""
        return "python_formatter"

    @property
    def question_text(self) -> str:
        """What to ask the user."""
        return "What formatter?"

    @property
    def explanation(self) -> str:
        """Why we're asking this."""
        return "Select your preferred code formatter for consistent style."

    @property
    def options(self) -> list[str]:
        """Available formatters."""
        return ["ruff", "black", "yapf", "autopep8"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "ruff"

    @property
    def allow_multiple(self) -> bool:
        """Allow multiple formatters."""
        return True

    @property
    def option_explanations(self) -> dict[str, str]:
        """Explanations for each option."""
        return {
            "ruff": "Fast, opinionated, Rust-based",
            "black": "Uncompromising, deterministic formatting",
            "yapf": "Knobs for customization",
            "autopep8": "Auto-fix PEP 8 violations",
        }
