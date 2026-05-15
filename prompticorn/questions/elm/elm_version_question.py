# Elm version question

from prompticorn.questions.base.question import Question


class ElmVersionQuestion(Question):
    """Question handler for Elm version."""

    @property
    def key(self) -> str:
        return "elm_version"

    @property
    def question_text(self) -> str:
        return "What Elm version do you want to use?"

    @property
    def explanation(self) -> str:
        return """Elm version determines language features and package compatibility.

- Elm 0.19 is the current major version with significant improvements
- It features a smaller runtime, faster compilation, and better error messages
- The Elm architecture provides a reliable frontend development experience"""

    @property
    def options(self) -> list[str]:
        """Available options."""
        return ["0.19.1", "0.19.0"]

    @property
    def default(self) -> str:
        """Default selection."""
        return "0.19.1"

    config_key = "runtime"
